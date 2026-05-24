from __future__ import annotations

import pytest
from pydantic import ValidationError

from riot_lol_cli.esports_research.schemas import (
    ChampionDim,
    ComfortScore,
    CounterpickEntry,
    DraftAction,
    Game,
    Match,
    ParticipantGame,
    Patch,
    Player,
    Source,
    SourceStatus,
    SourceType,
    Team,
    Tournament,
    utcnow_iso,
)


def test_source_accepts_registry_shape():
    source = Source(
        id="leaguepedia",
        name="Leaguepedia",
        base_url="https://lol.fandom.com",
        source_type="community_api",
        status="active",
        created_at="2026-05-24T00:00:00Z",
        updated_at="2026-05-24T00:00:00Z",
    )
    assert source.source_type == SourceType.COMMUNITY_API
    assert source.status == SourceStatus.ACTIVE


@pytest.mark.parametrize(
    "model,payload",
    [
        (Tournament, {"tournament_id": "t1", "name": "Worlds", "region": "INTL", "league": "WORLDS", "format": "BO5", "start_date": "2025-10-01", "source_origin": "leaguepedia"}),
        (Match, {"match_id": "m1", "tournament_id": "t1", "scheduled_at": "2025-10-01T00:00:00Z", "best_of": 5, "team_blue_id": "blue", "team_red_id": "red", "source_origin": "leaguepedia"}),
        (Game, {"game_id": "g1", "match_id": "m1", "game_number": 1, "patch_id": "15.20", "source_origin": "leaguepedia", "source_game_key": "raw"}),
        (DraftAction, {"game_id": "g1", "action_order": 1, "phase": "BAN_PHASE_1", "action_type": "ban", "team_side": "blue", "champion_id": "Varus"}),
        (Team, {"team_id": "t1", "name": "T1", "short": "T1", "region": "KR", "league": "LCK"}),
        (Player, {"player_id": "p1", "handle": "Faker", "primary_role": "MID"}),
        (ParticipantGame, {"participant_game_id": "pg1", "game_id": "g1", "team_id": "t1", "player_id": "p1", "side": "BLUE", "role": "MID", "champion_id": "Azir"}),
        (Patch, {"patch_id": "15.20", "version_ddragon": "15.20.1"}),
        (ChampionDim, {"champion_id": "MonkeyKing", "display_name": "Wukong"}),
        (CounterpickEntry, {"patch_id": "15.20", "role": "BOT", "region": "INTL", "champion_id": "Varus", "against_champion_id": "Ezreal", "games": 1, "wins": 1, "winrate_raw": 1.0, "winrate_shrunken": 0.6, "sample_confidence": 0.03}),
        (ComfortScore, {"player_id": "p1", "champion_id": "Azir", "games_total": 5, "games_recent_90d": 2, "winrate_total": 0.6, "winrate_recent_90d": 0.5, "comfort_score": 0.38}),
    ],
)
def test_models_round_trip(model, payload):
    instance = model.model_validate(payload)
    assert model.model_validate(instance.model_dump(mode="json"))


def test_draft_action_normalizes_tokens():
    action = DraftAction(game_id="g1", action_order=1, phase="x", action_type="pick", team_side="red", champion_id="Ahri")
    assert action.action_type == "PICK"
    assert action.team_side == "RED"


def test_game_rejects_bad_winner_side():
    with pytest.raises(ValidationError):
        Game(
            game_id="g1",
            match_id="m1",
            game_number=1,
            patch_id="15.20",
            winner_side="GREEN",
            source_origin="x",
            source_game_key="x",
        )


def test_utcnow_iso_z_suffix():
    assert utcnow_iso().endswith("Z")
