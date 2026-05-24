from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.esports_research.analytics.comfort import compute_comfort_scores
from riot_lol_cli.esports_research.pipelines.compute_comfort_scores import compute_and_save

PARTICIPANTS = [
    {"player_id": "faker", "champion_id": "Azir", "win": True, "played_at": "2026-05-01T00:00:00Z"},
    {"player_id": "faker", "champion_id": "Azir", "win": False, "played_at": "2026-04-01T00:00:00Z"},
    {"player_id": "faker", "champion_id": "Orianna", "win": True, "played_at": "2025-01-01T00:00:00Z"},
]


def test_compute_comfort_groups_by_player_champion():
    scores = compute_comfort_scores(PARTICIPANTS, now=datetime(2026, 5, 24, tzinfo=timezone.utc))
    assert {(score.player_id, score.champion_id) for score in scores} == {("faker", "Azir"), ("faker", "Orianna")}


def test_compute_comfort_recent_window():
    scores = compute_comfort_scores(PARTICIPANTS, now=datetime(2026, 5, 24, tzinfo=timezone.utc))
    azir = next(score for score in scores if score.champion_id == "Azir")
    assert azir.games_total == 2
    assert azir.games_recent_90d == 2
    assert azir.winrate_recent_90d == 0.5


def test_compute_comfort_falls_back_to_total_when_no_recent():
    scores = compute_comfort_scores(PARTICIPANTS, now=datetime(2026, 5, 24, tzinfo=timezone.utc))
    orianna = next(score for score in scores if score.champion_id == "Orianna")
    assert orianna.games_recent_90d == 0
    assert orianna.winrate_recent_90d == 1.0


def test_comfort_score_formula():
    scores = compute_comfort_scores(PARTICIPANTS, now=datetime(2026, 5, 24, tzinfo=timezone.utc))
    azir = next(score for score in scores if score.champion_id == "Azir")
    assert azir.comfort_score == pytest.approx(0.38)


def test_compute_and_save_comfort(esports_tmp_root):
    result = compute_and_save(PARTICIPANTS, report_date="2026-05-24")
    assert result["success"] is True
    assert result["entries"] == 2
