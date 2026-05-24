"""daily_report: gaps controlados, risers/fallers, contradictions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.reports import daily_report


@pytest.fixture
def tmp_storage(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    ftd = tmp_path / "final_jungle_tierlist"
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_DIR", ftd)
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_LATEST", ftd / "latest.json")
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_HISTORY", ftd / "history")
    csd = tmp_path / "champion_meta_snapshots"
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_DIR", csd)
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_LATEST", csd / "latest.json")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_BACKUPS", csd / "backups")
    monkeypatch.setattr(json_storage, "DAILY_REPORTS_DIR", tmp_path / "daily_reports")
    return tmp_path


def _entry(champion: str, *, tier: str = "A", score: float = 0.7, confidence: float = 0.6) -> dict:
    return {
        "champion_name": champion,
        "role": "jungle",
        "final_tier": tier,
        "final_score": score,
        "confidence": confidence,
        "source_count": 2,
        "warning_flags": [],
        "generated_at": "2026-05-11T20:00:00Z",
        "patch": "26.10",
        "region": "GLOBAL",
        "elo": "EMERALD_PLUS",
    }


def _tierlist(entries) -> dict:
    return {
        "generated_at": "2026-05-11T20:00:00Z",
        "patch": "26.10",
        "region": "GLOBAL",
        "elo": "EMERALD_PLUS",
        "queue": "ranked_solo_5x5",
        "entries": entries,
        "source_count_total": 3,
        "gaps": [],
        "warning_flags": [],
    }


def test_no_tierlist_returns_none(tmp_storage):
    report = daily_report.generate(report_date="2026-05-11", persist=False)
    assert report is None


def test_with_tierlist_no_backup_returns_top_only(tmp_storage):
    json_storage.FINAL_TIERLIST_LATEST.parent.mkdir(parents=True, exist_ok=True)
    json_storage.FINAL_TIERLIST_LATEST.write_text(
        json.dumps(_tierlist([_entry("Wukong", score=0.9), _entry("LeeSin", score=0.8)])),
        encoding="utf-8",
    )
    report = daily_report.generate(report_date="2026-05-11", persist=False)
    assert report is not None
    assert len(report.top_junglers) == 2
    assert report.risers == []
    assert report.fallers == []


def test_with_backup_detects_risers_and_fallers(tmp_storage):
    backups = json_storage.FINAL_TIERLIST_DIR / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    (backups / "2026-05-10T20-00-00.json").write_text(
        json.dumps(_tierlist([_entry("Wukong", score=0.5), _entry("LeeSin", score=0.9)])),
        encoding="utf-8",
    )
    json_storage.FINAL_TIERLIST_LATEST.write_text(
        json.dumps(_tierlist([_entry("Wukong", score=0.9), _entry("LeeSin", score=0.5)])),
        encoding="utf-8",
    )
    report = daily_report.generate(report_date="2026-05-11", persist=False)
    assert report is not None
    risers_names = {m.champion_name for m in report.risers}
    fallers_names = {m.champion_name for m in report.fallers}
    assert "Wukong" in risers_names
    assert "LeeSin" in fallers_names


def test_contradictions_detected_when_wr_spread_high(tmp_storage):
    json_storage.FINAL_TIERLIST_LATEST.parent.mkdir(parents=True, exist_ok=True)
    json_storage.FINAL_TIERLIST_LATEST.write_text(json.dumps(_tierlist([_entry("X")])), encoding="utf-8")
    json_storage.CHAMPION_SNAPSHOTS_LATEST.parent.mkdir(parents=True, exist_ok=True)
    json_storage.CHAMPION_SNAPSHOTS_LATEST.write_text(
        json.dumps(
            {
                "snapshots": [
                    {"champion_name": "X", "source_id": "ugg", "win_rate": 45.0},
                    {"champion_name": "X", "source_id": "lolalytics", "win_rate": 56.0},
                    {"champion_name": "Y", "source_id": "ugg", "win_rate": 50.0},
                    {"champion_name": "Y", "source_id": "lolalytics", "win_rate": 50.5},
                ]
            }
        ),
        encoding="utf-8",
    )
    report = daily_report.generate(report_date="2026-05-11", persist=False)
    assert report is not None
    names = [c["champion_name"] for c in report.contradictions]
    assert "X" in names  # spread 11pp
    assert "Y" not in names  # spread 0.5pp


def test_persists_to_daily_reports_dir(tmp_storage):
    json_storage.FINAL_TIERLIST_LATEST.parent.mkdir(parents=True, exist_ok=True)
    json_storage.FINAL_TIERLIST_LATEST.write_text(
        json.dumps(_tierlist([_entry("Wukong")])), encoding="utf-8"
    )
    daily_report.generate(report_date="2026-05-11", persist=True)
    target = tmp_storage / "daily_reports" / "2026-05-11.json"
    assert target.exists()
