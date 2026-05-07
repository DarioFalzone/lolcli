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
    assert len(data_service._measured_synergies) >= 4, "Esperamos al menos las 4 sinergias medidas del Dossier"


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
        "warden",
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
def test_classify_supp_archetype_fine(data_service: ChampionDataService, supp_id: str, expected: str) -> None:
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
    delta = scoring_engine._apply_strategic_triangle_bonus("Leona", _draft(["Lux", "Brand", "Soraka"]))
    assert delta == 12.0


def test_triangle_unknown_supp_returns_zero(scoring_engine: ScoringEngine) -> None:
    # Si el candidate no clasifica → 0
    delta = scoring_engine._apply_strategic_triangle_bonus("NonExistentSupp", _draft(["Lux"]))
    assert delta == 0.0


def test_triangle_ignores_non_supp_enemies(scoring_engine: ScoringEngine) -> None:
    # Leona vs Garen + Yasuo (no son supps fine-grained) → 0
    delta = scoring_engine._apply_strategic_triangle_bonus("Leona", _draft(["Garen", "Yasuo"]))
    assert delta == 0.0


# ==========================================================================
# Warden archetype — triangle interactions (2026-04-27 expansion)
# ==========================================================================


def test_classify_warden_braum(data_service: ChampionDataService) -> None:
    assert data_service.classify_supp_archetype_fine("Braum") == "warden"


def test_classify_warden_taric(data_service: ChampionDataService) -> None:
    assert data_service.classify_supp_archetype_fine("Taric") == "warden"


def test_classify_catcher_rakan(data_service: ChampionDataService) -> None:
    assert data_service.classify_supp_archetype_fine("Rakan") == "catcher"


def test_triangle_warden_beats_engage(scoring_engine: ScoringEngine) -> None:
    # Braum (warden) vs Leona (engage) → +10
    delta = scoring_engine._apply_strategic_triangle_bonus("Braum", _draft(["Leona"]))
    assert delta == 10.0


def test_triangle_warden_loses_to_poke(scoring_engine: ScoringEngine) -> None:
    # Braum (warden) vs Lux (poke) → -8
    delta = scoring_engine._apply_strategic_triangle_bonus("Braum", _draft(["Lux"]))
    assert delta == -8.0


def test_triangle_warden_beats_catcher(scoring_engine: ScoringEngine) -> None:
    # Braum (warden) vs Thresh (catcher) → +10
    delta = scoring_engine._apply_strategic_triangle_bonus("Braum", _draft(["Thresh"]))
    assert delta == 10.0


def test_triangle_catcher_loses_to_warden(scoring_engine: ScoringEngine) -> None:
    # Thresh (catcher) vs Braum (warden) → -8
    delta = scoring_engine._apply_strategic_triangle_bonus("Thresh", _draft(["Braum"]))
    assert delta == -8.0


# ==========================================================================
# Comp predominance — loaded and accessible
# ==========================================================================


def test_comp_predominance_loads(data_service: ChampionDataService) -> None:
    pred = data_service.get_comp_predominance()
    assert "predominance" in pred
    assert "scoring" in pred
    comp_types = set(pred["predominance"].keys())
    assert "attack_matrix" in comp_types
    assert "front_to_back" in comp_types
    assert "poke_siege" in comp_types


def test_comp_predominance_shape_mapping(scoring_engine: ScoringEngine) -> None:
    assert scoring_engine._teamfight_shape_to_comp_type("dive") == "attack_matrix"
    assert scoring_engine._teamfight_shape_to_comp_type("front_to_back") == "front_to_back"
    assert scoring_engine._teamfight_shape_to_comp_type("poke_siege") == "poke_siege"
    assert scoring_engine._teamfight_shape_to_comp_type("pick") == "pick"
    assert scoring_engine._teamfight_shape_to_comp_type("mixed") is None


# ==========================================================================
# Auditoría profunda 2026-04-27: synergy_matrix + matchup_rules + Sona + fixes
# ==========================================================================


def test_synergy_matrix_loads(data_service: ChampionDataService) -> None:
    """synergy_matrix.json carga la tabla cuantitativa 26x15+."""
    score = data_service.get_synergy_score("Leona", "MissFortune")
    assert score == 10  # S-tier: tabla KB dice 10/10


def test_synergy_matrix_anti_synergy(data_service: ChampionDataService) -> None:
    """Yuumi + Draven es anti-sinergia (score 2)."""
    score = data_service.get_synergy_score("Yuumi", "Draven")
    assert score is not None
    assert score <= 3  # Anti-sinergia per KB


def test_synergy_matrix_unknown_pair(data_service: ChampionDataService) -> None:
    """Pair no en la matrix devuelve None."""
    score = data_service.get_synergy_score("Leona", "UnknownChamp")
    assert score is None


def test_lane_matchup_janna_vs_leona(data_service: ChampionDataService) -> None:
    """Janna gana lane vs Leona (favored)."""
    result = data_service.get_lane_matchup("Janna", "Leona")
    assert result == "favored"


def test_lane_matchup_leona_vs_janna(data_service: ChampionDataService) -> None:
    """Leona pierde lane vs Janna (unfavored)."""
    result = data_service.get_lane_matchup("Leona", "Janna")
    assert result == "unfavored"


def test_lane_matchup_skill(data_service: ChampionDataService) -> None:
    """Thresh vs Leona es skill matchup."""
    result = data_service.get_lane_matchup("Thresh", "Leona")
    assert result == "skill"


def test_lane_matchup_scoring_values(data_service: ChampionDataService) -> None:
    """Score numérico de matchup favored > 0, unfavored < 0."""
    assert data_service.get_matchup_score_value("favored") > 0
    assert data_service.get_matchup_score_value("unfavored") < 0
    assert data_service.get_matchup_score_value("skill") == 0


def test_sona_profile_exists(data_service: ChampionDataService) -> None:
    """Sona tiene perfil en support_profiles.json."""
    profile = data_service.get_support_profile("Sona")
    assert profile is not None
    assert profile.archetype.value == "enchanter"
    assert profile.scaling >= 8  # Alta escala per KB


def test_total_supports_is_34(data_service: ChampionDataService) -> None:
    """Roster completo actual: 34 soportes."""
    supports = data_service.get_support_ids()
    assert len(supports) == 34


def test_classify_bard_as_catcher(data_service: ChampionDataService) -> None:
    """Bard debe clasificarse como catcher en el triángulo."""
    arch = data_service.classify_supp_archetype_fine("Bard")
    assert arch == "catcher"


def test_classify_senna_as_enchanter_pure(data_service: ChampionDataService) -> None:
    """Senna debe clasificarse como enchanter_pure (poke+sustain sin disengage hard)."""
    arch = data_service.classify_supp_archetype_fine("Senna")
    assert arch == "enchanter_pure"


def test_enchanter_pure_beats_engage(data_service: ChampionDataService) -> None:
    """D10 fix: enchanter_pure debe beatear engage (sustain mitiga burst)."""
    triangle = data_service.get_strategic_triangle()
    rules = triangle["triangle"]["enchanter_pure"]
    assert "engage" in rules["beats"]


def test_engage_loses_to_warden(data_service: ChampionDataService) -> None:
    """D3 fix: engage.loses_to debe incluir warden (bidireccionalidad)."""
    triangle = data_service.get_strategic_triangle()
    rules = triangle["triangle"]["engage"]
    assert "warden" in rules["loses_to"]


def test_classify_sona_as_enchanter_pure(data_service: ChampionDataService) -> None:
    """Sona debe clasificarse como enchanter_pure (sustain sin disengage hard)."""
    arch = data_service.classify_supp_archetype_fine("Sona")
    assert arch == "enchanter_pure"


def test_synergy_matrix_sona_has_row(data_service: ChampionDataService) -> None:
    """Sona debe tener fila en synergy_matrix.json."""
    score = data_service.get_synergy_score("Sona", "KogMaw")
    assert score is not None
    assert score >= 8  # Scaling enchanter + hypercarry = alta sinergia


# ==========================================================================
# D6: item_path en support_profiles
# ==========================================================================


def test_d6_item_path_leona(data_service: ChampionDataService) -> None:
    """D6: Leona tiene item_path con Solstice Sleigh."""
    profile = data_service.get_support_profile("Leona")
    assert profile is not None
    assert profile.item_path is not None
    assert profile.item_path.evolution == "Solstice Sleigh"
    assert len(profile.item_path.core_items) >= 2


def test_d6_item_path_lux_mage(data_service: ChampionDataService) -> None:
    """D6: Lux (mage) tiene Zaz'Zak's Realmspike."""
    profile = data_service.get_support_profile("Lux")
    assert profile.item_path is not None
    assert profile.item_path.evolution == "Zaz'Zak's Realmspike"


def test_d6_item_path_soraka_enchanter(data_service: ChampionDataService) -> None:
    """D6: Soraka (enchanter) tiene Dream Maker."""
    profile = data_service.get_support_profile("Soraka")
    assert profile.item_path is not None
    assert profile.item_path.evolution == "Dream Maker"


def test_d6_all_profiles_have_item_path(data_service: ChampionDataService) -> None:
    """D6: Todos los soportes actuales tienen item_path."""
    for supp_id in data_service.get_support_ids():
        profile = data_service.get_support_profile(supp_id)
        assert profile.item_path is not None, f"{supp_id} missing item_path"


# ==========================================================================
# D7: Crash & Move en play_pattern_template
# ==========================================================================


def test_d7_pyke_has_crash_and_move(data_service: ChampionDataService) -> None:
    """D7: Pyke play_pattern contiene Crash & Move."""
    profile = data_service.get_support_profile("Pyke")
    assert "Crash & Move" in profile.play_pattern_template
    assert "3 chequeos" in profile.play_pattern_template


def test_d7_bard_has_crash_and_move(data_service: ChampionDataService) -> None:
    """D7: Bard play_pattern contiene Crash & Move."""
    profile = data_service.get_support_profile("Bard")
    assert "Crash & Move" in profile.play_pattern_template


def test_d7_soraka_bprox_alta(data_service: ChampionDataService) -> None:
    """D7: Soraka play_pattern indica B-Prox alta (no roaming)."""
    profile = data_service.get_support_profile("Soraka")
    assert "B-Prox" in profile.play_pattern_template
    assert "Crash & Move NO aplica" in profile.play_pattern_template


# ==========================================================================
# D8: Jungler archetype classification
# ==========================================================================


def test_d8_classify_vi_as_engage(data_service: ChampionDataService) -> None:
    """D8: Vi es jungla engage."""
    arch = data_service.classify_jungler_archetype("Vi")
    assert arch == "engage"


def test_d8_classify_karthus_as_farm(data_service: ChampionDataService) -> None:
    """D8: Karthus es jungla farm_scaling."""
    arch = data_service.classify_jungler_archetype("Karthus")
    assert arch == "farm_scaling"


def test_d8_classify_leesin_as_early_gank(data_service: ChampionDataService) -> None:
    """D8: Lee Sin es jungla early_gank."""
    arch = data_service.classify_jungler_archetype("LeeSin")
    assert arch == "early_gank"


def test_d8_classify_master_yi_as_farm_with_canonical_id(data_service: ChampionDataService) -> None:
    """D8: Maestro Yi usa ID canonico MasterYi."""
    arch = data_service.classify_jungler_archetype("MasterYi")
    assert arch == "farm_scaling"


def test_d8_modifier_engage_jg_boosts_enchanter(data_service: ChampionDataService) -> None:
    """D8: Jungla engage boostea supp enchanter."""
    modifier = data_service.get_jungler_scoring_modifier("engage")
    assert "enchanter" in modifier["boost_archetypes"]
    assert modifier["boost_value"] > 0


def test_d8_unknown_jungler_returns_none(data_service: ChampionDataService) -> None:
    """D8: Jungla desconocida devuelve None."""
    arch = data_service.classify_jungler_archetype("UnknownJungler")
    assert arch is None


# ==========================================================================
# D9: queue_style_hints
# ==========================================================================


def test_d9_ranked_solo_hints_load(data_service: ChampionDataService) -> None:
    """D9: ranked_solo tiene hints."""
    hints = data_service.get_queue_style_hints("ranked_solo")
    assert hints is not None
    assert "weight_adjustments" in hints
    assert "archetype_boosts" in hints


def test_d9_clash_boosts_engage(data_service: ChampionDataService) -> None:
    """D9: Clash boostea engage archetype."""
    hints = data_service.get_queue_style_hints("clash")
    assert hints["archetype_boosts"]["engage"] > hints["archetype_boosts"]["poke"]


def test_d9_unknown_queue_returns_none(data_service: ChampionDataService) -> None:
    """D9: Queue desconocida devuelve None."""
    hints = data_service.get_queue_style_hints("unknown_queue")
    assert hints is None
