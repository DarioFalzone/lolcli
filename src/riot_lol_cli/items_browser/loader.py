"""Load and cache the items database (EN + ES merged from Data Dragon)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MODULE_DIR = Path(__file__).resolve().parent
_DATA_FILE = _MODULE_DIR.parent.parent.parent / "data" / "items" / "database.json"

_cache: dict[str, Any] | None = None
SUMMONERS_RIFT_MAP_ID = "11"


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
    for item in _annotated_items(db.get("items", [])):
        if item["id"] == item_id:
            return item
    return None


def list_items(*, include_deprecated: bool = False, include_variants: bool = False) -> list[dict[str, Any]]:
    """Lista items para catalogo, ocultando variantes duplicadas por modo por default."""
    db = load_items_database()
    items = _annotated_items(db.get("items", []))
    result = []
    for item in items:
        if item.get("deprecated") and not include_deprecated:
            continue
        if item.get("catalog_variant") and not include_variants:
            continue
        result.append(item)
    return result


def list_categories() -> list[str]:
    """Conjunto unico de tags presentes en items vigentes."""
    cats: set[str] = set()
    for item in list_items():
        for tag in item.get("tags") or []:
            cats.add(tag)
    return sorted(cats)


def list_groups(*, include_variants: bool = False) -> dict[str, list[int]]:
    """Agrupacion creativa: starter / boots / consumable / legendary / mythic-ish / trinket / deprecated.

    Riot ya no tiene mythics formales (post 2024); usamos depth para aproximar
    legendary tier. Trinkets se identifican por id range tradicional (3340-3364).
    """
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

    for item in list_items(include_deprecated=True, include_variants=include_variants):
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


def search_items(query: str, lang: str = "en", *, include_variants: bool = False) -> list[dict[str, Any]]:
    """Busqueda por substring en name_en o name_es (case-insensitive)."""
    if not query:
        return []
    needle = query.lower()
    results: list[dict[str, Any]] = []
    for item in list_items(include_variants=include_variants):
        name_field = item.get("name_es" if lang == "es" else "name_en", "")
        if needle in name_field.lower():
            results.append(item)
    return results


def _annotated_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    canonical_by_name = _canonical_item_ids_by_name(items)
    result = []
    for item in items:
        item_copy = dict(item)
        key = _item_name_key(item_copy)
        canonical_id = canonical_by_name.get(key, item_copy["id"])
        is_variant = not item_copy.get("deprecated") and item_copy["id"] != canonical_id
        item_copy["canonical_item_id"] = canonical_id
        item_copy["catalog_variant"] = is_variant
        if is_variant:
            item_copy["variant_reason"] = "Variante por mapa o modo; oculta del catalogo por defecto."
        result.append(item_copy)
    return result


def _canonical_item_ids_by_name(items: list[dict[str, Any]]) -> dict[str, int]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if item.get("deprecated"):
            continue
        groups.setdefault(_item_name_key(item), []).append(item)

    return {key: min(group, key=_catalog_canonical_sort_key)["id"] for key, group in groups.items() if key}


def _item_name_key(item: dict[str, Any]) -> str:
    return str(item.get("name_en", "")).strip().casefold()


def _catalog_canonical_sort_key(item: dict[str, Any]) -> tuple[bool, bool, bool, int]:
    maps = {str(map_id) for map_id in item.get("maps", [])}
    item_id = int(item["id"])
    return (
        SUMMONERS_RIFT_MAP_ID not in maps,
        len(maps) <= 1,
        item_id >= 100000,
        item_id,
    )
