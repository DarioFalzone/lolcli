"""Bronze ingest helpers for Leaguepedia Cargo payloads."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.meta_scraper.adapters.esports.leaguepedia import LeaguepediaAdapter


def ingest_tournament(tournament_page: str, adapter: LeaguepediaAdapter | None = None) -> dict[str, Any]:
    client = adapter or LeaguepediaAdapter()
    payload = client.fetch_matches(tournament_page)
    target = json_storage.save_bronze_json("leaguepedia", tournament_page, "matches", payload)
    return {"success": True, "source": "leaguepedia", "raw_uri": str(target), "payload": payload}


def ingest_draft(game_id: str, adapter: LeaguepediaAdapter | None = None) -> dict[str, Any]:
    client = adapter or LeaguepediaAdapter()
    payload = client.fetch_draft(game_id)
    target = json_storage.save_bronze_json("leaguepedia", game_id, "draft", payload)
    return {"success": True, "source": "leaguepedia", "raw_uri": str(target), "payload": payload}
