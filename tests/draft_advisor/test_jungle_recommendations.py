from __future__ import annotations

import pytest

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.jungle_meta_provider import JungleMetaSnapshot
from riot_lol_cli.draft_advisor.schemas import AdvisorMode, DraftState, UserPool
from riot_lol_cli.draft_advisor.scoring import ScoringEngine
from riot_lol_cli.jungle_meta.loader import load_jungle_tier_list


@pytest.fixture()
def data_service() -> ChampionDataService:
    service = ChampionDataService()
    service._jungle_meta_snapshot = JungleMetaSnapshot(
        data=load_jungle_tier_list(),
        status="local_fallback",
        error="test fallback",
    )
    return service


@pytest.fixture()
def engine(data_service: ChampionDataService) -> ScoringEngine:
    return ScoringEngine(data_service)


def test_jungle_meta_uses_canonical_champion_ids(data_service: ChampionDataService) -> None:
    champion_ids = data_service.get_all_champion_ids()
    unknown = data_service.get_jungle_meta_without_champion_base()

    assert unknown == []
    assert data_service.get_jungler_ids() <= champion_ids
    assert "XinZhao" in data_service.get_jungler_ids()


def test_jungle_s_tier_beats_b_tier_even_with_pool(engine: ScoringEngine) -> None:
    draft = DraftState(
        target_role=AdvisorMode.JUNGLE,
        user_pool=UserPool(mode="pool_only", champions=["LeeSin", "XinZhao"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "XinZhao"
    assert result.top_pick.jungle_context is not None
    assert result.top_pick.jungle_context.tier == "S"
    assert any(alt.id == "LeeSin" for alt in result.alternatives)


def test_jungle_b_tier_can_be_fallback_when_better_tiers_are_blocked(engine: ScoringEngine) -> None:
    draft = DraftState(
        target_role=AdvisorMode.JUNGLE,
        user_pool=UserPool(mode="pool_only", champions=["LeeSin", "Kindred"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id in {"LeeSin", "Kindred"}
    assert result.top_pick.jungle_context is not None
    assert result.top_pick.jungle_context.tier == "B"
    assert result.top_pick.jungle_context.eligibility == "fallback_tier_b"


def test_jungle_c_tier_is_not_top_outside_pool_only(engine: ScoringEngine) -> None:
    draft = DraftState(
        target_role=AdvisorMode.JUNGLE,
        user_pool=UserPool(mode="pool_preferred", champions=["Evelynn"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id != "Evelynn"
    assert result.top_pick.jungle_context is not None
    assert result.top_pick.jungle_context.tier in {"S", "A"}


def test_jungle_c_tier_can_be_top_only_when_pool_only_has_no_better_option(engine: ScoringEngine) -> None:
    draft = DraftState(
        target_role=AdvisorMode.JUNGLE,
        user_pool=UserPool(mode="pool_only", champions=["Evelynn"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Evelynn"
    assert result.top_pick.jungle_context is not None
    assert result.top_pick.jungle_context.tier == "C"
    assert result.top_pick.jungle_context.eligibility == "fallback_tier_c_pool_only"


def test_jungle_picked_or_banned_champions_are_not_recommended(engine: ScoringEngine) -> None:
    draft = DraftState(
        target_role=AdvisorMode.JUNGLE,
        bans=["XinZhao", "Shyvana", "Udyr", "Kayn"],
    )

    result = engine.recommend(draft)
    recommended_ids = {result.top_pick.id, *[alt.id for alt in result.alternatives]}

    assert recommended_ids.isdisjoint({"XinZhao", "Shyvana", "Udyr", "Kayn"})
    assert result.top_pick.jungle_context is not None
    assert result.top_pick.jungle_context.source_status == "local_fallback"
