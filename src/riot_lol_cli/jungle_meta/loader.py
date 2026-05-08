"""Load and cache jungle metagame data from patch JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MODULE_DIR = Path(__file__).resolve().parent
_DATA_DIR = _MODULE_DIR.parent.parent.parent / "data" / "jungle_meta"

_jungle_data_cache: dict[str, Any] | None = None


def load_jungle_tier_list(patch: str = "26.09") -> dict[str, Any]:
    """Load jungle tier list data for a given patch."""
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
    """Get detail for a specific jungle champion."""
    tier_list = load_jungle_tier_list(patch)
    for champ in tier_list.get("jungle_champions", []):
        if champ["id"].lower() == champion_id.lower():
            return champ
    return None


def list_champions_by_tier(tier: str, patch: str = "26.09") -> list[dict[str, Any]]:
    """Get all champions in a specific tier."""
    tier_list = load_jungle_tier_list(patch)
    return [champ for champ in tier_list.get("jungle_champions", []) if champ["tier"] == tier]


def get_categories(patch: str = "26.09") -> dict[str, list[dict[str, Any]]]:
    """Return champions grouped by curated categories (overpowered/low_elo_picks/bans).

    Each category resolves champion IDs to full champion dicts so the frontend
    can render icons + tier badges without an extra round-trip.
    """
    tier_list = load_jungle_tier_list(patch)
    categories = tier_list.get("categories", {})
    champions_by_id = {c["id"]: c for c in tier_list.get("jungle_champions", [])}

    result: dict[str, list[dict[str, Any]]] = {}
    for category_name, champion_ids in categories.items():
        result[category_name] = [
            champions_by_id[cid] for cid in champion_ids if cid in champions_by_id
        ]
    return result


def get_item_abusers(item_key: str, patch: str = "26.09") -> list[dict[str, Any]]:
    """Return champions tagged as abusers of a specific item (from items_meta)."""
    tier_list = load_jungle_tier_list(patch)
    items_meta = tier_list.get("items_meta", {})
    champion_ids = items_meta.get(item_key, [])
    champions_by_id = {c["id"]: c for c in tier_list.get("jungle_champions", [])}
    return [champions_by_id[cid] for cid in champion_ids if cid in champions_by_id]


def list_used_item_ids(patch: str = "26.09") -> set[int]:
    """Return unique Data Dragon item IDs referenced across all core_builds."""
    tier_list = load_jungle_tier_list(patch)
    used: set[int] = set()
    for champ in tier_list.get("jungle_champions", []):
        for build in champ.get("core_builds", []):
            for item_id in build.get("items", []):
                if isinstance(item_id, int):
                    used.add(item_id)
    return used
