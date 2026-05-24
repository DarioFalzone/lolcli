from __future__ import annotations

from riot_lol_cli.esports_research.pipelines.reconcile_sources import reconcile_records


def test_reconcile_keeps_single_record():
    result = reconcile_records([{"game_id": "g1", "source_origin": "leaguepedia"}], "game_id")
    assert result["records"] == [{"game_id": "g1", "source_origin": "leaguepedia"}]
    assert result["divergences"] == []


def test_reconcile_prefers_leaguepedia_over_gol():
    result = reconcile_records(
        [
            {"game_id": "g1", "source_origin": "gol_gg", "value": 1},
            {"game_id": "g1", "source_origin": "leaguepedia", "value": 2},
        ],
        "game_id",
    )
    assert result["records"][0]["value"] == 2
    assert result["divergences"]


def test_reconcile_logs_discarded_lower_priority():
    result = reconcile_records(
        [
            {"game_id": "g1", "source_origin": "leaguepedia", "value": 1},
            {"game_id": "g1", "source_origin": "gol_gg", "value": 2},
        ],
        "game_id",
    )
    assert result["records"][0]["value"] == 1
    assert result["divergences"][0]["discarded"] == "gol_gg"


def test_reconcile_missing_id_is_divergence():
    result = reconcile_records([{"source_origin": "leaguepedia"}], "game_id")
    assert result["records"] == []
    assert result["divergences"][0]["reason"] == "missing_id"


def test_reconcile_same_record_no_divergence():
    row = {"game_id": "g1", "source_origin": "leaguepedia", "value": 1}
    result = reconcile_records([row, row], "game_id")
    assert result["records"] == [row]
    assert result["divergences"] == []
