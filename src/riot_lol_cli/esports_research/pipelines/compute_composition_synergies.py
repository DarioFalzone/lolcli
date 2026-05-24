"""Gold pipeline for composition synergies."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.analytics.synergy import compute_synergy_pairs


def compute_and_save(participant_games: list[dict[str, Any]], *, patch_id: str, region: str) -> dict[str, Any]:
    pairs = compute_synergy_pairs(participant_games, patch_id=patch_id, region=region)
    payload = [pair.model_dump(mode="json") for pair in pairs]
    target = json_storage.save_gold_feature(f"synergy_pairs_{patch_id}.json", payload)
    return {"success": True, "entries": len(payload), "path": str(target)}
