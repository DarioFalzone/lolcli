"""Stub for Riot Esports Data via GRID."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class RiotEsportsGridAdapter(BaseEsportsAdapter):
    platform_name = "riot_esports_grid"
    source_id = "riot_esports_grid"

    def connect_session(self) -> dict[str, Any]:
        return self._stub("connect_session")

    def subscribe_feed(self) -> dict[str, Any]:
        return self._stub("subscribe_feed")

    def _stub(self, method: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "method": method,
            "status": "not_implemented",
            "payload_available": ["player_positions", "current_hp_mana", "item_details", "objective_status"],
            "gaps": ["contractual GRID access required"],
        }
