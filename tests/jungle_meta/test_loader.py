"""Test jungle meta data loader."""

from __future__ import annotations

from riot_lol_cli.jungle_meta.loader import (
    get_categories,
    get_champion_detail,
    get_item_abusers,
    list_champions_by_tier,
    list_used_item_ids,
    load_jungle_tier_list,
)


def test_load_jungle_tier_list():
    data = load_jungle_tier_list("26.09")
    assert data["patch"] == "26.09"
    assert "jungle_champions" in data
    assert len(data["jungle_champions"]) > 0


def test_tier_list_has_all_required_tiers():
    data = load_jungle_tier_list("26.09")
    tiers = {champ["tier"] for champ in data["jungle_champions"]}
    assert tiers == {"S", "A", "B", "C"}


def test_champion_detail_xin_zhao():
    champ = get_champion_detail("XinZhao")
    assert champ is not None
    assert champ["id"] == "XinZhao"
    assert champ["tier"] == "S"
    assert champ["winrate"] > 50


def test_champion_not_found():
    champ = get_champion_detail("NonExistentChamp")
    assert champ is None


def test_list_champions_by_tier():
    s_tier = list_champions_by_tier("S")
    assert len(s_tier) > 0
    assert all(champ["tier"] == "S" for champ in s_tier)

    a_tier = list_champions_by_tier("A")
    assert len(a_tier) > 0
    assert all(champ["tier"] == "A" for champ in a_tier)


def test_champion_fields_required():
    """Validate the new schema (core_builds list with item IDs + structured rune)."""
    data = load_jungle_tier_list("26.09")
    for champ in data["jungle_champions"]:
        required_fields = {
            "id",
            "display_name",
            "tier",
            "winrate",
            "pickrate",
            "banrate",
            "primary_reason",
            "reason_text",
            "core_builds",
            "core_rune",
            "playstyle",
        }
        assert required_fields.issubset(set(champ.keys())), f"Missing fields in {champ['id']}"

        assert isinstance(champ["core_builds"], list)
        assert len(champ["core_builds"]) >= 1
        for build in champ["core_builds"]:
            assert "label" in build
            assert "items" in build
            assert isinstance(build["items"], list)
            assert all(isinstance(i, int) for i in build["items"])

        assert isinstance(champ["core_rune"], dict)
        assert "name" in champ["core_rune"]
        assert "tree" in champ["core_rune"]


def test_xin_zhao_has_two_builds():
    """Xin Zhao screenshot shows two core build options."""
    champ = get_champion_detail("XinZhao")
    assert champ is not None
    assert len(champ["core_builds"]) == 2


def test_get_categories_returns_overpowered_low_elo_bans():
    categories = get_categories()
    assert "overpowered" in categories
    assert "low_elo_picks" in categories
    assert "bans" in categories
    assert all(isinstance(champ, dict) and "id" in champ for champ in categories["overpowered"])


def test_get_item_abusers_voltaic_sword():
    abusers = get_item_abusers("voltaic_sword_abusers")
    assert len(abusers) > 0
    assert all("id" in champ and "tier" in champ for champ in abusers)


def test_list_used_item_ids_includes_voltaic_sword():
    item_ids = list_used_item_ids()
    assert 6699 in item_ids
    assert 3071 in item_ids
