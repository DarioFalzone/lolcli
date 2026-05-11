"""
Scoring Engine — Multi-factor ADC recommendation scorer.

Scoring formula (unambiguous):
    base_factors = [ally_synergy, enemy_matchup, blind_pick_safety,
                    comp_gap_fill, solo_queue_reliability, scaling_fit]

    weighted_sum = sum(raw_factor_i * weight_i)
        where sum(weight_i) = 1.0 (always normalized after context adjustments)

    comfort_bonus = 0                                      if mode == unrestricted
                  = (comfort_score / 10) * max_pts * w     if mode in {pool_preferred, pool_only}
        where max_pts = comfort_bonus_max_points (20)
              w       = comfort_bonus_weight (0.15)

    total_score = clamp(0, 100, weighted_sum + comfort_bonus)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from .analyzer import CompositionAnalyzer
from .champion_data import ChampionDataService
from .schemas import (
    AdcPickContext,
    AdcPriorityContext,
    AdcProfile,
    AdvisorMode,
    AlternativePick,
    DamageType,
    DraftAnalysis,
    DraftChampion,
    DraftState,
    EnemyCompProfile,
    JunglePickContext,
    PickPosition,
    PoolMode,
    RawScores,
    RecommendationOutput,
    RecommendedPick,
    ScoreBreakdown,
    SupportArchetype,
    SupportProfile,
    TeamfightShape,
    ThreatLevel,
    WeightedScores,
)
from .scoring_rules import score_comp_gap_fill, score_scaling_fit

_PERSONAL_TIER_SCORES = {
    "S": 100.0,
    "A": 82.0,
    "B": 55.0,
    "C": 25.0,
    "D": 0.0,
}

_STRONG_PERSONAL_TIERS = {"S", "A"}
_STRONG_META_TIERS = {"S"}
_STRONG_META_CLIMB_SCORE = 80.0

_JUNGLE_TIER_SCORES = {
    "S": 92.0,
    "A": 80.0,
    "B": 62.0,
    "C": 40.0,
}
_JUNGLE_TOP_TIERS = {"S", "A"}


@dataclass(frozen=True)
class _AdcPriority:
    personal_tier: str | None
    personal_score: float
    meta_tier: str | None
    meta_score: float
    meta_climb_score: float | None
    eligibility: str
    eligibility_reason: str
    is_core: bool
    can_be_top_pick: bool = True


@dataclass(frozen=True)
class _AdcMetaContext:
    meta_tier: str | None
    meta_score: float
    meta_climb_score: float | None
    is_current: bool
    is_strong: bool


@dataclass(frozen=True)
class _AdcLaneRuleResult:
    rule_id: str
    score_delta: float
    top_pick_block: bool
    reason: str


@dataclass(frozen=True)
class _AdcMatchupBonusResult:
    rule_id: str
    score_delta: float
    reason: str


@dataclass(frozen=True)
class _JunglePriority:
    eligibility: str
    eligibility_reason: str
    is_core: bool
    can_be_top_pick: bool


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


_YASUO_AIRBORNE_ENABLERS = {
    "Alistar",
    "Diana",
    "Gragas",
    "JarvanIV",
    "Malphite",
    "Nautilus",
    "Orianna",
    "Rakan",
    "Rell",
    "Wukong",
    "Zac",
}

_YASUO_PROJECTILE_TARGETS = {
    "Ashe",
    "Brand",
    "Caitlyn",
    "Ezreal",
    "Jhin",
    "Jinx",
    "Lux",
    "Seraphine",
    "Sivir",
    "Varus",
    "Velkoz",
    "Xerath",
    "Ziggs",
}


class ScoringEngine:
    """Multi-factor scorer for ADC draft recommendations."""

    def __init__(self, data_service: ChampionDataService):
        self._data = data_service
        self._analyzer = CompositionAnalyzer(data_service)
        self._weights_config = data_service.get_scoring_weights()

    def recommend(self, draft_state: DraftState) -> RecommendationOutput:
        """
        Given a draft state, return the full recommendation output.

        Routes to _recommend_adc() or _recommend_support() based on draft_state.target_role.
        """
        if draft_state.target_role == AdvisorMode.SUPPORT:
            return self._recommend_support(draft_state)
        if draft_state.target_role == AdvisorMode.JUNGLE:
            return self._recommend_jungle(draft_state)
        return self._recommend_adc(draft_state)

    def _recommend_adc(self, draft_state: DraftState) -> RecommendationOutput:
        """
        ADC mode (original behavior).

        1. Analyze compositions
        2. Determinar candidatos ADC segun pool mode
        3. Puntuar cada candidato
        4. Sort, pick top, generate explanations
        5. Return structured output
        """
        # 1. Analyze compositions
        analysis = self._analyzer.analyze(draft_state)

        # 2. Determinar pool de candidatos.
        candidates = self._get_candidates(draft_state)
        if not candidates:
            raise ValueError("No hay candidatos ADC disponibles para puntuar.")

        # 3. Compute weights (with context adjustments)
        weights = self._compute_weights(draft_state)

        # 4. Puntuar cada candidato y aplicar gates ADC de maestria/meta.
        scored: list[tuple[str, float, ScoreBreakdown, _AdcPriority]] = []
        fallback_scored: list[tuple[str, float, ScoreBreakdown, _AdcPriority]] = []
        for adc_id in candidates:
            profile = self._data.get_adc_profile(adc_id)
            if profile is None:
                continue
            raw = self._compute_raw_scores(profile, draft_state, analysis)
            breakdown = self._build_breakdown(raw, weights, draft_state, adc_id)
            priority = self._get_adc_priority(profile, draft_state, analysis)
            final_score = self._apply_adc_priority_score(breakdown, priority)
            row = (adc_id, final_score, breakdown, priority)
            if priority.is_core:
                scored.append(row)
            elif priority.eligibility.startswith("fallback"):
                fallback_scored.append(row)

        # 5. Ordenar por score total descendente. Los candidatos core siempre
        # superan a alternativas; las alternativas se usan si no hay suficientes
        # candidatos fuertes por maestria/meta.
        scored.sort(key=lambda x: x[1], reverse=True)
        fallback_scored.sort(key=lambda x: x[1], reverse=True)

        visible_scored = scored + fallback_scored
        top_candidates = [row for row in visible_scored if row[3].can_be_top_pick]
        if not top_candidates and visible_scored:
            # Si todos los candidatos quedaron vetados por contexto, mostramos
            # la mejor alternativa para que la UI explique por que es riesgosa.
            top_candidates = visible_scored
        if not top_candidates:
            raise ValueError("Ningun ADC paso los gates de maestria personal y meta.")

        # 6. Build output
        top = top_candidates[0]
        alternatives = [row for row in visible_scored if row[0] != top[0]][:3]  # up to 3

        top_profile = self._data.get_adc_profile(top[0])
        top_pick = self._build_top_pick(top[0], top[2], top_profile, analysis, draft_state, top[3])

        alt_picks = []
        for alt_id, _, alt_breakdown, alt_priority in alternatives:
            alt_profile = self._data.get_adc_profile(alt_id)
            alt_pick = self._build_alternative(
                alt_id,
                alt_breakdown,
                alt_profile,
                top[0],
                top_profile,
                analysis,
                alt_priority,
            )
            alt_picks.append(alt_pick)

        # 7. Hash the draft state for caching
        state_hash = hashlib.md5(
            json.dumps(draft_state.model_dump(), sort_keys=True, default=str).encode()
        ).hexdigest()[:12]

        return RecommendationOutput(
            timestamp=datetime.now(timezone.utc).isoformat(),
            draft_state_hash=state_hash,
            mode=draft_state.user_pool.mode,
            top_pick=top_pick,
            alternatives=alt_picks,
            draft_analysis=analysis,
            adc_priority_context=self._build_adc_priority_context(len(scored), len(fallback_scored)),
        )

    # ========================================================================
    # Candidate selection
    # ========================================================================

    def _get_candidates(self, draft_state: DraftState) -> list[str]:
        """Get the list of ADC IDs to score based on pool mode."""
        all_adcs = self._data.get_adc_ids()
        pool = draft_state.user_pool

        # Remove already picked champions (allies + enemies + bans)
        picked = set()
        for ally in draft_state.allies:
            picked.add(ally.id)
        for enemy in draft_state.enemies:
            picked.add(enemy.id)
        for ban in draft_state.bans:
            picked.add(ban)

        available_adcs = all_adcs - picked

        if pool.mode == PoolMode.POOL_ONLY:
            return [c for c in pool.champions if c in available_adcs and c in all_adcs]
        elif pool.mode == PoolMode.POOL_PREFERRED:
            return list(available_adcs)
        else:  # UNRESTRICTED
            return list(available_adcs)

    def _get_adc_priority(
        self,
        profile: AdcProfile,
        draft_state: DraftState,
        analysis: DraftAnalysis,
    ) -> _AdcPriority:
        """Clasificar un ADC bajo la politica de maestria personal + meta vigente."""
        adc_id = profile.id
        personal_tier = self._data.get_personal_adc_tier(adc_id)
        personal_score = _PERSONAL_TIER_SCORES.get(personal_tier or "", 0.0)
        can_be_top_pick = not self._data.is_adc_never_top_pick(adc_id)

        blocked_priority = self._get_adc_user_block_priority(adc_id, personal_tier)
        if blocked_priority:
            return blocked_priority

        meta_context = self._build_adc_meta_context(adc_id)
        veto_priority = self._get_adc_veto_priority(
            profile,
            draft_state,
            analysis,
            personal_tier,
            personal_score,
            meta_context,
        )
        if veto_priority:
            return veto_priority

        core_priority = self._get_adc_core_priority(
            personal_tier,
            personal_score,
            can_be_top_pick,
            meta_context,
        )
        if core_priority:
            return core_priority

        return self._get_adc_fallback_priority(
            personal_tier,
            personal_score,
            can_be_top_pick,
            meta_context,
        )

    def _get_adc_user_block_priority(self, adc_id: str, personal_tier: str | None) -> _AdcPriority | None:
        if not self._data.is_adc_excluded_by_user(adc_id):
            return None
        return _AdcPriority(
            personal_tier=personal_tier,
            personal_score=0.0,
            meta_tier=None,
            meta_score=0.0,
            meta_climb_score=None,
            eligibility="blocked_user_excluded",
            eligibility_reason="Bloqueado por preferencia personal del usuario.",
            is_core=False,
            can_be_top_pick=False,
        )

    def _build_adc_meta_context(self, adc_id: str) -> _AdcMetaContext:
        meta_info = self._data.get_adc_meta_snapshot_info()
        meta_is_current = bool(meta_info) and not meta_info.get("is_stale", True)
        meta = self._data.get_adc_meta(adc_id) if meta_is_current else None
        stats = meta.get("stats", {}) if meta else {}
        meta_tier = stats.get("tier") if meta else None
        meta_climb_score = _float_or_none(stats.get("climb_score")) if meta else None
        meta_score = meta_climb_score if meta_climb_score is not None else 50.0
        meta_is_strong = meta_tier in _STRONG_META_TIERS or (
            meta_climb_score is not None and meta_climb_score >= _STRONG_META_CLIMB_SCORE
        )
        return _AdcMetaContext(
            meta_tier=meta_tier,
            meta_score=meta_score,
            meta_climb_score=meta_climb_score,
            is_current=meta_is_current,
            is_strong=meta_is_strong,
        )

    def _get_adc_veto_priority(
        self,
        profile: AdcProfile,
        draft_state: DraftState,
        analysis: DraftAnalysis,
        personal_tier: str | None,
        personal_score: float,
        meta_context: _AdcMetaContext,
    ) -> _AdcPriority | None:
        lane_rule = self._get_adc_lane_rule_result(profile, draft_state)

        if lane_rule and lane_rule.top_pick_block and personal_tier in _STRONG_PERSONAL_TIERS:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=meta_context.meta_tier,
                meta_score=meta_context.meta_score,
                meta_climb_score=meta_context.meta_climb_score,
                eligibility="fallback_lane_veto",
                eligibility_reason=f"Alternativa vetada por draft: {lane_rule.reason}",
                is_core=False,
                can_be_top_pick=False,
            )

        tactical_veto_reason = self._get_adc_tactical_veto_reason(profile, analysis)
        if tactical_veto_reason and personal_tier in _STRONG_PERSONAL_TIERS:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=meta_context.meta_tier,
                meta_score=meta_context.meta_score,
                meta_climb_score=meta_context.meta_climb_score,
                eligibility="fallback_draft_veto",
                eligibility_reason=f"Alternativa vetada por draft: {tactical_veto_reason}",
                is_core=False,
                can_be_top_pick=False,
            )
        return None

    @staticmethod
    def _get_adc_core_priority(
        personal_tier: str | None,
        personal_score: float,
        can_be_top_pick: bool,
        meta_context: _AdcMetaContext,
    ) -> _AdcPriority | None:
        if personal_tier in _STRONG_PERSONAL_TIERS and meta_context.is_strong:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=meta_context.meta_tier,
                meta_score=meta_context.meta_score,
                meta_climb_score=meta_context.meta_climb_score,
                eligibility="core",
                eligibility_reason="Maestría personal S/A y meta ADC fuerte vigente (tier S o climb 80+).",
                is_core=True,
                can_be_top_pick=can_be_top_pick,
            )
        return None

    @staticmethod
    def _get_adc_fallback_priority(
        personal_tier: str | None,
        personal_score: float,
        can_be_top_pick: bool,
        meta_context: _AdcMetaContext,
    ) -> _AdcPriority:
        if personal_tier == "B" and meta_context.meta_tier == "S":
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=meta_context.meta_tier,
                meta_score=meta_context.meta_score,
                meta_climb_score=meta_context.meta_climb_score,
                eligibility="fallback_personal_b_meta_s",
                eligibility_reason="Alternativa: tier personal B, pero el scraping lo marca S.",
                is_core=False,
                can_be_top_pick=can_be_top_pick,
            )

        if personal_tier in _STRONG_PERSONAL_TIERS and not meta_context.is_current:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=None,
                meta_score=50.0,
                meta_climb_score=None,
                eligibility="fallback_meta_unavailable",
                eligibility_reason="Alternativa: maestría S/A, pero el snapshot ADC no está vigente.",
                is_core=False,
                can_be_top_pick=can_be_top_pick,
            )

        if personal_tier in _STRONG_PERSONAL_TIERS and meta_context.meta_tier is None:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=None,
                meta_score=50.0,
                meta_climb_score=None,
                eligibility="fallback_meta_missing",
                eligibility_reason="Alternativa: maestría S/A, pero el snapshot ADC no trae este campeón.",
                is_core=False,
                can_be_top_pick=can_be_top_pick,
            )

        if personal_tier in _STRONG_PERSONAL_TIERS and meta_context.meta_tier:
            return _AdcPriority(
                personal_tier=personal_tier,
                personal_score=personal_score,
                meta_tier=meta_context.meta_tier,
                meta_score=meta_context.meta_score,
                meta_climb_score=meta_context.meta_climb_score,
                eligibility="fallback_meta_soft" if meta_context.meta_tier == "A" else "fallback_meta_low",
                eligibility_reason=(
                    f"Alternativa: meta ADC {meta_context.meta_tier}; "
                    "la recomendación principal requiere tier S o climb 80+."
                ),
                is_core=False,
                can_be_top_pick=can_be_top_pick,
            )

        return _AdcPriority(
            personal_tier=personal_tier,
            personal_score=personal_score,
            meta_tier=meta_context.meta_tier,
            meta_score=meta_context.meta_score,
            meta_climb_score=meta_context.meta_climb_score,
            eligibility="blocked_personal_low",
            eligibility_reason="Bloqueado: requiere maestria personal S/A; B solo entra si meta es S.",
            is_core=False,
            can_be_top_pick=False,
        )

    def _apply_adc_priority_score(self, breakdown: ScoreBreakdown, priority: _AdcPriority) -> float:
        """Replace ADC final score with 30% mastery, 30% meta, 40% draft fit."""
        draft_fit = max(0.0, min(100.0, breakdown.pre_clamp_total))
        final_score = (priority.personal_score * 0.30) + (priority.meta_score * 0.30) + (draft_fit * 0.40)
        final_score = max(0.0, min(100.0, final_score))

        breakdown.draft_fit_score = round(draft_fit, 2)
        breakdown.personal_mastery_score = round(priority.personal_score, 2)
        breakdown.meta_strength_score = round(priority.meta_score, 2)
        breakdown.adc_priority_score = round(final_score, 2)
        breakdown.pre_clamp_total = round(final_score, 2)
        return final_score

    def _build_adc_pick_context(self, priority: _AdcPriority) -> AdcPickContext:
        meta_info = self._data.get_adc_meta_snapshot_info()
        return AdcPickContext(
            personal_tier=priority.personal_tier,
            meta_tier=priority.meta_tier,
            meta_climb_score=priority.meta_climb_score,
            meta_patch=meta_info.get("patch"),
            meta_scraped_at=meta_info.get("scraped_at"),
            eligibility=priority.eligibility,
            eligibility_reason=priority.eligibility_reason,
        )

    def _build_adc_priority_context(self, eligible_count: int, fallback_count: int) -> AdcPriorityContext:
        meta_info = self._data.get_adc_meta_snapshot_info()
        status = meta_info.get("status", "missing")
        warning = None
        if status == "missing":
            warning = "No hay snapshot ADC del Meta Scraper; se usó una alternativa por maestría personal."
        elif status == "stale":
            warning = "El snapshot ADC tiene más de 72 horas; se usó una alternativa por maestría personal."
        elif eligible_count == 0 and fallback_count > 0:
            warning = "No hay ADC core con meta S o climb 80+; se mostró la mejor alternativa con advertencias."

        return AdcPriorityContext(
            status=status,
            warning=warning,
            meta_patch=meta_info.get("patch"),
            meta_scraped_at=meta_info.get("scraped_at"),
            meta_sources=meta_info.get("sources", []),
            meta_champion_count=meta_info.get("champion_count", 0),
            meta_age_hours=meta_info.get("age_hours"),
            stale_after_hours=meta_info.get("stale_after_hours", 72),
            eligible_count=eligible_count,
            fallback_count=fallback_count,
            meta_only_missing_profiles=self._data.get_adc_meta_without_local_profile(),
        )

    # ========================================================================
    # Weight computation (with context adjustments)
    # ========================================================================

    def _compute_weights(self, draft_state: DraftState) -> dict[str, float]:
        """Compute final weights after applying context adjustments and normalizing."""
        base = dict(self._weights_config.base_weights)
        position = draft_state.context.pick_position.value

        # Apply context deltas
        adjustments = self._weights_config.context_adjustments.get(position, {})
        for factor, delta in adjustments.items():
            if factor in base:
                base[factor] += delta

        # D9: Apply queue_style_hints weight adjustments
        queue_type = draft_state.context.queue_type.value if hasattr(draft_state.context, "queue_type") else None
        if queue_type:
            queue_hints = self._data.get_queue_style_hints(queue_type)
            if queue_hints:
                for factor, delta in queue_hints.get("weight_adjustments", {}).items():
                    if factor in base:
                        base[factor] += delta

        # Clamp to >= 0
        for factor in base:
            base[factor] = max(0.0, base[factor])

        # Re-normalize to sum = 1.0
        total = sum(base.values())
        if total > 0:
            for factor in base:
                base[factor] /= total

        return base

    # ========================================================================
    # Raw score computation (each factor 0-100)
    # ========================================================================

    def _compute_raw_scores(
        self,
        profile: AdcProfile,
        draft_state: DraftState,
        analysis: DraftAnalysis,
    ) -> RawScores:
        """Compute raw 0-100 scores for each factor."""
        return RawScores(
            ally_synergy=self._score_ally_synergy(profile, draft_state, analysis),
            enemy_matchup=self._score_enemy_matchup(profile, draft_state, analysis),
            blind_pick_safety=self._score_blind_pick_safety(profile, draft_state),
            comp_gap_fill=self._score_comp_gap_fill(profile, analysis),
            solo_queue_reliability=self._score_solo_queue_reliability(profile),
            scaling_fit=self._score_scaling_fit(profile, analysis),
        )

    def _score_ally_synergy(self, profile: AdcProfile, draft: DraftState, analysis: DraftAnalysis) -> float:
        """
        Que tan bien sinergiza este ADC con el equipo aliado.
        Considers: support type synergy, frontline dependency, peel dependency.
        """
        if not draft.allies:
            return 50.0  # Neutral cuando no hay aliados conocidos

        score = 50.0  # Start neutral
        allied = analysis.allied_comp_profile

        # Support synergy (check if any ally is a support)
        for ally in draft.allies:
            champ = self._data.get_champion(ally.id)
            pp = self._data.get_priority_profile(ally.id)
            if pp is None or champ is None:
                continue

            if pp.category.value == "engage_support":
                score += (profile.synergy_engage_support - 5) * 4
            elif pp.category.value == "enchanter_support":
                score += (profile.synergy_enchanter_support - 5) * 4
            elif pp.category.value == "mage_support":
                score += (profile.synergy_mage_support - 5) * 4
            elif pp.category.value == "catcher_support":
                score += (profile.synergy_engage_support - 5) * 3

        # Frontline dependency satisfaction
        if allied.has_frontline:
            score += (profile.synergy_frontline_comp - 5) * 3
        else:
            # Penalize ADCs that NEED frontline
            score -= (profile.dependence_on_frontline - 5) * 2

        # Peel dependency satisfaction
        if allied.has_peel:
            score += (profile.synergy_peel_comp - 5) * 3
        else:
            score -= (profile.dependence_on_peel - 5) * 2

        # Best-with bonus
        for ally in draft.allies:
            if ally.id in profile.best_with:
                score += 8

        if profile.id == "Yasuo" and not self._has_yasuo_airborne_setup(draft):
            score -= 25

        return max(0.0, min(100.0, score))

    def _score_enemy_matchup(self, profile: AdcProfile, draft: DraftState, analysis: DraftAnalysis) -> float:
        """
        Que tan bien rinde este ADC contra el equipo enemigo.
        Considera anti-dive, anti-poke, anti-tank y penalizaciones worst-into.
        """
        if not draft.enemies:
            return 50.0  # Neutral cuando no hay enemigos conocidos

        score = 50.0
        enemy = analysis.enemy_comp_profile
        allied = analysis.allied_comp_profile

        # Anti-dive capability vs dive comps
        if enemy.has_dive:
            score += (profile.anti_dive - 5) * 4

        # Anti-burst capability vs burst comps
        if enemy.has_burst:
            score += (profile.self_peel - 5) * 3
            score += (profile.mobility - 5) * 2

        # Anti-tank capability vs tank comps
        if enemy.has_tanks:
            score += (profile.anti_tank - 5) * 4
            if profile.anti_tank >= 9 and profile.objective_dps >= 8:
                score += (profile.anti_tank - 8) * 6
                score += max(0, profile.objective_dps - 7) * 4

        # Anti-poke
        if enemy.has_poke:
            score += (profile.anti_poke - 5) * 3

        if profile.id == "Yasuo":
            if not self._has_yasuo_projectile_target(draft, enemy):
                score -= 14
            if enemy.has_dive or enemy.has_burst:
                score -= 8

        # Worst-into penalties
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.worst_into:
                score -= 10

        lane_rule = self._get_adc_lane_rule_result(profile, draft)
        if lane_rule:
            score += lane_rule.score_delta

        for bonus_rule in self._get_adc_matchup_bonus_results(profile, draft):
            score += bonus_rule.score_delta

        # Threat level adjustment
        threat = enemy.threat_level_to_adc
        if threat == ThreatLevel.CRITICAL:
            # Reward self-sufficient ADCs
            score += (profile.self_peel - 5) * 3
            score += (profile.mobility - 5) * 2
        elif threat == ThreatLevel.MINIMAL:
            # Reward greedy ADCs
            score += (profile.scaling - 5) * 2

        # Protective comps unlock riskier hypercarries against hostile drafts.
        if enemy.has_dive or enemy.has_burst:
            if not allied.has_frontline and profile.dependence_on_frontline >= 7:
                score -= 24
            if not allied.has_frontline and profile.mobility <= 3 and profile.self_peel <= 4:
                score -= 12
            if allied.has_frontline:
                score += max(0, profile.synergy_frontline_comp - 5) * 2
            if allied.has_peel:
                score += max(0, profile.synergy_peel_comp - 5) * 2.5

        return max(0.0, min(100.0, score))

    def _get_adc_lane_rule_result(self, profile: AdcProfile, draft: DraftState) -> _AdcLaneRuleResult | None:
        """Evaluar reglas KB de linea que degradan ADCs situacionales."""
        rule_set = self._data.get_matchup_rules().get("adc_lane_veto_rules", {})
        if not rule_set:
            return None

        ally_ids = {ally.id for ally in draft.allies}
        enemy_ids = {enemy.id for enemy in draft.enemies}

        for rule in rule_set.get("exact_pairs", []):
            if (
                rule.get("adc") == profile.id
                and rule.get("ally_support") in ally_ids
                and rule.get("enemy_adc") in enemy_ids
                and rule.get("enemy_support") in enemy_ids
            ):
                return _AdcLaneRuleResult(
                    rule_id=rule.get("id", "exact_lane_rule"),
                    score_delta=float(rule.get("score_delta", 0.0)),
                    top_pick_block=bool(rule.get("top_pick_block", False)),
                    reason=rule.get("reason", "Regla de linea desfavorable desde KB."),
                )

        for rule in rule_set.get("general_rules", []):
            if profile.effective_range > int(rule.get("adc_effective_range_max", 10)):
                continue

            ally_support = self._find_support_profile(
                draft.allies,
                set(rule.get("ally_support_archetypes", [])),
                lane_kill_pressure_max=rule.get("ally_support_lane_kill_pressure_max"),
            )
            enemy_support = self._find_support_profile(
                draft.enemies,
                set(rule.get("enemy_support_archetypes", [])),
                lane_kill_pressure_min=rule.get("enemy_support_lane_kill_pressure_min"),
            )
            enemy_adc = self._find_enemy_adc_profile(
                draft,
                effective_range_min=rule.get("enemy_adc_effective_range_min"),
                lane_priority_min=rule.get("enemy_adc_lane_priority_min"),
            )
            if ally_support and enemy_support and enemy_adc:
                return _AdcLaneRuleResult(
                    rule_id=rule.get("id", "general_lane_rule"),
                    score_delta=float(rule.get("score_delta", 0.0)),
                    top_pick_block=bool(rule.get("top_pick_block", False)),
                    reason=rule.get("reason", "Regla general de linea desfavorable desde KB."),
                )

        return None

    def _get_adc_matchup_bonus_results(self, profile: AdcProfile, draft: DraftState) -> list[_AdcMatchupBonusResult]:
        """Evaluar bonos KB de matchup que mejoran el fit tactico de un ADC."""
        rules = self._data.get_matchup_rules().get("adc_matchup_bonus_rules", [])
        if not rules or not draft.enemies:
            return []

        enemy_ids = {enemy.id for enemy in draft.enemies}
        results: list[_AdcMatchupBonusResult] = []
        for rule in rules:
            if rule.get("adc") != profile.id:
                continue
            if enemy_ids.isdisjoint(set(rule.get("enemy_any", []))):
                continue
            results.append(
                _AdcMatchupBonusResult(
                    rule_id=rule.get("id", "adc_matchup_bonus_rule"),
                    score_delta=float(rule.get("score_delta", 0.0)),
                    reason=rule.get("reason", "Bonus de matchup desde KB."),
                )
            )
        return results

    @staticmethod
    def _get_adc_tactical_veto_reason(profile: AdcProfile, analysis: DraftAnalysis) -> str | None:
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile
        if (
            (enemy.has_dive or enemy.has_burst)
            and not allied.has_frontline
            and profile.dependence_on_frontline >= 7
            and profile.mobility <= 3
            and profile.self_peel <= 4
        ):
            return (
                "necesita frontline contra dive/burst enemigo; sin frente, "
                "su DPS de late no se puede aplicar con seguridad."
            )
        return None

    def _find_support_profile(
        self,
        picks: list[DraftChampion],
        archetypes: set[str],
        lane_kill_pressure_min: object | None = None,
        lane_kill_pressure_max: object | None = None,
    ) -> SupportProfile | None:
        for pick in picks:
            support = self._data.get_support_profile(pick.id)
            if support is None:
                continue
            if archetypes and support.archetype.value not in archetypes:
                continue
            if lane_kill_pressure_min is not None and support.lane_kill_pressure < int(lane_kill_pressure_min):
                continue
            if lane_kill_pressure_max is not None and support.lane_kill_pressure > int(lane_kill_pressure_max):
                continue
            return support
        return None

    def _find_enemy_adc_profile(
        self,
        draft: DraftState,
        effective_range_min: object | None = None,
        lane_priority_min: object | None = None,
    ) -> AdcProfile | None:
        for enemy in draft.enemies:
            enemy_adc = self._data.get_adc_profile(enemy.id)
            if enemy_adc is None:
                continue
            if effective_range_min is not None and enemy_adc.effective_range < int(effective_range_min):
                continue
            if lane_priority_min is not None and enemy_adc.lane_priority < int(lane_priority_min):
                continue
            return enemy_adc
        return None

    def _score_blind_pick_safety(self, profile: AdcProfile, draft: DraftState) -> float:
        """
        How safe is this ADC as a blind pick?
        Directly maps from the profile rating, adjusted by information level.
        """
        base = profile.blind_pick_safety * 10  # 1-10 -> 10-100

        # If we have full info, blind pick safety matters less
        # (this is handled by weights, but we also slightly adjust)
        if draft.context.pick_position == PickPosition.LATE:
            # You know what you're facing, safety matters less
            return base * 0.9
        elif draft.context.pick_position == PickPosition.BLIND:
            return base
        else:
            return base * 0.95

    def _score_comp_gap_fill(self, profile: AdcProfile, analysis: DraftAnalysis) -> float:
        """Does this ADC fill gaps in the team composition?"""
        return score_comp_gap_fill(profile, analysis.allied_comp_profile, self._data)

    def _score_solo_queue_reliability(self, profile: AdcProfile) -> float:
        """
        How reliable is this ADC in solo queue?
        Direct mapping from profile with difficulty penalty.
        """
        base = profile.solo_queue_stability * 10  # 1-10 -> 10-100
        # Penalize high execution difficulty
        difficulty_penalty = max(0, (profile.execution_difficulty - 5)) * 3
        meta_bonus = self._score_adc_climb_meta_bonus(profile.id)
        return max(0.0, min(100.0, base - difficulty_penalty + meta_bonus))

    def _score_adc_climb_meta_bonus(self, adc_id: str) -> float:
        """
        Ajuste opcional de meta vigente desde snapshots ADC del Meta Scraper.

        Bounded deliberately so external data nudges solo queue reliability
        without overriding draft fit, matchup, comfort or comp logic.
        """
        if self._data.get_adc_meta_snapshot_info().get("is_stale", True):
            return 0.0

        meta = self._data.get_adc_meta(adc_id)
        if not meta:
            return 0.0

        stats = meta.get("stats", {})
        climb_score = float(stats.get("climb_score", 50.0))
        win_rate = float(stats.get("win_rate", 50.0))
        pick_rate = float(stats.get("pick_rate", 0.0))
        ban_rate = float(stats.get("ban_rate", 0.0))

        score = (climb_score - 50.0) * 0.35
        score += (win_rate - 50.0) * 1.2
        score += min(pick_rate, 12.0) * 0.25
        score -= min(ban_rate, 30.0) * 0.15
        return max(-10.0, min(12.0, score))

    def _has_yasuo_airborne_setup(self, draft: DraftState) -> bool:
        return any(ally.id in _YASUO_AIRBORNE_ENABLERS for ally in draft.allies)

    def _has_yasuo_projectile_target(self, draft: DraftState, enemy: EnemyCompProfile) -> bool:
        return enemy.has_poke or any(enemy_champ.id in _YASUO_PROJECTILE_TARGETS for enemy_champ in draft.enemies)

    def _score_scaling_fit(self, profile: AdcProfile, analysis: DraftAnalysis) -> float:
        """Does this ADC's scaling profile match the comp's game plan?"""
        return score_scaling_fit(profile, analysis.allied_comp_profile)

    # ========================================================================
    # Score breakdown assembly
    # ========================================================================

    def _build_breakdown(
        self,
        raw: RawScores,
        weights: dict[str, float],
        draft_state: DraftState,
        adc_id: str,
    ) -> ScoreBreakdown:
        """Assemble the full score breakdown."""
        raw_dict = raw.model_dump()
        weighted_dict = {}
        weighted_sum = 0.0

        for factor, raw_value in raw_dict.items():
            w = weights.get(factor, 0.0)
            contribution = raw_value * w
            weighted_dict[factor] = round(contribution, 2)
            weighted_sum += contribution

        weighted_sum = round(weighted_sum, 2)

        # Comfort bonus
        comfort_bonus = self._compute_comfort_bonus(draft_state, adc_id)

        pre_clamp = round(weighted_sum + comfort_bonus, 2)

        return ScoreBreakdown(
            raw=raw,
            weighted=WeightedScores(**weighted_dict),
            comfort_bonus=round(comfort_bonus, 2),
            weighted_sum=weighted_sum,
            pre_clamp_total=pre_clamp,
            weights_used=weights,
        )

    def _compute_comfort_bonus(self, draft_state: DraftState, adc_id: str) -> float:
        """
        Compute comfort bonus for pool_preferred / pool_only modes.

        Formula: (comfort_score / 10) * max_points * weight
          comfort_score: 1-10 from user (defaults to 5 if in pool without explicit score)
          max_points: 20 (config)
          weight: 0.15 (config)
        """
        pool = draft_state.user_pool

        if pool.mode == PoolMode.UNRESTRICTED:
            return 0.0

        if adc_id not in pool.champions:
            return 0.0

        comfort_score = pool.comfort.get(adc_id, 5)  # Default 5 if not specified
        max_pts = self._weights_config.comfort_bonus_max_points
        w = self._weights_config.comfort_bonus_weight

        return (comfort_score / 10.0) * max_pts * w

    # ========================================================================
    # Output builders
    # ========================================================================

    def _build_top_pick(
        self,
        adc_id: str,
        breakdown: ScoreBreakdown,
        profile: AdcProfile,
        analysis: DraftAnalysis,
        draft_state: DraftState,
        adc_priority: _AdcPriority,
    ) -> RecommendedPick:
        """Build the top pick recommendation with full explanation."""
        display_name = self._data.get_champion_display_name(adc_id)
        total = max(0.0, min(100.0, breakdown.pre_clamp_total))

        strengths = self._generate_strengths(profile, analysis, draft_state)
        risks = self._generate_risks(profile, analysis, draft_state)
        not_rec = profile.weaknesses[:3]  # Use weaknesses as "not recommended when"
        play_pattern = self._generate_play_pattern(profile, analysis)

        return RecommendedPick(
            id=adc_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=breakdown,
            adc_context=self._build_adc_pick_context(adc_priority),
            strengths_in_this_draft=strengths,
            risks_in_this_draft=risks,
            not_recommended_when=not_rec,
            enabled_play_pattern=play_pattern,
        )

    def _build_alternative(
        self,
        alt_id: str,
        alt_breakdown: ScoreBreakdown,
        alt_profile: AdcProfile,
        top_id: str,
        top_profile: AdcProfile,
        analysis: DraftAnalysis,
        adc_priority: _AdcPriority,
    ) -> AlternativePick:
        """Build an alternative pick with comparison to top pick."""
        display_name = self._data.get_champion_display_name(alt_id)
        total = max(0.0, min(100.0, alt_breakdown.pre_clamp_total))

        # Generate one-line reason
        reason = self._generate_one_liner(alt_profile, top_profile, alt_breakdown)

        # Compare to top pick
        advantages = self._compare_advantages(alt_profile, top_profile)
        disadvantages = self._compare_disadvantages(alt_profile, top_profile)

        return AlternativePick(
            id=alt_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=alt_breakdown,
            adc_context=self._build_adc_pick_context(adc_priority),
            one_line_reason=reason,
            advantages_over_top_pick=advantages,
            disadvantages_vs_top_pick=disadvantages,
        )

    # ========================================================================
    # Explanation generators
    # ========================================================================

    def _generate_strengths(self, profile: AdcProfile, analysis: DraftAnalysis, draft: DraftState) -> list[str]:
        """Generate human-readable strengths for the top pick in this draft."""
        strengths = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        if allied.has_frontline and profile.synergy_frontline_comp >= 7:
            strengths.append(
                f"Tu equipo tiene frontline sólida — {profile.display_name} rinde al máximo protegido "
                f"(sinergia con frontline: {profile.synergy_frontline_comp}/10)"
            )

        if allied.has_peel and profile.synergy_peel_comp >= 7:
            strengths.append(
                f"El peel aliado permite a {profile.display_name} pegar libremente "
                f"(sinergia peel: {profile.synergy_peel_comp}/10)"
            )

        if allied.has_engage and profile.synergy_engage_support >= 7:
            strengths.append(f"El engage aliado genera oportunidades de kill para {profile.display_name}")

        if enemy.has_tanks and profile.anti_tank >= 7:
            strengths.append(f"Alta capacidad anti-tank vs la frontline enemiga (anti-tank: {profile.anti_tank}/10)")

        if not enemy.has_dive and profile.scaling >= 8:
            strengths.append(
                f"El enemigo no tiene dive — {profile.display_name} puede scalear con seguridad (escalado: {profile.scaling}/10)"
            )

        # Check for specific synergies with best_with
        for ally in draft.allies:
            if ally.id in profile.best_with:
                ally_name = self._data.get_champion_display_name(ally.id)
                strengths.append(f"Sinergia fuerte con {ally_name} aliado")

        for bonus_rule in self._get_adc_matchup_bonus_results(profile, draft):
            strengths.append(bonus_rule.reason)

        # Comp gap fill
        if "physical_dps" in allied.missing:
            champ = self._data.get_champion(profile.id)
            if champ and champ.damage_type == DamageType.PHYSICAL:
                strengths.append("Cubre la necesidad de daño físico del equipo")

        if not strengths:
            strengths = profile.strengths[:3]

        return strengths[:5]

    def _generate_risks(self, profile: AdcProfile, analysis: DraftAnalysis, draft: DraftState) -> list[str]:
        """Generate risk warnings for the top pick in this draft."""
        risks = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        if enemy.has_dive and profile.anti_dive <= 5:
            risks.append(
                f"El enemigo tiene amenazas de dive y el anti-dive de {profile.display_name} es limitado ({profile.anti_dive}/10)"
            )

        if enemy.has_burst and profile.self_peel <= 4:
            risks.append(f"Vulnerable al burst — peel propio limitado ({profile.self_peel}/10)")

        if not allied.has_frontline and profile.dependence_on_frontline >= 7:
            risks.append(
                f"{profile.display_name} depende de frontline ({profile.dependence_on_frontline}/10) "
                f"pero tu equipo no tiene frontline confiable"
            )

        if not allied.has_peel and profile.dependence_on_peel >= 7:
            risks.append(
                f"No hay peel disponible y {profile.display_name} lo necesita "
                f"(dependencia de peel: {profile.dependence_on_peel}/10)"
            )

        if profile.lane_priority <= 4:
            risks.append(
                f"Lane phase débil — puede quedar atrás temprano (prioridad de lane: {profile.lane_priority}/10)"
            )

        lane_rule = self._get_adc_lane_rule_result(profile, draft)
        if lane_rule:
            risks.append(lane_rule.reason)

        tactical_veto_reason = self._get_adc_tactical_veto_reason(profile, analysis)
        if tactical_veto_reason:
            risks.append(tactical_veto_reason)

        # Worst-into warnings
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.worst_into:
                enemy_name = self._data.get_champion_display_name(enemy_champ.id)
                risks.append(f"Matchup desfavorable contra {enemy_name} (peor matchup conocido)")

        if not risks:
            risks = profile.weaknesses[:2]

        return risks[:4]

    def _generate_play_pattern(self, profile: AdcProfile, analysis: DraftAnalysis) -> str:
        """Generate the enabled play pattern description."""
        shape = analysis.allied_comp_profile.teamfight_shape

        patterns = {
            TeamfightShape.FRONT_TO_BACK: (
                f"Teamfight frontal. Tu frontline inicia y pelea mientras "
                f"{profile.display_name} hace daño sostenido desde la retaguardia. "
                f"Picos de poder: {', '.join(profile.power_spikes)}."
            ),
            TeamfightShape.DIVE: (
                f"Composición de dive agresivo. {profile.display_name} sigue el dive del equipo "
                f"o juega split mientras el equipo presiona. "
                f"Buscar escaramuzas y peleas en torno a objetivos."
            ),
            TeamfightShape.POKE_SIEGE: (
                f"Composición de poke y asedio. {profile.display_name} contribuye a la presión "
                f"de torres y el daño de poke. Evitar el engage duro y forzar objetivos con ventaja de rango."
            ),
            TeamfightShape.PICK: (
                f"Composición de picks. {profile.display_name} sigue las capturas y juega en torno "
                f"al control de visión. Agruparse para objetivos y castigar las rotaciones enemigas."
            ),
            TeamfightShape.SPLIT: (
                f"Composición de split-push. {profile.display_name} sostiene el medio mientras "
                f"el split-pusher atrae presión. Estar listos para tomar torres u objetivos "
                f"cuando aparezca la ventaja numérica."
            ),
            TeamfightShape.MIXED: (
                f"Composición flexible. {profile.display_name} se adapta al plan del equipo — "
                f"teamfight agrupado, escaramuza en split. "
                f"Picos de poder: {', '.join(profile.power_spikes)}."
            ),
        }

        base = patterns.get(shape, patterns[TeamfightShape.MIXED])

        # Add draft notes if they add value
        if profile.draft_notes:
            base += f" Clave: {profile.draft_notes[:150]}"

        return base

    def _generate_one_liner(self, alt: AdcProfile, top: AdcProfile, breakdown: ScoreBreakdown) -> str:
        """Generate a one-line summary of why this alternative ranks lower."""
        raw = breakdown.raw
        # Find the factor where this ADC is strongest
        raw_dict = raw.model_dump()
        best_factor = max(raw_dict, key=raw_dict.get)
        factor_names = {
            "ally_synergy": "sinergia aliada",
            "enemy_matchup": "ventaja de matchup",
            "blind_pick_safety": "seguridad de pick ciego",
            "comp_gap_fill": "ajuste a la composición",
            "solo_queue_reliability": "fiabilidad en SoloQ",
            "scaling_fit": "ajuste de escalado",
        }
        best_name = factor_names.get(best_factor, best_factor)
        return f"Fuerte en {best_name} ({raw_dict[best_factor]:.0f}/100), pero puntúa menos en el draft que {top.display_name}."

    def _compare_advantages(self, alt: AdcProfile, top: AdcProfile) -> list[str]:
        """What does the alternative do better than the top pick?"""
        advantages = []

        if alt.mobility > top.mobility + 1:
            advantages.append(f"Mayor movilidad ({alt.mobility} vs {top.mobility})")
        if alt.self_peel > top.self_peel + 1:
            advantages.append(f"Mejor auto-peel ({alt.self_peel} vs {top.self_peel})")
        if alt.anti_dive > top.anti_dive + 1:
            advantages.append(f"Mejor anti-dive ({alt.anti_dive} vs {top.anti_dive})")
        if alt.blind_pick_safety > top.blind_pick_safety + 1:
            advantages.append(f"Pick ciego más seguro ({alt.blind_pick_safety} vs {top.blind_pick_safety})")
        if alt.lane_priority > top.lane_priority + 1:
            advantages.append(f"Lane phase más fuerte ({alt.lane_priority} vs {top.lane_priority})")
        if alt.scaling > top.scaling + 1:
            advantages.append(f"Mejor escalado ({alt.scaling} vs {top.scaling})")
        if alt.execution_difficulty < top.execution_difficulty - 1:
            advantages.append(f"Más fácil de ejecutar ({alt.execution_difficulty} vs {top.execution_difficulty})")
        if alt.skirmish_power > top.skirmish_power + 1:
            advantages.append(f"Más fuerte en escaramuzas ({alt.skirmish_power} vs {top.skirmish_power})")

        if not advantages:
            advantages.append("Más versátil en ciertas composiciones")

        return advantages[:3]

    def _compare_disadvantages(self, alt: AdcProfile, top: AdcProfile) -> list[str]:
        """What does the alternative do worse than the top pick?"""
        disadvantages = []

        if alt.scaling < top.scaling - 1:
            disadvantages.append(f"Menor escalado ({alt.scaling} vs {top.scaling})")
        if alt.teamfight_consistency < top.teamfight_consistency - 1:
            disadvantages.append(
                f"Menos consistente en teamfights ({alt.teamfight_consistency} vs {top.teamfight_consistency})"
            )
        if alt.anti_tank < top.anti_tank - 1:
            disadvantages.append(f"Más débil contra tanques ({alt.anti_tank} vs {top.anti_tank})")
        if alt.objective_dps < top.objective_dps - 1:
            disadvantages.append(f"Menor DPS en objetivos ({alt.objective_dps} vs {top.objective_dps})")
        if alt.solo_queue_stability < top.solo_queue_stability - 1:
            disadvantages.append(f"Menos fiable en SoloQ ({alt.solo_queue_stability} vs {top.solo_queue_stability})")
        if alt.self_peel < top.self_peel - 1:
            disadvantages.append(f"Menos auto-peel ({alt.self_peel} vs {top.self_peel})")

        if not disadvantages:
            disadvantages.append("Puntaje general levemente inferior en este draft")

        return disadvantages[:3]

    # ========================================================================
    # JUNGLE MODE — Jungle Meta as source of truth
    # ========================================================================

    def _recommend_jungle(self, draft_state: DraftState) -> RecommendationOutput:
        """Recommend junglers using Jungle Meta as the primary source."""
        analysis = self._analyzer.analyze(draft_state)
        snapshot = self._data.get_jungle_meta_snapshot()
        jungle_rows = self._data.get_jungle_meta_champions()
        if not snapshot.is_available or not jungle_rows:
            raise ValueError("Jungle Meta no esta disponible para recomendar junglas.")

        candidates = self._get_jungle_candidates(draft_state, jungle_rows)
        if not candidates:
            raise ValueError("No hay candidatos de Jungla disponibles para puntuar.")

        tier_rank = {"S": 0, "A": 1, "B": 2, "C": 3}
        best_rank = min(tier_rank.get(str(jungle_rows[cid].get("tier", "")).upper(), 9) for cid in candidates)

        scored: list[tuple[str, float, ScoreBreakdown, _JunglePriority]] = []
        fallback_scored: list[tuple[str, float, ScoreBreakdown, _JunglePriority]] = []
        for jungler_id in candidates:
            row = jungle_rows[jungler_id]
            champion = self._data.get_champion(jungler_id)
            if champion is None:
                continue
            priority = self._get_jungle_priority(row, draft_state, best_rank)
            if priority.eligibility == "blocked_low_tier":
                continue
            raw = self._compute_raw_scores_jungle(row, draft_state, analysis)
            breakdown = self._build_breakdown_jungle(raw, draft_state, jungler_id)
            score = max(0.0, min(100.0, breakdown.pre_clamp_total))
            item = (jungler_id, score, breakdown, priority)
            if priority.is_core:
                scored.append(item)
            else:
                fallback_scored.append(item)

        scored.sort(key=lambda x: x[1], reverse=True)
        fallback_scored.sort(key=lambda x: x[1], reverse=True)
        visible_scored = scored + fallback_scored
        top_candidates = [row for row in visible_scored if row[3].can_be_top_pick]
        if not top_candidates:
            raise ValueError("Ningun jungla paso los gates de tier del Jungle Meta.")

        top = top_candidates[0]
        alternatives = [row for row in visible_scored if row[0] != top[0]][:3]
        top_pick = self._build_top_pick_jungle(top[0], top[2], jungle_rows[top[0]], analysis, draft_state, top[3])

        alt_picks = []
        for alt_id, _, alt_breakdown, alt_priority in alternatives:
            alt_pick = self._build_alternative_jungle(
                alt_id,
                alt_breakdown,
                jungle_rows[alt_id],
                jungle_rows[top[0]],
                alt_priority,
            )
            alt_picks.append(alt_pick)

        state_hash = hashlib.md5(
            json.dumps(draft_state.model_dump(), sort_keys=True, default=str).encode()
        ).hexdigest()[:12]

        return RecommendationOutput(
            timestamp=datetime.now(timezone.utc).isoformat(),
            draft_state_hash=state_hash,
            mode=draft_state.user_pool.mode,
            top_pick=top_pick,
            alternatives=alt_picks,
            draft_analysis=analysis,
        )

    def _get_jungle_candidates(self, draft_state: DraftState, jungle_rows: dict[str, dict]) -> list[str]:
        picked = {champ.id for champ in draft_state.allies}
        picked.update(champ.id for champ in draft_state.enemies)
        picked.update(draft_state.bans)

        available = {cid for cid in jungle_rows if cid not in picked}
        pool = draft_state.user_pool

        if pool.mode == PoolMode.POOL_ONLY:
            return [cid for cid in pool.champions if cid in available]

        def tier_of(cid: str) -> str:
            return str(jungle_rows[cid].get("tier", "")).upper()

        meta_candidates = {cid for cid in available if tier_of(cid) in {"S", "A", "B"}}
        if pool.mode == PoolMode.POOL_PREFERRED:
            pool_candidates = {cid for cid in pool.champions if cid in available}
            meta_candidates.update(pool_candidates)
        return list(meta_candidates)

    def _get_jungle_priority(self, row: dict, draft_state: DraftState, best_rank: int) -> _JunglePriority:
        tier = str(row.get("tier", "")).upper()
        pool_only = draft_state.user_pool.mode == PoolMode.POOL_ONLY
        in_pool = row.get("id") in draft_state.user_pool.champions

        if tier in _JUNGLE_TOP_TIERS:
            return _JunglePriority(
                eligibility="core",
                eligibility_reason=f"Tier {tier} vigente en Jungle Meta.",
                is_core=True,
                can_be_top_pick=True,
            )
        if tier == "B":
            return _JunglePriority(
                eligibility="fallback_tier_b",
                eligibility_reason="Tier B: alternativa usable si no hay S/A disponible.",
                is_core=False,
                can_be_top_pick=best_rank >= 2,
            )
        if tier == "C" and pool_only:
            return _JunglePriority(
                eligibility="fallback_tier_c_pool_only",
                eligibility_reason="Tier C: solo top si tu pool no tiene una opcion mejor.",
                is_core=False,
                can_be_top_pick=best_rank >= 3,
            )
        if tier == "C" and in_pool:
            return _JunglePriority(
                eligibility="fallback_tier_c_pool_preferred",
                eligibility_reason="Tier C de tu pool: visible como alternativa, no como prioridad.",
                is_core=False,
                can_be_top_pick=False,
            )
        return _JunglePriority(
            eligibility="blocked_low_tier",
            eligibility_reason="Fuera del rango recomendado por Jungle Meta.",
            is_core=False,
            can_be_top_pick=False,
        )

    def _compute_raw_scores_jungle(
        self,
        row: dict,
        draft_state: DraftState,
        analysis: DraftAnalysis,
    ) -> RawScores:
        jungler_id = str(row.get("id", ""))
        comfort = draft_state.user_pool.comfort.get(jungler_id)
        comfort_raw = float(comfort * 10) if comfort is not None else 50.0
        return RawScores(
            ally_synergy=self._score_jungle_meta_strength(row),
            enemy_matchup=self._score_jungle_draft_fit(row, analysis),
            blind_pick_safety=self._score_jungle_blind_safety(row),
            comp_gap_fill=self._score_jungle_comp_gap(row, analysis),
            solo_queue_reliability=self._score_jungle_tempo(row),
            scaling_fit=max(0.0, min(100.0, comfort_raw)),
        )

    def _score_jungle_meta_strength(self, row: dict) -> float:
        tier = str(row.get("tier", "")).upper()
        score = _JUNGLE_TIER_SCORES.get(tier, 30.0)
        winrate = _float_or_none(row.get("winrate")) or 50.0
        pickrate = _float_or_none(row.get("pickrate")) or 0.0
        banrate = _float_or_none(row.get("banrate")) or 0.0
        snapshot = self._data.get_jungle_meta_snapshot()
        categories = snapshot.categories

        score += max(-12.0, min(14.0, (winrate - 50.0) * 3.0))
        score += min(pickrate, 18.0) * 0.35
        score += min(banrate, 25.0) * 0.12
        if row.get("id") in categories.get("overpowered", []):
            score += 5.0
        if row.get("id") in categories.get("bans", []):
            score += 2.0
        return max(0.0, min(100.0, score))

    def _score_jungle_draft_fit(self, row: dict, analysis: DraftAnalysis) -> float:
        champ = self._data.get_champion(str(row.get("id", "")))
        if champ is None:
            return 50.0
        tags = champ.tags
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile
        score = 50.0

        if not allied.has_engage:
            score += (tags.engage - 5) * 4
            score += (tags.cc - 5) * 2
        if not allied.has_frontline:
            score += (tags.tankiness - 5) * 3
        if enemy.has_dive:
            score += (tags.cc - 5) * 2
            score += (tags.tankiness - 5) * 2
        if enemy.has_tanks:
            score += (tags.sustained_dps - 5) * 3
        if enemy.has_poke:
            score += (tags.engage - 5) * 2
            score += (tags.mobility - 5) * 2
        if allied.primary_damage_existing and champ.damage_type != allied.primary_damage_existing:
            score += 6
        elif allied.primary_damage_existing and champ.damage_type == allied.primary_damage_existing:
            score -= 4

        return max(0.0, min(100.0, score))

    def _score_jungle_blind_safety(self, row: dict) -> float:
        champ = self._data.get_champion(str(row.get("id", "")))
        tier = str(row.get("tier", "")).upper()
        score = {"S": 76.0, "A": 68.0, "B": 56.0, "C": 42.0}.get(tier, 35.0)
        if champ is not None:
            score += (champ.tags.mobility - 5) * 2
            score += (champ.tags.tankiness - 5) * 1.5
            score += (champ.tags.cc - 5) * 1.5
        pickrate = _float_or_none(row.get("pickrate")) or 0.0
        score += min(pickrate, 15.0) * 0.45
        return max(0.0, min(100.0, score))

    def _score_jungle_comp_gap(self, row: dict, analysis: DraftAnalysis) -> float:
        champ = self._data.get_champion(str(row.get("id", "")))
        if champ is None:
            return 50.0
        tags = champ.tags
        allied = analysis.allied_comp_profile
        score = 50.0

        if "frontline" in allied.missing:
            score += (tags.tankiness - 5) * 4
        if "engage" in allied.missing:
            score += (tags.engage - 5) * 4
        if "peel" in allied.missing:
            score += (tags.peel - 5) * 2
            score += (tags.cc - 5) * 2
        if "magic_dps" in allied.missing and champ.damage_type in (DamageType.MAGIC, DamageType.MIXED):
            score += 10
        if "physical_dps" in allied.missing and champ.damage_type in (DamageType.PHYSICAL, DamageType.MIXED):
            score += 10

        return max(0.0, min(100.0, score))

    def _score_jungle_tempo(self, row: dict) -> float:
        champ = self._data.get_champion(str(row.get("id", "")))
        if champ is None:
            return 50.0
        score = 45.0
        tags = champ.tags
        score += (tags.early_power - 5) * 4
        score += (tags.mobility - 5) * 2
        score += (tags.pick_potential - 5) * 2
        if row.get("primary_reason") in {"item_synergy", "champ_buff", "meta_stable"}:
            score += 6
        return max(0.0, min(100.0, score))

    def _build_breakdown_jungle(self, raw: RawScores, draft_state: DraftState, jungler_id: str) -> ScoreBreakdown:
        has_comfort = jungler_id in draft_state.user_pool.comfort
        weights = {
            "ally_synergy": 0.70 if has_comfort else 0.80,
            "enemy_matchup": 0.05,
            "blind_pick_safety": 0.05,
            "comp_gap_fill": 0.05,
            "solo_queue_reliability": 0.05,
            "scaling_fit": 0.10 if has_comfort else 0.0,
        }
        weighted_dict = {}
        weighted_sum = 0.0
        for factor, raw_value in raw.model_dump().items():
            contribution = raw_value * weights.get(factor, 0.0)
            weighted_dict[factor] = round(contribution, 2)
            weighted_sum += contribution
        weighted_sum = round(weighted_sum, 2)
        return ScoreBreakdown(
            raw=raw,
            weighted=WeightedScores(**weighted_dict),
            comfort_bonus=0.0,
            weighted_sum=weighted_sum,
            pre_clamp_total=weighted_sum,
            weights_used=weights,
            draft_fit_score=round(
                (raw.enemy_matchup + raw.blind_pick_safety + raw.comp_gap_fill + raw.solo_queue_reliability) / 4,
                2,
            ),
            meta_strength_score=raw.ally_synergy,
        )

    def _build_top_pick_jungle(
        self,
        jungler_id: str,
        breakdown: ScoreBreakdown,
        row: dict,
        analysis: DraftAnalysis,
        draft_state: DraftState,
        priority: _JunglePriority,
    ) -> RecommendedPick:
        display_name = self._data.get_champion_display_name(jungler_id)
        total = max(0.0, min(100.0, breakdown.pre_clamp_total))
        strengths = self._generate_strengths_jungle(row, analysis)
        risks = self._generate_risks_jungle(row, priority)
        not_rec = self._generate_not_recommended_jungle(row, draft_state)
        pattern = row.get("playstyle") or "Juga alrededor del tempo de jungla y objetivos neutrales."

        return RecommendedPick(
            id=jungler_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=breakdown,
            jungle_context=self._build_jungle_pick_context(row, priority),
            strengths_in_this_draft=strengths,
            risks_in_this_draft=risks,
            not_recommended_when=not_rec,
            enabled_play_pattern=pattern,
        )

    def _build_alternative_jungle(
        self,
        alt_id: str,
        alt_breakdown: ScoreBreakdown,
        alt_row: dict,
        top_row: dict,
        priority: _JunglePriority,
    ) -> AlternativePick:
        display_name = self._data.get_champion_display_name(alt_id)
        total = max(0.0, min(100.0, alt_breakdown.pre_clamp_total))
        reason = f"Tier {alt_row.get('tier')} en Jungle Meta"
        if priority.eligibility.startswith("fallback"):
            reason += f" - {priority.eligibility_reason}"

        advantages = []
        disadvantages = []
        if (_float_or_none(alt_row.get("winrate")) or 0.0) > (_float_or_none(top_row.get("winrate")) or 0.0):
            advantages.append("Mejor winrate bruto en la fuente actual.")
        if str(alt_row.get("tier")) != str(top_row.get("tier")):
            disadvantages.append(f"Menor prioridad de tier que {top_row.get('display_name', 'el top pick')}.")
        if priority.can_be_top_pick is False:
            disadvantages.append("No deberia ser primera opcion con mejores tiers disponibles.")

        return AlternativePick(
            id=alt_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=alt_breakdown,
            jungle_context=self._build_jungle_pick_context(alt_row, priority),
            one_line_reason=reason,
            advantages_over_top_pick=advantages[:3],
            disadvantages_vs_top_pick=disadvantages[:3],
        )

    def _build_jungle_pick_context(self, row: dict, priority: _JunglePriority) -> JunglePickContext:
        snapshot = self._data.get_jungle_meta_snapshot()
        return JunglePickContext(
            tier=row.get("tier"),
            winrate=_float_or_none(row.get("winrate")),
            pickrate=_float_or_none(row.get("pickrate")),
            banrate=_float_or_none(row.get("banrate")),
            patch=snapshot.patch,
            updated_at=snapshot.date_updated,
            source_status=snapshot.status,
            source=snapshot.source,
            reason_text=row.get("reason_text"),
            core_builds=row.get("core_builds", []),
            core_rune=row.get("core_rune"),
            eligibility=priority.eligibility,
            eligibility_reason=priority.eligibility_reason,
        )

    def _generate_strengths_jungle(self, row: dict, analysis: DraftAnalysis) -> list[str]:
        tier = row.get("tier", "?")
        strengths = [f"Tier {tier} en la fuente viva de Jungle Meta."]
        if row.get("reason_text"):
            strengths.append(str(row["reason_text"]))
        if analysis.allied_comp_profile.missing:
            strengths.append("Aporta al armado de composicion segun los huecos detectados.")
        if row.get("core_builds"):
            strengths.append("Tiene build core registrada en Jungle Meta para este parche.")
        return strengths[:4]

    def _generate_risks_jungle(self, row: dict, priority: _JunglePriority) -> list[str]:
        risks = []
        tier = str(row.get("tier", "")).upper()
        if tier in {"B", "C"}:
            risks.append(priority.eligibility_reason)
        banrate = _float_or_none(row.get("banrate")) or 0.0
        if banrate >= 12:
            risks.append("Ban rate alto: puede no llegar libre al draft.")
        if priority.eligibility.startswith("fallback"):
            risks.append("Es alternativa contextual, no prioridad si hay S/A disponible.")
        return risks[:3] or ["Sin riesgos criticos detectados desde Jungle Meta."]

    def _generate_not_recommended_jungle(self, row: dict, draft_state: DraftState) -> list[str]:
        notes = []
        tier = str(row.get("tier", "")).upper()
        if tier == "C":
            notes.append("Si tenes disponible un jungla S/A del meta actual.")
        if draft_state.context.pick_position == PickPosition.BLIND and tier not in _JUNGLE_TOP_TIERS:
            notes.append("Como blind pick si hay opciones de tier superior.")
        notes.append("Si no dominas su pathing o ventana de primer clear.")
        return notes[:3]

    # ========================================================================
    # SUPPORT MODE — Mainear soporte
    # ========================================================================

    def _recommend_support(self, draft_state: DraftState) -> RecommendationOutput:
        """
        Support mode. Análogo a _recommend_adc pero usando support_profiles.

        Reutiliza analyzer.analyze() (gaps de comp + amenazas enemigas son agnosticos al rol).
        """
        # 1. Analyze compositions (mismo analyzer)
        analysis = self._analyzer.analyze(draft_state)

        # 2. Determinar pool de candidatos (soportes con perfil).
        candidates = self._get_support_candidates(draft_state)
        if not candidates:
            raise ValueError("No hay candidatos Support disponibles para puntuar.")

        # 3. Compute weights (mismas que ADC pero con default redistribution)
        weights = self._compute_weights(draft_state)

        # 4. Puntuar cada candidato.
        scored: list[tuple[str, float, ScoreBreakdown]] = []
        for supp_id in candidates:
            profile = self._data.get_support_profile(supp_id)
            if profile is None:
                continue
            raw = self._compute_raw_scores_supp(profile, draft_state, analysis)
            breakdown = self._build_breakdown_supp(raw, weights, draft_state, supp_id)
            scored.append((supp_id, breakdown.pre_clamp_total, breakdown))

        # 5. Sort
        scored.sort(key=lambda x: x[1], reverse=True)

        # 6. Build output
        top = scored[0]
        alternatives = scored[1:4]

        top_profile = self._data.get_support_profile(top[0])
        top_pick = self._build_top_pick_supp(top[0], top[2], top_profile, analysis, draft_state)

        alt_picks = []
        for alt_id, _, alt_breakdown in alternatives:
            alt_profile = self._data.get_support_profile(alt_id)
            alt_pick = self._build_alternative_supp(alt_id, alt_breakdown, alt_profile, top[0], top_profile, analysis)
            alt_picks.append(alt_pick)

        # 7. Hash
        state_hash = hashlib.md5(
            json.dumps(draft_state.model_dump(), sort_keys=True, default=str).encode()
        ).hexdigest()[:12]

        return RecommendationOutput(
            timestamp=datetime.now(timezone.utc).isoformat(),
            draft_state_hash=state_hash,
            mode=draft_state.user_pool.mode,
            top_pick=top_pick,
            alternatives=alt_picks,
            draft_analysis=analysis,
        )

    def _get_support_candidates(self, draft_state: DraftState) -> list[str]:
        """Get list of Support IDs to score based on pool mode."""
        all_supports = self._data.get_support_ids()
        pool = draft_state.user_pool

        picked = set()
        for ally in draft_state.allies:
            picked.add(ally.id)
        for enemy in draft_state.enemies:
            picked.add(enemy.id)
        for ban in draft_state.bans:
            picked.add(ban)

        available = all_supports - picked

        if pool.mode == PoolMode.POOL_ONLY:
            return [c for c in pool.champions if c in available]
        else:  # POOL_PREFERRED, UNRESTRICTED — score everyone available
            return list(available)

    # ------------------------------------------------------------------------
    # Raw scores for Support
    # ------------------------------------------------------------------------

    def _compute_raw_scores_supp(
        self,
        profile: SupportProfile,
        draft_state: DraftState,
        analysis: DraftAnalysis,
    ) -> RawScores:
        """Compute 0-100 raw scores per factor, support edition."""
        # D9: Queue archetype boost (flat bonus)
        queue_arch_boost = 0.0
        queue_type = draft_state.context.queue_type.value if hasattr(draft_state.context, "queue_type") else None
        if queue_type:
            queue_hints = self._data.get_queue_style_hints(queue_type)
            if queue_hints:
                arch_boosts = queue_hints.get("archetype_boosts", {})
                queue_arch_boost = arch_boosts.get(profile.archetype.value, 0.0)

        return RawScores(
            ally_synergy=self._score_supp_ally_synergy(profile, draft_state, analysis),
            enemy_matchup=self._score_supp_enemy_matchup(profile, draft_state, analysis),
            blind_pick_safety=profile.blind_pick_safety * 10.0 + queue_arch_boost,
            comp_gap_fill=self._score_supp_comp_gap_fill(profile, analysis),
            solo_queue_reliability=self._score_supp_solo_queue(profile),
            scaling_fit=self._score_supp_scaling_fit(profile, analysis),
        )

    def _score_supp_ally_synergy(self, profile: SupportProfile, draft: DraftState, analysis: DraftAnalysis) -> float:
        """
        Sinergia con el equipo aliado:
        - Fuerte premio si el ADC aliado está en best_with_adcs.
        - Penalty si está en worst_with_adcs.
        - Bonus por sinergia con la jungla aliada (engage vs farm).
        - Bonus por encajar con el "shape" (scaling, dive, poke).
        - **NotebookLM 2026-04-27**: bonus por sinergia medida 2v2 (measured_synergies.json).
        """
        if not draft.allies:
            return 50.0

        score = 50.0
        allied = analysis.allied_comp_profile

        for ally in draft.allies:
            ally_id = ally.id

            # ADC aliado: el factor más pesado
            if ally_id in self._data.get_adc_ids():
                # Auditoría 2026-04-27: usar synergy_matrix cuantitativa (1-10) si disponible
                matrix_score = self._data.get_synergy_score(profile.id, ally_id)
                if matrix_score is not None:
                    # Escalar 1-10 a bonus: 5=neutral(0), 10=+20, 1=-16
                    score += (matrix_score - 5) * 4
                elif ally_id in profile.best_with_adcs:
                    score += 18  # Match S-tier (alternativa sin matrix)
                elif ally_id in profile.worst_with_adcs:
                    score -= 12  # Anti-sinergia (alternativa sin matrix)
                else:
                    score += 2  # Neutral

                # NotebookLM bonus: sinergia medida con WR comprobado/heurístico
                score += self._score_measured_synergy_bonus(ally_id, profile.id)

            # Jungla aliada: D8 — clasificación explícita por arquetipo
            ally_champ = self._data.get_champion(ally_id)
            if ally_champ is not None and ally_champ.primary_role.value == "Jungle":
                jg_arch = self._data.classify_jungler_archetype(ally_id)
                if jg_arch is not None:
                    # Usar scoring_modifiers del JSON
                    modifier = self._data.get_jungler_scoring_modifier(jg_arch)
                    supp_arch = profile.archetype.value
                    if supp_arch in modifier.get("boost_archetypes", []):
                        score += modifier.get("boost_value", 4.0)
                    elif supp_arch in modifier.get("penalize_archetypes", []):
                        score += modifier.get("penalty_value", -3.0)
                else:
                    # Alternativa: heuristica basada en tags.
                    tags = ally_champ.tags
                    if tags.engage >= 7 and tags.cc >= 5:
                        score += (profile.synergy_engage_jungler - 5) * 2
                    else:
                        score += (profile.synergy_farm_jungler - 5) * 2

        # Comp shape match
        if allied.teamfight_shape.value == "scaling" or "scaling" in allied.missing:
            score += (profile.synergy_with_scaling_comp - 5) * 2
        if allied.teamfight_shape.value == "dive":
            score += (profile.synergy_with_dive_comp - 5) * 2
        if allied.teamfight_shape.value == "poke_siege":
            score += (profile.synergy_with_poke_comp - 5) * 2

        return max(0.0, min(100.0, score))

    def _score_measured_synergy_bonus(self, adc_id: str, supp_id: str) -> float:
        """NotebookLM 2026-04-27: bonus por sinergia medida 2v2.

        Si la pareja {ADC aliado, supp candidato} está en measured_synergies.json:
        - confidence='measured' con WR > 50%: bonus interpolado (cada 1pp sobre 50% = +3,
          cap 15pts)
        - confidence='heuristic' (sin WR comprobado): bonus reducido por factor 0.6
          (cap 9pts)

        Si no hay match, devuelve 0.
        """
        entry = self._data.get_measured_synergy(adc_id, supp_id)
        if entry is None:
            return 0.0

        cfg = self._data.get_measured_synergy_config()
        threshold = cfg.get("wr_threshold_for_bonus", 0.50)
        max_bonus = cfg.get("max_bonus", 15.0)
        h_factor = cfg.get("heuristic_confidence_factor", 0.6)
        h_max = cfg.get("heuristic_max_bonus", 9.0)

        confidence = entry.get("confidence", "heuristic")

        if confidence == "measured":
            wr = entry.get("winrate")
            if wr is None or wr <= threshold:
                return 0.0
            excess_pp = (wr - threshold) * 100  # 0.537 → 3.7
            return min(max_bonus, excess_pp * 3.0)

        # heuristic: bonus base fijo modulado por h_factor (asume ~52% efectivo)
        return min(h_max, 12.0 * h_factor)

    def _score_supp_enemy_matchup(self, profile: SupportProfile, draft: DraftState, analysis: DraftAnalysis) -> float:
        """
        Matchup contra el equipo enemigo:
        - Anti-dive premia si hay dive enemigo.
        - Anti-assassin-peel premia vs burst.
        - Anti-poke-in-lane premia vs poke.
        - Bonos especificos por support enemigo en strong/weak_against_supports.
        - **NotebookLM 2026-04-27**: triángulo Engage > Poke > Sustain con eje invertido
          Disengage > Engage (strategic_triangle.json).
        """
        if not draft.enemies:
            return 50.0

        score = 50.0
        enemy = analysis.enemy_comp_profile

        if enemy.has_dive:
            score += (profile.anti_dive - 5) * 4
        if enemy.has_burst:
            score += (profile.anti_assassin_peel - 5) * 3
        if enemy.has_poke:
            score += (profile.anti_poke_in_lane - 5) * 3
        if enemy.has_tanks:
            # Contra tanques, preferir supports de poke/daño.
            if profile.archetype == SupportArchetype.POKE:
                score += 8
            elif profile.archetype == SupportArchetype.ENGAGE:
                score -= 4  # tanks resisten engage hard

        # Matchup contra support enemigo.
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.strong_against_supports:
                score += 8
            elif enemy_champ.id in profile.weak_against_supports:
                score -= 8

            # Auditoría 2026-04-27: lane matchup individual (matchup_rules.json)
            lane_result = self._data.get_lane_matchup(profile.id, enemy_champ.id)
            if lane_result is not None:
                score += self._data.get_matchup_score_value(lane_result)

        # Triangulo estrategico NotebookLM: aplica una vez por support enemigo detectado.
        score += self._apply_strategic_triangle_bonus(profile.id, draft)

        # Threat level
        if enemy.threat_level_to_adc == ThreatLevel.CRITICAL:
            # Hace falta peel extra.
            score += (profile.peel_strength - 5) * 2

        # Anti-meta counterpicks necesitan romper el techo de 100 para superar la penalización
        # de seguridad a ciegas. Si el score es masivo, lo permitimos hasta 150.
        return max(0.0, min(150.0, score))

    def _apply_strategic_triangle_bonus(self, candidate_supp_id: str, draft: DraftState) -> float:
        """NotebookLM 2026-04-27: aplica el triángulo Engage > Poke > Sustain.

        Detecta el arquetipo fine-grained del candidato y de los supports enemigos
        identificables en draft.enemies. Devuelve:
        - +10 score por cada support enemigo que el candidato counterea ('beats')
        - -8 score por cada support enemigo contra el que el candidato pierde ('loses_to')
        - Cap por defensa: máximo +-12 total para no eclipsar otros factores.
        """
        triangle = self._data.get_strategic_triangle()
        if not triangle:
            return 0.0

        my_arch = self._data.classify_supp_archetype_fine(candidate_supp_id)
        if my_arch is None:
            return 0.0

        triangle_rules = triangle.get("triangle", {}).get(my_arch, {})
        beats = set(triangle_rules.get("beats", []))
        loses_to = set(triangle_rules.get("loses_to", []))

        scoring_cfg = triangle.get("scoring", {})
        beats_bonus = scoring_cfg.get("beats_bonus", 10.0)
        loses_penalty = scoring_cfg.get("loses_to_penalty", -8.0)
        cap = scoring_cfg.get("max_total_modifier_per_pick", 12.0)

        delta = 0.0
        for enemy_champ in draft.enemies:
            enemy_arch = self._data.classify_supp_archetype_fine(enemy_champ.id)
            if enemy_arch is None:
                continue
            if enemy_arch in beats:
                delta += beats_bonus
            elif enemy_arch in loses_to:
                delta += loses_penalty

        # Cap simétrico
        return max(-cap, min(cap, delta))

    def _score_supp_comp_gap_fill(self, profile: SupportProfile, analysis: DraftAnalysis) -> float:
        """¿Cubrís un gap del equipo? Engage si falta engage, peel si falta peel.

        NotebookLM 2026-04-27: bonus/penalty por ciclo de predominancia de comps
        (comp_predominance.json: Attack > Siege > Protect > Catch > Attack).
        """
        score = 50.0
        allied = analysis.allied_comp_profile

        if not allied.has_engage:
            score += (profile.engage_strength - 5) * 4
        else:
            # If team has engage already, peel is what we need
            score += (profile.peel_strength - 5) * 2

        if not allied.has_peel:
            score += (profile.peel_strength - 5) * 4

        if not allied.has_frontline:
            # Need a tanky support to compensate
            if profile.archetype in (SupportArchetype.ENGAGE, SupportArchetype.CATCHER, SupportArchetype.WARDEN):
                score += 10
            elif profile.archetype == SupportArchetype.ENCHANTER:
                score -= 6

        if "physical_dps" in allied.missing or "magic_dps" in allied.missing:
            # If team needs damage, mage support helps
            if profile.archetype == SupportArchetype.POKE:
                score += 12

        # Comp predominance cycle bonus (piedra-papel-tijera entre comps)
        score += self._apply_comp_predominance_bonus(profile, analysis)

        return max(0.0, min(100.0, score))

    def _apply_comp_predominance_bonus(self, profile: SupportProfile, analysis: DraftAnalysis) -> float:
        """NotebookLM 2026-04-27: bonus/penalty por ciclo de predominancia.

        Si la comp aliada (inferida del teamfight_shape) counterea la comp enemiga,
        y el soporte candidato es del arquetipo recomendado para esa comp aliada,
        aplica bonus. Si pierde contra la enemiga, penaliza.

        Usa comp_predominance.json para los matchups entre comp types.
        """
        predominance = self._data.get_comp_predominance()
        if not predominance:
            return 0.0

        pred_data = predominance.get("predominance", {})
        scoring_cfg = predominance.get("scoring", {})
        beats_bonus = scoring_cfg.get("comp_beats_enemy_bonus", 12.0)
        loses_penalty = scoring_cfg.get("comp_loses_to_enemy_penalty", -8.0)
        allied_shape = analysis.allied_comp_profile.teamfight_shape.value
        allied_comp_type = self._teamfight_shape_to_comp_type(allied_shape)

        if allied_comp_type is None:
            return 0.0

        comp_def = pred_data.get(allied_comp_type, {})
        if not comp_def:
            return 0.0

        # Revisar si el arquetipo del candidato se recomienda para esta composicion.
        fine_arch = self._data.classify_supp_archetype_fine(profile.id)
        coarse_arch = profile.archetype.value  # engage, enchanter, poke, catcher, warden
        recommended = comp_def.get("supp_archetypes_recommended", [])

        archetype_match = (fine_arch in recommended) or (coarse_arch in recommended)
        if not archetype_match:
            return 0.0

        # Revisar composicion enemiga: nuestro tipo de comp le gana o pierde?
        # Intentamos inferir la comp enemiga desde su forma de teamfight.
        enemy_has_dive = analysis.enemy_comp_profile.has_dive
        enemy_has_poke = analysis.enemy_comp_profile.has_poke
        enemy_has_tanks = analysis.enemy_comp_profile.has_tanks
        enemy_has_burst = analysis.enemy_comp_profile.has_burst

        # Clasificacion heuristica de composicion enemiga.
        enemy_comp_type = None
        if enemy_has_dive and enemy_has_burst:
            enemy_comp_type = "attack_matrix"
        elif enemy_has_poke and not enemy_has_dive:
            enemy_comp_type = "poke_siege"
        elif enemy_has_tanks and not enemy_has_dive:
            enemy_comp_type = "front_to_back"
        elif not enemy_has_tanks and not enemy_has_poke and not enemy_has_dive:
            enemy_comp_type = "pick"

        if enemy_comp_type is None:
            return 0.0

        beats = comp_def.get("beats", [])
        loses = comp_def.get("loses_to", [])

        if enemy_comp_type in beats:
            return beats_bonus
        elif enemy_comp_type in loses:
            return loses_penalty
        return 0.0

    @staticmethod
    def _teamfight_shape_to_comp_type(shape: str) -> str | None:
        """Map TeamfightShape enum values to comp_predominance keys."""
        mapping = {
            "front_to_back": "front_to_back",
            "dive": "attack_matrix",
            "poke_siege": "poke_siege",
            "pick": "pick",
            "split": "split",
        }
        return mapping.get(shape)

    def _score_supp_solo_queue(self, profile: SupportProfile) -> float:
        """Reliability en solo queue: balance entre seguridad y capacidad de hacer plays.

        En elo medio-alto (Esmeralda+), los enchanters pasivos no pueden
        compensar un ADC inconsistente. Los playmakers (Thresh, Rakan, Pyke)
        tienen más agency para generar ventaja propia.

        Fórmula v2:
        - Base: blind_pick_safety * 8 (reducido de *10)
        - Playmaking bonus: (lane_kill_pressure + engage_strength + cc_chain) / 3 * 4
        - Execution penalty: suave (-2 por punto > 5, era -3)
        """
        safety_base = profile.blind_pick_safety * 8

        # Playmaking agency: promedio de presión de kill + engage + CC
        playmaking_avg = (profile.lane_kill_pressure + profile.engage_strength + profile.cc_chain_length) / 3.0
        playmaking_bonus = playmaking_avg * 4

        # Execution penalty más suave (skill es esperado en Esmeralda+)
        difficulty_penalty = max(0, profile.execution_difficulty - 5) * 2

        meta_bonus = self._score_support_meta_bonus(profile.id)
        score = safety_base + playmaking_bonus - difficulty_penalty + meta_bonus
        return max(0.0, min(100.0, score))

    def _score_support_meta_bonus(self, supp_id: str) -> float:
        """
        Ajuste opcional de meta vigente desde snapshots Support del Meta Scraper.

        Misma lógica que el ADC pero sin climb_score (el snapshot de support
        no lo calcula). Nudge acotado a [-10, 12] para no pisar sinergias ni
        matchups.
        """
        meta = self._data.get_support_meta(supp_id)
        if not meta:
            return 0.0

        stats = meta.get("stats", {})
        win_rate = float(stats.get("win_rate", 50.0))
        pick_rate = float(stats.get("pick_rate", 0.0))
        ban_rate = float(stats.get("ban_rate", 0.0))

        score = (win_rate - 50.0) * 1.2
        score += min(pick_rate, 12.0) * 0.25
        score -= min(ban_rate, 30.0) * 0.15
        return max(-10.0, min(12.0, score))

    def _score_supp_scaling_fit(self, profile: SupportProfile, analysis: DraftAnalysis) -> float:
        """Cómo encaja la curva de poder del soporte con el equipo."""
        score = 50.0
        # Lane phase strength important if comp is early-mid
        score += (profile.lane_phase_strength - 5) * 2
        score += (profile.midgame_strength - 5) * 2
        score += (profile.lategame_strength - 5) * 2

        return max(0.0, min(100.0, score))

    # ------------------------------------------------------------------------
    # Construccion de outputs (Support)
    # ------------------------------------------------------------------------

    def _build_breakdown_supp(
        self,
        raw: RawScores,
        weights: dict[str, float],
        draft_state: DraftState,
        supp_id: str,
    ) -> ScoreBreakdown:
        """Same as _build_breakdown but uses support pool for comfort bonus."""
        raw_dict = raw.model_dump()
        weighted_dict = {}
        weighted_sum = 0.0

        for factor, raw_value in raw_dict.items():
            w = weights.get(factor, 0.0)
            contribution = raw_value * w
            weighted_dict[factor] = round(contribution, 2)
            weighted_sum += contribution

        weighted_sum = round(weighted_sum, 2)

        # Comfort bonus (same logic, just using the support id)
        comfort_bonus = self._compute_comfort_bonus(draft_state, supp_id)
        pre_clamp = round(weighted_sum + comfort_bonus, 2)

        return ScoreBreakdown(
            raw=raw,
            weighted=WeightedScores(**weighted_dict),
            comfort_bonus=round(comfort_bonus, 2),
            weighted_sum=weighted_sum,
            pre_clamp_total=pre_clamp,
            weights_used=weights,
        )

    def _build_top_pick_supp(
        self,
        supp_id: str,
        breakdown: ScoreBreakdown,
        profile: SupportProfile,
        analysis: DraftAnalysis,
        draft_state: DraftState,
    ) -> RecommendedPick:
        display_name = self._data.get_champion_display_name(supp_id)
        total = max(0.0, min(100.0, breakdown.pre_clamp_total))

        strengths = self._generate_strengths_supp(profile, analysis, draft_state)
        risks = self._generate_risks_supp(profile, analysis, draft_state)
        not_rec = profile.weaknesses[:3]
        play_pattern = self._generate_play_pattern_supp(profile, analysis, draft_state)

        return RecommendedPick(
            id=supp_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=breakdown,
            strengths_in_this_draft=strengths,
            risks_in_this_draft=risks,
            not_recommended_when=not_rec,
            enabled_play_pattern=play_pattern,
        )

    def _build_alternative_supp(
        self,
        alt_id: str,
        alt_breakdown: ScoreBreakdown,
        alt_profile: SupportProfile,
        top_id: str,
        top_profile: SupportProfile,
        analysis: DraftAnalysis,
    ) -> AlternativePick:
        display_name = self._data.get_champion_display_name(alt_id)
        total = max(0.0, min(100.0, alt_breakdown.pre_clamp_total))

        reason = self._generate_one_liner_supp(alt_profile, top_profile, alt_breakdown)
        advantages = self._compare_advantages_supp(alt_profile, top_profile)
        disadvantages = self._compare_disadvantages_supp(alt_profile, top_profile)

        return AlternativePick(
            id=alt_id,
            display_name=display_name,
            total_score=round(total, 1),
            score_breakdown=alt_breakdown,
            one_line_reason=reason,
            advantages_over_top_pick=advantages,
            disadvantages_vs_top_pick=disadvantages,
        )

    # ------------------------------------------------------------------------
    # Explanation generators (Support)
    # ------------------------------------------------------------------------

    def _generate_strengths_supp(
        self, profile: SupportProfile, analysis: DraftAnalysis, draft: DraftState
    ) -> list[str]:
        """Generate 'Razones' for the support pick — specific to this draft."""
        strengths: list[str] = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        # Sinergia con ADC aliado específica
        for ally in draft.allies:
            if ally.id in profile.best_with_adcs:
                ally_name = self._data.get_champion_display_name(ally.id)
                strengths.append(f"Sinergia top-tier con {ally_name} aliado — pareja recomendada en KB.")

        # Engage gap fill
        if not allied.has_engage and profile.engage_strength >= 7:
            strengths.append(
                f"Tu equipo no tiene engage — {profile.display_name} lo aporta "
                f"({profile.engage_strength}/10 engage strength)."
            )

        # Peel para ADC squishy
        if not allied.has_peel and profile.peel_strength >= 7:
            strengths.append(
                f"Tu equipo necesita peel y {profile.display_name} es premier en eso "
                f"({profile.peel_strength}/10 peel strength)."
            )

        # Anti-dive contra amenazas enemigas.
        if enemy.has_dive and profile.anti_dive >= 7:
            strengths.append(
                f"Counter al dive enemigo ({enemy.primary_threat or 'múltiples amenazas'}) "
                f"con tu kit de peel ({profile.anti_dive}/10 anti-dive)."
            )

        # Anti-poke
        if enemy.has_poke and profile.anti_poke_in_lane >= 7:
            strengths.append(f"Sobrevivís el poke enemigo en línea ({profile.anti_poke_in_lane}/10 anti-poke).")

        # Anti-burst
        if enemy.has_burst and profile.anti_assassin_peel >= 7:
            strengths.append(
                f"Tu peel anti-assassin ({profile.anti_assassin_peel}/10) salva al ADC contra el burst enemigo."
            )

        # Fuerte contra support enemigo.
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.strong_against_supports:
                enemy_name = self._data.get_champion_display_name(enemy_champ.id)
                strengths.append(f"Ganás lane phase contra {enemy_name} (matchup favorable).")

        # Lane kill pressure si hay engage jungler aliada
        for ally in draft.allies:
            ally_champ = self._data.get_champion(ally.id)
            if ally_champ and ally_champ.primary_role.value == "Jungle":
                if ally_champ.tags.engage >= 7 and profile.lane_kill_pressure >= 7:
                    ally_name = self._data.get_champion_display_name(ally.id)
                    strengths.append(
                        f"Jungla aliada ({ally_name}) tiene engage; coordiná ganks "
                        f"con tu kill pressure ({profile.lane_kill_pressure}/10)."
                    )

        if not strengths:
            strengths = [s for s in profile.strengths[:3]]

        return strengths[:5]

    def _generate_risks_supp(self, profile: SupportProfile, analysis: DraftAnalysis, draft: DraftState) -> list[str]:
        """Generate risks for the support pick in this draft."""
        risks: list[str] = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        if enemy.has_dive and profile.anti_dive <= 5:
            risks.append(
                f"El equipo enemigo tiene dive y {profile.display_name} no peelea bien ({profile.anti_dive}/10 anti-dive)."
            )

        if enemy.has_poke and profile.anti_poke_in_lane <= 4:
            risks.append(
                f"El enemigo tiene poke pesado y {profile.display_name} sufre en línea ({profile.anti_poke_in_lane}/10 anti-poke)."
            )

        # ADC aliado en worst_with
        for ally in draft.allies:
            if ally.id in profile.worst_with_adcs:
                ally_name = self._data.get_champion_display_name(ally.id)
                risks.append(f"Anti-sinergia con {ally_name} aliado — win conditions opuestas.")

        # Debil contra support enemigo.
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.weak_against_supports:
                enemy_name = self._data.get_champion_display_name(enemy_champ.id)
                risks.append(f"Perdés lane phase contra {enemy_name} (matchup desfavorable).")

        # Engage support sin follow-up
        if profile.archetype == SupportArchetype.ENGAGE and not allied.has_frontline and len(draft.allies) >= 2:
            # Check if there's any damage burst follow-up
            risks.append("Engage support sin frontline aliada — riesgo de pickeos aislados.")

        # No peel para scaling ADC
        if profile.archetype == SupportArchetype.ENGAGE:
            for ally in draft.allies:
                if ally.id in self._data.get_adc_ids():
                    adc_profile = self._data.get_adc_profile(ally.id)
                    if adc_profile and adc_profile.dependence_on_peel >= 7:
                        ally_name = self._data.get_champion_display_name(ally.id)
                        risks.append(
                            f"{ally_name} aliado depende de peel ({adc_profile.dependence_on_peel}/10) "
                            f"— engage support no se lo aporta."
                        )

        if profile.lane_phase_strength <= 4:
            risks.append(f"Lane phase débil ({profile.lane_phase_strength}/10) — depende de scalear hasta mid.")

        if not risks:
            risks = profile.weaknesses[:2]

        return risks[:4]

    def _generate_play_pattern_supp(self, profile: SupportProfile, analysis: DraftAnalysis, draft: DraftState) -> str:
        """
        Generate the 'Plan de Juego' by substituting placeholders in profile.play_pattern_template.
        """
        template = profile.play_pattern_template

        # Discover placeholders
        allied_adc_id = None
        ally_jungler_id = None
        for ally in draft.allies:
            if ally.id in self._data.get_adc_ids() and allied_adc_id is None:
                allied_adc_id = ally.id
            ally_champ = self._data.get_champion(ally.id)
            if ally_champ and ally_champ.primary_role.value == "Jungle" and ally_jungler_id is None:
                ally_jungler_id = ally.id

        enemy_adc_id = None
        enemy_support_id = None
        for enemy in draft.enemies:
            if enemy.id in self._data.get_adc_ids() and enemy_adc_id is None:
                enemy_adc_id = enemy.id
            enemy_pp = self._data.get_priority_profile(enemy.id)
            if enemy_pp and "support" in enemy_pp.category.value and enemy_support_id is None:
                enemy_support_id = enemy.id

        # Sustituir placeholders con fallbacks legibles.
        replacements = {
            "{allied_adc}": self._data.get_champion_display_name(allied_adc_id) if allied_adc_id else "tu ADC",
            "{enemy_adc}": self._data.get_champion_display_name(enemy_adc_id) if enemy_adc_id else "el ADC enemigo",
            "{enemy_support}": self._data.get_champion_display_name(enemy_support_id)
            if enemy_support_id
            else "el soporte enemigo",
            "{ally_jungler}": self._data.get_champion_display_name(ally_jungler_id) if ally_jungler_id else "tu jungla",
            "{primary_threat}": analysis.enemy_comp_profile.primary_threat or "los carries enemigos",
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        # Append warnings on dive heavy comp
        if analysis.enemy_comp_profile.has_dive and profile.archetype == SupportArchetype.ENGAGE:
            result += " ⚠ Cuidado: el equipo enemigo tiene dive; no inicies sin todo el equipo presente."

        return result

    def _generate_one_liner_supp(self, alt: SupportProfile, top: SupportProfile, breakdown: ScoreBreakdown) -> str:
        raw_dict = breakdown.raw.model_dump()
        best_factor = max(raw_dict, key=raw_dict.get)
        factor_names = {
            "ally_synergy": "sinergia aliada",
            "enemy_matchup": "matchup contra enemigo",
            "blind_pick_safety": "seguridad de pick ciego",
            "comp_gap_fill": "gap fill",
            "solo_queue_reliability": "solo queue reliability",
            "scaling_fit": "scaling alignment",
        }
        best_name = factor_names.get(best_factor, best_factor)
        return (
            f"Fuerte en {best_name} ({raw_dict[best_factor]:.0f}/100), "
            f"pero scorea menos que {top.display_name} en este draft."
        )

    def _compare_advantages_supp(self, alt: SupportProfile, top: SupportProfile) -> list[str]:
        """What does the alternative do better than the top?"""
        advantages = []

        if alt.engage_strength > top.engage_strength + 1:
            advantages.append(f"Mejor engage ({alt.engage_strength} vs {top.engage_strength})")
        if alt.peel_strength > top.peel_strength + 1:
            advantages.append(f"Mejor peel ({alt.peel_strength} vs {top.peel_strength})")
        if alt.poke > top.poke + 1:
            advantages.append(f"Mejor poke ({alt.poke} vs {top.poke})")
        if alt.disengage > top.disengage + 1:
            advantages.append(f"Mejor disengage ({alt.disengage} vs {top.disengage})")
        if alt.anti_dive > top.anti_dive + 1:
            advantages.append(f"Mejor anti-dive ({alt.anti_dive} vs {top.anti_dive})")
        if alt.lategame_strength > top.lategame_strength + 1:
            advantages.append(f"Mejor late game ({alt.lategame_strength} vs {top.lategame_strength})")
        if alt.execution_difficulty < top.execution_difficulty - 1:
            advantages.append(f"Más fácil de ejecutar ({alt.execution_difficulty} vs {top.execution_difficulty})")

        if not advantages:
            advantages.append("Más versátil en ciertas situaciones de draft.")
        return advantages[:3]

    def _compare_disadvantages_supp(self, alt: SupportProfile, top: SupportProfile) -> list[str]:
        disadvantages = []

        if alt.engage_strength < top.engage_strength - 1:
            disadvantages.append(f"Menos engage ({alt.engage_strength} vs {top.engage_strength})")
        if alt.peel_strength < top.peel_strength - 1:
            disadvantages.append(f"Menos peel ({alt.peel_strength} vs {top.peel_strength})")
        if alt.lane_kill_pressure < top.lane_kill_pressure - 1:
            disadvantages.append(f"Menos kill pressure en lane ({alt.lane_kill_pressure} vs {top.lane_kill_pressure})")
        if alt.lane_phase_strength < top.lane_phase_strength - 1:
            disadvantages.append(f"Lane phase más débil ({alt.lane_phase_strength} vs {top.lane_phase_strength})")
        if alt.execution_difficulty > top.execution_difficulty + 1:
            disadvantages.append(f"Más difícil de ejecutar ({alt.execution_difficulty} vs {top.execution_difficulty})")

        if not disadvantages:
            disadvantages.append("Score ligeramente menor en este contexto específico.")
        return disadvantages[:3]
