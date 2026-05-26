"""
Duo Analiser Server — FastAPI endpoint for best jungle synergies and duo analysis.

Puerto: 8006
Endpoints: /health, /api/v1/duo/champions, /api/v1/duo/synergies/{champion_id}
Sirve el frontend SPA interactivo en la raíz del servicio.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.http_utils import UTF8JSONResponse
from riot_lol_cli.settings import get_duo_analiser_host, get_duo_analiser_port

from .api import router as api_router

logger = logging.getLogger(__name__)

_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_FAVICON_PATH = _STATIC_DIR / "favicon.svg"
_DESIGN_SYSTEM_DIR = _MODULE_DIR.parent / "draft_advisor" / "static" / "design-system"

router = APIRouter()


# --- Frontend Static Routes ---

@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Sirve el visor e index HTML principal del Duo Analiser."""
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Duo Analiser: Frontend no encontrado</h1><p>Verificá la existencia del archivo index.html en static.</p>",
            status_code=404,
        )
    return FileResponse(str(index_path))


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Evita 404s ruidosos sirviendo el favicon explícito de static."""
    if _FAVICON_PATH.exists():
        return FileResponse(str(_FAVICON_PATH), media_type="image/svg+xml")
    return Response(status_code=204)


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI para Duo Analiser."""
    application = FastAPI(
        title="Duo Analiser — LoL Champion Synergies",
        description="Encuentra las mejores sinergias y dúos entre carriles individuales y la jungla.",
        version="1.0.0",
        default_response_class=UTF8JSONResponse,
    )

    # Routers primero para que las rutas de API no se vean opacadas por mounts estáticos
    application.include_router(router)
    application.include_router(api_router)

    # Mount del directorio static propio
    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Mount virtual de la biblioteca de patrones centralizada (Design System)
    if _DESIGN_SYSTEM_DIR.exists():
        application.mount(
            "/design-system",
            StaticFiles(directory=str(_DESIGN_SYSTEM_DIR)),
            name="design-system",
        )
    else:
        logger.warning("Design system central no encontrado en: %s", _DESIGN_SYSTEM_DIR)

    return application


app = create_app()


# --- Entry Point command ---

def run() -> None:
    """Levanta el servidor en host y puerto configurados (puerto por defecto 8006)."""
    import uvicorn

    host = get_duo_analiser_host()
    port = get_duo_analiser_port()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Duo Analiser Server en http://%s:%d", host, port)
    logger.info("Visualizador interactivo en http://%s:%d", host, port)
    logger.info("API Docs en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
