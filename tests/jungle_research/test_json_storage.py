"""json_storage: snapshots inmutables, rotación y helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage


@pytest.fixture
def tmp_root(tmp_path: Path, monkeypatch) -> Path:
    """Reapunta TODO el storage canónico a un tmp_path aislado."""
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)

    monkeypatch.setattr(json_storage, "SOURCES_FILE", tmp_path / "sources.json")
    monkeypatch.setattr(
        json_storage, "PRO_PLAYERS_SEED_FILE", tmp_path / "pro_players_seed.json"
    )
    monkeypatch.setattr(json_storage, "PRO_ACCOUNTS_FILE", tmp_path / "pro_accounts.json")

    csd = tmp_path / "champion_meta_snapshots"
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_DIR", csd)
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_LATEST", csd / "latest.json")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_BACKUPS", csd / "backups")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_HISTORY", csd / "history")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_RAW", csd / "raw")

    monkeypatch.setattr(json_storage, "MATCH_HISTORY_DIR", tmp_path / "match_history")
    monkeypatch.setattr(json_storage, "OTP_RANKINGS_DIR", tmp_path / "otp_rankings")

    ftd = tmp_path / "final_jungle_tierlist"
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_DIR", ftd)
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_LATEST", ftd / "latest.json")
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_HISTORY", ftd / "history")

    monkeypatch.setattr(json_storage, "DAILY_REPORTS_DIR", tmp_path / "daily_reports")

    return tmp_path


def test_ensure_directories_creates_all(tmp_root: Path):
    json_storage.ensure_directories()
    for sub in (
        "champion_meta_snapshots",
        "champion_meta_snapshots/backups",
        "champion_meta_snapshots/history",
        "champion_meta_snapshots/raw",
        "match_history",
        "otp_rankings",
        "final_jungle_tierlist",
        "final_jungle_tierlist/history",
        "daily_reports",
    ):
        assert (tmp_root / sub).is_dir()


def test_read_json_returns_none_for_missing_file(tmp_root: Path):
    assert json_storage.read_json(tmp_root / "nope.json") is None


def test_save_champion_snapshots_creates_latest_and_history(tmp_root: Path):
    payload = {"snapshots": [{"champion_name": "Wukong"}]}
    latest, backup, history = json_storage.save_champion_snapshots(payload)
    assert latest.exists()
    assert backup is None  # primera escritura, no hay versión previa
    assert history.exists()
    assert json.loads(latest.read_text(encoding="utf-8"))["snapshots"][0]["champion_name"] == "Wukong"


def test_save_champion_snapshots_rotates_to_backup(tmp_root: Path):
    json_storage.save_champion_snapshots({"v": 1})
    _, backup, _ = json_storage.save_champion_snapshots({"v": 2})
    assert backup is not None
    assert json.loads(backup.read_text(encoding="utf-8"))["v"] == 1
    latest_text = (tmp_root / "champion_meta_snapshots" / "latest.json").read_text(encoding="utf-8")
    assert json.loads(latest_text)["v"] == 2


def test_save_final_tierlist_rotates(tmp_root: Path):
    json_storage.save_final_tierlist({"v": 1})
    _, backup, history = json_storage.save_final_tierlist({"v": 2})
    assert backup is not None
    assert history.exists()


def test_save_daily_report_uses_date_filename(tmp_root: Path):
    target = json_storage.save_daily_report("2026-05-11", {"ok": True})
    assert target.name == "2026-05-11.json"
    assert json.loads(target.read_text(encoding="utf-8"))["ok"] is True


def test_save_match_history_partitioned_by_puuid(tmp_root: Path):
    target = json_storage.save_match_history("ABC", {"matches": []})
    assert target.parent.name == "ABC"


def test_save_otp_ranking_partitioned_by_champion(tmp_root: Path):
    target = json_storage.save_otp_ranking("LeeSin", {"ranking": []})
    assert target.parent.name == "LeeSin"


def test_save_raw_payload_partitioned_by_source(tmp_root: Path):
    target = json_storage.save_raw_payload("ugg", {"raw": "html"})
    assert target.parent.name == "ugg"
    assert target.parent.parent.name == "raw"


def test_read_sources_handles_dict_or_list(tmp_root: Path):
    json_storage.SOURCES_FILE.write_text(
        json.dumps({"sources": [{"id": "x"}]}), encoding="utf-8"
    )
    assert json_storage.read_sources() == [{"id": "x"}]


def test_read_sources_handles_missing(tmp_root: Path):
    assert json_storage.read_sources() == []


def test_atomic_write_no_partial_file(tmp_root: Path):
    """No debe quedar archivo .tmp después de una escritura exitosa."""
    json_storage.save_daily_report("2026-05-11", {"ok": True})
    tmps = list(tmp_root.rglob("*.tmp"))
    assert tmps == []
