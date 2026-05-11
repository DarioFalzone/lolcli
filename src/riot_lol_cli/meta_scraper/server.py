"""
Servidor FastAPI para el Meta Scraper.

Puerto: 8002
Endpoints: tier list, detalle de campeón, trigger de scraping, health.
Sirve el frontend estático para el dashboard de meta.
"""

from __future__ import annotations

import logging
from pathlib import Path

import uvicorn
from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.settings import get_meta_scraper_host, get_meta_scraper_port

from .messages import NO_ADAPTERS_AVAILABLE_MESSAGE
from .normalizer import load_latest
from .orchestrator import ScrapingOrchestrator

logger = logging.getLogger(__name__)

# Paths
_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_FAVICON_PATH = _STATIC_DIR / "favicon.svg"

_DESIGN_SYSTEM_DIR = _MODULE_DIR.parent / "draft_advisor" / "static" / "design-system"
router = APIRouter()


def _get_state_orchestrator(request: Request) -> ScrapingOrchestrator:
    """Return the orchestrator scoped to this FastAPI app instance."""
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if orchestrator is None:
        orchestrator = ScrapingOrchestrator()
        request.app.state.orchestrator = orchestrator
    return orchestrator


def _create_orchestrator() -> ScrapingOrchestrator:
    """Crea un orquestador fresco con adapters recién instanciados."""
    # Crear adapters frescos cada vez (evita cachear estados fallidos)
    orchestrator = ScrapingOrchestrator()

    try:
        from .adapters.lolalytics import LolalyticsAdapter

        orchestrator.register_adapter(LolalyticsAdapter())
    except ImportError:
        logger.warning("LolalyticsAdapter no disponible (falta playwright)")

    try:
        from .adapters.opgg import OpggAdapter

        orchestrator.register_adapter(OpggAdapter())
    except ImportError:
        logger.warning("OpggAdapter no disponible (falta playwright)")

    try:
        from .adapters.ugg import UggAdapter

        orchestrator.register_adapter(UggAdapter())
    except ImportError:
        logger.warning("UggAdapter no disponible (falta playwright)")

    return orchestrator


# --- Frontend ---


@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Sirve el dashboard HTML del Meta Scraper."""
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


def _snapshot_summary(role: str) -> dict:
    """Resumen liviano del ultimo snapshot por rol."""
    latest = load_latest(role)
    if not latest:
        return {
            "last_scrape": None,
            "patch": None,
            "champion_count": 0,
            "sources": [],
            "source_gaps": [],
        }
    return {
        "last_scrape": latest.get("scraped_at"),
        "patch": latest.get("patch"),
        "champion_count": latest.get("champion_count", 0),
        "sources": latest.get("sources", []),
        "source_gaps": latest.get("source_gaps", []),
    }


@router.get("/health")
async def health(request: Request):
    """Health check con estado del sistema."""
    return {
        "status": "ok",
        "service": "meta_scraper",
        "port": get_meta_scraper_port(),
        "support": _snapshot_summary("support"),
        "adc": _snapshot_summary("adc"),
        "jungle": _snapshot_summary("jungle"),
        "is_scraping": _get_state_orchestrator(request).is_running,
    }


@router.get("/api/v1/meta/support/tier")
async def get_support_tier_list():
    """
    Devuelve la tier list de soportes del último snapshot normalizado.

    Incluye WR, PR, BR, tier y source breakdown por cada campeón.
    """
    data = load_latest()
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No hay datos de meta disponibles. Ejecutá un scraping primero.",
        )
    return data


@router.get("/api/v1/meta/adc/tier")
async def get_adc_tier_list():
    """
    Devuelve la tier list de ADCs del ultimo snapshot normalizado.

    Incluye WR, PR, BR, tier, climb_score y source breakdown por cada campeon.
    """
    data = load_latest("adc")
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No hay datos de meta ADC disponibles. Ejecuta un scraping ADC primero.",
        )
    return data


@router.get("/api/v1/meta/jungle/tier")
async def get_jungle_tier_list():
    """
    Devuelve la tier list de jungla del ultimo snapshot normalizado.

    Incluye meta total ponderado, desglose por fuente y gaps de scraping.
    """
    data = load_latest("jungle")
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No hay datos de meta jungla disponibles. Ejecuta un scraping jungla primero.",
        )
    return data


@router.get("/api/v1/meta/support/champion/{champion_id}")
async def get_champion_detail(champion_id: str):
    """
    Devuelve el detalle de un soporte específico del último snapshot.
    """
    data = load_latest()
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos disponibles.")

    # Buscar campeón (case-insensitive)
    for champ in data.get("champions", []):
        if champ["id"].lower() == champion_id.lower():
            return {
                "success": True,
                "champion": champ,
                "patch": data.get("patch"),
                "scraped_at": data.get("scraped_at"),
            }

    raise HTTPException(status_code=404, detail=f"Campeón '{champion_id}' no encontrado.")


@router.get("/api/v1/meta/adc/champion/{champion_id}")
async def get_adc_champion_detail(champion_id: str):
    """Devuelve el detalle de un ADC especifico del ultimo snapshot."""
    data = load_latest("adc")
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos ADC disponibles.")

    for champ in data.get("champions", []):
        if champ["id"].lower() == champion_id.lower():
            return {
                "success": True,
                "champion": champ,
                "patch": data.get("patch"),
                "scraped_at": data.get("scraped_at"),
            }

    raise HTTPException(status_code=404, detail=f"ADC '{champion_id}' no encontrado.")


@router.get("/api/v1/meta/jungle/champion/{champion_id}")
async def get_jungle_champion_detail(champion_id: str):
    """Devuelve el detalle de un jungla especifico del ultimo snapshot."""
    data = load_latest("jungle")
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos de jungla disponibles.")

    for champ in data.get("champions", []):
        if champ["id"].lower() == champion_id.lower():
            return {
                "success": True,
                "champion": champ,
                "patch": data.get("patch"),
                "scraped_at": data.get("scraped_at"),
                "source_gaps": data.get("source_gaps", []),
            }

    raise HTTPException(status_code=404, detail=f"Jungla '{champion_id}' no encontrado.")


@router.get("/api/v1/meta/support/history")
async def get_scrape_history():
    """Devuelve el manifest con el historial de snapshots."""
    import json

    manifest_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "meta_scraper" / "manifest.json"
    if not manifest_path.exists():
        return {"snapshots": [], "last_scrape": None}

    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


@router.post("/api/v1/meta/scrape")
async def trigger_scrape(request: Request, background_tasks: BackgroundTasks):
    """
    Dispara un scraping manual.

    Se ejecuta en background para no bloquear la respuesta HTTP.
    El frontend puede pollear /health para ver el progreso.
    """
    current_orchestrator = _get_state_orchestrator(request)

    if current_orchestrator.is_running:
        raise HTTPException(
            status_code=409,
            detail="Ya hay un scraping en curso. Esperá a que termine.",
        )

    orchestrator = _create_orchestrator()
    if not orchestrator.adapters:
        raise HTTPException(status_code=503, detail=NO_ADAPTERS_AVAILABLE_MESSAGE)

    request.app.state.orchestrator = orchestrator
    background_tasks.add_task(_run_scrape_background, request.app, orchestrator, "support")

    return {
        "status": "started",
        "message": "Scraping iniciado en background. Consultá /health para ver el progreso.",
        "adapters": [a.platform_name for a in orchestrator.adapters],
    }


@router.post("/api/v1/meta/scrape/adc")
async def trigger_adc_scrape(request: Request, background_tasks: BackgroundTasks):
    """Dispara un scraping manual de ADCs para climb."""
    current_orchestrator = _get_state_orchestrator(request)

    if current_orchestrator.is_running:
        raise HTTPException(
            status_code=409,
            detail="Ya hay un scraping en curso. Espera a que termine.",
        )

    orchestrator = _create_orchestrator()
    if not orchestrator.adapters:
        raise HTTPException(status_code=503, detail=NO_ADAPTERS_AVAILABLE_MESSAGE)

    request.app.state.orchestrator = orchestrator
    background_tasks.add_task(_run_scrape_background, request.app, orchestrator, "adc")

    return {
        "status": "started",
        "message": "Scraping ADC iniciado en background. Consulta /health para ver el progreso.",
        "adapters": [a.platform_name for a in orchestrator.adapters],
    }


@router.post("/api/v1/meta/scrape/jungle")
async def trigger_jungle_scrape(request: Request, background_tasks: BackgroundTasks):
    """Dispara un scraping manual de jungla."""
    current_orchestrator = _get_state_orchestrator(request)

    if current_orchestrator.is_running:
        raise HTTPException(
            status_code=409,
            detail="Ya hay un scraping en curso. Espera a que termine.",
        )

    orchestrator = _create_orchestrator()
    if not orchestrator.adapters:
        raise HTTPException(status_code=503, detail=NO_ADAPTERS_AVAILABLE_MESSAGE)

    request.app.state.orchestrator = orchestrator
    background_tasks.add_task(_run_scrape_background, request.app, orchestrator, "jungle")

    return {
        "status": "started",
        "message": "Scraping jungla iniciado en background. Consulta /health para ver el progreso.",
        "adapters": [a.platform_name for a in orchestrator.adapters],
    }


def _run_scrape_background(application: FastAPI, orchestrator: ScrapingOrchestrator, role: str = "support") -> None:
    """Ejecuta el scraping en background."""
    try:
        logger.info("=== Scraping background iniciado ===")
        result = orchestrator.run_full_scrape(role=role)
        application.state.last_scrape_result = result
        logger.info("=== Scraping background completado ===")
    except Exception as e:
        logger.error("=== Scraping background fallido: %s ===", e, exc_info=True)
        application.state.last_scrape_result = {"error": str(e)}


def create_app() -> FastAPI:
    """Create the Meta Scraper FastAPI application."""
    application = FastAPI(
        title="Meta Scraper — LoL Meta Dashboard",
        description="Scrapea y visualiza el meta de soporte, ADC y jungla de League of Legends.",
        version="1.0.0",
    )
    application.state.orchestrator = ScrapingOrchestrator()
    application.state.last_scrape_result = None
    application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    if _DESIGN_SYSTEM_DIR.exists():
        application.mount(
            "/design-system",
            StaticFiles(directory=str(_DESIGN_SYSTEM_DIR)),
            name="design-system",
        )
    application.include_router(router)
    return application


app = create_app()


# --- Entry point ---


def run():
    """Levanta el servidor en puerto 8002."""
    host = get_meta_scraper_host()
    port = get_meta_scraper_port()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Meta Scraper en http://%s:%d", host, port)
    logger.info("Dashboard en http://%s:%d", host, port)
    logger.info("Documentacion en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
