"""Adapter Mobalytics — Patch Notes Breakdown (guías detalladas de cambios).

URL: https://mobalytics.gg/lol/guides/patch-notes-breakdown

Extrae el resumen editorial de Mobalytics sobre los cambios en champions, items y runas.
A diferencia de `mobalytics_patch.py` (tier list), este adapter enfatiza análisis de meta.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..messages import PLAYWRIGHT_UNAVAILABLE_MESSAGE
from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_BREAKDOWN_URL = "https://mobalytics.gg/lol/guides/patch-notes-breakdown"


class MobalyticsBrakedownAdapter(PatchNotesAdapterBase):
    """Scraper del patch notes breakdown de Mobalytics."""

    platform_name = "mobalytics_breakdown"
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
        """Devuelve la URL del breakdown actual."""
        return [_BREAKDOWN_URL]

    def extract(self, url: str, locale: str, patch_version: str | None = None) -> dict[str, Any]:
        """Extrae contenido del breakdown."""
        self._ensure_playwright()
        context = self._browser.new_context(  # type: ignore[union-attr]
            viewport={"width": 1920, "height": 1080},
            service_workers="block",
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)

            # Extraer versión del parche
            reported_patch = patch_version
            try:
                body_text = page.text_content("body") or ""
                m = re.search(r"Patch\s+(\d+\.\d+)", body_text, re.IGNORECASE)
                if m:
                    reported_patch = m.group(1)
            except Exception:
                pass

            # Extraer secciones principales (Buffs, Nerfs, Champion Changes, Items, Runes)
            sections_data: dict[str, Any] = page.evaluate(
                """() => {
                    const root = document.querySelector('main') || document.body;
                    const sections = {};

                    // Extraer título principal
                    const titleEl = root.querySelector('h1');
                    sections.title = titleEl ? titleEl.textContent.trim() : '';

                    // Extraer H2 y contenido agrupado
                    const h2s = root.querySelectorAll('h2');
                    let currentSection = null;
                    const sectionContent = [];

                    for (const h2 of h2s) {
                        const sectionTitle = h2.textContent.trim();
                        let blocks = [];
                        let el = h2.nextElementSibling;

                        while (el && el.tagName !== 'H2') {
                            if (el.tagName === 'H3' || el.tagName === 'H4') {
                                const txt = el.textContent.trim();
                                if (txt) blocks.push({ type: el.tagName.toLowerCase(), text: txt });
                            } else if (el.tagName === 'P' || el.tagName === 'UL' || el.tagName === 'OL') {
                                const txt = el.textContent.trim();
                                if (txt && txt.length > 0) blocks.push({ type: el.tagName.toLowerCase(), text: txt });
                            }
                            el = el.nextElementSibling;
                        }

                        if (blocks.length > 0) {
                            sectionContent.push({
                                title: sectionTitle,
                                blocks: blocks,
                                heading_level: 2
                            });
                        }
                    }

                    sections.sections = sectionContent;

                    // Extraer fecha de publicación
                    const dateEl = root.querySelector('time') || root.querySelector('[datetime]');
                    sections.published_at = dateEl ? dateEl.getAttribute('datetime') || dateEl.textContent : null;

                    // Extraer imágenes
                    const images = [];
                    for (const img of root.querySelectorAll('img[src]')) {
                        images.push({ src: img.src, alt: img.alt || null });
                    }
                    sections.images = images;

                    // Extraer links
                    const links = [];
                    for (const a of root.querySelectorAll('a[href]')) {
                        const text = a.textContent.trim();
                        if (text && text.length > 0 && text.length < 200) {
                            links.push({ text, href: a.href });
                        }
                    }
                    sections.links = links;

                    return sections;
                }"""
            )

            self._humanized_delay()

            return {
                "source_url": url,
                "patch_label_active": patch_version,
                "patch_label_reported": reported_patch,
                "title": sections_data.get("title", ""),
                "sections": sections_data.get("sections", []),
                "published_at": sections_data.get("published_at"),
                "images": sections_data.get("images", []),
                "links": sections_data.get("links", []),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
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
