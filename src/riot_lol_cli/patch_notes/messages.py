"""Shared operational messages for Patch Notes runtime prerequisites."""

from __future__ import annotations

PLAYWRIGHT_BROWSER_INSTALL_COMMAND = "playwright install chromium"

PLAYWRIGHT_UNAVAILABLE_MESSAGE = (
    "Playwright no esta disponible. Verifica las dependencias instaladas y ejecuta:\n"
    f"  {PLAYWRIGHT_BROWSER_INSTALL_COMMAND}"
)

NO_ADAPTERS_AVAILABLE_MESSAGE = (
    "No hay adapters de patch notes disponibles. Verifica dependencias y luego ejecuta:\n"
    f"  {PLAYWRIGHT_BROWSER_INSTALL_COMMAND}"
)

SCRAPER_VERSION = "patch_notes_v2.0.0"
"""Version del pipeline de scraping. Cambia cuando muta el algoritmo de extracción
para que `content_hash` pueda regenerarse de forma intencional."""

SUPPORTED_LOCALES = ("es-es",)
"""V2.2 — Español-only: la fuente de verdad es es-es de leagueoflegends.com.

Los otros locales (es-mx, en-us) ya no se scrapean ni se exponen en la UI.
La tupla se mantiene como tupla por compatibilidad con código que itera
`for locale in SUPPORTED_LOCALES`.
"""

DEFAULT_LOCALE = "es-es"

# --- V2: Sources adicionales (enrichments) ---

SOURCE_LOL_OFFICIAL = "lol_official"
SOURCE_LOL_DEV = "lol_dev"
SOURCE_RIOT_CALENDAR = "riot_calendar"
SOURCE_DDRAGON = "ddragon"
SOURCE_UGG_PATCH = "ugg_patch"
SOURCE_OPGG_PATCH = "opgg_patch"
SOURCE_LOLALYTICS_PATCH = "lolalytics_patch"
SOURCE_MOBALYTICS_PATCH = "mobalytics_patch"
SOURCE_MOBALYTICS_BREAKDOWN = "mobalytics_breakdown"

CANONICAL_SOURCE = SOURCE_LOL_OFFICIAL

ENRICHMENT_SOURCES = (
    SOURCE_LOL_DEV,
    SOURCE_RIOT_CALENDAR,
    SOURCE_DDRAGON,
    SOURCE_UGG_PATCH,
    SOURCE_OPGG_PATCH,
    SOURCE_LOLALYTICS_PATCH,
    SOURCE_MOBALYTICS_PATCH,
    SOURCE_MOBALYTICS_BREAKDOWN,
)

SOURCE_LABELS = {
    SOURCE_LOL_OFFICIAL: "Notas oficiales (Riot)",
    SOURCE_LOL_DEV: "Dev blog (Riot)",
    SOURCE_RIOT_CALENDAR: "Calendario oficial",
    SOURCE_DDRAGON: "Data Dragon (CDN técnico)",
    SOURCE_UGG_PATCH: "U.GG — Tier list por parche",
    SOURCE_OPGG_PATCH: "OP.GG — Estado por parche",
    SOURCE_LOLALYTICS_PATCH: "LoLalytics — Tier list por parche",
    SOURCE_MOBALYTICS_PATCH: "Mobalytics — Tier list por parche",
    SOURCE_MOBALYTICS_BREAKDOWN: "Mobalytics — Patch Notes Breakdown",
}
