"""Test jungle meta data loader."""

from __future__ import annotations

import pytest

from riot_lol_cli.jungle_meta.loader import get_champion_detail, list_champions_by_tier, load_jungle_tier_list


def test_load_jungle_tier_list():
    """Load tier list for patch 26.09."""
    data = load_jungle_tier_list("26.09")
    assert data["patch"] == "26.09"
    assert "jungle_champions" in data
    assert len(data["jungle_champions"]) > 0


def test_tier_list_has_all_required_tiers():
    """Verify all tiers S/A/B/C are represented."""
    data = load_jungle_tier_list("26.09")
    tiers = {champ["tier"] for champ in data["jungle_champions"]}
    assert tiers == {"S", "A", "B", "C"}


def test_champion_detail_xin_zhao():
    """Get detail for Xin Zhao (S tier)."""
    champ = get_champion_detail("XinZhao")
    assert champ is not None
    assert champ["id"] == "XinZhao"
    assert champ["tier"] == "S"
    assert champ["winrate"] > 50


def test_champion_not_found():
    """Non-existent champion returns None."""
    champ = get_champion_detail("NonExistentChamp")
    assert champ is None


def test_list_champions_by_tier():
    """List all S tier champions."""
    s_tier = list_champions_by_tier("S")
    assert len(s_tier) > 0
    assert all(champ["tier"] == "S" for champ in s_tier)

    a_tier = list_champions_by_tier("A")
    assert len(a_tier) > 0
    assert all(champ["tier"] == "A" for champ in a_tier)


def test_champion_fields():
    """Verify champion data has required fields."""
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
            "core_items",
            "core_rune",
        }
        assert required_fields.issubset(set(champ.keys())), f"Missing fields in {champ['id']}"
