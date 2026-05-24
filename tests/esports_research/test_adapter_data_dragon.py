from __future__ import annotations

from tests.esports_research.conftest import load_json_fixture

from riot_lol_cli.meta_scraper.adapters.esports.data_dragon import DataDragonEsportsAdapter


class _JsonResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_fetch_versions(monkeypatch):
    adapter = DataDragonEsportsAdapter()
    monkeypatch.setattr(adapter, "_safe_get", lambda url: _JsonResponse(["15.20.1", "15.19.1"]))
    payload = adapter.fetch_versions()
    assert payload["latest"] == "15.20.1"


def test_fetch_champions_maps_champion_dim(monkeypatch):
    adapter = DataDragonEsportsAdapter()

    def fake_get(url):
        if url.endswith("versions.json"):
            return _JsonResponse(["15.20.1"])
        return _JsonResponse(load_json_fixture("data_dragon_champion_sample.json"))

    monkeypatch.setattr(adapter, "_safe_get", fake_get)
    payload = adapter.fetch_champions()
    assert payload["patch"] == "15.20.1"
    assert {"champion_id": "MonkeyKing", "display_name": "Wukong", "primary_role": "Fighter"} in payload["champions"]


def test_domain_methods_are_gaps():
    adapter = DataDragonEsportsAdapter()
    assert adapter.fetch_tournaments("LCK", "2025")["status"] == "gap"
    assert adapter.fetch_matches("m")["status"] == "gap"
    assert adapter.fetch_game_detail("g")["status"] == "gap"
    assert adapter.fetch_draft("g")["status"] == "gap"
