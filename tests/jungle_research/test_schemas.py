"""Schemas Pydantic V2 de Jungle Research."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from riot_lol_cli.jungle_research.schemas import (
    ChampionMetaSnapshot,
    DailyReport,
    FinalJungleTierEntry,
    FinalJungleTierList,
    JungleTier,
    MatchHistoryEntry,
    OtpRankingEntry,
    ProAccount,
    ProPlayer,
    Source,
    SourceStatus,
    SourceType,
    utcnow_iso,
)


def test_source_minimal_valid():
    src = Source(
        id="test",
        name="Test Source",
        base_url="https://example.com",
        source_type=SourceType.SOLOQ_META,
        created_at="2026-05-11T20:00:00Z",
        updated_at="2026-05-11T20:00:00Z",
    )
    assert src.status == SourceStatus.PLANNED
    assert src.scrape_priority == 50
    assert src.region_focus == []


def test_source_extra_field_allowed():
    src = Source.model_validate(
        {
            "id": "x",
            "name": "X",
            "base_url": "https://x",
            "source_type": "soloq_meta",
            "status": "active",
            "created_at": "2026-05-11T20:00:00Z",
            "updated_at": "2026-05-11T20:00:00Z",
            "experimental_field": "ignored_safely",
        }
    )
    assert src.id == "x"


def test_source_invalid_type_rejected():
    with pytest.raises(ValidationError):
        Source(
            id="x",
            name="X",
            base_url="https://x",
            source_type="not_a_real_type",  # type: ignore[arg-type]
            created_at="2026-05-11T20:00:00Z",
            updated_at="2026-05-11T20:00:00Z",
        )


def test_champion_meta_snapshot_with_optional_fields():
    snap = ChampionMetaSnapshot(
        source_id="ugg",
        source_name="U.GG",
        source_url="https://u.gg/lol/jungle-tier-list",
        extracted_at=utcnow_iso(),
        patch="14.10",
        region="GLOBAL",
        queue="ranked_solo_5x5",
        elo="EMERALD_PLUS",
        role="jungle",
        champion_id="LeeSin",
        champion_name="Lee Sin",
        win_rate=51.4,
        pick_rate=8.3,
        ban_rate=12.0,
        games=15234,
    )
    assert snap.tier is None
    assert snap.warning_flags == []


def test_pro_player_default_role_is_jungle():
    p = ProPlayer(
        player_name="Canyon",
        priority_tier="S",
        created_at=utcnow_iso(),
        updated_at=utcnow_iso(),
    )
    assert p.role == "jungle"
    assert p.urls.trackingthepros is None


def test_pro_account_gap_flag_serializes():
    acc = ProAccount(
        pro_player_id="Canyon",
        source="manual_seed",
        gap_flag="needs_account_resolution",
    )
    dumped = acc.model_dump()
    assert dumped["gap_flag"] == "needs_account_resolution"
    assert dumped["puuid"] is None


def test_match_history_entry_required_fields():
    entry = MatchHistoryEntry(
        match_id="KR_7000000000",
        puuid="abc123",
        game_datetime="2026-05-10T10:00:00Z",
        champion_name="Wukong",
        created_at=utcnow_iso(),
    )
    assert entry.win is None
    assert entry.source == "riot_api"


def test_otp_ranking_entry():
    entry = OtpRankingEntry(
        source_id="onetricks",
        champion_name="LeeSin",
        role="jungle",
        region="KR",
        summoner_name="HideOnLee",
        ranking_position=1,
        source_url="https://www.onetricks.gg/champions/ranking/LeeSin",
        extracted_at=utcnow_iso(),
    )
    assert entry.ranking_position == 1


def test_final_jungle_tier_entry():
    entry = FinalJungleTierEntry(
        champion_name="Wukong",
        final_tier=JungleTier.S,
        final_score=0.92,
        soloq_score=0.88,
        confidence=0.75,
        source_count=3,
        generated_at=utcnow_iso(),
        patch="14.10",
        region="GLOBAL",
        elo="EMERALD_PLUS",
    )
    assert entry.role == "jungle"
    assert entry.final_tier == JungleTier.S


def test_final_jungle_tier_list_round_trip():
    tl = FinalJungleTierList(
        generated_at=utcnow_iso(),
        patch="14.10",
        region="GLOBAL",
        elo="EMERALD_PLUS",
        entries=[
            FinalJungleTierEntry(
                champion_name="Wukong",
                final_tier=JungleTier.S,
                final_score=0.92,
                generated_at=utcnow_iso(),
                patch="14.10",
                region="GLOBAL",
                elo="EMERALD_PLUS",
            )
        ],
    )
    dumped = tl.model_dump()
    rehydrated = FinalJungleTierList.model_validate(dumped)
    assert rehydrated.entries[0].final_tier == JungleTier.S


def test_daily_report_defaults():
    r = DailyReport(
        report_date="2026-05-11",
        generated_at=utcnow_iso(),
        patch="14.10",
    )
    assert r.risers == []
    assert r.fallers == []


def test_utcnow_iso_format():
    iso = utcnow_iso()
    assert iso.endswith("Z")
    assert "T" in iso
