from __future__ import annotations

import json
from pathlib import Path

from riot_lol_cli.esports_research import json_storage


def test_ensure_directories_creates_layout(esports_tmp_root: Path):
    for sub in ("bronze", "silver", "gold", "reports", "silver/matches", "silver/games"):
        assert (esports_tmp_root / sub).is_dir()


def test_read_json_missing_returns_none(esports_tmp_root: Path):
    assert json_storage.read_json(esports_tmp_root / "missing.json") is None


def test_write_json_atomic_no_tmp_left(esports_tmp_root: Path):
    target = json_storage.write_json_atomic(esports_tmp_root / "x" / "data.json", {"ok": True})
    assert json.loads(target.read_text(encoding="utf-8")) == {"ok": True}
    assert list(esports_tmp_root.rglob("*.tmp")) == []


def test_write_text_atomic_no_bom(esports_tmp_root: Path):
    target = json_storage.write_text_atomic(esports_tmp_root / "x" / "page.html", "<h1>ok</h1>")
    assert target.read_bytes()[:3] != b"\xef\xbb\xbf"


def test_save_bronze_json_partitions_by_source(esports_tmp_root: Path):
    target = json_storage.save_bronze_json("leaguepedia", "worlds", "matches", {"rows": []})
    assert "bronze" in target.parts
    assert "leaguepedia" in target.parts
    assert target.suffix == ".json"


def test_save_bronze_text_uses_suffix(esports_tmp_root: Path):
    target = json_storage.save_bronze_text("gol_gg", "today", "worlds", "<html></html>", ".html")
    assert target.suffix == ".html"


def test_silver_collection_round_trip(esports_tmp_root: Path):
    json_storage.save_silver_collection("teams", [{"team_id": "t1"}])
    assert json_storage.read_silver_collection("teams") == [{"team_id": "t1"}]


def test_silver_entity_round_trip(esports_tmp_root: Path):
    json_storage.save_silver_entity("games", "g1", {"game_id": "g1"})
    assert json_storage.read_silver_entity("games", "g1") == {"game_id": "g1"}


def test_gold_feature_round_trip(esports_tmp_root: Path):
    json_storage.save_gold_feature("counterpick_matrix_15.20.json", [{"x": 1}])
    assert json_storage.read_gold_feature("counterpick_matrix_15.20.json") == [{"x": 1}]


def test_report_round_trip(esports_tmp_root: Path):
    json_storage.save_report("coverage_2026-05-24.json", {"ok": True})
    assert json_storage.read_json(esports_tmp_root / "reports" / "coverage_2026-05-24.json")["ok"] is True


def test_read_sources_handles_dict(esports_tmp_root: Path):
    assert len(json_storage.read_sources()) == 12


def test_list_json_rows_reads_directory(esports_tmp_root: Path):
    json_storage.save_silver_entity("matches", "m1", {"match_id": "m1"})
    assert json_storage.list_json_rows(esports_tmp_root / "silver" / "matches") == [{"match_id": "m1"}]
