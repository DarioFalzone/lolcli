from __future__ import annotations

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.meta_api.routes import esports as esports_routes


def seed_storage() -> None:
    json_storage.save_silver_collection(
        "tournaments",
        [
            {
                "tournament_id": "worlds-2025",
                "name": "Worlds 2025",
                "region": "INTL",
                "league": "WORLDS",
                "format": "BO5",
                "start_date": "2025-10-01",
                "source_origin": "leaguepedia",
            }
        ],
    )
    json_storage.save_silver_entity(
        "matches",
        "m1",
        {
            "match_id": "m1",
            "tournament_id": "worlds-2025",
            "scheduled_at": "2025-10-01T00:00:00Z",
            "best_of": 5,
            "team_blue_id": "t1",
            "team_red_id": "geng",
            "source_origin": "leaguepedia",
        },
    )
    json_storage.save_silver_entity(
        "games",
        "g1",
        {
            "game_id": "g1",
            "match_id": "m1",
            "game_number": 1,
            "patch_id": "15.20",
            "source_origin": "leaguepedia",
            "source_game_key": "raw",
        },
    )
    json_storage.save_silver_collection(
        "draft_actions",
        [
            {
                "game_id": "g1",
                "action_order": 1,
                "phase": "PICK_PHASE_1",
                "action_type": "PICK",
                "team_side": "BLUE",
                "champion_id": "Varus",
                "is_flex": False,
            }
        ],
    )
    json_storage.save_silver_collection(
        "participants",
        [
            {"participant_game_id": "p1", "game_id": "g1", "team_id": "t1", "player_id": "gumayusi", "side": "BLUE", "role": "BOT", "champion_id": "Varus", "win": True, "patch_id": "15.20", "region": "INTL", "played_at": "2025-10-01T00:00:00Z"},
            {"participant_game_id": "p2", "game_id": "g1", "team_id": "geng", "player_id": "ruler", "side": "RED", "role": "BOT", "champion_id": "Ezreal", "win": False, "patch_id": "15.20", "region": "INTL", "played_at": "2025-10-01T00:00:00Z"},
        ],
    )
    json_storage.save_silver_collection(
        "teams",
        [
            {"team_id": "t1", "name": "T1", "short": "T1", "region": "KR", "league": "LCK", "active": True},
            {"team_id": "geng", "name": "Gen.G", "short": "GEN", "region": "KR", "league": "LCK", "active": True},
        ],
    )
    json_storage.save_silver_collection(
        "players",
        [
            {"player_id": "gumayusi", "handle": "Gumayusi", "primary_role": "BOT", "current_team_id": "t1"},
            {"player_id": "ruler", "handle": "Ruler", "primary_role": "BOT", "current_team_id": "geng"},
        ],
    )
    json_storage.save_silver_collection("patches", [{"patch_id": "15.20", "version_ddragon": "15.20.1"}])
    json_storage.save_gold_feature(
        "counterpick_matrix_15.20.json",
        [
            {
                "patch_id": "15.20",
                "role": "BOT",
                "region": "INTL",
                "champion_id": "Varus",
                "against_champion_id": "Ezreal",
                "games": 1,
                "wins": 1,
                "winrate_raw": 1.0,
                "winrate_shrunken": 0.6,
                "sample_confidence": 0.03,
            }
        ],
    )
    json_storage.save_gold_feature(
        "comfort_features_2026-05-24.json",
        [
            {
                "player_id": "gumayusi",
                "champion_id": "Varus",
                "games_total": 1,
                "games_recent_90d": 0,
                "winrate_total": 1.0,
                "winrate_recent_90d": 1.0,
                "comfort_score": 0.6,
                "last_played_at": "2025-10-01T00:00:00Z",
            }
        ],
    )


def test_health(esports_client):
    resp = esports_client.get("/api/v1/esports/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "esports_research"


def test_sources(esports_client):
    body = esports_client.get("/api/v1/esports/sources").json()
    assert body["summary"]["total"] == 12


def test_coverage_empty_returns_200(esports_client):
    body = esports_client.get("/api/v1/esports/coverage").json()
    assert body["success"] is True
    assert body["data"]["active_sources"] == 4


def test_tournaments_empty_gap(esports_client):
    body = esports_client.get("/api/v1/esports/tournaments").json()
    assert body["data"] == []
    assert body["gaps"]


def test_tournaments_with_data(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/tournaments?league=WORLDS&season=2025").json()
    assert body["total_records"] == 1


def test_tournament_detail(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/tournaments/worlds-2025").json()
    assert body["data"]["name"] == "Worlds 2025"


def test_match_detail(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/matches/m1").json()["data"]["best_of"] == 5


def test_game_detail(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/games/g1").json()["data"]["patch_id"] == "15.20"


def test_game_draft(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/games/g1/draft").json()
    assert body["data"][0]["champion_id"] == "Varus"


def test_game_participants(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/games/g1/participants").json()["total_records"] == 2


def test_teams(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/teams").json()["total_records"] == 2


def test_team_detail(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/teams/t1").json()["data"]["name"] == "T1"


def test_team_recent(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/teams/t1/recent?limit=5").json()
    assert body["total_records"] == 1


def test_team_champions(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/teams/t1/champions").json()
    assert body["data"][0]["champion_id"] == "Varus"


def test_player_detail(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/players/gumayusi").json()["data"]["handle"] == "Gumayusi"


def test_player_comfort(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/players/gumayusi/comfort").json()
    assert body["data"][0]["champion_id"] == "Varus"


def test_player_games(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/players/gumayusi/games").json()["total_records"] == 1


def test_champion_pro_stage(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/champions/Varus/pro-stage").json()["total_records"] == 1


def test_champion_matchups(esports_client):
    seed_storage()
    assert esports_client.get("/api/v1/esports/champions/Varus/matchups?patch=15.20").json()["total_records"] == 1


def test_counterpicks(esports_client):
    seed_storage()
    body = esports_client.get("/api/v1/esports/counterpicks?role=BOT&patch=15.20&region=INTL&limit=10").json()
    assert body["data"][0]["against_champion_id"] == "Ezreal"


def test_refresh_gold_with_no_silver_returns_gap(esports_client):
    body = esports_client.post("/api/v1/esports/refresh?mode=gold&tournament=worlds-2025").json()
    assert body["success"] is True
    assert body["gaps"]


def test_refresh_gold_with_silver_runs(esports_client):
    seed_storage()
    body = esports_client.post("/api/v1/esports/refresh?mode=gold&tournament=worlds-2025").json()
    assert body["data"]["success"] is True
    assert body["data"]["steps"]


def test_ingest_unknown_source(esports_client):
    body = esports_client.post("/api/v1/esports/ingest?source=missing&tournament=Worlds_2025").json()
    assert "unknown source" in body["gaps"][0]


def test_ingest_known_source_is_dry_run(esports_client):
    body = esports_client.post("/api/v1/esports/ingest?source=leaguepedia&tournament=Worlds_2025").json()
    assert body["data"]["status"] == "dry_run"


def test_ingest_real_leaguepedia_success(esports_client, monkeypatch):
    def fake_ingest(tournament):
        return {"success": True, "source": "leaguepedia", "raw_uri": f"bronze/{tournament}.json"}

    monkeypatch.setattr(esports_routes.ingest_leaguepedia, "ingest_tournament", fake_ingest)

    body = esports_client.post(
        "/api/v1/esports/ingest?source=leaguepedia&tournament=Worlds_2025&dry_run=false"
    ).json()

    assert body["data"]["status"] == "success"
    assert body["data"]["raw_uri"] == "bronze/Worlds_2025.json"
    assert body["gaps"] == []


def test_ingest_real_returns_gap_for_unwired_source(esports_client):
    body = esports_client.post("/api/v1/esports/ingest?source=oracles_elixir&dry_run=false").json()
    assert body["data"]["status"] == "gap"
    assert body["gaps"] == ["api ingest not implemented for source: oracles_elixir"]
