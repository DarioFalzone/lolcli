"""pipeline meta_soloq sobre fixtures sintéticos del Meta Scraper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import meta_soloq


@pytest.fixture
def tmp_storage(tmp_path: Path, monkeypatch) -> Path:
    """Aisla `data/meta_analyzer/jungle_research/` en tmp."""
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    csd = tmp_path / "champion_meta_snapshots"
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_DIR", csd)
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_LATEST", csd / "latest.json")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_BACKUPS", csd / "backups")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_HISTORY", csd / "history")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_RAW", csd / "raw")
    return tmp_path


@pytest.fixture
def fake_meta_scraper(tmp_path: Path, monkeypatch):
    """Reapunta META_SCRAPER_NORMALIZED a un fixture sintético."""
    src = tmp_path / "fake_jungle_tier.json"
    src.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "patch": "26.10",
                "scraped_at": "2026-05-11T10:00:00.000000+00:00",
                "champions": [
                    {
                        "id": "Wukong",
                        "display_name": "Wukong",
                        "stats": {
                            "win_rate": 52.0,
                            "pick_rate": 8.0,
                            "ban_rate": 5.0,
                            "games_analyzed": 50000,
                            "tier": "S",
                        },
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 51.5,
                                "pick_rate": 8.2,
                                "ban_rate": 5.1,
                                "games_analyzed": 25000,
                                "tier": "S",
                                "patch": "26.10",
                                "scraped_at": "2026-05-11T10:00:00Z",
                            },
                            "lolalytics": {
                                "win_rate": 52.5,
                                "pick_rate": 7.8,
                                "ban_rate": 4.9,
                                "games_analyzed": 25000,
                                "tier": "A+",
                                "patch": "16.10",
                                "scraped_at": "2026-05-11T09:30:00Z",
                            },
                        },
                    },
                ],
                "source_gaps": [{"source": "opgg", "reason": "timeout"}],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", src)
    return src


@pytest.fixture
def fake_jungle_meta(tmp_path: Path, monkeypatch):
    """Reapunta JUNGLE_META_DIR a un fixture sintético."""
    target_dir = tmp_path / "jungle_meta"
    target_dir.mkdir()
    (target_dir / "patch_26.10.json").write_text(
        json.dumps(
            {
                "patch": "26.10",
                "date_updated": "2026-05-10T00:00:00Z",
                "jungle_champions": [
                    {
                        "id": "Wukong",
                        "display_name": "Wukong",
                        "tier": "A",
                        "winrate": 53.0,
                        "pickrate": 7.5,
                        "banrate": 5.0,
                        "primary_reason": "human_curated",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", target_dir)
    return target_dir


def test_run_with_no_sources_returns_gaps(tmp_path: Path, monkeypatch, tmp_storage):
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", tmp_path / "no.json")
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "nope")
    result = meta_soloq.run(persist=False)
    assert result.snapshots == []
    assert len(result.gaps) >= 2  # ambas fuentes faltantes
    assert result.sources_used == []


def test_run_consumes_meta_scraper(tmp_storage, fake_meta_scraper, monkeypatch):
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_storage / "absent")
    result = meta_soloq.run(persist=False)
    assert len(result.snapshots) == 2  # ugg + lolalytics
    assert "ugg" in result.sources_used
    assert "lolalytics" in result.sources_used
    assert result.patch == "26.10"


def test_run_consumes_jungle_meta_local(tmp_storage, fake_jungle_meta, monkeypatch):
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", tmp_storage / "absent.json")
    result = meta_soloq.run(persist=False)
    assert len(result.snapshots) == 1
    assert result.snapshots[0].source_id == "jungle_meta_local"


def test_run_combines_both_sources(tmp_storage, fake_meta_scraper, fake_jungle_meta):
    result = meta_soloq.run(persist=False)
    # 2 del scraper + 1 curated = 3 total
    assert len(result.snapshots) == 3
    assert "jungle_meta_local" in result.sources_used


def test_run_persists_to_storage(tmp_storage, fake_meta_scraper, fake_jungle_meta):
    meta_soloq.run(persist=True)
    assert json_storage.CHAMPION_SNAPSHOTS_LATEST.exists()
    payload = json.loads(json_storage.CHAMPION_SNAPSHOTS_LATEST.read_text(encoding="utf-8"))
    assert payload["snapshot_count"] == 3


def test_unknown_tier_gets_warning(tmp_path: Path, tmp_storage, monkeypatch):
    src = tmp_path / "weird_tier.json"
    src.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": "X",
                        "display_name": "X",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50.0,
                                "tier": "GOD",
                                "scraped_at": "2026-05-11T10:00:00Z",
                            }
                        },
                    }
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", src)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "nope")
    result = meta_soloq.run(persist=False)
    assert result.snapshots[0].tier is None
    assert any("unknown_tier" in f for f in result.snapshots[0].warning_flags)


def test_normalize_iso_handles_microseconds():
    assert meta_soloq._normalize_iso("2026-05-11T10:00:00.123456+00:00") == "2026-05-11T10:00:00Z"
    assert meta_soloq._normalize_iso("2026-05-11T10:00:00Z") == "2026-05-11T10:00:00Z"
    assert meta_soloq._normalize_iso("2026-05-11T10:00:00") == "2026-05-11T10:00:00Z"
    assert meta_soloq._normalize_iso(None).endswith("Z")
