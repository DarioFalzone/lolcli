"""Load and cache jungle metagame data from patch JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MODULE_DIR = Path(__file__).resolve().parent
_DATA_DIR = _MODULE_DIR.parent.parent.parent / "data" / "jungle_meta"

# In-memory cache
_jungle_data_cache: dict[str, Any] | None = None


def load_jungle_tier_list(patch: str = "26.09") -> dict[str, Any]:
    """Load jungle tier list data for a given patch.

    Args:
        patch: Patch identifier (e.g., "26.09"). Defaults to latest.

    Returns:
        Dictionary with tier list metadata and champions.
    """
    global _jungle_data_cache

    if _jungle_data_cache is not None and _jungle_data_cache.get("patch") == patch:
        return _jungle_data_cache

    patch_file = _DATA_DIR / f"patch_{patch}.json"
    if not patch_file.exists():
        raise FileNotFoundError(f"Patch file not found: {patch_file}")

    with open(patch_file, encoding="utf-8") as f:
        data = json.load(f)

    _jungle_data_cache = data
    return data


def get_champion_detail(champion_id: str, patch: str = "26.09") -> dict[str, Any] | None:
    """Get detail for a specific jungle champion.

    Args:
        champion_id: Champion ID (e.g., "XinZhao").
        patch: Patch identifier.

    Returns:
        Champion data or None if not found.
    """
    tier_list = load_jungle_tier_list(patch)
    for champ in tier_list.get("jungle_champions", []):
        if champ["id"].lower() == champion_id.lower():
            return champ
    return None


def list_champions_by_tier(tier: str, patch: str = "26.09") -> list[dict[str, Any]]:
    """Get all champions in a specific tier.

    Args:
        tier: Tier letter (S, A, B, C).
        patch: Patch identifier.

    Returns:
        List of champions in that tier.
    """
    tier_list = load_jungle_tier_list(patch)
    return [champ for champ in tier_list.get("jungle_champions", []) if champ["tier"] == tier]
