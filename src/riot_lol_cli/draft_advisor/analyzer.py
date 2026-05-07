"""
Analizador de composicion.

Toma el estado del draft y produce perfiles estructurados que describen:
- que tiene tu equipo (frontline, engage, peel, poke, tipo de daño)
- que le falta a tu equipo (gaps que el ADC puede cubrir)
- que amenazas presenta la composicion enemiga contra tu ADC
- que forma de teamfight habilita tu composicion
"""

from __future__ import annotations

from .champion_data import ChampionDataService
from .schemas import (
    AlliedCompProfile,
    Confidence,
    DamageType,
    DraftAnalysis,
    DraftChampion,
    DraftState,
    EnemyCompProfile,
    TeamfightShape,
    ThreatLevel,
)

# ============================================================================
# Thresholds for boolean flags
# ============================================================================

_FRONTLINE_THRESHOLD = 7  # tankiness tag >= 7 counts as frontline
_ENGAGE_THRESHOLD = 7  # engage tag >= 7 counts as engage
_PEEL_THRESHOLD = 7  # peel tag >= 7 counts as peel
_POKE_THRESHOLD = 7  # poke tag >= 7 counts as poke
_DIVE_THRESHOLD = 7  # engage + mobility >= 14 counts as dive threat
_BURST_THRESHOLD = 8  # burst tag >= 8 counts as burst threat
_TANK_THRESHOLD = 7  # tankiness >= 7 counts as tank presence


class CompositionAnalyzer:
    """Analyzes team compositions from the draft state."""

    def __init__(self, data_service: ChampionDataService):
        self._data = data_service

    def analyze(self, draft_state: DraftState) -> DraftAnalysis:
        """
        Produce a full DraftAnalysis from the current draft state.

        Returns:
            DraftAnalysis with allied_comp_profile, enemy_comp_profile,
            information_quality, and confidence.
        """
        allied_profile = self._analyze_allies(draft_state.allies)
        enemy_profile = self._analyze_enemies(draft_state.enemies)
        info_quality = draft_state.context.information_level
        confidence = self._compute_confidence(draft_state)

        return DraftAnalysis(
            allied_comp_profile=allied_profile,
            enemy_comp_profile=enemy_profile,
            information_quality=info_quality,
            confidence=confidence,
        )

    # ========================================================================
    # Allied composition analysis
    # ========================================================================

    def _analyze_allies(self, allies: list[DraftChampion]) -> AlliedCompProfile:
        """Analyze what the allied team brings and what's missing."""
        if not allies:
            return AlliedCompProfile(missing=["frontline", "engage", "peel", "poke", "physical_dps", "magic_dps"])

        has_frontline = False
        has_engage = False
        has_peel = False
        has_poke = False
        physical_damage_count = 0
        magic_damage_count = 0
        engage_score_sum = 0
        peel_score_sum = 0
        dive_score_sum = 0

        for ally in allies:
            tags = self._data.get_champion_tags(ally.id)
            champ = self._data.get_champion(ally.id)
            if tags is None or champ is None:
                continue

            if tags["tankiness"] >= _FRONTLINE_THRESHOLD:
                has_frontline = True
            if tags["engage"] >= _ENGAGE_THRESHOLD:
                has_engage = True
            if tags["peel"] >= _PEEL_THRESHOLD:
                has_peel = True
            if tags["poke"] >= _POKE_THRESHOLD:
                has_poke = True

            engage_score_sum += tags["engage"]
            peel_score_sum += tags["peel"]
            dive_score_sum += tags["engage"] + tags["mobility"]

            if champ.damage_type == DamageType.PHYSICAL:
                physical_damage_count += 1
            elif champ.damage_type == DamageType.MAGIC:
                magic_damage_count += 1
            else:  # mixed
                physical_damage_count += 0.5
                magic_damage_count += 0.5

        # Determine primary damage type
        if physical_damage_count > magic_damage_count:
            primary_damage = DamageType.PHYSICAL
        elif magic_damage_count > physical_damage_count:
            primary_damage = DamageType.MAGIC
        else:
            primary_damage = DamageType.MIXED

        # Determine teamfight shape
        teamfight_shape = self._infer_teamfight_shape(
            has_frontline, has_engage, has_peel, has_poke, engage_score_sum, peel_score_sum, dive_score_sum, len(allies)
        )

        # Determine what's missing
        missing = []
        if not has_frontline:
            missing.append("frontline")
        if not has_engage:
            missing.append("engage")
        if not has_peel:
            missing.append("peel")
        if not has_poke:
            missing.append("poke")
        if physical_damage_count < 1:
            missing.append("physical_dps")
        if magic_damage_count < 1:
            missing.append("magic_dps")
        # ADC role itself is always missing (that's what we're recommending)
        # Only add objective_damage if no marksman is already in allies
        has_marksman = any(
            self._data.get_champion(a.id) and self._data.get_champion(a.id).combat_class.value == "Marksman"
            for a in allies
        )
        if not has_marksman:
            missing.append("objective_damage")

        return AlliedCompProfile(
            has_frontline=has_frontline,
            has_engage=has_engage,
            has_peel=has_peel,
            has_poke=has_poke,
            primary_damage_existing=primary_damage,
            teamfight_shape=teamfight_shape,
            missing=missing,
        )

    def _infer_teamfight_shape(
        self,
        has_frontline: bool,
        has_engage: bool,
        has_peel: bool,
        has_poke: bool,
        engage_sum: int,
        peel_sum: int,
        dive_sum: int,
        ally_count: int,
    ) -> TeamfightShape:
        """Infer the likely teamfight pattern from ally composition."""
        if ally_count == 0:
            return TeamfightShape.MIXED

        avg_engage = engage_sum / ally_count
        avg_peel = peel_sum / ally_count
        avg_dive = dive_sum / ally_count

        if has_frontline and has_peel and avg_peel > avg_engage:
            return TeamfightShape.FRONT_TO_BACK
        if has_engage and avg_dive >= 12:
            return TeamfightShape.DIVE
        if has_poke and not has_engage:
            return TeamfightShape.POKE_SIEGE
        if has_engage and not has_frontline:
            return TeamfightShape.PICK
        if has_frontline and has_engage:
            return TeamfightShape.FRONT_TO_BACK

        return TeamfightShape.MIXED

    # ========================================================================
    # Enemy composition analysis
    # ========================================================================

    def _analyze_enemies(self, enemies: list[DraftChampion]) -> EnemyCompProfile:
        """Analizar amenazas enemigas contra el ADC."""
        if not enemies:
            return EnemyCompProfile(
                threat_level_to_adc=ThreatLevel.MEDIUM,
                primary_threat="Unknown (no enemies visible)",
            )

        has_dive = False
        has_burst = False
        has_tanks = False
        has_poke = False

        threats: list[tuple[str, int]] = []  # (champion_display_name, threat_score)

        for enemy in enemies:
            tags = self._data.get_champion_tags(enemy.id)
            champ = self._data.get_champion(enemy.id)
            if tags is None or champ is None:
                continue

            # Dive detection: engage + mobility
            if tags["engage"] + tags["mobility"] >= _DIVE_THRESHOLD * 2:
                has_dive = True
            if tags["burst"] >= _BURST_THRESHOLD:
                has_burst = True
            if tags["tankiness"] >= _TANK_THRESHOLD:
                has_tanks = True
            if tags["poke"] >= _POKE_THRESHOLD:
                has_poke = True

            # Compute per-champion threat to ADC
            threat_score = self._data.get_threat_level(enemy.id)
            threats.append((champ.display_name, threat_score))

        # Overall ADC threat level
        if not threats:
            overall_threat = ThreatLevel.MEDIUM
        else:
            max_threat = max(t[1] for t in threats)
            avg_threat = sum(t[1] for t in threats) / len(threats)
            combined = max_threat * 0.6 + avg_threat * 0.4

            if combined >= 8:
                overall_threat = ThreatLevel.CRITICAL
            elif combined >= 6:
                overall_threat = ThreatLevel.HIGH
            elif combined >= 4:
                overall_threat = ThreatLevel.MEDIUM
            elif combined >= 2:
                overall_threat = ThreatLevel.LOW
            else:
                overall_threat = ThreatLevel.MINIMAL

        # Primary threat
        if threats:
            primary = max(threats, key=lambda t: t[1])
            primary_threat_str = f"{primary[0]} (threat: {primary[1]}/10)"
        else:
            primary_threat_str = "None identified"

        return EnemyCompProfile(
            has_dive=has_dive,
            has_burst=has_burst,
            has_tanks=has_tanks,
            has_poke=has_poke,
            threat_level_to_adc=overall_threat,
            primary_threat=primary_threat_str,
        )

    # ========================================================================
    # Confidence estimation
    # ========================================================================

    def _compute_confidence(self, draft_state: DraftState) -> Confidence:
        """
        Estimate confidence in the recommendation based on information available.
        More allies + enemies = higher confidence.
        """
        ally_count = len(draft_state.allies)
        enemy_count = len(draft_state.enemies)
        total_info = ally_count + enemy_count

        if total_info >= 7:
            return Confidence.HIGH
        elif total_info >= 4:
            return Confidence.MEDIUM
        else:
            return Confidence.LOW
