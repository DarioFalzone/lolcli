"""
Adaptador METAsrc — Jungle.

Estrategia: HTML estatico parseable con httpx + BeautifulSoup. METAsrc no
requiere Playwright para tier list de jungla (lo hidrata con JS pero el HTML
inicial ya trae los datos).

URL canonica: https://www.metasrc.com/lol/tier-list/jungle
Filtros via query string:
  - region: na, euw, eune, kr, ...
  - elo: emerald_plus, platinum_plus, diamond_plus, master_plus, ...
  - patch: latest | <patch>

Estado V1: stub. La interfaz esta completa, las URLs y patrones de scrape
estan documentados, pero el extract real se activa solo cuando el operador
revise el markup actual y habilite el adapter (ver `_NOT_IMPLEMENTED_NOTE`).
Mientras tanto, retorna `status: not_implemented` con razon clara.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL_TEMPLATE = "https://www.metasrc.com/lol/{region}/tier-list/jungle"
_DEFAULT_REGION = "na"

_NOT_IMPLEMENTED_NOTE = (
    "Adapter stub. Para activar: implementar parse_html() con BeautifulSoup "
    "sobre el HTML inicial (METAsrc trae datos en el SSR), validar selectores "
    "contra la pagina actual, y eliminar este short-circuit."
)


class MetaSrcAdapter(BaseAdapter):
    platform_name = "metasrc"

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
        url = _TIERLIST_URL_TEMPLATE.format(region=_DEFAULT_REGION)
        logger.info("[%s] stub fetch_%s_tier_list (no scrape real aun)", self.platform_name, role)
        return {
            "platform": self.platform_name,
            "source_url": url,
            "role": role,
            "patch": patch,
            "elo": elo,
            "status": "not_implemented",
            "reason": _NOT_IMPLEMENTED_NOTE,
            "champions": [],
            "champion_count": 0,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
