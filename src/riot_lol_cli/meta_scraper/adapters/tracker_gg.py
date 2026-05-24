"""
Adaptador Tracker.gg — LoL Insights.

Estrategia: SPA con datos hidratados via JS. Posibles XHR/JSON internos
accesibles si se inspecciona Network. Dos approaches:

1. Playwright (Capa 3) si los XHR no son estables.
2. httpx contra el endpoint XHR si se identifica un patron limpio.

URL canonica: https://tracker.gg/lol/insights

Estado V1: stub. Es la fuente con mayor friccion del set V3 — agregar al
final si los otros 3 (METAsrc, Mobalytics, LoG) ya cubren la redundancia.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_INSIGHTS_URL = "https://tracker.gg/lol/insights"

_NOT_IMPLEMENTED_NOTE = (
    "Adapter stub. Para activar: inspeccionar Network del SPA, identificar "
    "endpoints XHR/JSON internos y consumirlos directo (preferir sobre "
    "Playwright). Si no hay endpoints estables, fallback a Playwright."
)


class TrackerGgAdapter(BaseAdapter):
    platform_name = "tracker_gg"
    min_delay = 6.0
    max_delay = 12.0

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
            "source_url": _INSIGHTS_URL,
            "role": role,
            "patch": patch,
            "elo": elo,
            "status": "not_implemented",
            "reason": _NOT_IMPLEMENTED_NOTE,
            "champions": [],
            "champion_count": 0,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
