"""Load and cache the items database (EN + ES merged from Data Dragon)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MODULE_DIR = Path(__file__).resolve().parent
_DATA_FILE = _MODULE_DIR.parent.parent.parent / "data" / "items" / "database.json"

_cache: dict[str, Any] | None = None


def load_items_database() -> dict[str, Any]:
    """Carga (con cache en memoria) la database de items."""
    global _cache
    if _cache is not None:
        return _cache
    if not _DATA_FILE.exists():
        raise FileNotFoundError(
            f"Items database no encontrada en {_DATA_FILE}. Ejecutar primero: python scripts/update_items_database.py"
        )
    with open(_DATA_FILE, encoding="utf-8") as f:
        _cache = json.load(f)
    return _cache


def get_item(item_id: int) -> dict[str, Any] | None:
    db = load_items_database()
    for item in db.get("items", []):
        if item["id"] == item_id:
            return item
    return None


def list_categories() -> list[str]:
    """Conjunto unico de tags presentes en items vigentes."""
    db = load_items_database()
    cats: set[str] = set()
    for item in db.get("items", []):
        if item.get("deprecated"):
            continue
        for tag in item.get("tags") or []:
            cats.add(tag)
    return sorted(cats)


def list_groups() -> dict[str, list[int]]:
    """Agrupacion creativa: starter / boots / consumable / legendary / mythic-ish / trinket / deprecated.

    Riot ya no tiene mythics formales (post 2024); usamos depth para aproximar
    legendary tier. Trinkets se identifican por id range tradicional (3340-3364).
    """
    db = load_items_database()
    groups: dict[str, list[int]] = {
        "starter": [],
        "boots": [],
        "components": [],
        "legendary": [],
        "consumables": [],
        "trinkets": [],
        "jungle_specific": [],
        "deprecated": [],
    }

    for item in db.get("items", []):
        item_id = item["id"]
        tags = set(item.get("tags") or [])
        if item.get("deprecated"):
            groups["deprecated"].append(item_id)
            continue
        if 3340 <= item_id <= 3364 or "Trinket" in tags:
            groups["trinkets"].append(item_id)
            continue
        if "Consumable" in tags:
            groups["consumables"].append(item_id)
            continue
        if "Boots" in tags:
            groups["boots"].append(item_id)
            continue
        if "Jungle" in tags:
            groups["jungle_specific"].append(item_id)
            continue
        if "Lane" in tags or item.get("depth", 1) <= 1:
            groups["components"].append(item_id)
            continue
        if item.get("depth", 1) >= 3:
            groups["legendary"].append(item_id)
        else:
            groups["components"].append(item_id)

    return groups


def search_items(query: str, lang: str = "en") -> list[dict[str, Any]]:
    """Busqueda por substring en name_en o name_es (case-insensitive)."""
    if not query:
        return []
    needle = query.lower()
    db = load_items_database()
    results: list[dict[str, Any]] = []
    for item in db.get("items", []):
        name_field = item.get("name_es" if lang == "es" else "name_en", "")
        if needle in name_field.lower():
            results.append(item)
    return results
