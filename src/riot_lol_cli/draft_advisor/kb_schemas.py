"""
Pydantic schemas for the Knowledge Base system.

Covers: research note frontmatter, source manifest entries,
golden draft evaluation cases, patch overrides, comp archetypes,
and matchup rules.
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# PATCH FORMAT
# ============================================================================

PATCH_PATTERN = re.compile(r"^\d+\.\d+$")


def validate_patch(v: str) -> str:
    """Validate patch format: 'X.Y' or '*' for patch-agnostic."""
    if v == "*":
        return v
    if not PATCH_PATTERN.match(v):
        raise ValueError(f"Patch must match 'X.Y' or '*', got '{v}'")
    return v


# ============================================================================
# ENUMS
# ============================================================================

class NoteType(str, Enum):
    ADC_CHAMPION_NOTE = "adc_champion_note"
    SUPPORT_SYNERGY_NOTE = "support_synergy_note"
    THREAT_NOTE = "threat_note"
    ARCHETYPE_NOTE = "archetype_note"
    MATCHUP_NOTE = "matchup_note"
    PATCH_SUMMARY = "patch_summary"
    HEURISTIC_NOTE = "heuristic_note"
    META_SNAPSHOT = "meta_snapshot"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPECULATIVE = "speculative"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    STALE = "stale"
    SUPERSEDED = "superseded"


class SourceType(str, Enum):
    EXPERT_ANALYSIS = "expert_analysis"
    RIOT_PATCH_NOTES = "riot_patch_notes"
    WEB_RESEARCH = "web_research"
    PDF_EXTRACTION = "pdf_extraction"
    PERSONAL_NOTE = "personal_note"
    COMMUNITY_GUIDE = "community_guide"
    PRO_PLAY_ANALYSIS = "pro_play_analysis"


class TrustLevel(str, Enum):
    AUTHORITATIVE = "authoritative"
    EXPERT = "expert"
    COMMUNITY = "community"
    SPECULATIVE = "speculative"


# ============================================================================
# RESEARCH NOTE FRONTMATTER
# ============================================================================

class ResearchNoteMeta(BaseModel):
    """Parsed YAML frontmatter from a research markdown note."""

    schema_version: str = "1.0"
    kb_version: str = "1"
    id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9\-]*$")
    title: str
    type: NoteType
    domain: str = "draft_advisor"
    patch_scope: str = "*"
    live_patch_label: Optional[str] = None
    static_data_version: Optional[str] = None
    source_type: SourceType
    source_url: str = ""
    source_file: str = ""
    created_at: str
    last_reviewed_at: str
    review_status: ReviewStatus
    confidence: ConfidenceLevel
    champions: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    derived_from: List[str] = Field(default_factory=list)
    supersedes: List[str] = Field(default_factory=list)
    superseded_by: List[str] = Field(default_factory=list)

    @field_validator("patch_scope")
    @classmethod
    def check_patch_scope(cls, v: str) -> str:
        return validate_patch(v)

    @field_validator("id")
    @classmethod
    def check_id_prefix(cls, v: str) -> str:
        # ID must start with a valid note type prefix
        valid_prefixes = ("adc-", "syn-", "thr-", "arch-", "mu-", "patch-", "heur-", "meta-")
        if not any(v.startswith(p) for p in valid_prefixes):
            raise ValueError(
                f"Note ID '{v}' must start with one of: {', '.join(valid_prefixes)}"
            )
        return v


# ============================================================================
# SOURCE MANIFEST
# ============================================================================

class SourceManifestEntry(BaseModel):
    """A single entry in the source manifest."""

    source_id: str
    file_path: Optional[str] = None
    source_type: str
    origin_url: Optional[str] = None
    capture_date: str
    patch_scope: str = "*"
    live_patch_label: Optional[str] = None
    trust_level: TrustLevel
    review_status: ReviewStatus
    linked_research_notes: List[str] = Field(default_factory=list)
    linked_structured_updates: List[str] = Field(default_factory=list)
    notes: str = ""

    @field_validator("patch_scope")
    @classmethod
    def check_patch_scope(cls, v: str) -> str:
        return validate_patch(v)


class SourceManifest(BaseModel):
    """Full source manifest file."""

    schema_version: str
    last_updated: str
    sources: List[SourceManifestEntry]


# ============================================================================
# PATCH OVERRIDES
# ============================================================================

class PatchOverride(BaseModel):
    """A single patch-specific score override."""

    champion_id: str
    field: str
    original_value: int
    override_value: int
    reason: str
    source_research_note: str = ""
    applied_at: str
    expires_at_patch_label: str

    @field_validator("expires_at_patch_label")
    @classmethod
    def check_patch_label(cls, v: str) -> str:
        return validate_patch(v)


class PatchOverridesFile(BaseModel):
    """Patch overrides file."""

    schema_version: str
    live_patch_label: str
    last_updated: str
    description: str = ""
    overrides: List[PatchOverride] = Field(default_factory=list)

    @field_validator("live_patch_label")
    @classmethod
    def check_patch_label(cls, v: str) -> str:
        return validate_patch(v)


# ============================================================================
# COMP ARCHETYPES
# ============================================================================

class ArchetypeDetectionRules(BaseModel):
    min_frontline: Optional[int] = None
    min_peel_sources: Optional[int] = None
    min_dive_threats: Optional[int] = None
    high_team_mobility: Optional[bool] = None
    min_poke_sources: Optional[int] = None
    has_waveclear: Optional[bool] = None
    min_pick_potential_sources: Optional[int] = None
    has_cc_chain: Optional[bool] = None
    has_split_pusher: Optional[bool] = None
    split_pusher_roles: List[str] = Field(default_factory=list)
    excluded_shapes: List[str] = Field(default_factory=list)


class ArchetypeAdcPreferences(BaseModel):
    boost_traits: List[str] = Field(default_factory=list)
    penalize_traits: List[str] = Field(default_factory=list)
    preferred_adcs: List[str] = Field(default_factory=list)
    avoid_adcs: List[str] = Field(default_factory=list)


class CompArchetype(BaseModel):
    id: str
    display_name: str
    description: str
    detection_rules: ArchetypeDetectionRules
    adc_preferences: ArchetypeAdcPreferences
    weight_adjustments: Dict[str, float] = Field(default_factory=dict)
    research_notes: List[str] = Field(default_factory=list)


class CompArchetypesFile(BaseModel):
    schema_version: str
    last_updated: str
    description: str = ""
    archetypes: Dict[str, CompArchetype]


# ============================================================================
# MATCHUP RULES
# ============================================================================

class MatchupRule(BaseModel):
    """A specific scoring rule triggered by champion interactions."""

    rule_id: str
    description: str
    trigger: Dict[str, object]  # e.g. {"enemy_contains": "Zed", "adc_trait_below": {"self_peel": 4}}
    score_adjustment: Dict[str, float]  # e.g. {"enemy_matchup": -15}
    source_research_note: str = ""


class MatchupRulesFile(BaseModel):
    schema_version: str
    last_updated: str
    description: str = ""
    rules: List[MatchupRule] = Field(default_factory=list)


# ============================================================================
# GOLDEN DRAFT CASES
# ============================================================================

class GoldenDraftState(BaseModel):
    """A draft state for evaluation."""

    allies: List[Dict[str, str]] = Field(default_factory=list)
    enemies: List[Dict[str, str]] = Field(default_factory=list)
    bans: List[str] = Field(default_factory=list)
    context: Dict[str, str] = Field(default_factory=dict)
    user_pool: Optional[Dict[str, object]] = None


class GoldenAssertions(BaseModel):
    """Assertions about expected recommendation output."""

    top_pick_must_be_one_of: List[str] = Field(default_factory=list)
    top_3_must_include_any_of: List[str] = Field(default_factory=list)
    must_not_recommend_as_top: List[str] = Field(default_factory=list)
    top_pick_score_min: Optional[float] = None
    total_candidates_max: Optional[int] = None


class GoldenDraftCase(BaseModel):
    """A single golden draft evaluation case."""

    case_id: str
    description: str
    draft_state: GoldenDraftState
    assertions: GoldenAssertions


class GoldenDraftsFile(BaseModel):
    """Golden drafts evaluation file."""

    schema_version: str
    last_updated: str
    description: str = ""
    cases: List[GoldenDraftCase]
