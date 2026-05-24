"""Data Dragon bronze/silver sync."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.meta_scraper.adapters.esports.data_dragon import DataDragonEsportsAdapter


def sync_patch(
    patch: str = "latest",
    locale: str = "en_US",
    adapter: DataDragonEsportsAdapter | None = None,
) -> dict[str, Any]:
    client = adapter or DataDragonEsportsAdapter()
    payload = client.fetch_champions(patch=patch, locale=locale)
    resolved_patch = payload.get("patch", patch)
    json_storage.save_bronze_json("data_dragon", resolved_patch, "champion", payload.get("raw", payload))
    champions = payload.get("champions", [])
    patches = [
        {
            "patch_id": resolved_patch.split(".")[0] + "." + resolved_patch.split(".")[1]
            if "." in resolved_patch
            else resolved_patch,
            "version_ddragon": resolved_patch,
            "release_date": None,
            "is_current": patch == "latest",
        }
    ]
    json_storage.save_silver_collection("champion_dim", champions)
    json_storage.save_silver_collection("patches", patches)
    return {"success": True, "patch": resolved_patch, "champions": len(champions)}
