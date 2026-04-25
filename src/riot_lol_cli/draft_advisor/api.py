"""
Draft Advisor API — FastAPI router for ADC recommendation.

Endpoints:
    POST /api/v1/draft/recommend     — Get ADC recommendation from draft state
    GET  /api/v1/draft/champions     — Get all champions for UI
    GET  /api/v1/draft/champions/adcs — Get ADC subset
    GET  /api/v1/draft/health        — Health check
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional

from .champion_data import ChampionDataService
from .scoring import ScoringEngine
from .schemas import DraftState, RecommendationOutput, GameplayRole

# ============================================================================
# Initialize services (loaded once at module import)
# ============================================================================

_data_service: Optional[ChampionDataService] = None
_engine: Optional[ScoringEngine] = None


def _get_services():
    """Lazy initialization of services."""
    global _data_service, _engine
    if _data_service is None:
        _data_service = ChampionDataService()
        _engine = ScoringEngine(_data_service)
    return _data_service, _engine


# ============================================================================
# Router
# ============================================================================

router = APIRouter(prefix="/api/v1/draft", tags=["draft"])


# ============================================================================
# Models for simplified responses
# ============================================================================

class ChampionListItem(BaseModel):
    id: str
    display_name: str
    primary_role: str
    combat_class: str
    damage_type: str
    range_type: str
    is_adc: bool
    has_priority_profile: bool


class HealthResponse(BaseModel):
    status: str
    total_champions: int
    total_adcs: int
    total_priority: int


class VersionInfoResponse(BaseModel):
    live_patch_label: str
    static_data_version: str
    last_verified_at: str
    validator_status: str


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check — confirms data is loaded."""
    svc, _ = _get_services()
    return HealthResponse(
        status="ok",
        total_champions=svc.total_champions,
        total_adcs=svc.total_adcs,
        total_priority=svc.total_priority,
    )


@router.get("/meta/version-info", response_model=VersionInfoResponse)
async def version_info():
    """Get decoupled telemetry version context."""
    svc, _ = _get_services()
    manifest = svc.manifest
    return VersionInfoResponse(
        live_patch_label=manifest.live_patch_label if manifest else "unknown",
        static_data_version=manifest.static_data_version if manifest else "unknown",
        last_verified_at=manifest.last_verified_at if manifest else "unknown",
        validator_status=manifest.validator_status if manifest else "unknown",
    )


@router.get("/champions", response_model=List[ChampionListItem])
async def get_champions():
    """Get all champions for the UI champion selector."""
    svc, _ = _get_services()
    adc_ids = svc.get_adc_ids()
    result = []

    for champ_id, champ in svc.get_all_champions().items():
        result.append(ChampionListItem(
            id=champ.id,
            display_name=champ.display_name,
            primary_role=champ.primary_role.value,
            combat_class=champ.combat_class.value,
            damage_type=champ.damage_type.value,
            range_type=champ.range_type.value,
            is_adc=champ.id in adc_ids,
            has_priority_profile=svc.is_priority_champion(champ.id),
        ))

    result.sort(key=lambda x: x.display_name)
    return result


@router.get("/champions/adcs", response_model=List[ChampionListItem])
async def get_adcs():
    """Get ADC champions only."""
    svc, _ = _get_services()
    adc_ids = svc.get_adc_ids()
    result = []

    for adc_id in adc_ids:
        champ = svc.get_champion(adc_id)
        if champ:
            result.append(ChampionListItem(
                id=champ.id,
                display_name=champ.display_name,
                primary_role=champ.primary_role.value,
                combat_class=champ.combat_class.value,
                damage_type=champ.damage_type.value,
                range_type=champ.range_type.value,
                is_adc=True,
                has_priority_profile=svc.is_priority_champion(champ.id),
            ))

    result.sort(key=lambda x: x.display_name)
    return result


@router.post("/recommend", response_model=RecommendationOutput)
async def recommend(draft_state: DraftState):
    """
    Get ADC recommendation from draft state.

    Accepts allies, enemies, bans, context, and user pool.
    Returns top pick + up to 3 alternatives with full score breakdown
    and structured explainability.
    """
    svc, engine = _get_services()

    # Validate champion IDs
    all_ids = svc.get_all_champion_ids()
    for ally in draft_state.allies:
        if ally.id not in all_ids:
            raise HTTPException(400, f"Unknown champion ID: {ally.id}")
    for enemy in draft_state.enemies:
        if enemy.id not in all_ids:
            raise HTTPException(400, f"Unknown champion ID: {enemy.id}")
    for champ_id in draft_state.user_pool.champions:
        if champ_id not in svc.get_adc_ids():
            raise HTTPException(400, f"Champion '{champ_id}' is not in ADC profiles")

    try:
        result = engine.recommend(draft_state)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Scoring engine error: {str(e)}")
