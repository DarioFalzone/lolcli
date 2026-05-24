"""Adapter para `leagueoflegends.com` — fuente canónica de patch notes oficiales.

Estrategia (basada en el deep research):
1. Discovery: HTTP simple a `sitemap.xml` o índice por tags + Playwright con click
   en "Ver más" si hace falta. Filtra URLs que matcheen `/news/game-updates/patch-XX-YY-notes/`.
2. Extract: Playwright sobre cada URL, evalúa JS para obtener H1, fecha ISO, jerarquía
   H2/H3/H4 con bloques P/LI, imágenes y links.

Service workers se bloquean (`service_workers="block"`) — el deep research advierte
que pueden engullir eventos de red durante la inspección.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_TAG_INDEX_TEMPLATE = "https://www.leagueoflegends.com/{locale}/news/tags/patch-notes/"
_PATCH_URL_PATTERN = re.compile(
    r"/news/game-updates/(?:league-of-legends-)?patch-(\d+)-(\d+)([a-z]?)-notes",
    re.IGNORECASE,
)
"""Acepta ambos formatos de URL que usa Riot:
- Legacy: /news/game-updates/patch-26-3-notes (parches <= 26.3)
- Nuevo:  /news/game-updates/league-of-legends-patch-26-10-notes (parches >= 26.4)
"""

_EXTRACT_JS = r"""
() => {
  const root = document.querySelector('main') || document.body;
  const titleEl = root.querySelector('h1');
  const title = titleEl ? titleEl.textContent.trim() : '';

  let publishedAt = null;
  const timeEl = root.querySelector('time[datetime]');
  if (timeEl) {
    publishedAt = timeEl.getAttribute('datetime');
  } else {
    const candidates = [...root.querySelectorAll('span, p, div')]
      .map(n => n.textContent ? n.textContent.trim() : '')
      .find(t => /^\d{4}-\d{2}-\d{2}T/.test(t));
    if (candidates) publishedAt = candidates;
  }

  const images = [];
  for (const img of root.querySelectorAll('img')) {
    if (img.src) {
      images.push({
        src: img.src,
        alt: img.alt || null,
      });
    }
  }

  const links = [];
  for (const a of root.querySelectorAll('a[href]')) {
    const text = a.textContent ? a.textContent.trim() : '';
    if (text && a.href) {
      links.push({ text, href: a.href });
    }
  }

  const sections = [];
  let currentH2 = null;
  let currentH3 = null;
  let currentH4 = null;

  const buildSection = (level, t) => ({ heading_level: level, title: t, blocks: [], subsections: [] });

  for (const el of root.querySelectorAll('h2, h3, h4, p, li')) {
    const text = el.textContent ? el.textContent.trim() : '';
    if (!text) continue;
    const tag = el.tagName;
    if (tag === 'H2') {
      currentH2 = buildSection(2, text);
      currentH3 = null;
      currentH4 = null;
      sections.push(currentH2);
    } else if (tag === 'H3') {
      if (!currentH2) {
        currentH2 = buildSection(2, '');
        sections.push(currentH2);
      }
      currentH3 = buildSection(3, text);
      currentH4 = null;
      currentH2.subsections.push(currentH3);
    } else if (tag === 'H4') {
      if (!currentH3) {
        currentH3 = buildSection(3, '');
        if (!currentH2) {
          currentH2 = buildSection(2, '');
          sections.push(currentH2);
        }
        currentH2.subsections.push(currentH3);
      }
      currentH4 = buildSection(4, text);
      currentH3.subsections.push(currentH4);
    } else {
      if (currentH4) currentH4.blocks.push(text);
      else if (currentH3) currentH3.blocks.push(text);
      else if (currentH2) currentH2.blocks.push(text);
    }
  }

  return { title, publishedAt, sections, images, links };
}
"""


class LolOfficialAdapter(PatchNotesAdapterBase):
    """Adapter para leagueoflegends.com/{locale}/news/."""

    platform_name = "lol_official"
    min_delay = 3.0
    max_delay = 7.0

    def __init__(self) -> None:
        super().__init__()
        self._browser = None
        self._playwright = None

    def _ensure_playwright(self) -> None:
        if self._browser is not None:
            return
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise ImportError(PLAYWRIGHT_UNAVAILABLE_MESSAGE) from e
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        logger.info("[lol_official] Playwright iniciado")

    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """Recorre el índice por tags y devuelve URLs canónicas de patches."""
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            locale=locale,
            service_workers="block",
        )
        page = context.new_page()
        index_url = _TAG_INDEX_TEMPLATE.format(locale=locale)
        try:
            logger.info("[lol_official] Discover %s", index_url)
            page.goto(index_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

            # Click "ver más / load more" hasta agotar (con tope de 5 clicks).
            for _ in range(5):
                try:
                    button = page.get_by_role("button", name=re.compile(r"ver m[áa]s|load more", re.IGNORECASE))
                    if button.is_visible():
                        before = page.locator('a[href*="/news/game-updates/"]').count()
                        button.click()
                        page.wait_for_function(
                            "(n) => document.querySelectorAll('a[href*=\"/news/game-updates/\"]').length > n",
                            arg=before,
                            timeout=10000,
                        )
                    else:
                        break
                except Exception:
                    break

            raw_hrefs: list[str] = page.evaluate(
                "() => Array.from(document.querySelectorAll('a[href*=\"/news/game-updates/\"]')).map(a => a.href)"
            )
        finally:
            context.close()

        urls = []
        seen = set()
        for href in raw_hrefs:
            if not _PATCH_URL_PATTERN.search(href):
                continue
            if href in seen:
                continue
            seen.add(href)
            urls.append(href)
            if len(urls) >= max_patches:
                break
        logger.info("[lol_official] Descubiertas %d URLs para locale=%s", len(urls), locale)
        return urls

    def extract(self, url: str, locale: str) -> dict[str, Any]:
        """Descarga un patch note y devuelve dict listo para PatchNote."""
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            locale=locale,
            service_workers="block",
        )
        page = context.new_page()
        try:
            logger.info("[lol_official] Extract %s", url)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("main", timeout=15000)
            page.wait_for_timeout(1500)

            data: dict[str, Any] = page.evaluate(_EXTRACT_JS)

            patch_version = _extract_patch_version(data.get("title", ""), url)
            published_at = _parse_iso_datetime(data.get("publishedAt"))
            summary = _build_summary(data.get("sections", []))

            assets: list[dict[str, Any]] = []
            for img in data.get("images", []):
                assets.append({"asset_type": "image", "src": img["src"], "alt": img.get("alt")})
            for link in data.get("links", []):
                assets.append({"asset_type": "link", "src": link["href"], "text": link.get("text")})

            self._humanized_delay()
            return {
                "publisher": "riot",
                "game": "lol",
                "channel": "site",
                "source_locale": locale,
                "patch_version": patch_version,
                "title": data.get("title", ""),
                "canonical_url": url,
                "published_at": published_at.isoformat() if published_at else None,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "summary": summary,
                "sections": data.get("sections", []),
                "assets": assets,
            }
        finally:
            context.close()

    def close(self) -> None:
        super().close()
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        logger.info("[lol_official] Playwright cerrado")


def _extract_patch_version(title: str, url: str) -> str:
    """Saca la versión de un título tipo 'Notas de la versión 26.10b' o del slug de URL."""
    m = re.search(r"(\d+\.\d+[a-z]?)", title)
    if m:
        return m.group(1)
    m = _PATCH_URL_PATTERN.search(url)
    if m:
        suffix = m.group(3) or ""
        return f"{int(m.group(1))}.{int(m.group(2)):02d}{suffix}"
    return "unknown"


def _parse_iso_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _build_summary(sections: list[dict[str, Any]], max_chars: int = 280) -> str | None:
    """Toma los primeros 280 chars del primer bloque que tenga texto."""
    for section in sections:
        for block in section.get("blocks", []):
            if block and len(block) > 40:
                return block[:max_chars].rstrip() + ("…" if len(block) > max_chars else "")
        for sub in section.get("subsections", []):
            for block in sub.get("blocks", []):
                if block and len(block) > 40:
                    return block[:max_chars].rstrip() + ("…" if len(block) > max_chars else "")
    return None
