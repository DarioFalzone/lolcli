"""Bronze ingest helpers for Gol.gg HTML pages."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.meta_scraper.adapters.esports.gol_gg import GolGGAdapter


def ingest_tournament(tournament_slug: str, adapter: GolGGAdapter | None = None) -> dict[str, Any]:
    client = adapter or GolGGAdapter()
    payload = client.fetch_tournament(tournament_slug)
    if payload.get("status") == "gap":
        return {"success": True, "source": "gol_gg", "gaps": [payload], "raw_uri": None}
    target = json_storage.save_bronze_text(
        "gol_gg",
        payload.get("fetched_date", "unknown"),
        tournament_slug,
        payload.get("html", ""),
        ".html",
    )
    return {"success": True, "source": "gol_gg", "raw_uri": str(target), "payload": payload}
