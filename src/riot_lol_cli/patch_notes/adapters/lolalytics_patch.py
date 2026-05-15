"""Adapter LoLalytics — tier list ancorada a un patch específico.

LoLalytics soporta URLs como `https://lolalytics.com/lol/tierlist/?patch=26.10`.
Cuando el sitio expone el patch como query, podemos scrapear la tier list por
versión histórica. Si no está disponible, scrapeamos el estado actual y lo
tageamos con el patch activo.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_BASE_URL = "https://lolalytics.com/lol/tierlist/"


class LolalyticsPatchAdapter(PatchNotesAdapterBase):
    """Snapshot por patch de la tier list de LoLalytics."""

    platform_name = "lolalytics_patch"
    min_delay = 4.0
    max_delay = 8.0

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

    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """Una URL por patch — el orchestrator pasa max_patches=1 normalmente."""
        return [_BASE_URL]

    def extract(self, url: str, locale: str, patch_version: str | None = None) -> dict[str, Any]:
        """Tier list ancorada al patch dado. Si patch_version es None, snapshot actual."""
        self._ensure_playwright()
        target_url = _BASE_URL
        if patch_version:
            target_url = f"{_BASE_URL}?patch={patch_version}"

        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            service_workers="block",
        )
        page = context.new_page()
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)

            detected_patch = patch_version
            try:
                body_text = page.text_content("body") or ""
                m = re.search(r"Patch\s+(\d+\.\d+)", body_text, re.IGNORECASE)
                if m:
                    detected_patch = m.group(1)
            except Exception:
                pass

            rows: list[dict[str, Any]] = page.evaluate(
                """() => {
                    const out = [];
                    const links = document.querySelectorAll('a[href*=\"/lol/\"][href*=\"/build/\"]');
                    for (const a of links) {
                        const txt = a.textContent ? a.textContent.trim() : '';
                        if (!txt || txt.length > 30) continue;
                        const row = a.closest('div');
                        const rowText = row ? row.textContent : '';
                        const percents = (rowText.match(/(\\d+\\.\\d+)%/g) || []).slice(0, 3);
                        out.push({
                            name: txt,
                            href: a.href,
                            percents: percents.map(p => parseFloat(p)),
                        });
                        if (out.length >= 80) break;
                    }
                    return out;
                }"""
            )
        finally:
            context.close()

        self._humanized_delay()
        return {
            "source_url": target_url,
            "patch_label": detected_patch,
            "rows_count": len(rows),
            "rows": rows[:60],
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
