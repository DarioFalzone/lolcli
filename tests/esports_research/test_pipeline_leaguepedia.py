from __future__ import annotations

from tests.esports_research.conftest import load_json_fixture

from riot_lol_cli.esports_research.pipelines.normalize_leaguepedia import normalize_payload


def test_normalize_leaguepedia_tournament():
    payload = normalize_payload(load_json_fixture("leaguepedia_cargo_picks_and_bans.json"))
    assert payload["tournaments"][0]["name"] == "Worlds 2025"


def test_normalize_leaguepedia_match_and_game():
    payload = normalize_payload(load_json_fixture("leaguepedia_cargo_picks_and_bans.json"))
    assert payload["matches"][0]["best_of"] == 5
    assert payload["games"][0]["winner_side"] == "BLUE"


def test_normalize_leaguepedia_draft_actions():
    payload = normalize_payload(load_json_fixture("leaguepedia_cargo_picks_and_bans.json"))
    assert [row["action_type"] for row in payload["draft_actions"]] == ["BAN", "PICK"]


def test_normalize_leaguepedia_participants_and_players():
    payload = normalize_payload(load_json_fixture("leaguepedia_cargo_picks_and_bans.json"))
    assert len(payload["participants"]) == 2
    assert {player["handle"] for player in payload["players"]} == {"Gumayusi", "Ruler"}


def test_normalize_leaguepedia_generates_teams():
    payload = normalize_payload(load_json_fixture("leaguepedia_cargo_picks_and_bans.json"))
    names = {team["name"] for team in payload["teams"]}
    assert names == {"T1", "Gen.G"}


def test_normalize_leaguepedia_empty_payload():
    payload = normalize_payload({})
    assert payload["tournaments"] == []
    assert payload["participants"] == []
