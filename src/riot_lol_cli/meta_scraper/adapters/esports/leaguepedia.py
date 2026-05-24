"""Leaguepedia Cargo adapter."""

from __future__ import annotations

import os
from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class LeaguepediaAdapter(BaseEsportsAdapter):
    platform_name = "leaguepedia"
    source_id = "leaguepedia"
    base_url = "https://lol.fandom.com/api.php"
    min_delay = 2.0
    max_delay = 4.0

    def cargo_query(
        self,
        *,
        tables: str,
        fields: str,
        where: str | None = None,
        limit: int = 500,
        offset: int = 0,
        continue_pages: bool = True,
    ) -> dict[str, Any]:
        safe_limit = min(limit, 500)
        rows: list[dict[str, Any]] = []
        current_offset = offset
        auth_gap = None
        if not (os.getenv("LEAGUEPEDIA_USER") and os.getenv("LEAGUEPEDIA_BOT_PASSWORD")):
            auth_gap = "bot_password_not_configured; using anonymous Cargo reads"

        while True:
            params: dict[str, Any] = {
                "action": "cargoquery",
                "format": "json",
                "tables": tables,
                "fields": fields,
                "limit": safe_limit,
                "offset": current_offset,
            }
            if where:
                params["where"] = where
            response = self._safe_get(self.base_url, params=params)
            payload = response.json()
            batch = [entry.get("title", entry) for entry in payload.get("cargoquery", [])]
            rows.extend(batch)
            if not continue_pages or len(batch) < safe_limit:
                break
            current_offset += safe_limit
            self._humanized_delay()

        gaps = [auth_gap] if auth_gap else []
        return {"source": self.source_id, "tables": tables, "fields": fields, "rows": rows, "gaps": gaps}

    def fetch_tournaments(self, league: str, season: str) -> dict[str, Any]:
        where = f'League="{league}" AND OverviewPage LIKE "%{season}%"'
        return self.cargo_query(
            tables="Tournaments",
            fields="Name,OverviewPage,Region,League,DateStart,Date",
            where=where,
        )

    def fetch_matches(self, tournament_id: str) -> dict[str, Any]:
        return self.cargo_query(
            tables="MatchSchedule",
            fields="Team1,Team2,Winner,BestOf,DateTime_UTC,OverviewPage,MatchId",
            where=f'OverviewPage="{tournament_id}"',
        )

    def fetch_game_detail(self, game_id: str) -> dict[str, Any]:
        return self.cargo_query(
            tables="ScoreboardGames,ScoreboardPlayers",
            fields="ScoreboardGames.GameId,ScoreboardGames.Patch,ScoreboardPlayers.Link,ScoreboardPlayers.Champion",
            where=f'ScoreboardGames.GameId="{game_id}"',
        )

    def fetch_draft(self, game_id: str) -> dict[str, Any]:
        return self.cargo_query(
            tables="PicksAndBansS7",
            fields="GameId,Order,Team,Champion,IsBan,Phase",
            where=f'GameId="{game_id}"',
        )
