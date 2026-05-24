"""Orchestrator for Esports Research V0 pipelines."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.pipelines import (
    compute_comfort_scores,
    compute_composition_synergies,
    compute_counterpick_matrix,
)


def run_full_pipeline(tournament_id: str, patches: list[str] | None = None) -> dict[str, Any]:
    """Run available V0 gold steps from existing silver JSON.

    Bronze network ingest is intentionally not triggered here; callers can run
    source-specific ingest first and then normalize. This keeps API refresh safe.
    """
    json_storage.ensure_directories()
    participants = json_storage.read_silver_collection("participants")
    if not participants:
        return {
            "success": True,
            "tournament_id": tournament_id,
            "gaps": ["silver/participants.json no existe o esta vacio"],
            "steps": [],
        }

    patch_list = patches or sorted({row.get("patch_id") for row in participants if row.get("patch_id")}) or ["unknown"]
    steps: list[dict[str, Any]] = []
    for patch_id in patch_list:
        patch_rows = [row for row in participants if (row.get("patch_id") or patch_id) == patch_id]
        steps.append(compute_counterpick_matrix.compute_and_save(patch_rows, patch_id=patch_id, region="GLOBAL"))
        steps.append(compute_composition_synergies.compute_and_save(patch_rows, patch_id=patch_id, region="GLOBAL"))
    steps.append(compute_comfort_scores.compute_and_save(participants))
    return {"success": True, "tournament_id": tournament_id, "patches": patch_list, "steps": steps, "gaps": []}
