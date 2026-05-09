"""Tests for items_browser loader."""

from __future__ import annotations

from riot_lol_cli.items_browser.loader import (
    get_item,
    list_categories,
    list_groups,
    list_items,
    load_items_database,
    search_items,
)


def test_load_items_database():
    db = load_items_database()
    assert "version" in db
    assert "items" in db
    assert db["total_count"] == len(db["items"])
    assert db["current_count"] >= 700


def test_get_item_voltaic_cyclosword():
    item = get_item(6699)
    assert item is not None
    assert item["name_en"] == "Voltaic Cyclosword"
    assert "Espada" in item["name_es"] or "Cicloespada" in item["name_es"]
    assert item["deprecated"] is False


def test_get_item_not_found():
    assert get_item(99999999) is None


def test_list_categories_includes_known_tags():
    categories = list_categories()
    assert "Damage" in categories
    assert "Boots" in categories


def test_list_groups_buckets():
    groups = list_groups()
    assert "boots" in groups
    assert "legendary" in groups
    assert "trinkets" in groups
    assert len(groups["boots"]) > 0


def test_catalog_hides_duplicate_mode_variants_by_default():
    item_ids = {item["id"] for item in list_items(include_deprecated=True)}

    assert 4633 in item_ids
    assert 224633 not in item_ids
    assert {1101, 1102, 1103}.issubset(item_ids)
    assert {1105, 1106, 1107}.isdisjoint(item_ids)


def test_catalog_can_include_variants_for_debugging():
    item_ids = {item["id"] for item in list_items(include_deprecated=True, include_variants=True)}

    assert 224633 in item_ids
    assert {1105, 1106, 1107}.issubset(item_ids)


def test_jungle_group_hides_duplicate_smite_variants():
    groups = list_groups()

    assert {1101, 1102, 1103}.issubset(set(groups["jungle_specific"]))
    assert {1105, 1106, 1107}.isdisjoint(set(groups["jungle_specific"]))


def test_search_en():
    results = search_items("voltaic", lang="en")
    assert len(results) >= 1
    assert any(r["id"] == 6699 for r in results)


def test_search_es():
    results = search_items("espada", lang="es")
    assert len(results) >= 1


def test_search_deduplicates_mode_variants():
    results = search_items("agrie", lang="es")
    result_ids = [item["id"] for item in results if item["name_en"] == "Riftmaker"]

    assert result_ids == [4633]


def test_search_empty():
    assert search_items("", lang="en") == []
