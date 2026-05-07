from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.schemas import DraftChampion, DraftContext, DraftState, UserPool
from riot_lol_cli.draft_advisor.scoring import ScoringEngine


@pytest.fixture()
def data_service() -> ChampionDataService:
    service = ChampionDataService()
    service._adc_meta_snapshot["scraped_at"] = datetime.now(timezone.utc).isoformat()
    return service


@pytest.fixture()
def engine(data_service: ChampionDataService) -> ScoringEngine:
    return ScoringEngine(data_service)


def test_personal_adc_mastery_uses_canonical_ids(data_service: ChampionDataService) -> None:
    info = data_service.get_personal_adc_mastery_info()
    champion_ids = data_service.get_all_champion_ids()
    errors: list[str] = []

    for tier, tier_ids in info["tiers"].items():
        if tier not in {"S", "A", "B", "C", "D"}:
            errors.append(f"invalid tier: {tier}")
        for champion_id in tier_ids:
            if champion_id not in champion_ids:
                errors.append(f"non-canonical mastery id: {champion_id}")

    for entry in info["needs_review"]:
        for champion_id in entry.get("candidate_ids", []):
            if champion_id not in champion_ids:
                errors.append(f"non-canonical review id: {champion_id}")

    for field_name in ("excluded_from_recommendations", "never_top_pick"):
        for champion_id in info[field_name]:
            if champion_id not in champion_ids:
                errors.append(f"non-canonical {field_name} id: {champion_id}")

    assert errors == []


def test_ezreal_meta_b_does_not_beat_strong_personal_meta_pick(engine: ScoringEngine) -> None:
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Ezreal", "Ashe"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Ashe"
    assert result.top_pick.adc_context is not None
    assert result.top_pick.adc_context.personal_tier == "A"
    assert result.top_pick.adc_context.meta_tier == "S"
    assert result.alternatives[0].id == "Ezreal"
    assert result.alternatives[0].adc_context is not None
    assert result.alternatives[0].adc_context.eligibility == "fallback_meta_low"


def test_ezreal_is_never_first_option_even_when_only_fallbacks_exist(engine: ScoringEngine) -> None:
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Ezreal", "Smolder"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Smolder"
    assert result.alternatives[0].id == "Ezreal"


def test_vladimir_is_excluded_by_personal_policy(engine: ScoringEngine) -> None:
    result = engine.recommend(DraftState())
    recommended_ids = [result.top_pick.id, *[alt.id for alt in result.alternatives]]

    assert "Vladimir" not in recommended_ids


def test_personal_b_meta_s_is_fallback_only(engine: ScoringEngine) -> None:
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Smolder"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Smolder"
    assert result.top_pick.adc_context is not None
    assert result.top_pick.adc_context.personal_tier == "B"
    assert result.top_pick.adc_context.meta_tier == "S"
    assert result.top_pick.adc_context.eligibility == "fallback_personal_b_meta_s"


def test_meta_a_under_80_is_soft_fallback_even_with_personal_s(engine: ScoringEngine) -> None:
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Nilah"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Nilah"
    assert result.top_pick.adc_context is not None
    assert result.top_pick.adc_context.personal_tier == "S"
    assert result.top_pick.adc_context.meta_tier == "A"
    assert result.top_pick.adc_context.meta_climb_score is not None
    assert result.top_pick.adc_context.meta_climb_score < 80
    assert result.top_pick.adc_context.eligibility == "fallback_meta_soft"
    assert result.adc_priority_context is not None
    assert result.adc_priority_context.warning is not None


def test_meta_s_or_climb_80_core_beats_personal_s_meta_soft(engine: ScoringEngine) -> None:
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Nilah", "Brand"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Brand"
    assert result.top_pick.adc_context is not None
    assert result.top_pick.adc_context.eligibility == "core"
    assert result.alternatives[0].id == "Nilah"
    assert result.alternatives[0].adc_context is not None
    assert result.alternatives[0].adc_context.eligibility == "fallback_meta_soft"


def test_nilah_soraka_vs_caitlyn_nautilus_is_lane_veto(engine: ScoringEngine) -> None:
    draft = DraftState(
        allies=[DraftChampion(id="Soraka", role="Support")],
        enemies=[DraftChampion(id="Caitlyn", role="Bot"), DraftChampion(id="Nautilus", role="Support")],
        context=DraftContext(pick_position="late", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Nilah", "Ashe"]),
    )

    result = engine.recommend(draft)
    recommended = [result.top_pick, *result.alternatives]
    nilah_pick = next(pick for pick in recommended if pick.id == "Nilah")

    assert result.top_pick.id != "Nilah"
    assert nilah_pick.adc_context is not None
    assert nilah_pick.adc_context.eligibility == "fallback_lane_veto"
    assert "Caitlyn + Nautilus" in nilah_pick.adc_context.eligibility_reason


def test_hypercarry_without_frontline_vs_dive_is_draft_veto(engine: ScoringEngine) -> None:
    draft = DraftState(
        allies=[DraftChampion(id="Lulu", role="Support"), DraftChampion(id="Fiora", role="Top")],
        enemies=[
            DraftChampion(id="Camille", role="Top"),
            DraftChampion(id="Nocturne", role="Jungle"),
            DraftChampion(id="Katarina", role="Mid"),
        ],
        context=DraftContext(pick_position="late", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Jinx", "Ashe"]),
    )

    result = engine.recommend(draft)
    recommended = [result.top_pick, *result.alternatives]
    jinx_pick = next(pick for pick in recommended if pick.id == "Jinx")

    assert result.top_pick.id != "Jinx"
    assert jinx_pick.adc_context is not None
    assert jinx_pick.adc_context.eligibility == "fallback_draft_veto"


def test_adc_lane_veto_rules_use_canonical_ids(data_service: ChampionDataService) -> None:
    champion_ids = data_service.get_all_champion_ids()
    rules = data_service.get_matchup_rules()["adc_lane_veto_rules"]["exact_pairs"]
    errors: list[str] = []

    for rule in rules:
        for field_name in ("adc", "ally_support", "enemy_adc", "enemy_support"):
            champion_id = rule[field_name]
            if champion_id not in champion_ids:
                errors.append(f"{rule['id']} {field_name} uses non-canonical id {champion_id}")

    assert errors == []


def test_xayah_matchup_bonus_rules_apply_vs_malphite_tahmkench(
    engine: ScoringEngine, data_service: ChampionDataService
) -> None:
    profile = data_service.get_adc_profile("Xayah")
    assert profile is not None
    draft = DraftState(
        enemies=[DraftChampion(id="Malphite", role="Top"), DraftChampion(id="TahmKench", role="Support")],
        user_pool=UserPool(mode="pool_only", champions=["Xayah"]),
    )

    bonuses = engine._get_adc_matchup_bonus_results(profile, draft)

    assert {bonus.rule_id for bonus in bonuses} == {
        "xayah_vs_predecible_frontal_engage",
        "xayah_vs_melee_warden_frontline",
    }
    assert sum(bonus.score_delta for bonus in bonuses) == 22.0


def test_xayah_matchup_bonus_is_visible_when_recommended(engine: ScoringEngine) -> None:
    draft = DraftState(
        enemies=[DraftChampion(id="Malphite", role="Top"), DraftChampion(id="TahmKench", role="Support")],
        user_pool=UserPool(mode="pool_only", champions=["Xayah"]),
    )

    result = engine.recommend(draft)

    assert any("Malphite" in strength for strength in result.top_pick.strengths_in_this_draft)
    assert any("Tahm Kench" in strength for strength in result.top_pick.strengths_in_this_draft)


def test_adc_matchup_bonus_rules_use_canonical_ids(data_service: ChampionDataService) -> None:
    champion_ids = data_service.get_all_champion_ids()
    rules = data_service.get_matchup_rules()["adc_matchup_bonus_rules"]
    errors: list[str] = []

    for rule in rules:
        if rule["adc"] not in champion_ids:
            errors.append(f"{rule['id']} adc uses non-canonical id {rule['adc']}")
        for enemy_id in rule["enemy_any"]:
            if enemy_id not in champion_ids:
                errors.append(f"{rule['id']} enemy_any uses non-canonical id {enemy_id}")

    assert errors == []


def test_stale_adc_snapshot_returns_warning_and_personal_fallback(data_service: ChampionDataService) -> None:
    data_service._adc_meta_snapshot["scraped_at"] = "2026-01-01T00:00:00+00:00"
    engine = ScoringEngine(data_service)
    draft = DraftState(
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="pool_only", champions=["Ashe"]),
    )

    result = engine.recommend(draft)

    assert result.top_pick.id == "Ashe"
    assert result.top_pick.adc_context is not None
    assert result.top_pick.adc_context.eligibility == "fallback_meta_unavailable"
    assert result.adc_priority_context is not None
    assert result.adc_priority_context.status == "stale"
    assert result.adc_priority_context.warning is not None


def test_scraper_only_adc_champions_are_reported_not_recommended(data_service: ChampionDataService) -> None:
    engine = ScoringEngine(data_service)
    result = engine.recommend(DraftState())

    assert result.adc_priority_context is not None
    missing = result.adc_priority_context.meta_only_missing_profiles
    assert "Xerath" in missing
    assert "Xerath" not in [result.top_pick.id, *[alt.id for alt in result.alternatives]]
