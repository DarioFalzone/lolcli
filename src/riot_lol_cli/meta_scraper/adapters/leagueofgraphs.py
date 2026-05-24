"""
Adaptador League of Graphs — Jungle stats.

Estrategia: HTML estatico parseable con httpx + BeautifulSoup. LoG sirve los
datos en el HTML inicial (no SPA), pero tiene rate limit estricto.

URLs canonicas:
  - Stats por rol:    https://www.leagueofgraphs.com/champions/stats/jungle
  - Rankings summoners por campeon/region:
      https://www.leagueofgraphs.com/rankings/summoners/<champion>/<region>/jungle

Estado V1: stub. La interfaz esta lista para agregar parse_html() cuando se
verifique el markup actual.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL = "https://www.leagueofgraphs.com/champions/stats/jungle"
_RANKINGS_URL_TEMPLATE = (
    "https://www.leagueofgraphs.com/rankings/summoners/{champion}/{region}/jungle"
)

# LoG es estricto con rate limit; usar delays conservadores.
_NOT_IMPLEMENTED_NOTE = (
    "Adapter stub. Para activar: parse del HTML inicial con BeautifulSoup, "
    "extraer rows de la tabla principal con champion + WR/PR. CUIDADO: LoG "
    "tiene rate limit estricto, mantener min_delay >= 8s y respetar 429."
)


class LeagueOfGraphsAdapter(BaseAdapter):
    platform_name = "leagueofgraphs"
    # Rate limit estricto observado historicamente.
    min_delay = 8.0
    max_delay = 15.0

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
            "rankings_template": _RANKINGS_URL_TEMPLATE,
            "role": role,
            "patch": patch,
            "elo": elo,
            "status": "not_implemented",
            "reason": _NOT_IMPLEMENTED_NOTE,
            "champions": [],
            "champion_count": 0,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
