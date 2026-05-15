"""Adapter Mobalytics — reporte de meta + tier list por patch.

Mobalytics es SPA pesada con React/Next.js. Scraping conservador: solo
extraemos el patch reportado + lista de champions visibles en la tier list
actual. Si la página tarda o cambia, se devuelve `error` y el orchestrator
persiste el enrichment con `error` para tracking.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_TIER_URL = "https://mobalytics.gg/lol/tier-list"


class MobalyticsPatchAdapter(PatchNotesAdapterBase):
    """Snapshot conservador del tier list Mobalytics + patch reportado."""

    platform_name = "mobalytics_patch"
    min_delay = 5.0
    max_delay = 10.0

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
        return [_TIER_URL]

    def extract(self, url: str, locale: str, patch_version: str | None = None) -> dict[str, Any]:
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            service_workers="block",
        )
        page = context.new_page()
        try:
            page.goto(_TIER_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)  # más conservador, SPA pesada

            reported_patch = patch_version
            try:
                body_text = page.text_content("body") or ""
                m = re.search(r"Patch\s+(\d+\.\d+)", body_text, re.IGNORECASE)
                if m:
                    reported_patch = m.group(1)
            except Exception:
                pass

            rows: list[dict[str, Any]] = page.evaluate(
                """() => {
                    const out = [];
                    const seen = new Set();
                    const links = document.querySelectorAll('a[href*=\"/lol/champions/\"]');
                    for (const a of links) {
                        const txt = a.textContent ? a.textContent.trim() : '';
                        if (!txt || txt.length > 30) continue;
                        const slug = (a.getAttribute('href') || '').match(/\\/champions\\/([^/?#]+)/);
                        const slugKey = slug ? slug[1] : txt;
                        if (seen.has(slugKey)) continue;
                        seen.add(slugKey);
                        out.push({ name: txt, slug: slugKey, href: a.href });
                        if (out.length >= 80) break;
                    }
                    return out;
                }"""
            )
        finally:
            context.close()

        self._humanized_delay()
        return {
            "source_url": _TIER_URL,
            "patch_label_active": patch_version,
            "patch_label_reported": reported_patch,
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
