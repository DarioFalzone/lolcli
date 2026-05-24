from __future__ import annotations

from tests.esports_research.conftest import load_text_fixture

from riot_lol_cli.meta_scraper.adapters.esports.gol_gg import GolGGAdapter, parse_draft_html, parse_tournament_html


class _HtmlResponse:
    text = load_text_fixture("gol_gg_tournament_sample.html")


def test_min_delay_compliance():
    assert GolGGAdapter.min_delay >= 4.0
    assert GolGGAdapter.max_delay >= GolGGAdapter.min_delay


def test_parse_tournament_html_extracts_title_and_rows():
    payload = parse_tournament_html(load_text_fixture("gol_gg_tournament_sample.html"))
    assert payload["tournament"] == "LCK Spring 2025"
    assert len(payload["rows"]) == 3


def test_parse_draft_html_extracts_champions():
    actions = parse_draft_html(load_text_fixture("gol_gg_tournament_sample.html"))
    assert [action["champion_id"] for action in actions] == ["Varus", "Ezreal"]


def test_parse_draft_html_extracts_real_game_bans_and_picks():
    actions = parse_draft_html(load_text_fixture("gol_gg_game_draft_sample.html"))

    assert len(actions) == 20
    assert actions[0] == {
        "action_order": 1,
        "champion_id": "Orianna",
        "action_type": "BAN",
        "team_side": "BLUE",
        "phase": "BAN_PHASE_1",
    }
    assert actions[4]["phase"] == "BAN_PHASE_2"
    assert actions[5]["team_side"] == "BLUE"
    assert actions[5]["action_type"] == "PICK"
    assert actions[6]["champion_id"] == "JarvanIV"
    assert actions[10]["team_side"] == "RED"
    assert actions[10]["action_type"] == "BAN"
    assert actions[15]["champion_id"] == "Bard"
    assert actions[15]["action_type"] == "PICK"
    assert actions[15]["team_side"] == "RED"


def test_fetch_tournament_respects_robots_gap(monkeypatch):
    adapter = GolGGAdapter()
    monkeypatch.setattr(adapter, "robots_allowed", lambda url: False)
    payload = adapter.fetch_tournament("worlds-2025")
    assert payload["status"] == "gap"
    assert payload["gap"] == "robots_disallow"


def test_fetch_tournament_success(monkeypatch):
    adapter = GolGGAdapter()
    monkeypatch.setattr(adapter, "robots_allowed", lambda url: True)
    monkeypatch.setattr(adapter, "_safe_get", lambda url: _HtmlResponse())
    payload = adapter.fetch_tournament("worlds-2025")
    assert payload["status"] == "ok"
    assert payload["tournament"] == "LCK Spring 2025"


def test_fetch_draft_wraps_actions(monkeypatch):
    adapter = GolGGAdapter()
    monkeypatch.setattr(adapter, "robots_allowed", lambda url: True)
    monkeypatch.setattr(adapter, "_safe_get", lambda url: _HtmlResponse())
    payload = adapter.fetch_draft("G1")
    assert payload["draft_actions"][0]["champion_id"] == "Varus"
