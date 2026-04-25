from __future__ import annotations

from typing import TYPE_CHECKING

from .schemas import DamageType, TeamfightShape

if TYPE_CHECKING:
    from .champion_data import ChampionDataService
    from .schemas import AdcProfile, AlliedCompProfile


def score_comp_gap_fill(profile: AdcProfile, allied: AlliedCompProfile, data_service: ChampionDataService) -> float:
    """Reglas puras para evaluar cómo un ADC llena los gaps del equipo."""
    score = 50.0
    missing = allied.missing
    base_champ = data_service.get_champion(profile.id)

    if "physical_dps" in missing and base_champ and base_champ.damage_type == DamageType.PHYSICAL:
        score += 10

    if "frontline" in missing:
        score += (profile.self_peel - 5) * 1.5

    if "engage" in missing and base_champ and base_champ.tags.engage >= 5:
        score += (base_champ.tags.engage - 4) * 3

    if "peel" in missing:
        score += (profile.self_peel - 5) * 1.5

    if "poke" in missing and base_champ and base_champ.tags.poke >= 6:
        score += (base_champ.tags.poke - 5) * 3

    if "objective_damage" in missing:
        score += (profile.objective_dps - 5) * 3

    teamfight_shape_modifiers = {
        TeamfightShape.FRONT_TO_BACK: (profile.teamfight_consistency - 5) * 3,
        TeamfightShape.DIVE: (profile.skirmish_power - 5) * 3,
        TeamfightShape.POKE_SIEGE: (profile.siege_value - 5) * 3,
        TeamfightShape.PICK: (profile.pick_potential - 5) * 3,
    }
    score += teamfight_shape_modifiers.get(allied.teamfight_shape, 0.0)
    return max(0.0, min(100.0, score))


def score_scaling_fit(profile: AdcProfile, allied: AlliedCompProfile) -> float:
    """Reglas puras para alinear escalado del ADC con el plan de la comp."""
    score = 50.0

    if allied.has_frontline and allied.has_engage:
        score += (profile.scaling - 5) * 4

    if not allied.has_frontline:
        score += (profile.self_peel - 5) * 2
        score += (profile.mobility - 5) * 2
        score -= profile.scaling - 5

    if allied.teamfight_shape == TeamfightShape.DIVE:
        score += (profile.skirmish_power - 5) * 3
        score -= (profile.dependence_on_frontline - 5) * 2

    return max(0.0, min(100.0, score))
