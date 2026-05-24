"""Stub for Riot local game client API.

This source is useful only for scrims/testing on localhost and is not a public
historical data source.
"""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class GameClientLocalAdapter(BaseEsportsAdapter):
    platform_name = "game_client_local"
    source_id = "game_client_local"
    base_url = "https://127.0.0.1:2999"

    def get_live_game_data(self) -> dict[str, Any]:
        return self._stub("get_live_game_data")

    def get_player_list(self) -> dict[str, Any]:
        return self._stub("get_player_list")

    def _stub(self, method: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "method": method,
            "status": "not_implemented",
            "gaps": ["localhost-only source; not a historical public feed"],
        }
