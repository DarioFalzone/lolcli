"""
Jungle Metagame Server — FastAPI endpoint for jungle champion tiers, items, and stats.

Puerto: 8003
Endpoints: tier-list, champion detail, health check.
Sirve el frontend SPA para el dashboard de meta jungla.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .loader import get_champion_detail, list_champions_by_tier, load_jungle_tier_list

logger = logging.getLogger(__name__)

# Paths
_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"

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


# --- API Endpoints ---


@router.get("/health")
async def health():
    """Health check con estado del sistema."""
    try:
        tier_list = load_jungle_tier_list()
        return {
            "status": "ok",
            "service": "jungle_meta",
            "port": 8003,
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
        data = load_jungle_tier_list()
        return data
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Patch data not found: {e}",
        )


@router.get("/api/v1/jungle/tier/{tier}")
async def get_tier(tier: str):
    """Devuelve todos los campeones de un tier específico (S, A, B, C)."""
    tier = tier.upper()
    if tier not in ["S", "A", "B", "C"]:
        raise HTTPException(
            status_code=400,
            detail="Tier debe ser S, A, B o C",
        )

    try:
        champions = list_champions_by_tier(tier)
        if not champions:
            raise HTTPException(
                status_code=404,
                detail=f"No champions found in tier {tier}",
            )
        return {
            "tier": tier,
            "champions": champions,
            "count": len(champions),
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Patch data not found",
        )


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
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Patch data not found",
        )


def create_app() -> FastAPI:
    """Create the Jungle Meta FastAPI application."""
    application = FastAPI(
        title="Jungle Metagame — LoL Jungle Champion Tiers",
        description="Visualiza el meta actual de junglas por parche con items y estadísticas.",
        version="1.0.0",
    )

    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    application.include_router(router)

    return application


app = create_app()


# --- Entry point ---


def run() -> None:
    """Levanta el servidor en puerto 8003."""
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Jungle Meta Server en http://localhost:8003")
    logger.info("Dashboard en http://localhost:8003")
    logger.info("API docs en http://localhost:8003/docs")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")


if __name__ == "__main__":
    run()
