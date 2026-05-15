"""Scoring engine: percentiles, tiers, warnings, confidence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from riot_lol_cli.jungle_research.schemas import ChampionMetaSnapshot, JungleTier
from riot_lol_cli.jungle_research.scoring_engine import (
    THRESHOLD_LOW_SAMPLE,
    score_snapshots,
)

NOW = datetime(2026, 5, 11, 20, 0, 0, tzinfo=timezone.utc)


def _snap(
    champion: str,
    *,
    source_id: str = "ugg",
    win_rate: float = 50.0,
    pick_rate: float = 5.0,
    ban_rate: float = 1.0,
    games: int = 5000,
    extracted_at: str = "2026-05-11T18:00:00Z",
) -> ChampionMetaSnapshot:
    return ChampionMetaSnapshot(
        source_id=source_id,
        source_name=source_id.upper(),
        source_url=f"https://example.com/{source_id}",
        extracted_at=extracted_at,
        patch="14.10",
        region="GLOBAL",
        queue="ranked_solo_5x5",
        elo="EMERALD_PLUS",
        role="jungle",
        champion_id=champion.replace(" ", ""),
        champion_name=champion,
        win_rate=win_rate,
        pick_rate=pick_rate,
        ban_rate=ban_rate,
        games=games,
    )


def test_empty_snapshots_returns_empty_list():
    assert score_snapshots([], patch="14.10", region="GLOBAL", elo="EMERALD_PLUS") == []


def test_higher_winrate_gets_higher_score():
    snaps = [
        _snap("LowWR", win_rate=45.0),
        _snap("MidWR", win_rate=50.0),
        _snap("HighWR", win_rate=55.0),
    ]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    by_name = {e.champion_name: e for e in entries}
    assert by_name["HighWR"].final_score > by_name["LowWR"].final_score


def test_results_are_sorted_descending():
    snaps = [_snap(f"C{i}", win_rate=40 + i) for i in range(5)]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    scores = [e.final_score for e in entries]
    assert scores == sorted(scores, reverse=True)


def test_top_champion_gets_S_tier():
    snaps = [_snap(f"C{i}", win_rate=45 + i) for i in range(20)]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert entries[0].final_tier == JungleTier.S


def test_low_sample_warning_appears():
    snaps = [_snap("Niche", games=THRESHOLD_LOW_SAMPLE - 1)]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert "sample_size_low" in entries[0].warning_flags


def test_stale_warning_when_extraction_old():
    old = (NOW - timedelta(hours=80)).isoformat().replace("+00:00", "Z")
    snaps = [_snap("OldData", extracted_at=old)]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert "stale_>72h" in entries[0].warning_flags


def test_multiple_sources_aggregated_per_champion():
    snaps = [
        _snap("Wukong", source_id="ugg", win_rate=52.0),
        _snap("Wukong", source_id="lolalytics", win_rate=51.0),
        _snap("Wukong", source_id="opgg", win_rate=53.0),
    ]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert len(entries) == 1
    assert entries[0].source_count == 3


def test_pro_presence_lifts_score():
    snaps = [_snap("Wukong", win_rate=50.0), _snap("Other", win_rate=50.0)]
    entries_no_pro = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    entries_pro = score_snapshots(
        snaps,
        patch="14.10",
        region="GLOBAL",
        elo="EMERALD_PLUS",
        pro_presence={"Wukong": 1.0},
        now=NOW,
    )
    no_pro = next(e for e in entries_no_pro if e.champion_name == "Wukong")
    with_pro = next(e for e in entries_pro if e.champion_name == "Wukong")
    assert with_pro.final_score > no_pro.final_score


def test_outlier_winrate_marked():
    """52% rodeado de 50%; 75% es outlier (>3σ)."""
    snaps = [_snap(f"C{i}", win_rate=50.0 + (i % 3) * 0.5) for i in range(15)]
    snaps.append(_snap("OutlierBoost", win_rate=75.0))
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    outlier = next(e for e in entries if e.champion_name == "OutlierBoost")
    assert "outlier:win_rate" in outlier.warning_flags


def test_confidence_above_zero():
    snaps = [_snap("Wukong", source_id="ugg"), _snap("Wukong", source_id="opgg")]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert entries[0].confidence > 0


def test_explanation_contains_sources_and_n():
    snaps = [_snap("Wukong", games=5432)]
    entries = score_snapshots(
        snaps, patch="14.10", region="GLOBAL", elo="EMERALD_PLUS", now=NOW
    )
    assert "sources=1" in entries[0].explanation
    assert "N=5432" in entries[0].explanation
