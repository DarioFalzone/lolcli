"""Adapter para el dev blog de Riot — `leagueoflegends.com/{locale}/news/dev/`.

Provee el `rationale` detrás de cambios de parche: artículos largos donde devs
explican el por qué del balance. No es el changelog canónico, pero enriquece la
nota oficial con contexto.

Asociación a un patch: regex sobre el título del artículo + `published_at` cercano
a la fecha del patch oficial (±14 días).
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_DEV_INDEX_TEMPLATE = "https://www.leagueoflegends.com/{locale}/news/dev/"
_PATCH_VERSION_RE = re.compile(r"(\d{1,2}\.\d{1,2}[a-z]?)")

_EXTRACT_DEV_JS = r"""
() => {
  const root = document.querySelector('main') || document.body;
  const titleEl = root.querySelector('h1');
  const title = titleEl ? titleEl.textContent.trim() : '';

  let publishedAt = null;
  const timeEl = root.querySelector('time[datetime]');
  if (timeEl) publishedAt = timeEl.getAttribute('datetime');

  const paragraphs = [...root.querySelectorAll('p, li')]
    .map(p => p.textContent ? p.textContent.trim() : '')
    .filter(t => t && t.length > 30)
    .slice(0, 30);

  return { title, publishedAt, paragraphs };
}
"""


class LolDevAdapter(PatchNotesAdapterBase):
    """Adapter del dev blog oficial de Riot."""

    platform_name = "lol_dev"
    min_delay = 3.0
    max_delay = 6.0

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
        logger.info("[lol_dev] Playwright iniciado")

    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """Lista los últimos artículos del dev blog para el locale dado."""
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            locale=locale,
            service_workers="block",
        )
        page = context.new_page()
        url = _DEV_INDEX_TEMPLATE.format(locale=locale)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            hrefs: list[str] = page.evaluate(
                "() => Array.from(document.querySelectorAll('a[href*=\"/news/dev/\"]')).map(a => a.href)"
            )
        finally:
            context.close()

        seen: set[str] = set()
        out: list[str] = []
        for href in hrefs:
            if "/news/dev/" not in href:
                continue
            # Excluir el índice raíz
            if href.rstrip("/").endswith("/news/dev"):
                continue
            if href in seen:
                continue
            seen.add(href)
            out.append(href)
            if len(out) >= max_patches * 2:  # buscar 2x para tener candidatos
                break
        logger.info("[lol_dev] Descubiertos %d artículos para locale=%s", len(out), locale)
        return out

    def extract(self, url: str, locale: str) -> dict[str, Any]:
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            locale=locale,
            service_workers="block",
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("main", timeout=15000)
            page.wait_for_timeout(1000)
            data: dict[str, Any] = page.evaluate(_EXTRACT_DEV_JS)
        finally:
            context.close()

        title = data.get("title", "")
        related_versions = sorted(set(_PATCH_VERSION_RE.findall(title or "")))
        # También buscar versiones mencionadas en los primeros párrafos
        for para in (data.get("paragraphs") or [])[:5]:
            for match in _PATCH_VERSION_RE.findall(para):
                if match not in related_versions:
                    related_versions.append(match)

        self._humanized_delay()

        return {
            "url": url,
            "title": title,
            "published_at": data.get("publishedAt"),
            "paragraphs": data.get("paragraphs", []),
            "related_patch_versions": related_versions,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def close(self) -> None:
        super().close()
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
