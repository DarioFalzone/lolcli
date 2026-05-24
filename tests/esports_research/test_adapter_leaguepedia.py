from __future__ import annotations

import pytest

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import CONTACT_EMAIL, ESPORTS_USER_AGENT
from riot_lol_cli.meta_scraper.adapters.esports.leaguepedia import LeaguepediaAdapter


class _JsonResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_headers_are_identifiable():
    adapter = LeaguepediaAdapter()
    headers = adapter._build_headers()
    assert CONTACT_EMAIL in headers["User-Agent"]
    assert headers["From"] == CONTACT_EMAIL
    assert headers["User-Agent"] == ESPORTS_USER_AGENT


def test_min_delay_compliance():
    assert LeaguepediaAdapter.min_delay >= 2.0


def test_cargo_query_single_page(monkeypatch):
    adapter = LeaguepediaAdapter()

    def fake_get(url, **kwargs):
        assert kwargs["params"]["limit"] == 500
        return _JsonResponse({"cargoquery": [{"title": {"Name": "Worlds"}}]})

    monkeypatch.setattr(adapter, "_safe_get", fake_get)
    payload = adapter.cargo_query(tables="Tournaments", fields="Name")
    assert payload["rows"] == [{"Name": "Worlds"}]
    assert payload["source"] == "leaguepedia"


def test_cargo_query_paginates(monkeypatch):
    adapter = LeaguepediaAdapter()
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["params"]["offset"])
        if len(calls) == 1:
            return _JsonResponse({"cargoquery": [{"title": {"Name": str(i)}} for i in range(500)]})
        return _JsonResponse({"cargoquery": [{"title": {"Name": "last"}}]})

    monkeypatch.setattr(adapter, "_safe_get", fake_get)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: None)
    payload = adapter.cargo_query(tables="Tournaments", fields="Name")
    assert calls == [0, 500]
    assert len(payload["rows"]) == 501


@pytest.mark.parametrize(
    "method,args,table",
    [
        ("fetch_tournaments", ("LCK", "2025"), "Tournaments"),
        ("fetch_matches", ("Worlds_2025",), "MatchSchedule"),
        ("fetch_game_detail", ("G1",), "ScoreboardGames,ScoreboardPlayers"),
        ("fetch_draft", ("G1",), "PicksAndBansS7"),
    ],
)
def test_domain_methods_use_expected_tables(monkeypatch, method, args, table):
    adapter = LeaguepediaAdapter()
    seen = {}

    def fake_query(**kwargs):
        seen.update(kwargs)
        return {"rows": []}

    monkeypatch.setattr(adapter, "cargo_query", fake_query)
    getattr(adapter, method)(*args)
    assert seen["tables"] == table
