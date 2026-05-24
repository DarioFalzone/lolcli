"""
Draft Advisor API — Router FastAPI para recomendaciones de draft.

Endpoints:
    POST /api/v1/draft/recommend     — Obtener recomendación según estado del draft
    GET  /api/v1/draft/champions     — Listar todos los campeones para la UI
    GET  /api/v1/draft/champions/adcs — Subconjunto de ADCs
    GET  /api/v1/draft/health        — Chequeo de salud
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from .champion_data import ChampionDataService
from .schemas import AdvisorMode, DraftState, RecommendationOutput
from .scoring import ScoringEngine

# ============================================================================
# Services
# ============================================================================


@dataclass(frozen=True)
class DraftAdvisorServices:
    data_service: ChampionDataService
    scoring_engine: ScoringEngine


def create_services() -> DraftAdvisorServices:
    """Create isolated service instances for one FastAPI app."""
    data_service = ChampionDataService()
    return DraftAdvisorServices(
        data_service=data_service,
        scoring_engine=ScoringEngine(data_service),
    )


def get_services(request: Request) -> DraftAdvisorServices:
    """Return services scoped to the current FastAPI app instance."""
    services = getattr(request.app.state, "draft_services", None)
    if services is None:
        services = create_services()
        request.app.state.draft_services = services
    return services


DraftServicesDep = Annotated[DraftAdvisorServices, Depends(get_services)]


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
    is_jungler: bool = False
    has_priority_profile: bool


class JungleChampionListItem(ChampionListItem):
    jungle_tier: str | None = None
    jungle_winrate: float | None = None
    jungle_pickrate: float | None = None
    jungle_banrate: float | None = None
    jungle_reason: str | None = None


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
    adc_meta_patch: str | None = None
    adc_meta_scraped_at: str | None = None
    adc_meta_status: str = "missing"
    adc_meta_sources: list[str] = []
    adc_meta_champion_count: int = 0
    adc_meta_age_hours: float | None = None
    adc_mastery_last_updated: str | None = None
    adc_mastery_source_image: str | None = None
    jungle_meta_patch: str | None = None
    jungle_meta_updated_at: str | None = None
    jungle_meta_status: str = "missing"
    jungle_meta_source: str | None = None
    jungle_meta_champion_count: int = 0


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/health", response_model=HealthResponse)
async def health(services: DraftServicesDep):
    """Chequeo de salud — confirma que los datos están cargados."""
    svc = services.data_service
    return HealthResponse(
        status="ok",
        total_champions=svc.total_champions,
        total_adcs=svc.total_adcs,
        total_priority=svc.total_priority,
    )


@router.get("/meta/version-info", response_model=VersionInfoResponse)
async def version_info(services: DraftServicesDep):
    """Get decoupled telemetry version context."""
    svc = services.data_service
    manifest = svc.manifest
    adc_meta = svc.get_adc_meta_snapshot_info()
    adc_mastery = svc.get_personal_adc_mastery_info()
    jungle_meta = svc.get_jungle_meta_snapshot_info()
    return VersionInfoResponse(
        live_patch_label=manifest.live_patch_label if manifest else "unknown",
        static_data_version=manifest.static_data_version if manifest else "unknown",
        last_verified_at=manifest.last_verified_at if manifest else "unknown",
        validator_status=manifest.validator_status if manifest else "unknown",
        adc_meta_patch=adc_meta.get("patch"),
        adc_meta_scraped_at=adc_meta.get("scraped_at"),
        adc_meta_status=adc_meta.get("status", "missing"),
        adc_meta_sources=adc_meta.get("sources", []),
        adc_meta_champion_count=adc_meta.get("champion_count", 0),
        adc_meta_age_hours=adc_meta.get("age_hours"),
        adc_mastery_last_updated=adc_mastery.get("last_updated"),
        adc_mastery_source_image=adc_mastery.get("source_image"),
        jungle_meta_patch=jungle_meta.get("patch"),
        jungle_meta_updated_at=jungle_meta.get("date_updated"),
        jungle_meta_status=jungle_meta.get("status", "missing"),
        jungle_meta_source=jungle_meta.get("source"),
        jungle_meta_champion_count=jungle_meta.get("champion_count", 0),
    )


@router.get("/champions", response_model=list[ChampionListItem])
async def get_champions(services: DraftServicesDep):
    """Listar todos los campeones para el selector de la UI."""
    svc = services.data_service
    adc_ids = svc.get_adc_ids()
    support_ids = svc.get_support_ids()
    jungler_ids = svc.get_jungler_ids()
    result = []

    for champ in svc.get_all_champions().values():
        result.append(
            ChampionListItem(
                id=champ.id,
                display_name=champ.display_name,
                primary_role=champ.primary_role.value,
                combat_class=champ.combat_class.value,
                damage_type=champ.damage_type.value,
                range_type=champ.range_type.value,
                is_adc=champ.id in adc_ids,
                is_support=champ.id in support_ids,
                is_jungler=champ.id in jungler_ids,
                has_priority_profile=svc.is_priority_champion(champ.id),
            )
        )

    result.sort(key=lambda x: x.display_name)
    return result


@router.get("/champions/adcs", response_model=list[ChampionListItem])
async def get_adcs(services: DraftServicesDep):
    """Get ADC champions only."""
    svc = services.data_service
    adc_ids = svc.get_adc_ids()
    result = []

    for adc_id in adc_ids:
        champ = svc.get_champion(adc_id)
        if champ:
            result.append(
                ChampionListItem(
                    id=champ.id,
                    display_name=champ.display_name,
                    primary_role=champ.primary_role.value,
                    combat_class=champ.combat_class.value,
                    damage_type=champ.damage_type.value,
                    range_type=champ.range_type.value,
                    is_adc=True,
                    is_support=False,
                    is_jungler=False,
                    has_priority_profile=svc.is_priority_champion(champ.id),
                )
            )

    result.sort(key=lambda x: x.display_name)
    return result


@router.get("/champions/junglers", response_model=list[JungleChampionListItem])
async def get_junglers(services: DraftServicesDep):
    """Get jungle champions from Jungle Meta."""
    svc = services.data_service
    jungle_rows = svc.get_jungle_meta_champions()
    result = []

    for champ_id, meta in jungle_rows.items():
        champ = svc.get_champion(champ_id)
        if champ:
            result.append(
                JungleChampionListItem(
                    id=champ.id,
                    display_name=champ.display_name,
                    primary_role=champ.primary_role.value,
                    combat_class=champ.combat_class.value,
                    damage_type=champ.damage_type.value,
                    range_type=champ.range_type.value,
                    is_adc=champ.id in svc.get_adc_ids(),
                    is_support=champ.id in svc.get_support_ids(),
                    is_jungler=True,
                    has_priority_profile=svc.is_priority_champion(champ.id),
                    jungle_tier=meta.get("tier"),
                    jungle_winrate=meta.get("winrate"),
                    jungle_pickrate=meta.get("pickrate"),
                    jungle_banrate=meta.get("banrate"),
                    jungle_reason=meta.get("reason_text"),
                )
            )

    tier_order = {"S": 0, "A": 1, "B": 2, "C": 3}
    result.sort(key=lambda x: (tier_order.get(x.jungle_tier or "", 9), x.display_name))
    return result


@router.post("/recommend", response_model=RecommendationOutput)
async def recommend(draft_state: DraftState, services: DraftServicesDep):
    """
    Obtener recomendación de pick según el estado del draft.

    Acepta aliados, enemigos, bans, contexto y pool del usuario.
    Devuelve top pick + hasta 3 alternativas con desglose de puntaje
    y explicaciones estructuradas.
    """
    svc = services.data_service
    engine = services.scoring_engine

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
        elif draft_state.target_role == AdvisorMode.JUNGLE and champ_id not in svc.get_jungler_ids():
            raise HTTPException(400, f"Campeón '{champ_id}' no está en Jungle Meta")

    try:
        result = engine.recommend(draft_state)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:
        raise HTTPException(500, f"Scoring engine error: {str(e)}") from e


# ============================================================================
# Endpoints — Knowledge Base Inspection
# ============================================================================


class StrategicTriangleResponse(BaseModel):
    champion_id: str
    display_name: str
    fine_grained_archetype: str | None
    coarse_archetype: str | None
    beats: list[str]
    loses_to: list[str]
    archetype_description: str


@router.get("/strategic-triangle/{champion_id}", response_model=StrategicTriangleResponse)
async def get_strategic_triangle(champion_id: str, services: DraftServicesDep):
    """Inspeccionar la posición de un campeón en el triángulo estratégico.

    Devuelve el arquetipo fine-grained, qué arquetipos counterea (beats)
    y cuáles lo counterean (loses_to).
    """
    svc = services.data_service

    if not svc.champion_exists(champion_id):
        raise HTTPException(404, f"Campeón '{champion_id}' no encontrado")

    fine_arch = svc.classify_supp_archetype_fine(champion_id)
    supp_profile = svc.get_support_profile(champion_id)
    coarse_arch = supp_profile.archetype.value if supp_profile else None

    triangle = svc.get_strategic_triangle()
    triangle_data = triangle.get("triangle", {})

    beats: list[str] = []
    loses_to: list[str] = []
    description = ""

    if fine_arch and fine_arch in triangle_data:
        arch_rules = triangle_data[fine_arch]
        beats = arch_rules.get("beats", [])
        loses_to = arch_rules.get("loses_to", [])

    archetypes = triangle.get("fine_grained_archetypes", {})
    if fine_arch and fine_arch in archetypes:
        description = archetypes[fine_arch].get("description", "")

    return StrategicTriangleResponse(
        champion_id=champion_id,
        display_name=svc.get_champion_display_name(champion_id),
        fine_grained_archetype=fine_arch,
        coarse_archetype=coarse_arch,
        beats=beats,
        loses_to=loses_to,
        archetype_description=description,
    )


class SupportRosterItem(BaseModel):
    id: str
    display_name: str
    archetype: str
    fine_grained_archetype: str | None
    engage_strength: int
    peel_strength: int
    blind_pick_safety: int
    scaling: int


@router.get("/champions/supports", response_model=list[SupportRosterItem])
async def get_supports(services: DraftServicesDep):
    """Listar todos los soportes con perfil detallado."""
    svc = services.data_service
    result = []

    for supp_id, profile in svc.get_all_support_profiles().items():
        result.append(
            SupportRosterItem(
                id=profile.id,
                display_name=profile.display_name,
                archetype=profile.archetype.value,
                fine_grained_archetype=svc.classify_supp_archetype_fine(supp_id),
                engage_strength=profile.engage_strength,
                peel_strength=profile.peel_strength,
                blind_pick_safety=profile.blind_pick_safety,
                scaling=profile.scaling,
            )
        )

    result.sort(key=lambda x: x.display_name)
    return result
