"""Adapter del calendario oficial de Riot.

V2.5: el Zendesk de support.leagueoflegends.com bloquea httpx con 403 incluso
con UA real. Cambiamos a Playwright para usar un browser real con cookies
y JS habilitados — el mismo enfoque que usamos para leagueoflegends.com en
`lol_official.py`.

Devuelve un snapshot global con `releases: [{patch_version, expected_release_date}]`.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_CALENDAR_URL = (
    "https://support-leagueoflegends.riotgames.com/hc/es-419/articles/"
    "360018987893-Calendario-de-lanzamiento-de-versiones-de-League-of-Legends"
)
_PATCH_VERSION_RE = re.compile(r"(\d{1,2}\.\d{1,2}[a-z]?)")
_DATE_RE = re.compile(r"\b(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?)", re.IGNORECASE)


class RiotCalendarAdapter(PatchNotesAdapterBase):
    """Scrapea el calendario público de versiones LoL via Playwright."""

    platform_name = "riot_calendar"
    min_delay = 1.0
    max_delay = 3.0

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
        logger.info("[riot_calendar] Playwright iniciado")

    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """Calendar es un único artículo global; devolvemos su URL."""
        return [_CALENDAR_URL]

    def extract(self, url: str, locale: str) -> dict[str, Any]:
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="es-419",
            service_workers="block",
        )
        page = context.new_page()
        try:
            logger.info("[riot_calendar] Navegando: %s", _CALENDAR_URL)
            page.goto(_CALENDAR_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

            # Extraer texto de tablas/párrafos que mencionen version + fecha
            blocks: list[str] = page.evaluate(
                """() => {
                    const article = document.querySelector('article, .article-body, body');
                    if (!article) return [];
                    const out = [];
                    const nodes = article.querySelectorAll('tr, li, p');
                    for (const n of nodes) {
                        const t = (n.textContent || '').trim();
                        if (t && t.length < 400) out.push(t);
                    }
                    return out;
                }"""
            )
        finally:
            context.close()

        releases: list[dict[str, str]] = []
        seen: set[str] = set()
        for text in blocks:
            version_match = _PATCH_VERSION_RE.search(text)
            date_match = _DATE_RE.search(text)
            if not (version_match and date_match):
                continue
            version = version_match.group(1)
            date_str = date_match.group(1).strip()
            key = f"{version}|{date_str.lower()}"
            if key in seen:
                continue
            seen.add(key)
            releases.append(
                {
                    "patch_version": version,
                    "expected_release_date": date_str,
                    "raw_line": text[:200],
                }
            )

        self._humanized_delay()
        return {
            "source_url": _CALENDAR_URL,
            "releases": releases,
            "release_count": len(releases),
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
