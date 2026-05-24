"""Data Dragon adapter for esports dimensions."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class DataDragonEsportsAdapter(BaseEsportsAdapter):
    platform_name = "data_dragon"
    source_id = "data_dragon"
    base_url = "https://ddragon.leagueoflegends.com"
    min_delay = 0.5
    max_delay = 1.0

    def fetch_versions(self) -> dict[str, Any]:
        response = self._safe_get(f"{self.base_url}/api/versions.json")
        versions = response.json()
        return {"source": self.source_id, "versions": versions, "latest": versions[0] if versions else None}

    def fetch_champions(self, patch: str = "latest", locale: str = "en_US") -> dict[str, Any]:
        resolved_patch = self.fetch_versions()["latest"] if patch == "latest" else patch
        response = self._safe_get(f"{self.base_url}/cdn/{resolved_patch}/data/{locale}/champion.json")
        raw = response.json()
        champions = [
            {
                "champion_id": value.get("id"),
                "display_name": value.get("name"),
                "primary_role": (value.get("tags") or [None])[0],
            }
            for value in raw.get("data", {}).values()
        ]
        return {"source": self.source_id, "patch": resolved_patch, "locale": locale, "champions": champions, "raw": raw}

    def fetch_tournaments(self, league: str, season: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["Data Dragon has no tournament data"], "league": league, "season": season}

    def fetch_matches(self, tournament_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["Data Dragon has no match data"], "tournament_id": tournament_id}

    def fetch_game_detail(self, game_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["Data Dragon has no game data"], "game_id": game_id}

    def fetch_draft(self, game_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["Data Dragon has no draft data"], "game_id": game_id}
