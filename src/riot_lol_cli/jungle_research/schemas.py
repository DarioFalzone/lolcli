"""
Schemas Pydantic V2 para Jungle Research.

Nombres y campos compatibles con migración futura a SQLite/PostgreSQL: cada
modelo equivale a una tabla. Snapshots de meta y match history son
append-only, nunca se mutan.

Reglas:

- `extra="allow"` evita que un campo nuevo de una fuente rompa el parseo.
- `region`, `elo`, `queue`, `role` siempre son string normalizados (lowercase
  para region/queue, UPPER para tier/elo cuando viene de Riot).
- Todo modelo lleva `extracted_at` o `created_at` en formato ISO 8601 UTC.
- `warning_flags` es lista de strings; cada flag identifica un problema
  conocido (`"outlier:winrate"`, `"sample_size_low"`, `"stale_>72h"`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums canónicos
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    """Categoría operativa de la fuente."""

    OFFICIAL_API = "official_api"
    SOLOQ_META = "soloq_meta"
    ASIA_META = "asia_meta"
    PRO_ACCOUNTS = "pro_accounts"
    PRO_STAGE = "pro_stage"
    OTP_RANKINGS = "otp_rankings"
    MATCHUP_DATA = "matchup_data"
    CURATED_LOCAL = "curated_local"


class SourceStatus(str, Enum):
    """Estado operativo de la fuente en V1."""

    ACTIVE = "active"
    PLANNED = "planned"
    GAP = "gap"


class JungleTier(str, Enum):
    """Tier final asignado a un campeón."""

    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------


class Source(BaseModel, extra="allow"):
    """Fuente externa o interna que aporta datos al sistema."""

    id: str
    name: str
    base_url: str
    source_type: SourceType
    region_focus: list[str] = Field(default_factory=list)
    requires_browser: bool = False
    has_public_api: bool = False
    scrape_priority: int = 50
    status: SourceStatus = SourceStatus.PLANNED
    notes: str = ""
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Meta snapshots por fuente
# ---------------------------------------------------------------------------


class ChampionMetaSnapshot(BaseModel, extra="allow"):
    """Una observación de un campeón en una fuente, contexto y momento."""

    source_id: str
    source_name: str
    source_url: str
    extracted_at: str
    patch: str
    region: str
    queue: str
    elo: str
    role: str
    champion_id: str
    champion_name: str
    tier: JungleTier | None = None
    rank_position: int | None = None
    win_rate: float | None = None
    pick_rate: float | None = None
    ban_rate: float | None = None
    games: int | None = None
    kda: float | None = None
    source_score: float | None = None
    methodology_notes: str = ""
    raw_payload_ref: str | None = None
    warning_flags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Pros y cuentas
# ---------------------------------------------------------------------------


class ProPlayerUrls(BaseModel, extra="allow"):
    trackingthepros: str | None = None
    dpm: str | None = None
    gol: str | None = None
    new_trackingthepros: str | None = None


class ProPlayer(BaseModel, extra="allow"):
    """Pro player seed; identidad estable, no cambia salvo retiro/cambio rol."""

    player_name: str
    real_name: str | None = None
    country: str | None = None
    role: str = "jungle"
    current_team: str | None = None
    historical_teams: list[str] = Field(default_factory=list)
    priority_tier: str  # "S" / "A" / "B" — solo para ordenar discovery
    urls: ProPlayerUrls = Field(default_factory=ProPlayerUrls)
    notes: str = ""
    created_at: str
    updated_at: str


class ProAccount(BaseModel, extra="allow"):
    """Cuenta concreta de un pro en un servidor; mutable (rank, last_seen)."""

    pro_player_id: str  # = ProPlayer.player_name
    source: str  # de dónde se obtuvo (manual_seed, trackingthepros, dpm, etc.)
    account_name: str | None = None
    riot_id_game_name: str | None = None
    riot_id_tagline: str | None = None
    server: str | None = None  # KR, EUW, NA, etc.
    region_cluster: str | None = None  # ASIA, EUROPE, AMERICAS
    puuid: str | None = None
    summoner_id: str | None = None
    account_id: str | None = None
    rank_tier: str | None = None
    rank_division: str | None = None
    league_points: int | None = None
    last_seen_at: str | None = None
    is_active: bool = True
    confidence_score: float = 0.0
    gap_flag: str | None = None  # "needs_account_resolution", "no_riot_key", etc.


# ---------------------------------------------------------------------------
# Match history
# ---------------------------------------------------------------------------


class MatchHistoryEntry(BaseModel, extra="allow"):
    """Una partida concreta de una cuenta tracked."""

    match_id: str
    puuid: str
    player_id: str | None = None  # ProPlayer.player_name si aplica
    source: str = "riot_api"
    server: str | None = None
    region_cluster: str | None = None
    queue_id: int | None = None
    game_datetime: str
    patch: str | None = None
    champion_id: str | None = None
    champion_name: str
    detected_role: str | None = None
    team_position: str | None = None
    win: bool | None = None
    kills: int | None = None
    deaths: int | None = None
    assists: int | None = None
    cs: int | None = None
    gold: int | None = None
    damage: int | None = None
    vision_score: int | None = None
    game_duration: int | None = None
    raw_payload_ref: str | None = None
    created_at: str


# ---------------------------------------------------------------------------
# OTP rankings (V1: planned)
# ---------------------------------------------------------------------------


class OtpRankingEntry(BaseModel, extra="allow"):
    """Ranking OTP por campeón (Onetricks/LeagueOfGraphs)."""

    source_id: str
    champion_name: str
    role: str
    region: str
    summoner_name: str
    riot_id_game_name: str | None = None
    riot_id_tagline: str | None = None
    server: str | None = None
    rank_tier: str | None = None
    rank_lp: int | None = None
    games_on_champion: int | None = None
    win_rate_on_champion: float | None = None
    ranking_position: int
    source_url: str
    extracted_at: str


# ---------------------------------------------------------------------------
# Output consolidado
# ---------------------------------------------------------------------------


class FinalJungleTierEntry(BaseModel, extra="allow"):
    """Una fila de la tier list final consolidada por consenso."""

    champion_name: str
    role: str = "jungle"
    final_tier: JungleTier
    final_score: float
    soloq_score: float | None = None
    asia_score: float | None = None
    pro_soloq_score: float | None = None
    pro_stage_score: float | None = None
    otp_score: float | None = None
    confidence: float = 0.0
    explanation: str = ""
    source_count: int = 0
    warning_flags: list[str] = Field(default_factory=list)
    generated_at: str
    patch: str
    region: str
    elo: str


class FinalJungleTierList(BaseModel, extra="allow"):
    """Snapshot completo de la tier list final."""

    generated_at: str
    patch: str
    region: str
    elo: str
    queue: str = "ranked_solo_5x5"
    entries: list[FinalJungleTierEntry] = Field(default_factory=list)
    source_count_total: int = 0
    gaps: list[str] = Field(default_factory=list)
    warning_flags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Daily report
# ---------------------------------------------------------------------------


class TierMovement(BaseModel, extra="allow"):
    champion_name: str
    previous_tier: JungleTier | None = None
    current_tier: JungleTier
    previous_score: float | None = None
    current_score: float
    delta: float


class DailyReport(BaseModel, extra="allow"):
    """Reporte diario de cambios y contradicciones."""

    report_date: str
    generated_at: str
    patch: str
    top_junglers: list[FinalJungleTierEntry] = Field(default_factory=list)
    risers: list[TierMovement] = Field(default_factory=list)
    fallers: list[TierMovement] = Field(default_factory=list)
    pro_recent_picks: list[dict[str, Any]] = Field(default_factory=list)
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    soloq_vs_pro_diff: list[dict[str, Any]] = Field(default_factory=list)
    confidence_summary: dict[str, float] = Field(default_factory=dict)
    gaps: list[str] = Field(default_factory=list)


def utcnow_iso() -> str:
    """Timestamp ISO 8601 UTC sin microsegundos, sufijo 'Z'."""
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"
