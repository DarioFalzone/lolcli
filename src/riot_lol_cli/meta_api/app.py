import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from riot_lol_cli import paths
from riot_lol_cli.http_utils import UTF8JSONResponse
from riot_lol_cli.meta_api import dependencies
from riot_lol_cli.meta_api.routes.champions import router as champions_router
from riot_lol_cli.meta_api.routes.core import router as core_router
from riot_lol_cli.meta_api.routes.esports import router as esports_router
from riot_lol_cli.meta_api.routes.jungle_research import router as jungle_research_router
from riot_lol_cli.meta_api.routes.maintenance import router as maintenance_router
from riot_lol_cli.meta_api.routes.stats import router as stats_router
from riot_lol_cli.settings import get_meta_api_host, get_meta_api_port


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            dependencies.db.init_db()
            dependencies.logger.info("✅ BD inicializada correctamente")
        except Exception as exc:
            dependencies.logger.error("❌ Error inicializando BD: %s", exc)
        yield

    app = FastAPI(
        title="LOLCLI Meta Analyzer API",
        description="API para detectar cambios en el meta de League of Legends",
        version="1.0.0",
        lifespan=lifespan,
        default_response_class=UTF8JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    paths.ensure_runtime_directories()
    if paths.OUTPUT_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(paths.OUTPUT_DIR)), name="static")

    design_system_dir = paths.SRC_DIR / "riot_lol_cli" / "draft_advisor" / "static" / "design-system"
    if design_system_dir.exists():
        app.mount("/design-system", StaticFiles(directory=str(design_system_dir)), name="design-system")

    esports_static_dir = paths.SRC_DIR / "riot_lol_cli" / "meta_api" / "static" / "esports"
    if esports_static_dir.exists():
        app.mount("/esports", StaticFiles(directory=str(esports_static_dir), html=True), name="esports")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "timestamp": dependencies.utcnow_iso(),
            },
        )

    app.include_router(core_router)
    app.include_router(stats_router)
    app.include_router(champions_router)
    app.include_router(maintenance_router)
    app.include_router(jungle_research_router)
    app.include_router(esports_router)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    host = get_meta_api_host()
    port = get_meta_api_port()
    _logger = logging.getLogger(__name__)
    _logger.info("Levantando API en http://%s:%d", host, port)
    _logger.info("Documentación en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, reload=False)
