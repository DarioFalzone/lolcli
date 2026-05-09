"""Shared operational messages for Meta Scraper runtime prerequisites."""

from __future__ import annotations

PLAYWRIGHT_BROWSER_INSTALL_COMMAND = "playwright install chromium"

PLAYWRIGHT_UNAVAILABLE_MESSAGE = (
    "Playwright no esta disponible. Verifica las dependencias instaladas y ejecuta:\n"
    f"  {PLAYWRIGHT_BROWSER_INSTALL_COMMAND}"
)

NO_ADAPTERS_AVAILABLE_MESSAGE = (
    "No hay adapters disponibles. Verifica que las dependencias esten instaladas y luego ejecuta:\n"
    f"  {PLAYWRIGHT_BROWSER_INSTALL_COMMAND}"
)
