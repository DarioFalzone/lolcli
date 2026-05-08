"""
Items Browser Server — FastAPI endpoint para catalogar items de LoL.

Puerto: 8004 (configurable via LOLCLI_ITEMS_BROWSER_PORT).
Endpoints: /api/v1/items/all, /api/v1/items/{id}, /api/v1/items/groups,
/api/v1/items/categories, /api/v1/items/search?q=
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.settings import get_items_browser_host, get_items_browser_port

from .loader import (
    get_item,
    list_categories,
    list_groups,
    load_items_database,
    search_items,
)

logger = logging.getLogger(__name__)

_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_ITEMS_ASSETS_DIR = _MODULE_DIR.parent.parent.parent / "assets" / "items"

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Frontend no encontrado</h1>",
            status_code=404,
        )
    return FileResponse(str(index_path))


@router.get("/health")
async def health():
    try:
        db = load_items_database()
        return {
            "status": "ok",
            "service": "items_browser",
            "port": get_items_browser_port(),
            "version": db.get("version"),
            "total_count": db.get("total_count", 0),
            "current_count": db.get("current_count", 0),
            "deprecated_count": db.get("deprecated_count", 0),
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return {"status": "error", "service": "items_browser", "error": str(e)}


@router.get("/api/v1/items/all")
async def get_all_items(
    include_deprecated: bool = Query(False, description="Incluir items obsoletos"),
):
    try:
        db = load_items_database()
        items = db.get("items", [])
        if not include_deprecated:
            items = [i for i in items if not i.get("deprecated")]
        return {
            "version": db.get("version"),
            "count": len(items),
            "items": items,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/v1/items/groups")
async def get_groups():
    try:
        return {"groups": list_groups()}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/v1/items/categories")
async def get_categories():
    try:
        return {"categories": list_categories()}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/v1/items/search")
async def search(
    q: str = Query(..., min_length=1),
    lang: str = Query("en", pattern="^(en|es)$"),
):
    try:
        results = search_items(q, lang=lang)
        return {"query": q, "lang": lang, "count": len(results), "items": results}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/v1/items/{item_id}")
async def get_one(item_id: int):
    try:
        item = get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_id} no existe")
        return item
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


def create_app() -> FastAPI:
    application = FastAPI(
        title="Items Browser — LoL Item Catalog",
        description="Navega items de League of Legends con nombres EN+ES y filtros por grupo.",
        version="1.0.0",
    )

    if _STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    if _ITEMS_ASSETS_DIR.exists():
        application.mount(
            "/items", StaticFiles(directory=str(_ITEMS_ASSETS_DIR)), name="items"
        )

    application.include_router(router)
    return application


app = create_app()


def run() -> None:
    import uvicorn

    host = get_items_browser_host()
    port = get_items_browser_port()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Items Browser en http://localhost:%d", port)
    logger.info("Dashboard en http://localhost:%d", port)
    logger.info("API docs en http://localhost:%d/docs", port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
