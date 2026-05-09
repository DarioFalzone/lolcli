"""
Home Hub Server — FastAPI endpoint central de acceso a todos los subsistemas.

Puerto: 8080 (configurable via LOLCLI_HOME_PORT).
Endpoints: /, /health, /api/v1/home/status, /api/v1/home/version
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.settings import (
    get_draft_advisor_port,
    get_home_host,
    get_home_port,
    get_items_browser_port,
    get_jungle_meta_port,
    get_meta_api_port,
    get_meta_scraper_port,
)

logger = logging.getLogger(__name__)

_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_DESIGN_SYSTEM_DIR = _MODULE_DIR.parent / "draft_advisor" / "static" / "design-system"
_VERSION_FILE = _MODULE_DIR.parent.parent.parent / "config" / "version.json"
_JUNGLAS_PRO_DIR = _MODULE_DIR.parent.parent.parent / "projects" / "active" / "junglas-pro"

router = APIRouter()

# Service registry — each entry defines a subsystem to monitor.
SERVICES = [
    {
        "id": "meta_api",
        "name": "Meta Analyzer",
        "description": "Tier lists, anomalías y análisis estadístico del meta actual.",
        "port_fn": get_meta_api_port,
        "health_path": "/health",
        "ui_path": "/dashboard-enhanced",
        "icon": "📊",
        "accent": "cyan",
    },
    {
        "id": "draft_advisor",
        "name": "Draft Advisor",
        "description": "Recomendador inteligente de picks ADC y Support para el draft.",
        "port_fn": get_draft_advisor_port,
        "health_path": "/api/v1/draft/health",
        "ui_path": "/draft",
        "icon": "🎯",
        "accent": "gold",
    },
    {
        "id": "meta_scraper",
        "name": "Meta Scraper",
        "description": "Scraping y normalización del meta desde OP.GG y LoLalytics.",
        "port_fn": get_meta_scraper_port,
        "health_path": "/health",
        "ui_path": "/",
        "icon": "🕷️",
        "accent": "error",
    },
    {
        "id": "jungle_meta",
        "name": "Jungle Meta",
        "description": "Tier list de campeones jungla por parche con builds e ítems.",
        "port_fn": get_jungle_meta_port,
        "health_path": "/health",
        "ui_path": "/",
        "icon": "🌿",
        "accent": "success",
    },
    {
        "id": "items_browser",
        "name": "Items Browser",
        "description": "Catálogo visual de ítems LoL con nombres EN+ES y filtros.",
        "port_fn": get_items_browser_port,
        "health_path": "/health",
        "ui_path": "/",
        "icon": "⚔️",
        "accent": "warning",
    },
]


def _load_version() -> str:
    """Read project version from config/version.json."""
    try:
        with open(_VERSION_FILE, encoding="utf-8") as f:
            return json.load(f).get("version", "?")
    except Exception:
        return "?"


# --- Frontend ---


@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the Home Hub SPA."""
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Frontend no encontrado</h1>",
            status_code=404,
        )
    return FileResponse(str(index_path))


# --- API ---


@router.get("/health")
async def health():
    """Health check del Home Hub."""
    return {
        "status": "ok",
        "service": "home",
        "port": get_home_port(),
        "version": _load_version(),
    }


@router.get("/api/v1/home/version")
async def version_info():
    """Devuelve la versión del proyecto."""
    return {"version": _load_version()}


@router.get("/api/v1/home/status")
async def aggregate_status():
    """Health check agregado de todos los subsistemas.

    Hace requests async con timeout corto a cada servicio registrado.
    Retorna el estado de cada uno sin bloquear.
    """
    results = []
    async with httpx.AsyncClient(timeout=2.0) as client:
        for svc in SERVICES:
            port = svc["port_fn"]()
            url = f"http://127.0.0.1:{port}{svc['health_path']}"
            entry = {
                "id": svc["id"],
                "name": svc["name"],
                "description": svc["description"],
                "port": port,
                "ui_path": svc["ui_path"],
                "icon": svc["icon"],
                "accent": svc["accent"],
                "status": "unknown",
                "details": None,
            }
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    entry["status"] = "online"
                    entry["details"] = resp.json()
                else:
                    entry["status"] = "error"
            except Exception:
                entry["status"] = "offline"

            results.append(entry)

    online_count = sum(1 for r in results if r["status"] == "online")
    return {
        "version": _load_version(),
        "services": results,
        "total": len(results),
        "online": online_count,
        "offline": len(results) - online_count,
    }


def create_app() -> FastAPI:
    """Create the Home Hub FastAPI application."""
    application = FastAPI(
        title="LOLCLI Home — Centro de Operaciones",
        description="Hub central de acceso a todos los subsistemas de riot_lol_cli.",
        version="1.0.0",
    )

    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Expose the canonical design system so the SPA can link to it.
    if _DESIGN_SYSTEM_DIR.exists():
        application.mount(
            "/design-system",
            StaticFiles(directory=str(_DESIGN_SYSTEM_DIR)),
            name="design-system",
        )

    # Expose Junglas Pro project
    if _JUNGLAS_PRO_DIR.exists():
        application.mount(
            "/junglas-pro",
            StaticFiles(directory=str(_JUNGLAS_PRO_DIR), html=True),
            name="junglas-pro",
        )

    application.include_router(router)
    return application


app = create_app()


# --- Entry point ---


def run() -> None:
    """Levanta el servidor en puerto configurado (default 8080)."""
    import uvicorn

    host = get_home_host()
    port = get_home_port()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Home Hub en http://%s:%d", host, port)
    logger.info("API docs en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
