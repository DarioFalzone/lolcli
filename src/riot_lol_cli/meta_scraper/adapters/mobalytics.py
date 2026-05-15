"""
Adaptador Mobalytics — Jungle Tier List.

Estrategia: SPA con hidratacion JS. Requiere Playwright (Capa 3) para
renderizar la pagina y extraer los datos del DOM.

URL canonica: https://mobalytics.gg/lol/tier-list/jungle
Variante de stats puras (sin curacion de tier): https://mobalytics.gg/lol/tier-list/stats/jungle

Estado V1: stub. Marca el contrato pero no extrae datos reales.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL = "https://mobalytics.gg/lol/tier-list/jungle"
_STATS_URL = "https://mobalytics.gg/lol/tier-list/stats/jungle"

_NOT_IMPLEMENTED_NOTE = (
    "Adapter stub. Para activar: usar Playwright (chromium) para renderizar "
    "la SPA, esperar selector de tabla de tiers, extraer rows con champion + "
    "tier + WR/PR/BR. Mobalytics tiene curacion propia de tier ademas de stats."
)


class MobalyticsAdapter(BaseAdapter):
    platform_name = "mobalytics"
    # SPA pesada: rate limit mas conservador.
    min_delay = 5.0
    max_delay = 10.0

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        return self._stub_response(role="support", patch=patch, elo=elo)

    def fetch_jungle_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        return self._stub_response(role="jungle", patch=patch, elo=elo)

    def fetch_champion_detail(self, champion_id: str) -> dict:
        return {
            "platform": self.platform_name,
            "champion_id": champion_id,
            "status": "not_implemented",
            "reason": _NOT_IMPLEMENTED_NOTE,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def _stub_response(self, *, role: str, patch: str, elo: str) -> dict:
        logger.info("[%s] stub fetch_%s_tier_list (no scrape real aun)", self.platform_name, role)
        return {
            "platform": self.platform_name,
            "source_url": _TIERLIST_URL,
            "stats_url": _STATS_URL,
            "role": role,
            "patch": patch,
            "elo": elo,
            "status": "not_implemented",
            "reason": _NOT_IMPLEMENTED_NOTE,
            "champions": [],
            "champion_count": 0,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
