"""Stub for Riot Tournament-V5 production API."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class RiotTournamentV5Adapter(BaseEsportsAdapter):
    platform_name = "riot_tournament_v5"
    source_id = "riot_tournament_v5"

    def _stub(self, method: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "method": method,
            "status": "not_implemented",
            "gaps": ["requires production Riot API key and public HTTPS callback"],
        }

    def create_provider(self) -> dict[str, Any]:
        return self._stub("create_provider")

    def create_tournament(self) -> dict[str, Any]:
        return self._stub("create_tournament")

    def create_code(self) -> dict[str, Any]:
        return self._stub("create_code")

    def register_callback(self) -> dict[str, Any]:
        return self._stub("register_callback")
