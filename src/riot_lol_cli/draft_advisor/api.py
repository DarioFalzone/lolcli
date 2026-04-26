"""
Draft Advisor API — Router FastAPI para recomendaciones de draft.

Endpoints:
    POST /api/v1/draft/recommend     — Obtener recomendación según estado del draft
    GET  /api/v1/draft/champions     — Listar todos los campeones para la UI
    GET  /api/v1/draft/champions/adcs — Subconjunto de ADCs
    GET  /api/v1/draft/health        — Chequeo de salud
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .champion_data import ChampionDataService
from .schemas import AdvisorMode, DraftState, RecommendationOutput
from .scoring import ScoringEngine

# ============================================================================
# Initialize services (loaded once at module import)
# ============================================================================

_data_service: ChampionDataService | None = None
_engine: ScoringEngine | None = None


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
    is_support: bool
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
    """Chequeo de salud — confirma que los datos están cargados."""
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


@router.get("/champions", response_model=list[ChampionListItem])
async def get_champions():
    """Listar todos los campeones para el selector de la UI."""
    svc, _ = _get_services()
    adc_ids = svc.get_adc_ids()
    support_ids = svc.get_support_ids()
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
            is_support=champ.id in support_ids,
            has_priority_profile=svc.is_priority_champion(champ.id),
        ))

    result.sort(key=lambda x: x.display_name)
    return result


@router.get("/champions/adcs", response_model=list[ChampionListItem])
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
    Obtener recomendación de pick según el estado del draft.

    Acepta aliados, enemigos, bans, contexto y pool del usuario.
    Devuelve top pick + hasta 3 alternativas con desglose de puntaje
    y explicaciones estructuradas.
    """
    svc, engine = _get_services()

    # Validar IDs de campeones
    all_ids = svc.get_all_champion_ids()
    for ally in draft_state.allies:
        if ally.id not in all_ids:
            raise HTTPException(400, f"ID de campeón desconocido: {ally.id}")
    for enemy in draft_state.enemies:
        if enemy.id not in all_ids:
            raise HTTPException(400, f"ID de campeón desconocido: {enemy.id}")
    for champ_id in draft_state.user_pool.champions:
        if draft_state.target_role == AdvisorMode.SUPPORT and champ_id not in svc.get_support_ids():
            raise HTTPException(400, f"Campeón '{champ_id}' no está en los perfiles de Soporte")
        elif draft_state.target_role == AdvisorMode.ADC and champ_id not in svc.get_adc_ids():
            raise HTTPException(400, f"Campeón '{champ_id}' no está en los perfiles de ADC")

    try:
        result = engine.recommend(draft_state)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Scoring engine error: {str(e)}")
