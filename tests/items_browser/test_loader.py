"""Tests for items_browser loader."""

from __future__ import annotations

from riot_lol_cli.items_browser.loader import (
    get_item,
    list_categories,
    list_groups,
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


def test_search_en():
    results = search_items("voltaic", lang="en")
    assert len(results) >= 1
    assert any(r["id"] == 6699 for r in results)


def test_search_es():
    results = search_items("espada", lang="es")
    assert len(results) >= 1


def test_search_empty():
    assert search_items("", lang="en") == []
