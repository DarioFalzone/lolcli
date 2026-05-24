"""Gold pipeline for player champion comfort."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.analytics.comfort import compute_comfort_scores
from riot_lol_cli.esports_research.schemas import utcnow_iso


def compute_and_save(participant_games: list[dict[str, Any]], *, report_date: str | None = None) -> dict[str, Any]:
    scores = compute_comfort_scores(participant_games)
    payload = [score.model_dump(mode="json") for score in scores]
    date_slug = report_date or utcnow_iso()[:10]
    target = json_storage.save_gold_feature(f"comfort_features_{date_slug}.json", payload)
    return {"success": True, "entries": len(payload), "path": str(target)}
