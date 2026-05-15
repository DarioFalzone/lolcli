"""Patch Notes Server — FastAPI (puerto 8005) — V2.

V2 agrega:
- `/api/v1/patch-notes/{version}/sources` — lista enrichments por patch.
- `/api/v1/patch-notes/{version}/sources/{source}` — payload específico.
- `/api/v1/patch-notes/search?q=&locale=` — búsqueda full-text.
- `/api/v1/patch-notes/diff/{a}/{b}?locale=` — diff entre dos versiones.
- `/api/v1/patch-notes/scrape/{source}` — dispara un solo source.
- `/api/v1/patch-notes/sources/registry` — registro de adapters disponibles.
- Hook de startup: build_index() para search.
- Hook opcional: APScheduler si LOLCLI_PATCH_NOTES_CRON_ENABLED=1.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from riot_lol_cli.http_utils import UTF8JSONResponse
from riot_lol_cli.settings import (
    get_patch_notes_cron_enabled,
    get_patch_notes_host,
    get_patch_notes_max_patches,
    get_patch_notes_port,
)

from .diff import diff_patches
from .loader import (
    available_locales,
    list_enrichments_for_patch,
    list_patches,
    list_sources_with_data,
    load_enrichment_for_patch,
    load_manifest_safe,
    load_patch,
    patch_count,
)
from .messages import (
    CANONICAL_SOURCE,
    DEFAULT_LOCALE,
    ENRICHMENT_SOURCES,
    SOURCE_LABELS,
    SUPPORTED_LOCALES,
)
from .orchestrator import create_default_orchestrator
from .schema import PatchDiff
from .search import build_index, index_status, search

logger = logging.getLogger(__name__)

_MODULE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _MODULE_DIR / "static"
_FAVICON_PATH = _STATIC_DIR / "favicon.svg"
_DESIGN_SYSTEM_DIR = _MODULE_DIR.parent / "draft_advisor" / "static" / "design-system"

router = APIRouter()

# Lazy: el orchestrator crea Playwright recién al primer scrape.
_orchestrator = None
_scheduler = None


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = create_default_orchestrator()
    return _orchestrator


# --- Frontend ---


@router.get("/", response_class=HTMLResponse)
async def serve_frontend() -> Response:
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(content="<h1>Frontend no encontrado</h1>", status_code=404)
    return FileResponse(str(index_path))


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    if _FAVICON_PATH.exists():
        return FileResponse(str(_FAVICON_PATH), media_type="image/svg+xml")
    return Response(status_code=204)


# --- API ---


SUBSYSTEM_VERSION = "2.2.0"
"""V2.2 = español-only + visual enrichment + scroll-to-top transversal.
V2.5 sub-features (lifespan, riot_calendar Playwright fallback) son refinamientos
sobre V2.2 sin cambiar el contract público."""


@router.get("/health")
async def health() -> dict:
    manifest = load_manifest_safe()
    return {
        "status": "ok",
        "service": "patch_notes",
        "version": SUBSYSTEM_VERSION,
        "port": get_patch_notes_port(),
        "patch_count": patch_count(),
        "locales": available_locales(),
        "last_scrape": manifest.last_scrape.isoformat() if manifest.last_scrape else None,
        "scraper_available": _get_orchestrator() is not None,
        "search_index": index_status(),
        "cron_enabled": get_patch_notes_cron_enabled(),
    }


@router.get("/api/v1/patch-notes/list")
async def api_list_patches(
    locale: str | None = Query(default=None, description="es-es / es-mx / en-us"),
) -> dict:
    if locale is not None and locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail=f"locale debe ser uno de {SUPPORTED_LOCALES}")
    items = list_patches(locale=locale)
    return {
        "locale_filter": locale,
        "count": len(items),
        "items": [i.model_dump(mode="json") for i in items],
    }


@router.get("/api/v1/patch-notes/manifest")
async def api_manifest() -> dict:
    """Manifest crudo incluyendo `sources_status` (V2)."""
    from .normalizer import _read_manifest_raw  # acceso directo al dict para V2

    return _read_manifest_raw()


@router.get("/api/v1/patch-notes/sources/registry")
async def api_sources_registry() -> dict:
    """Registro de adapters configurados + estado del último scrape por fuente."""
    from .normalizer import _read_manifest_raw

    manifest = _read_manifest_raw()
    sources_status = manifest.get("sources_status", {})

    orchestrator = _get_orchestrator()
    enrichment_keys = list(orchestrator.enrichment_adapters.keys()) if orchestrator else []
    canonical_available = orchestrator is not None and orchestrator.adapter is not None

    registry = []
    # Canonical primero
    registry.append(
        {
            "source": CANONICAL_SOURCE,
            "label": SOURCE_LABELS.get(CANONICAL_SOURCE, CANONICAL_SOURCE),
            "kind": "canonical",
            "available": canonical_available,
            "status": sources_status.get(CANONICAL_SOURCE, {}),
        }
    )
    for source in ENRICHMENT_SOURCES:
        registry.append(
            {
                "source": source,
                "label": SOURCE_LABELS.get(source, source),
                "kind": "enrichment",
                "available": source in enrichment_keys,
                "status": sources_status.get(source, {}),
            }
        )
    return {"registry": registry, "count": len(registry)}


@router.get("/api/v1/patch-notes/search")
async def api_search(
    q: str = Query(..., min_length=2, description="Texto a buscar"),
    locale: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    if locale is not None and locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail=f"locale debe ser uno de {SUPPORTED_LOCALES}")
    hits = search(q, locale=locale, limit=limit)
    return {
        "query": q,
        "locale": locale,
        "count": len(hits),
        "hits": [h.model_dump(mode="json") for h in hits],
    }


@router.get("/api/v1/patch-notes/diff/{a_version}/{b_version}")
async def api_diff(
    a_version: str,
    b_version: str,
    locale: str = Query(default=DEFAULT_LOCALE),
) -> dict:
    if locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail=f"locale debe ser uno de {SUPPORTED_LOCALES}")
    a = load_patch(a_version, locale=locale)
    b = load_patch(b_version, locale=locale)
    if a is None or b is None:
        missing = [v for v, n in [(a_version, a), (b_version, b)] if n is None]
        raise HTTPException(status_code=404, detail=f"Patches no encontrados: {missing}")
    diff: PatchDiff = diff_patches(a, b)
    return diff.model_dump(mode="json")


@router.get("/api/v1/patch-notes/{patch_version}/sources")
async def api_patch_sources(patch_version: str) -> dict:
    """Lista los enrichments disponibles para este patch."""
    enrichments = list_enrichments_for_patch(patch_version)
    return {
        "patch_version": patch_version,
        "count": len(enrichments),
        "available_sources": list_sources_with_data(patch_version),
        "enrichments": [
            {
                **e.model_dump(mode="json"),
                "label": SOURCE_LABELS.get(e.source, e.source),
            }
            for e in enrichments
        ],
    }


@router.get("/api/v1/patch-notes/{patch_version}/sources/{source}")
async def api_patch_source_detail(patch_version: str, source: str) -> dict:
    """Payload específico de una fuente para este patch."""
    enrichment = load_enrichment_for_patch(source, patch_version)
    if enrichment is None:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos de '{source}' para patch '{patch_version}'",
        )
    return {
        **enrichment.model_dump(mode="json"),
        "label": SOURCE_LABELS.get(enrichment.source, enrichment.source),
    }


@router.get("/api/v1/patch-notes/{patch_version}")
async def api_get_patch(
    patch_version: str,
    locale: str = Query(default=DEFAULT_LOCALE),
) -> dict:
    """Patch completo + enrichments hidratados."""
    if locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail=f"locale debe ser uno de {SUPPORTED_LOCALES}")
    note = load_patch(patch_version, locale=locale)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Patch '{patch_version}' en '{locale}' no encontrado")
    return note.model_dump(mode="json")


@router.post("/api/v1/patch-notes/scrape")
async def api_scrape(
    background_tasks: BackgroundTasks,
    max_patches: int = Query(default=None, ge=1, le=30),
    locales: str | None = Query(default=None, description="CSV de locales; default = todos"),
) -> dict:
    orchestrator = _get_orchestrator()
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Playwright no disponible. Ejecutá `playwright install chromium`.",
        )
    if orchestrator.is_running:
        raise HTTPException(status_code=409, detail="Ya hay un scraping en curso.")

    locale_tuple = SUPPORTED_LOCALES
    if locales:
        locale_tuple = tuple(loc.strip() for loc in locales.split(",") if loc.strip())
        invalid = [loc for loc in locale_tuple if loc not in SUPPORTED_LOCALES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"locales inválidos: {invalid}")

    effective_max = max_patches if max_patches else get_patch_notes_max_patches()

    def _run() -> None:
        try:
            orchestrator.run_full_scrape(locales=locale_tuple, max_patches=effective_max)
            build_index()
        except Exception as e:
            logger.error("[patch_notes/server] scrape background falló: %s", e, exc_info=True)

    # Usar threading.Thread en vez de BackgroundTasks: Playwright sync no puede
    # correr dentro del event loop asyncio de FastAPI (incluso si la func es sync,
    # BackgroundTasks la ejecuta en el threadpool de starlette PERO el loop sigue
    # activo y Playwright detecta `running asyncio loop` y rechaza el segundo start).
    import threading

    threading.Thread(target=_run, daemon=True, name="patch_notes_scrape").start()
    return {
        "status": "started",
        "locales": list(locale_tuple),
        "max_patches": effective_max,
    }


@router.post("/api/v1/patch-notes/scrape/{source}")
async def api_scrape_source(
    source: str,
    background_tasks: BackgroundTasks,
    patch_version: str | None = Query(default=None),
    locale: str | None = Query(default=None),
) -> dict:
    """Dispara un solo source. patch_version requerido para enrichments per-patch."""
    orchestrator = _get_orchestrator()
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator no disponible")
    if orchestrator.is_running:
        raise HTTPException(status_code=409, detail="Ya hay un scraping en curso")

    valid_sources = [CANONICAL_SOURCE, *ENRICHMENT_SOURCES]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"source debe ser uno de {valid_sources}")

    def _run() -> None:
        try:
            orchestrator.run_source_scrape(source, patch_version=patch_version, locale=locale)
            build_index()
        except Exception as e:
            logger.error("[patch_notes/server] scrape source %s falló: %s", source, e, exc_info=True)

    import threading

    threading.Thread(target=_run, daemon=True, name=f"patch_notes_scrape_{source}").start()
    return {
        "status": "started",
        "source": source,
        "patch_version": patch_version,
        "locale": locale,
    }


# --- App factory ---


@asynccontextmanager
async def _lifespan(application: FastAPI):
    """Reemplaza los `on_event("startup"|"shutdown")` deprecated de FastAPI."""
    # Startup: build_index + scheduler opcional
    try:
        build_index()
    except Exception as e:
        logger.warning("[patch_notes/server] build_index al startup falló: %s", e)

    if get_patch_notes_cron_enabled():
        try:
            from .scheduler import setup_scheduler

            orchestrator = _get_orchestrator()
            if orchestrator is not None:
                global _scheduler
                _scheduler = setup_scheduler(orchestrator)
                application.state.scheduler = _scheduler
        except Exception as e:
            logger.warning("[patch_notes/server] scheduler no se pudo arrancar: %s", e)

    yield

    # Shutdown: cierre del scheduler
    try:
        from .scheduler import shutdown_scheduler

        shutdown_scheduler(_scheduler)
    except Exception as e:
        logger.warning("[patch_notes/server] shutdown_scheduler falló: %s", e)


def create_app() -> FastAPI:
    application = FastAPI(
        title="LOLCLI Patch Notes V2",
        description="Visor + scraper multi-source de patch notes oficiales de LoL.",
        version=SUBSYSTEM_VERSION,
        lifespan=_lifespan,
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

    application.include_router(router)
    return application


app = create_app()


def run() -> None:
    import uvicorn

    host = get_patch_notes_host()
    port = get_patch_notes_port()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Levantando Patch Notes V2 en http://%s:%d", host, port)
    logger.info("API docs en http://%s:%d/docs", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
