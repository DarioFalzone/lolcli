"""Tests de wiring para rol jungla en adapters del Meta Scraper."""

from riot_lol_cli.meta_scraper.adapters.lolalytics import LolalyticsAdapter
from riot_lol_cli.meta_scraper.adapters.opgg import OpggAdapter
from riot_lol_cli.meta_scraper.adapters.ugg import UggAdapter


def test_ugg_jungle_uses_jungle_role(monkeypatch):
    calls = []

    def fake_fetch(self, role, patch, elo):
        calls.append({"role": role, "patch": patch, "elo": elo})
        return {"champions": []}

    monkeypatch.setattr(UggAdapter, "_fetch_tier_list", fake_fetch)

    UggAdapter().fetch_jungle_tier_list(patch="26.9", elo="emerald_plus")

    assert calls == [{"role": "jungle", "patch": "26.9", "elo": "emerald_plus"}]


def test_lolalytics_jungle_uses_jungle_lane(monkeypatch):
    calls = []

    def fake_fetch(self, role, lane, patch, elo):
        calls.append({"role": role, "lane": lane, "patch": patch, "elo": elo})
        return {"champions": []}

    monkeypatch.setattr(LolalyticsAdapter, "_fetch_tier_list", fake_fetch)

    LolalyticsAdapter().fetch_jungle_tier_list(patch="26.9", elo="emerald_plus")

    assert calls == [{"role": "jungle", "lane": "jungle", "patch": "26.9", "elo": "emerald_plus"}]


def test_opgg_jungle_uses_jungle_position(monkeypatch):
    calls = []

    def fake_fetch(self, role, position, patch, elo):
        calls.append({"role": role, "position": position, "patch": patch, "elo": elo})
        return {"champions": []}

    monkeypatch.setattr(OpggAdapter, "_fetch_tier_list", fake_fetch)

    OpggAdapter().fetch_jungle_tier_list(patch="26.9", elo="emerald_plus")

    assert calls == [{"role": "jungle", "position": "jungle", "patch": "26.9", "elo": "emerald_plus"}]
