"""Stub for PandaScore esports API."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class PandaScoreAdapter(BaseEsportsAdapter):
    platform_name = "pandascore"
    source_id = "pandascore"

    def list_tournaments(self) -> dict[str, Any]:
        return self._stub("list_tournaments")

    def get_match_frames(self) -> dict[str, Any]:
        return self._stub("get_match_frames")

    def subscribe_live(self) -> dict[str, Any]:
        return self._stub("subscribe_live")

    def _stub(self, method: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "method": method,
            "status": "not_implemented",
            "gaps": ["requires PandaScore API token and Pro Live plan for frames/events"],
            "notes": "WebSocket live plans have connection limits per match endpoint.",
        }
