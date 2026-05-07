import pytest

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.schemas import DraftChampion, DraftContext, DraftState, UserPool
from riot_lol_cli.draft_advisor.scoring import ScoringEngine


@pytest.fixture(scope="module")
def engine():
    svc = ChampionDataService()
    return ScoringEngine(svc)


def test_poppy_anti_dash_counter(engine):
    # Poppy should be the top pick against a heavy dash comp (Rakan, Leona, Pyke, Lee Sin)
    # Enemy team has Rakan (support) and LeeSin (jungle)
    draft = DraftState(
        allies=[
            DraftChampion(id="Jinx"),
            DraftChampion(id="Maokai"),  # Jungle
            DraftChampion(id="Syndra"),  # Mid
        ],
        enemies=[
            DraftChampion(id="Rakan"),  # Support
            DraftChampion(id="LeeSin"),  # Jungle
            DraftChampion(id="Lucian"),  # ADC
        ],
        target_role="support",
        context=DraftContext(pick_position="late", queue_type="ranked_solo"),
        user_pool=UserPool(mode="unrestricted"),
    )

    res = engine.recommend(draft)

    # Poppy should be in the top 3 recommendations, likely #1 due to double hard counter
    top_3_ids = [res.top_pick.id] + [a.id for a in res.alternatives[:2]]
    assert "Poppy" in top_3_ids, f"Poppy no fue recomendada contra Rakan+LeeSin. Top 3: {top_3_ids}"

    # Check that Poppy's enemy matchup score is extremely high
    poppy_pick = next((p for p in [res.top_pick] + res.alternatives if p.id == "Poppy"), None)
    if poppy_pick:
        matchup_score = poppy_pick.score_breakdown.raw.enemy_matchup
        assert matchup_score >= 80, f"Matchup score for Poppy is too low: {matchup_score}"


def test_anti_enchanter_counter(engine):
    # Squishy enchanters should surface a hard all-in counter.
    draft = DraftState(
        allies=[
            DraftChampion(id="Tristana"),  # High synergy
        ],
        enemies=[DraftChampion(id="Sona"), DraftChampion(id="Ashe")],
        target_role="support",
        context=DraftContext(pick_position="late", queue_type="ranked_solo"),
        user_pool=UserPool(mode="unrestricted"),
    )

    res = engine.recommend(draft)

    top_3_ids = [res.top_pick.id] + [a.id for a in res.alternatives[:2]]
    assert any(counter in top_3_ids for counter in {"Camille", "Pantheon"}), (
        f"No se recomendo un counter hard contra Sona. Top 3: {top_3_ids}"
    )


def test_antimeta_not_blind_picked(engine):
    # Poppy and Camille should NOT be recommended as blind picks
    draft = DraftState(
        allies=[],
        enemies=[],
        target_role="support",
        context=DraftContext(pick_position="blind", queue_type="ranked_solo"),
        user_pool=UserPool(mode="unrestricted"),
    )

    res = engine.recommend(draft)

    top_3_ids = [res.top_pick.id] + [a.id for a in res.alternatives[:2]]
    assert "Poppy" not in top_3_ids, "Poppy recomendada a ciegas"
    assert "Camille" not in top_3_ids, "Camille recomendada a ciegas"
    assert "Pantheon" not in top_3_ids, "Pantheon recomendado a ciegas"
    assert "Sylas" not in top_3_ids, "Sylas recomendado a ciegas"
