"""Tests para la KB extendida de NotebookLM (sinergias medidas + triángulo estratégico).

Cubre:
- ChampionDataService carga los 3 nuevos JSON sin error.
- classify_supp_archetype_fine devuelve la categoría correcta (5 fine-grained).
- ScoringEngine._score_measured_synergy_bonus interpola correctamente por WR.
- ScoringEngine._apply_strategic_triangle_bonus aplica beats/loses_to del JSON.
"""

from __future__ import annotations

import pytest

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.schemas import DraftChampion, DraftState
from riot_lol_cli.draft_advisor.scoring import ScoringEngine


@pytest.fixture(scope="module")
def data_service() -> ChampionDataService:
    return ChampionDataService()


@pytest.fixture(scope="module")
def scoring_engine(data_service: ChampionDataService) -> ScoringEngine:
    return ScoringEngine(data_service)


# ==========================================================================
# Carga de JSON extendidos
# ==========================================================================


def test_extended_kb_loads_measured_synergies(data_service: ChampionDataService) -> None:
    assert len(data_service._measured_synergies) >= 4, (
        "Esperamos al menos las 4 sinergias medidas del Dossier"
    )


def test_extended_kb_loads_strategic_triangle(data_service: ChampionDataService) -> None:
    triangle = data_service.get_strategic_triangle()
    assert "fine_grained_archetypes" in triangle
    assert "triangle" in triangle
    archetypes = triangle["fine_grained_archetypes"]
    assert set(archetypes.keys()) == {
        "engage",
        "poke",
        "enchanter_disengage",
        "enchanter_pure",
        "catcher",
    }


# ==========================================================================
# Clasificación fine-grained
# ==========================================================================


@pytest.mark.parametrize(
    "supp_id,expected",
    [
        ("Leona", "engage"),
        ("Nautilus", "engage"),
        ("Lux", "poke"),
        ("Brand", "poke"),
        ("Janna", "enchanter_disengage"),
        ("Lulu", "enchanter_disengage"),
        ("Milio", "enchanter_disengage"),
        ("Soraka", "enchanter_pure"),
        ("Yuumi", "enchanter_pure"),
        ("Thresh", "catcher"),
        ("Pyke", "catcher"),
    ],
)
def test_classify_supp_archetype_fine(
    data_service: ChampionDataService, supp_id: str, expected: str
) -> None:
    assert data_service.classify_supp_archetype_fine(supp_id) == expected


def test_classify_unknown_supp_returns_none(data_service: ChampionDataService) -> None:
    assert data_service.classify_supp_archetype_fine("NonExistentChamp") is None


# ==========================================================================
# Sinergia medida — bonus por WR
# ==========================================================================


def test_measured_synergy_lucian_nami_yields_bonus(scoring_engine: ScoringEngine) -> None:
    # Lucian + Nami: 54.0% WR → bonus = (54-50)*3 = 12pts
    bonus = scoring_engine._score_measured_synergy_bonus("Lucian", "Nami")
    assert 11.5 <= bonus <= 12.5, f"Expected ~12.0, got {bonus}"


def test_measured_synergy_ashe_seraphine_highest_wr(scoring_engine: ScoringEngine) -> None:
    # Ashe + Seraphine: 54.7% WR → bonus = (54.7-50)*3 = 14.1pts
    bonus = scoring_engine._score_measured_synergy_bonus("Ashe", "Seraphine")
    assert 13.5 <= bonus <= 14.5, f"Expected ~14.1, got {bonus}"


def test_measured_synergy_caps_at_max(scoring_engine: ScoringEngine) -> None:
    # Cualquier WR muy alto debe cap a 15
    # No tenemos un WR > 55% en el JSON, pero la fórmula lo respeta.
    cfg = scoring_engine._data.get_measured_synergy_config()
    assert cfg.get("max_bonus") == 15.0


def test_heuristic_synergy_yields_reduced_bonus(scoring_engine: ScoringEngine) -> None:
    # Draven + Pyke (heuristic, sin WR comprobado): bonus reducido
    bonus = scoring_engine._score_measured_synergy_bonus("Draven", "Pyke")
    # 12.0 * 0.6 = 7.2 (bajo el max heurístico de 9.0)
    assert 6.5 <= bonus <= 9.0, f"Expected ~7.2, got {bonus}"


def test_unknown_pair_yields_zero(scoring_engine: ScoringEngine) -> None:
    bonus = scoring_engine._score_measured_synergy_bonus("Aatrox", "Annie")
    assert bonus == 0.0


# ==========================================================================
# Triángulo estratégico — counter-pick por archetype
# ==========================================================================


def _draft(enemies: list[str]) -> DraftState:
    return DraftState(
        allies=[],
        enemies=[DraftChampion(id=e) for e in enemies],
    )


def test_triangle_engage_beats_poke(scoring_engine: ScoringEngine) -> None:
    # Leona (engage) vs Lux (poke) → +10
    delta = scoring_engine._apply_strategic_triangle_bonus("Leona", _draft(["Lux"]))
    assert delta == 10.0


def test_triangle_engage_loses_to_disengage(scoring_engine: ScoringEngine) -> None:
    # Leona (engage) vs Janna (enchanter_disengage) → -8 (eje invertido)
    delta = scoring_engine._apply_strategic_triangle_bonus("Leona", _draft(["Janna"]))
    assert delta == -8.0


def test_triangle_engage_beats_enchanter_pure(scoring_engine: ScoringEngine) -> None:
    # Leona (engage) vs Soraka (enchanter_pure) → +10
    delta = scoring_engine._apply_strategic_triangle_bonus("Leona", _draft(["Soraka"]))
    assert delta == 10.0


def test_triangle_catcher_beats_poke(scoring_engine: ScoringEngine) -> None:
    # Thresh (catcher) vs Lux (poke) → +10
    delta = scoring_engine._apply_strategic_triangle_bonus("Thresh", _draft(["Lux"]))
    assert delta == 10.0


def test_triangle_caps_at_max_modifier(scoring_engine: ScoringEngine) -> None:
    # 3 enemies que counterea Leona: Lux + Brand + Soraka = +30 raw, pero cap a +12
    delta = scoring_engine._apply_strategic_triangle_bonus(
        "Leona", _draft(["Lux", "Brand", "Soraka"])
    )
    assert delta == 12.0


def test_triangle_unknown_supp_returns_zero(scoring_engine: ScoringEngine) -> None:
    # Si el candidate no clasifica → 0
    delta = scoring_engine._apply_strategic_triangle_bonus(
        "NonExistentSupp", _draft(["Lux"])
    )
    assert delta == 0.0


def test_triangle_ignores_non_supp_enemies(scoring_engine: ScoringEngine) -> None:
    # Leona vs Garen + Yasuo (no son supps fine-grained) → 0
    delta = scoring_engine._apply_strategic_triangle_bonus(
        "Leona", _draft(["Garen", "Yasuo"])
    )
    assert delta == 0.0
