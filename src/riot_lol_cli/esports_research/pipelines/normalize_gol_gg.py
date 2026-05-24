"""Normalize conservative Gol.gg parsed payloads."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research.analytics.identities import make_stable_id


def normalize_tournament_payload(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    tournament_name = payload.get("tournament") or payload.get("title") or "Gol.gg Tournament"
    tournament_id = make_stable_id("tournament", tournament_name)
    return {
        "tournaments": [
            {
                "tournament_id": tournament_id,
                "name": tournament_name,
                "region": payload.get("region", "UNKNOWN"),
                "league": payload.get("league", "UNKNOWN"),
                "format": payload.get("format", "UNKNOWN"),
                "start_date": payload.get("start_date", "1970-01-01"),
                "end_date": payload.get("end_date"),
                "source_origin": "gol_gg",
            }
        ],
        "matches": payload.get("matches", []),
        "games": payload.get("games", []),
        "participants": payload.get("participants", []),
        "draft_actions": payload.get("draft_actions", []),
    }
