"""Gold pipeline for counterpick matrix."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.analytics.counterpick import compute_counterpick_entries


def compute_and_save(participant_games: list[dict[str, Any]], *, patch_id: str, region: str) -> dict[str, Any]:
    entries = compute_counterpick_entries(participant_games, patch_id=patch_id, region=region)
    payload = [entry.model_dump(mode="json") for entry in entries]
    target = json_storage.save_gold_feature(f"counterpick_matrix_{patch_id}.json", payload)
    return {"success": True, "entries": len(payload), "path": str(target)}
