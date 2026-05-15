"""
Jungle Metagame Server — FastAPI endpoint for jungle champion tiers, items, and stats.

Puerto: 8003
Endpoints: tier-list, champion detail, categories, item abusers, health check.
Sirve el frontend SPA para el dashboard de meta jungla y los iconos de items locales.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.http_utils import UTF8JSONResponse
from riot_lol_cli.settings import get_jungle_meta_host, get_jungle_meta_port

from .loader import (
    get_categories,
    get_champion_detail,
    get_item_abusers,
    list_champions_by_tier,
    list_used_item_ids,
    load_jungle_tier_list,
)

logger = logging.getLogger(__name__)

_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_ITEMS_DIR = _MODULE_DIR.parent.parent.parent / "assets" / "items"
_FAVICON_PATH = _STATIC_DIR / "favicon.svg"
_DESIGN_SYSTEM_DIR = _MODULE_DIR.parent / "draft_advisor" / "static" / "design-system"

router = APIRouter()


# --- Frontend ---


@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Sirve el dashboard SPA del Jungle Meta."""
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Frontend no encontrado</h1><p>Ejecutá la generación del frontend.</p>",
            status_code=404,
        )
    return FileResponse(str(index_path))


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Sirve favicon explicito para evitar 404 ruidosos en consola."""
    if _FAVICON_PATH.exists():
        return FileResponse(str(_FAVICON_PATH), media_type="image/svg+xml")
    return Response(status_code=204)


# --- API Endpoints ---


@router.get("/health")
async def health():
    """Health check con estado del sistema."""
    try:
        tier_list = load_jungle_tier_list()
        return {
            "status": "ok",
            "service": "jungle_meta",
            "port": get_jungle_meta_port(),
            "patch": tier_list.get("patch"),
            "date_updated": tier_list.get("date_updated"),
            "champion_count": len(tier_list.get("jungle_champions", [])),
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return {
            "status": "error",
            "service": "jungle_meta",
            "error": str(e),
        }


@router.get("/api/v1/jungle/tier-list")
async def get_tier_list():
    """Devuelve la tier list completa de junglas con todos sus datos."""
    try:
        return load_jungle_tier_list()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Patch data not found: {e}") from e


@router.get("/api/v1/jungle/tier/{tier}")
async def get_tier(tier: str):
    """Devuelve todos los campeones de un tier específico (S, A, B, C)."""
    tier = tier.upper()
    if tier not in ["S", "A", "B", "C"]:
        raise HTTPException(status_code=400, detail="Tier debe ser S, A, B o C")

    try:
        champions = list_champions_by_tier(tier)
        if not champions:
            raise HTTPException(
                status_code=404,
                detail=f"No champions found in tier {tier}",
            )
        return {"tier": tier, "champions": champions, "count": len(champions)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Patch data not found") from e


@router.get("/api/v1/jungle/champion/{champion_id}")
async def get_champion(champion_id: str):
    """Devuelve el detalle de un campeón específico del meta jungla."""
    try:
        champion = get_champion_detail(champion_id)
        if not champion:
            raise HTTPException(
                status_code=404,
                detail=f"Campeón '{champion_id}' no encontrado en jungla meta",
            )
        tier_list = load_jungle_tier_list()
        return {
            "success": True,
            "champion": champion,
            "patch": tier_list.get("patch"),
            "date_updated": tier_list.get("date_updated"),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Patch data not found") from e


@router.get("/api/v1/jungle/categories")
async def get_curated_categories():
    """Devuelve campeones agrupados por categoría curada (OP, low elo, bans)."""
    try:
        return get_categories()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Patch data not found") from e


@router.get("/api/v1/jungle/items/abusers/{item_key}")
async def get_item_abusers_route(item_key: str):
    """Devuelve campeones que abusan de un item específico (ej. voltaic_sword_abusers)."""
    try:
        champions = get_item_abusers(item_key)
        if not champions:
            raise HTTPException(
                status_code=404,
                detail=f"No abusers found for item key '{item_key}'",
            )
        return {"item_key": item_key, "champions": champions, "count": len(champions)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Patch data not found") from e


@router.get("/api/v1/jungle/items/used")
async def get_used_items():
    """Devuelve la lista de IDs de items referenciados en core_builds."""
    try:
        return {"item_ids": sorted(list_used_item_ids())}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Patch data not found") from e


def create_app() -> FastAPI:
    """Create the Jungle Meta FastAPI application."""
    application = FastAPI(
        title="Jungle Metagame — LoL Jungle Champion Tiers",
        description="Visualiza el meta actual de junglas por parche con items y estadísticas.",
        version="1.1.0",
        default_response_class=UTF8JSONResponse,
    )

    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    if _DESIGN_SYSTEM_DIR.exists():
        application.mount(
            "/design-system",
            StaticFiles(directory=str(_DESIGN_SYSTEM_DIR)),
            name="design-system",
        )

    if _ITEMS_DIR.exists():
        application.mount("/items", StaticFiles(directory=str(_ITEMS_DIR)), name="items")

    application.include_router(router)

    return application


app = create_app()


# --- Entry point ---


def run() -> None:
    """Levanta el servidor en puerto configurado (default 8003)."""
    import uvicorn

    host = get_jungle_meta_host()
    port = get_jungle_meta_port()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Jungle Meta Server en http://%s:%d", host, port)
    logger.info("Dashboard en http://%s:%d", host, port)
    logger.info("API docs en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
