"""Oracle's Elixir CSV adapter."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class OraclesElixirAdapter(BaseEsportsAdapter):
    platform_name = "oracles_elixir"
    source_id = "oracles_elixir"
    base_download_url = "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com"
    min_delay = 2.0
    max_delay = 4.0

    def fetch_csv(self, *, year: int, filename: str | None = None) -> dict[str, Any]:
        resolved = filename or f"{year}_LoL_esports_match_data_from_OraclesElixir.csv"
        url = f"{self.base_download_url}/{resolved}"
        response = self._safe_get(url)
        text = response.text
        return {
            "source": self.source_id,
            "year": year,
            "filename": resolved,
            "source_url": url,
            "csv_text": text,
            "row_count": len(parse_csv_text(text)),
        }

    def parse_csv_text(self, csv_text: str) -> list[dict[str, str]]:
        return parse_csv_text(csv_text)

    def fetch_tournaments(self, league: str, season: str) -> dict[str, Any]:
        payload = self.fetch_csv(year=int(season))
        rows = [row for row in parse_csv_text(payload["csv_text"]) if row.get("league") == league]
        return {**payload, "rows": rows, "row_count": len(rows)}

    def fetch_matches(self, tournament_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["match lookup requires CSV snapshot context"], "tournament_id": tournament_id}

    def fetch_game_detail(self, game_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["game lookup requires CSV snapshot context"], "game_id": game_id}

    def fetch_draft(self, game_id: str) -> dict[str, Any]:
        return {"source": self.source_id, "status": "gap", "gaps": ["Oracle's Elixir CSV does not include full pick/ban order"], "game_id": game_id}


def parse_csv_text(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(csv_text)))
