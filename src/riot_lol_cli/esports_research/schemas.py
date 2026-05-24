"""Pydantic V2 schemas for Esports Research.

The models intentionally mirror table-like records so V0 JSON storage can move
to SQLite/Postgres later without changing the public API shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    COMMUNITY_API = "community_api"
    COMMUNITY_CSV = "community_csv"
    COMMUNITY_HTML = "community_html"
    OFFICIAL_CDN = "official_cdn"
    OFFICIAL_API = "official_api"
    OFFICIAL_COMMERCIAL = "official_commercial"
    OFFICIAL_WEB = "official_web"
    OFFICIAL_LOCAL = "official_local"
    COMMERCIAL_API = "commercial_api"


class SourceStatus(str, Enum):
    ACTIVE = "active"
    STUB = "stub"
    PLANNED = "planned"
    RESTRICTED = "restricted"
    GAP = "gap"


class Source(BaseModel, extra="allow"):
    id: str
    name: str
    base_url: str
    source_type: SourceType
    status: SourceStatus = SourceStatus.PLANNED
    region_focus: list[str] = Field(default_factory=list)
    requires_browser: bool = False
    has_public_api: bool = False
    scrape_priority: int = 50
    min_delay_seconds: float = 0.0
    compliance_notes: str = ""
    notes: str = ""
    created_at: str
    updated_at: str


class Tournament(BaseModel, extra="allow"):
    tournament_id: str
    name: str
    region: str
    league: str
    format: str
    start_date: str
    end_date: str | None = None
    source_origin: str


class Match(BaseModel, extra="allow"):
    match_id: str
    tournament_id: str
    scheduled_at: str
    best_of: int
    team_blue_id: str
    team_red_id: str
    winner_team_id: str | None = None
    source_origin: str


class Game(BaseModel, extra="allow"):
    game_id: str
    match_id: str
    game_number: int
    patch_id: str
    side_selection: str = "UNKNOWN"
    fearless_context: list[str] = Field(default_factory=list)
    duration_seconds: int | None = None
    winner_side: str | None = None
    source_origin: str
    source_game_key: str

    @field_validator("winner_side")
    @classmethod
    def validate_winner_side(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.upper()
        if normalized not in {"BLUE", "RED"}:
            raise ValueError("winner_side must be BLUE, RED, or None")
        return normalized


class DraftAction(BaseModel, extra="allow"):
    game_id: str
    action_order: int
    phase: str
    action_type: str
    team_side: str
    champion_id: str
    intended_role: str | None = None
    is_flex: bool = False

    @field_validator("action_type", "team_side", mode="before")
    @classmethod
    def uppercase_token(cls, value: str) -> str:
        return value.upper()


class Team(BaseModel, extra="allow"):
    team_id: str
    name: str
    short: str
    region: str
    league: str
    active: bool = True


class Player(BaseModel, extra="allow"):
    player_id: str
    handle: str
    real_name: str | None = None
    country: str | None = None
    current_team_id: str | None = None
    primary_role: str


class ParticipantGame(BaseModel, extra="allow"):
    participant_game_id: str
    game_id: str
    team_id: str
    player_id: str
    side: str
    role: str
    champion_id: str
    summoner_spells: list[str] = Field(default_factory=list)
    keystone_rune: str | None = None
    kills: int | None = None
    deaths: int | None = None
    assists: int | None = None
    cs: int | None = None
    gold: int | None = None
    damage: int | None = None
    win: bool | None = None
    played_at: str | None = None
    patch_id: str | None = None
    region: str | None = None


class Patch(BaseModel, extra="allow"):
    patch_id: str
    version_ddragon: str
    release_date: str | None = None
    is_current: bool = False


class ChampionDim(BaseModel, extra="allow"):
    champion_id: str
    display_name: str
    primary_role: str | None = None


class CounterpickEntry(BaseModel, extra="allow"):
    patch_id: str
    role: str
    region: str
    champion_id: str
    against_champion_id: str
    games: int
    wins: int
    winrate_raw: float
    winrate_shrunken: float
    sample_confidence: float


class ComfortScore(BaseModel, extra="allow"):
    player_id: str
    champion_id: str
    games_total: int
    games_recent_90d: int
    winrate_total: float
    winrate_recent_90d: float
    comfort_score: float
    last_played_at: str | None = None


class SynergyPair(BaseModel, extra="allow"):
    patch_id: str
    region: str
    champion_a_id: str
    champion_b_id: str
    games: int
    wins: int
    winrate_raw: float


class CoverageReport(BaseModel, extra="allow"):
    generated_at: str
    tournaments: int = 0
    matches: int = 0
    games: int = 0
    teams: int = 0
    players: int = 0
    patches: int = 0
    active_sources: int = 0
    gaps: list[str] = Field(default_factory=list)
    storage_root: str | None = None


def utcnow_iso() -> str:
    """Return a UTC ISO timestamp with Z suffix and no microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"


JsonDict = dict[str, Any]
