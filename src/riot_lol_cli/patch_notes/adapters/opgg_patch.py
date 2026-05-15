"""Adapter OP.GG — snapshot del tier list tageado con patch.

OP.GG tampoco expone URLs históricas por patch. Scrapeamos el estado actual
y lo tageamos con el `patch_version` que pase el orchestrator.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.op.gg/champions"


class OpggPatchAdapter(PatchNotesAdapterBase):
    """Snapshot de OP.GG champion meta tageado con patch."""

    platform_name = "opgg_patch"
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
        return [_BASE_URL]

    def extract(self, url: str, locale: str, patch_version: str | None = None) -> dict[str, Any]:
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            service_workers="block",
        )
        page = context.new_page()
        try:
            page.goto(_BASE_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

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
                    const links = document.querySelectorAll('a[href*=\"/champions/\"]');
                    for (const a of links) {
                        const href = a.getAttribute('href') || '';
                        const slug = href.match(/\\/champions\\/([^/?#]+)/);
                        if (!slug || slug[1] === 'tier' || slug[1] === 'positions') continue;
                        if (seen.has(slug[1])) continue;
                        seen.add(slug[1]);
                        out.push({ slug: slug[1], href: a.href });
                        if (out.length >= 80) break;
                    }
                    return out;
                }"""
            )
        finally:
            context.close()

        self._humanized_delay()
        return {
            "source_url": _BASE_URL,
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
