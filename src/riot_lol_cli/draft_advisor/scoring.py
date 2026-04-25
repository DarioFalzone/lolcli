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
from datetime import datetime, timezone

from .analyzer import CompositionAnalyzer
from .champion_data import ChampionDataService
from .schemas import (
    AdcProfile,
    AlternativePick,
    DamageType,
    DraftAnalysis,
    DraftState,
    PickPosition,
    PoolMode,
    RawScores,
    RecommendationOutput,
    RecommendedPick,
    ScoreBreakdown,
    TeamfightShape,
    ThreatLevel,
    WeightedScores,
)
from .scoring_rules import score_comp_gap_fill, score_scaling_fit


class ScoringEngine:
    """Multi-factor scorer for ADC draft recommendations."""

    def __init__(self, data_service: ChampionDataService):
        self._data = data_service
        self._analyzer = CompositionAnalyzer(data_service)
        self._weights_config = data_service.get_scoring_weights()

    def recommend(self, draft_state: DraftState) -> RecommendationOutput:
        """
        Given a draft state, return the full recommendation output.

        1. Analyze compositions
        2. Determine candidate ADCs (based on pool mode)
        3. Score each candidate
        4. Sort, pick top, generate explanations
        5. Return structured output
        """
        # 1. Analyze compositions
        analysis = self._analyzer.analyze(draft_state)

        # 2. Determine candidate pool
        candidates = self._get_candidates(draft_state)
        if not candidates:
            raise ValueError("No ADC candidates available for scoring.")

        # 3. Compute weights (with context adjustments)
        weights = self._compute_weights(draft_state)

        # 4. Score every candidate
        scored: list[tuple[str, float, ScoreBreakdown]] = []
        for adc_id in candidates:
            profile = self._data.get_adc_profile(adc_id)
            if profile is None:
                continue
            raw = self._compute_raw_scores(profile, draft_state, analysis)
            breakdown = self._build_breakdown(raw, weights, draft_state, adc_id)
            scored.append((adc_id, breakdown.pre_clamp_total, breakdown))

        # 5. Sort by total score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # 6. Build output
        top = scored[0]
        alternatives = scored[1:4]  # up to 3

        top_profile = self._data.get_adc_profile(top[0])
        top_pick = self._build_top_pick(top[0], top[2], top_profile, analysis, draft_state)

        alt_picks = []
        for alt_id, _, alt_breakdown in alternatives:
            alt_profile = self._data.get_adc_profile(alt_id)
            alt_pick = self._build_alternative(
                alt_id, alt_breakdown, alt_profile, top[0], top_profile, analysis
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

    def _score_ally_synergy(
        self, profile: AdcProfile, draft: DraftState, analysis: DraftAnalysis
    ) -> float:
        """
        How well does this ADC synergize with the allied team?
        Considers: support type synergy, frontline dependency, peel dependency.
        """
        if not draft.allies:
            return 50.0  # Neutral when no allies known

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

        return max(0.0, min(100.0, score))

    def _score_enemy_matchup(
        self, profile: AdcProfile, draft: DraftState, analysis: DraftAnalysis
    ) -> float:
        """
        How well does this ADC perform against the enemy team?
        Considers: anti-dive, anti-poke, anti-tank, worst-into penalties.
        """
        if not draft.enemies:
            return 50.0  # Neutral when no enemies known

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

        # Anti-poke
        if enemy.has_poke:
            score += (profile.anti_poke - 5) * 3

        # Worst-into penalties
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.worst_into:
                score -= 10

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
            if allied.has_frontline:
                score += max(0, profile.synergy_frontline_comp - 5) * 2
            if allied.has_peel:
                score += max(0, profile.synergy_peel_comp - 5) * 2.5

        return max(0.0, min(100.0, score))

    def _score_blind_pick_safety(
        self, profile: AdcProfile, draft: DraftState
    ) -> float:
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

    def _score_comp_gap_fill(
        self, profile: AdcProfile, analysis: DraftAnalysis
    ) -> float:
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
        return max(0.0, min(100.0, base - difficulty_penalty))

    def _score_scaling_fit(
        self, profile: AdcProfile, analysis: DraftAnalysis
    ) -> float:
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
            one_line_reason=reason,
            advantages_over_top_pick=advantages,
            disadvantages_vs_top_pick=disadvantages,
        )

    # ========================================================================
    # Explanation generators
    # ========================================================================

    def _generate_strengths(
        self, profile: AdcProfile, analysis: DraftAnalysis, draft: DraftState
    ) -> list[str]:
        """Generate human-readable strengths for the top pick in this draft."""
        strengths = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        if allied.has_frontline and profile.synergy_frontline_comp >= 7:
            strengths.append(
                f"Your team has strong frontline — {profile.display_name} excels "
                f"when protected (frontline synergy: {profile.synergy_frontline_comp}/10)"
            )

        if allied.has_peel and profile.synergy_peel_comp >= 7:
            strengths.append(
                f"Allied peel enables {profile.display_name} to free-hit safely "
                f"(peel synergy: {profile.synergy_peel_comp}/10)"
            )

        if allied.has_engage and profile.synergy_engage_support >= 7:
            strengths.append(
                f"Engage from allies creates kill opportunities for {profile.display_name}"
            )

        if enemy.has_tanks and profile.anti_tank >= 7:
            strengths.append(
                f"Strong tank-shredding capability vs enemy frontline "
                f"(anti-tank: {profile.anti_tank}/10)"
            )

        if not enemy.has_dive and profile.scaling >= 8:
            strengths.append(
                f"Enemy lacks dive threats — {profile.display_name} can scale safely "
                f"(scaling: {profile.scaling}/10)"
            )

        # Check for specific synergies with best_with
        for ally in draft.allies:
            if ally.id in profile.best_with:
                ally_name = self._data.get_champion_display_name(ally.id)
                strengths.append(
                    f"Strong synergy with allied {ally_name}"
                )

        # Comp gap fill
        if "physical_dps" in allied.missing:
            champ = self._data.get_champion(profile.id)
            if champ and champ.damage_type == DamageType.PHYSICAL:
                strengths.append(
                    "Fills team's need for physical damage"
                )

        if not strengths:
            strengths = profile.strengths[:3]

        return strengths[:5]

    def _generate_risks(
        self, profile: AdcProfile, analysis: DraftAnalysis, draft: DraftState
    ) -> list[str]:
        """Generate risk warnings for the top pick in this draft."""
        risks = []
        allied = analysis.allied_comp_profile
        enemy = analysis.enemy_comp_profile

        if enemy.has_dive and profile.anti_dive <= 5:
            risks.append(
                f"Enemy has dive threats and {profile.display_name}'s anti-dive is limited "
                f"({profile.anti_dive}/10)"
            )

        if enemy.has_burst and profile.self_peel <= 4:
            risks.append(
                f"Vulnerable to burst damage — limited self-peel ({profile.self_peel}/10)"
            )

        if not allied.has_frontline and profile.dependence_on_frontline >= 7:
            risks.append(
                f"{profile.display_name} is frontline-dependent ({profile.dependence_on_frontline}/10) "
                f"but your team lacks reliable frontline"
            )

        if not allied.has_peel and profile.dependence_on_peel >= 7:
            risks.append(
                f"No peel available and {profile.display_name} needs it "
                f"(peel dependence: {profile.dependence_on_peel}/10)"
            )

        if profile.lane_priority <= 4:
            risks.append(
                f"Weak lane phase — may fall behind early "
                f"(lane priority: {profile.lane_priority}/10)"
            )

        # Worst-into warnings
        for enemy_champ in draft.enemies:
            if enemy_champ.id in profile.worst_into:
                enemy_name = self._data.get_champion_display_name(enemy_champ.id)
                risks.append(
                    f"Poor matchup into {enemy_name} (listed in worst-into)"
                )

        if not risks:
            risks = profile.weaknesses[:2]

        return risks[:4]

    def _generate_play_pattern(
        self, profile: AdcProfile, analysis: DraftAnalysis
    ) -> str:
        """Generate the enabled play pattern description."""
        shape = analysis.allied_comp_profile.teamfight_shape

        patterns = {
            TeamfightShape.FRONT_TO_BACK: (
                f"Front-to-back teamfighting. Your frontline engages and peels while "
                f"{profile.display_name} deals sustained damage from the backline. "
                f"Power spikes at {', '.join(profile.power_spikes)}."
            ),
            TeamfightShape.DIVE: (
                f"Aggressive dive composition. {profile.display_name} follows up on team's dive "
                f"or plays split-map while your team pressures. "
                f"Look for skirmishes and fights around objectives."
            ),
            TeamfightShape.POKE_SIEGE: (
                f"Poke and siege composition. {profile.display_name} contributes to tower pressure "
                f"and poke damage. Avoid hard engage and force objectives with range advantage."
            ),
            TeamfightShape.PICK: (
                f"Pick composition. {profile.display_name} follows up on catches and plays "
                f"around vision control. Group for objectives and punish enemy rotations."
            ),
            TeamfightShape.SPLIT: (
                f"Split-push composition. {profile.display_name} holds mid while split-pusher "
                f"draws pressure. Be ready to take towers or objectives when numbers advantage appears."
            ),
            TeamfightShape.MIXED: (
                f"Flexible composition. {profile.display_name} adapts to team's plan — "
                f"teamfight when grouped, skirmish when split. "
                f"Power spikes at {', '.join(profile.power_spikes)}."
            ),
        }

        base = patterns.get(shape, patterns[TeamfightShape.MIXED])

        # Add draft notes if they add value
        if profile.draft_notes:
            base += f" Key consideration: {profile.draft_notes[:150]}"

        return base

    def _generate_one_liner(
        self, alt: AdcProfile, top: AdcProfile, breakdown: ScoreBreakdown
    ) -> str:
        """Generate a one-line summary of why this alternative ranks lower."""
        raw = breakdown.raw
        # Find the factor where this ADC is strongest
        raw_dict = raw.model_dump()
        best_factor = max(raw_dict, key=raw_dict.get)
        factor_names = {
            "ally_synergy": "ally synergy",
            "enemy_matchup": "matchup strength",
            "blind_pick_safety": "blind pick safety",
            "comp_gap_fill": "composition fit",
            "solo_queue_reliability": "solo queue reliability",
            "scaling_fit": "scaling alignment",
        }
        best_name = factor_names.get(best_factor, best_factor)
        return (
            f"Strong {best_name} ({raw_dict[best_factor]:.0f}/100), "
            f"but scores lower overall than {top.display_name}."
        )

    def _compare_advantages(
        self, alt: AdcProfile, top: AdcProfile
    ) -> list[str]:
        """What does the alternative do better than the top pick?"""
        advantages = []

        if alt.mobility > top.mobility + 1:
            advantages.append(f"Higher mobility ({alt.mobility} vs {top.mobility})")
        if alt.self_peel > top.self_peel + 1:
            advantages.append(f"Better self-peel ({alt.self_peel} vs {top.self_peel})")
        if alt.anti_dive > top.anti_dive + 1:
            advantages.append(f"Better anti-dive ({alt.anti_dive} vs {top.anti_dive})")
        if alt.blind_pick_safety > top.blind_pick_safety + 1:
            advantages.append(f"Safer blind pick ({alt.blind_pick_safety} vs {top.blind_pick_safety})")
        if alt.lane_priority > top.lane_priority + 1:
            advantages.append(f"Stronger lane phase ({alt.lane_priority} vs {top.lane_priority})")
        if alt.scaling > top.scaling + 1:
            advantages.append(f"Better scaling ({alt.scaling} vs {top.scaling})")
        if alt.execution_difficulty < top.execution_difficulty - 1:
            advantages.append(f"Easier to execute ({alt.execution_difficulty} vs {top.execution_difficulty})")
        if alt.skirmish_power > top.skirmish_power + 1:
            advantages.append(f"Stronger in skirmishes ({alt.skirmish_power} vs {top.skirmish_power})")

        if not advantages:
            advantages.append("More versatile in certain team compositions")

        return advantages[:3]

    def _compare_disadvantages(
        self, alt: AdcProfile, top: AdcProfile
    ) -> list[str]:
        """What does the alternative do worse than the top pick?"""
        disadvantages = []

        if alt.scaling < top.scaling - 1:
            disadvantages.append(f"Lower scaling ({alt.scaling} vs {top.scaling})")
        if alt.teamfight_consistency < top.teamfight_consistency - 1:
            disadvantages.append(f"Less consistent in teamfights ({alt.teamfight_consistency} vs {top.teamfight_consistency})")
        if alt.anti_tank < top.anti_tank - 1:
            disadvantages.append(f"Weaker vs tanks ({alt.anti_tank} vs {top.anti_tank})")
        if alt.objective_dps < top.objective_dps - 1:
            disadvantages.append(f"Lower objective DPS ({alt.objective_dps} vs {top.objective_dps})")
        if alt.solo_queue_stability < top.solo_queue_stability - 1:
            disadvantages.append(f"Less reliable in solo queue ({alt.solo_queue_stability} vs {top.solo_queue_stability})")
        if alt.self_peel < top.self_peel - 1:
            disadvantages.append(f"Less self-peel ({alt.self_peel} vs {top.self_peel})")

        if not disadvantages:
            disadvantages.append("Slightly lower overall score in this specific draft context")

        return disadvantages[:3]
