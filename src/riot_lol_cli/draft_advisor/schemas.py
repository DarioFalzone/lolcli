"""
Pydantic schemas for Draft Advisor.
All domain model contracts live here as the single source of truth.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# ENUMS
# ============================================================================

class GameplayRole(str, Enum):
    TOP = "Top"
    JUNGLE = "Jungle"
    MID = "Mid"
    BOT = "Bot"
    SUPPORT = "Support"


class CombatClass(str, Enum):
    FIGHTER = "Fighter"
    TANK = "Tank"
    MAGE = "Mage"
    ASSASSIN = "Assassin"
    MARKSMAN = "Marksman"
    CONTROLLER = "Controller"
    SPECIALIST = "Specialist"


class Subclass(str, Enum):
    # Fighter
    JUGGERNAUT = "Juggernaut"
    DIVER = "Diver"
    # Tank
    VANGUARD = "Vanguard"
    WARDEN = "Warden"
    # Mage
    BURST_MAGE = "Burst"
    BATTLEMAGE = "Battlemage"
    ARTILLERY = "Artillery"
    # Assassin
    BURST_ASSASSIN = "BurstAssassin"
    SKIRMISHER = "Skirmisher"
    # Controller
    ENCHANTER = "Enchanter"
    CATCHER = "Catcher"
    # Cross-class / unique
    SPECIALIST = "Specialist"


class DamageType(str, Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    MIXED = "mixed"


class RangeType(str, Enum):
    MELEE = "melee"
    RANGED = "ranged"


class PickPosition(str, Enum):
    BLIND = "blind"
    EARLY = "early"
    LATE = "late"


class InformationLevel(str, Enum):
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


class QueueType(str, Enum):
    RANKED_SOLO = "ranked_solo"
    RANKED_FLEX = "ranked_flex"
    NORMAL = "normal"
    CLASH = "clash"


class PoolMode(str, Enum):
    UNRESTRICTED = "unrestricted"
    POOL_PREFERRED = "pool_preferred"
    POOL_ONLY = "pool_only"


class BotLaneImpact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriorityCategory(str, Enum):
    ENGAGE_SUPPORT = "engage_support"
    ENCHANTER_SUPPORT = "enchanter_support"
    MAGE_SUPPORT = "mage_support"
    CATCHER_SUPPORT = "catcher_support"
    DIVE_ASSASSIN = "dive_assassin"
    DIVE_FIGHTER = "dive_fighter"
    TANK_FRONTLINE = "tank_frontline"
    POKE_MAGE = "poke_mage"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TeamfightShape(str, Enum):
    FRONT_TO_BACK = "front_to_back"
    DIVE = "dive"
    POKE_SIEGE = "poke_siege"
    PICK = "pick"
    SPLIT = "split"
    MIXED = "mixed"


class ThreatLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


# ============================================================================
# SCHEMA 1: Champion Base (Tier 1 — all champions)
# ============================================================================

class ChampionTags(BaseModel):
    engage: int = Field(ge=0, le=10)
    disengage: int = Field(ge=0, le=10)
    peel: int = Field(ge=0, le=10)
    poke: int = Field(ge=0, le=10)
    burst: int = Field(ge=0, le=10)
    sustained_dps: int = Field(ge=0, le=10)
    cc: int = Field(ge=0, le=10)
    mobility: int = Field(ge=0, le=10)
    tankiness: int = Field(ge=0, le=10)
    utility: int = Field(ge=0, le=10)
    pick_potential: int = Field(ge=0, le=10)
    waveclear: int = Field(ge=0, le=10)
    scaling: int = Field(ge=0, le=10)
    early_power: int = Field(ge=0, le=10)


class ChampionBase(BaseModel):
    id: str                                     # Data Dragon canonical key
    display_name: str                           # Human-readable name
    title: str = ""
    primary_role: GameplayRole
    off_roles: list[GameplayRole] = []
    combat_class: CombatClass = Field(alias="class")
    subclass: Subclass | None = None
    damage_type: DamageType
    range_type: RangeType
    tags: ChampionTags

    model_config = {"populate_by_name": True}


class DataManifestFile(BaseModel):
    schema_version: str
    live_patch_label: str
    static_data_version: str
    last_verified_at: str
    validator_status: str


class ChampionBaseFile(BaseModel):
    schema_version: str
    last_updated: str
    source: str
    champions: dict[str, ChampionBase]


# ============================================================================
# SCHEMA 2: ADC Profile (Tier 2 — deep ADC data)
# ============================================================================

class AdcProfile(BaseModel):
    id: str
    display_name: str

    # Core identity (1-10)
    effective_range: int = Field(ge=1, le=10)
    mobility: int = Field(ge=1, le=10)
    self_peel: int = Field(ge=1, le=10)
    execution_difficulty: int = Field(ge=1, le=10)

    # Draft ratings (1-10)
    blind_pick_safety: int = Field(ge=1, le=10)
    lane_priority: int = Field(ge=1, le=10)
    scaling: int = Field(ge=1, le=10)
    anti_tank: int = Field(ge=1, le=10)
    anti_dive: int = Field(ge=1, le=10)
    anti_poke: int = Field(ge=1, le=10)
    teamfight_consistency: int = Field(ge=1, le=10)
    skirmish_power: int = Field(ge=1, le=10)
    objective_dps: int = Field(ge=1, le=10)
    siege_value: int = Field(ge=1, le=10)
    pick_potential: int = Field(ge=1, le=10)

    # Synergy ratings (1-10)
    synergy_engage_support: int = Field(ge=1, le=10)
    synergy_enchanter_support: int = Field(ge=1, le=10)
    synergy_mage_support: int = Field(ge=1, le=10)
    synergy_frontline_comp: int = Field(ge=1, le=10)
    synergy_peel_comp: int = Field(ge=1, le=10)

    # Dependency (1-10, higher = more dependent)
    dependence_on_frontline: int = Field(ge=1, le=10)
    dependence_on_peel: int = Field(ge=1, le=10)
    dependence_on_lane_support: int = Field(ge=1, le=10)

    # Solo queue
    solo_queue_stability: int = Field(ge=1, le=10)
    punish_immobile: int = Field(ge=1, le=10)
    punish_short_range: int = Field(ge=1, le=10)

    # Descriptive
    power_spikes: list[str]
    strengths: list[str]
    weaknesses: list[str]
    best_with: list[str]       # Champion IDs
    worst_into: list[str]      # Champion IDs
    draft_notes: str


class AdcProfilesFile(BaseModel):
    schema_version: str
    patch: str
    last_updated: str
    source: str
    profiles: dict[str, AdcProfile]


# ============================================================================
# SCHEMA 3: Priority Profile (Tier 3 — draft-impact non-ADCs)
# ============================================================================

class PriorityProfile(BaseModel):
    id: str
    display_name: str
    category: PriorityCategory
    bot_lane_impact: BotLaneImpact
    adc_threat_level: int = Field(ge=0, le=10)
    adc_synergy_level: int = Field(ge=0, le=10)
    adc_interaction_notes: str


class PriorityProfilesFile(BaseModel):
    schema_version: str
    patch: str
    last_updated: str
    source: str
    profiles: dict[str, PriorityProfile]


# ============================================================================
# SCHEMA 4: Draft State (Engine Input)
# ============================================================================

class DraftChampion(BaseModel):
    id: str
    role: GameplayRole | None = None


class DraftContext(BaseModel):
    pick_position: PickPosition = PickPosition.BLIND
    information_level: InformationLevel = InformationLevel.NONE
    queue_type: QueueType = QueueType.RANKED_SOLO


class UserPool(BaseModel):
    mode: PoolMode = PoolMode.UNRESTRICTED
    champions: list[str] = []
    comfort: dict[str, int] = {}     # champion_id -> 1-10

    @field_validator("comfort")
    @classmethod
    def validate_comfort(cls, v: dict[str, int]) -> dict[str, int]:
        for champ, score in v.items():
            if not 1 <= score <= 10:
                raise ValueError(f"Comfort score for {champ} must be 1-10, got {score}")
        return v


class DraftState(BaseModel):
    allies: list[DraftChampion] = Field(default_factory=list, max_length=4)
    enemies: list[DraftChampion] = Field(default_factory=list, max_length=5)
    bans: list[str] = Field(default_factory=list)
    context: DraftContext = Field(default_factory=DraftContext)
    user_pool: UserPool = Field(default_factory=UserPool)


# ============================================================================
# SCHEMA 5: Recommendation Output (Engine Output)
# ============================================================================

class RawScores(BaseModel):
    ally_synergy: float = Field(ge=0, le=100)
    enemy_matchup: float = Field(ge=0, le=100)
    blind_pick_safety: float = Field(ge=0, le=100)
    comp_gap_fill: float = Field(ge=0, le=100)
    solo_queue_reliability: float = Field(ge=0, le=100)
    scaling_fit: float = Field(ge=0, le=100)


class WeightedScores(BaseModel):
    ally_synergy: float
    enemy_matchup: float
    blind_pick_safety: float
    comp_gap_fill: float
    solo_queue_reliability: float
    scaling_fit: float


class ScoreBreakdown(BaseModel):
    raw: RawScores
    weighted: WeightedScores
    comfort_bonus: float = 0.0
    weighted_sum: float
    pre_clamp_total: float
    weights_used: dict[str, float]


class RecommendedPick(BaseModel):
    id: str
    display_name: str
    total_score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    strengths_in_this_draft: list[str]
    risks_in_this_draft: list[str]
    not_recommended_when: list[str]
    enabled_play_pattern: str


class AlternativePick(BaseModel):
    id: str
    display_name: str
    total_score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    one_line_reason: str
    advantages_over_top_pick: list[str]
    disadvantages_vs_top_pick: list[str]


class AlliedCompProfile(BaseModel):
    has_frontline: bool = False
    has_engage: bool = False
    has_peel: bool = False
    has_poke: bool = False
    primary_damage_existing: DamageType | None = None
    teamfight_shape: TeamfightShape = TeamfightShape.MIXED
    missing: list[str] = Field(default_factory=list)


class EnemyCompProfile(BaseModel):
    has_dive: bool = False
    has_burst: bool = False
    has_tanks: bool = False
    has_poke: bool = False
    threat_level_to_adc: ThreatLevel = ThreatLevel.MEDIUM
    primary_threat: str = ""


class DraftAnalysis(BaseModel):
    allied_comp_profile: AlliedCompProfile
    enemy_comp_profile: EnemyCompProfile
    information_quality: InformationLevel
    confidence: Confidence


class RecommendationOutput(BaseModel):
    timestamp: str
    draft_state_hash: str
    mode: PoolMode
    top_pick: RecommendedPick
    alternatives: list[AlternativePick] = Field(default_factory=list, max_length=3)
    draft_analysis: DraftAnalysis


# ============================================================================
# SCHEMA 6: Scoring Weights Config
# ============================================================================

class ScoringWeightsConfig(BaseModel):
    schema_version: str
    last_updated: str
    base_weights: dict[str, float]
    comfort_bonus_weight: float
    comfort_score_range: list[int]
    comfort_bonus_max_points: int
    context_adjustments: dict[str, dict[str, float]]
    normalization_rule: str

    @field_validator("base_weights")
    @classmethod
    def validate_weights_sum(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Base weights must sum to 1.0, got {total}")
        return v
