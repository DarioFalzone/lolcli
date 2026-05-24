from __future__ import annotations

import pytest

from riot_lol_cli.esports_research.analytics.counterpick import (
    bayesian_winrate,
    compute_counterpick_entries,
    sample_confidence,
)
from riot_lol_cli.esports_research.pipelines.compute_counterpick_matrix import compute_and_save

PARTICIPANTS = [
    {"game_id": "g1", "side": "BLUE", "role": "BOT", "champion_id": "Varus", "win": True, "patch_id": "15.20"},
    {"game_id": "g1", "side": "RED", "role": "BOT", "champion_id": "Ezreal", "win": False, "patch_id": "15.20"},
    {"game_id": "g2", "side": "BLUE", "role": "BOT", "champion_id": "Ezreal", "win": True, "patch_id": "15.20"},
    {"game_id": "g2", "side": "RED", "role": "BOT", "champion_id": "Varus", "win": False, "patch_id": "15.20"},
]


def test_bayesian_winrate_beta_2_2():
    assert bayesian_winrate(1, 1) == pytest.approx(0.6)


def test_bayesian_winrate_rejects_bad_counts():
    with pytest.raises(ValueError):
        bayesian_winrate(2, 1)


@pytest.mark.parametrize("games,expected", [(0, 0.0), (15, 0.5), (30, 1.0), (45, 1.0)])
def test_sample_confidence(games, expected):
    assert sample_confidence(games) == expected


def test_compute_counterpick_entries_two_way():
    entries = compute_counterpick_entries(PARTICIPANTS, patch_id="15.20", region="INTL")
    assert len(entries) == 2
    varus = next(entry for entry in entries if entry.champion_id == "Varus")
    assert varus.games == 2
    assert varus.wins == 1
    assert varus.winrate_shrunken == pytest.approx(0.5)


def test_compute_counterpick_skips_missing_opponent():
    entries = compute_counterpick_entries([PARTICIPANTS[0]], patch_id="15.20", region="INTL")
    assert entries == []


def test_compute_and_save_counterpick(esports_tmp_root):
    result = compute_and_save(PARTICIPANTS, patch_id="15.20", region="INTL")
    assert result["success"] is True
    assert result["entries"] == 2
