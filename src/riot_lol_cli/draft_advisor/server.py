"""
Draft Advisor Server — main entry point.

Usage:
    python -m riot_lol_cli.draft_advisor.server

    Then open http://localhost:8001/draft

Note: Runs on port 8001 to avoid conflict with the Meta Analyzer
API server (api_server.py) which uses port 8000.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from riot_lol_cli import paths
from riot_lol_cli.settings import get_draft_advisor_host, get_draft_advisor_port

from .api import router as draft_router

# ============================================================================
# App factory
# ============================================================================

_STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Create the Draft Advisor FastAPI application."""
    application = FastAPI(
        title="Draft Advisor",
        description="Motor de recomendación de picks para League of Legends",
        version="1.1.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(draft_router)

    assets_dir = paths.ASSETS_DIR / "splash_arts"
    if assets_dir.exists():
        application.mount("/assets/splash_arts", StaticFiles(directory=str(assets_dir)), name="splash_arts")

    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @application.get("/draft")
    async def serve_ui():
        """Serve the draft advisor SPA."""
        index = _STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"error": "UI not built yet. Static files not found."}

    @application.get("/")
    async def root():
        """Redirect root to draft UI."""
        return RedirectResponse(url="/draft")

    return application


app = create_app()


# ============================================================================
def run() -> None:
    import uvicorn

    port = get_draft_advisor_port()
    host = get_draft_advisor_host()
    _logger = logging.getLogger(__name__)
    _logger.info("ADC Draft Advisor levantado en http://localhost:%d/draft", port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
