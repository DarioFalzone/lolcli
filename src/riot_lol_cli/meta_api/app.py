from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from riot_lol_cli import paths
from riot_lol_cli.meta_api import dependencies
from riot_lol_cli.meta_api.routes.champions import router as champions_router
from riot_lol_cli.meta_api.routes.core import router as core_router
from riot_lol_cli.meta_api.routes.maintenance import router as maintenance_router
from riot_lol_cli.meta_api.routes.stats import router as stats_router
from riot_lol_cli.settings import get_meta_api_host, get_meta_api_port


def create_app() -> FastAPI:
    app = FastAPI(
        title="LOLCLI Meta Analyzer API",
        description="API para detectar cambios en el meta de League of Legends",
        version="1.0.0",
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

    @app.on_event("startup")
    async def startup_event():
        try:
            dependencies.db.init_db()
            dependencies.logger.info("✅ BD inicializada correctamente")
        except Exception as exc:
            dependencies.logger.error("❌ Error inicializando BD: %s", exc)

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
    return app


app = create_app()


def run() -> None:
    import uvicorn

    host = get_meta_api_host()
    port = get_meta_api_port()
    print(f"🚀 Levantando API en http://localhost:{port}")
    print(f"📚 Documentación en http://localhost:{port}/docs")
    uvicorn.run(app, host=host, port=port, reload=False)
