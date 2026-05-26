from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

from riot_lol_cli import gaps_registry
from riot_lol_cli.meta_api import dependencies

router = APIRouter(tags=["core"])
_META_API_FAVICON = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\">
<defs>
<linearGradient id=\"metaBg\" x1=\"8\" y1=\"8\" x2=\"56\" y2=\"56\" gradientUnits=\"userSpaceOnUse\">
<stop stop-color=\"#0a1e3d\"/><stop offset=\"1\" stop-color=\"#010a13\"/>
</linearGradient>
</defs>
<rect x=\"6\" y=\"6\" width=\"52\" height=\"52\" rx=\"14\" fill=\"url(#metaBg)\"/>
<path d=\"M18 46V20H26V46H18ZM29 38V14H37V38H29ZM40 46V28H48V46H40Z\" fill=\"#f0f0f0\"/>
<path d=\"M16 50H50\" stroke=\"#c89b3c\" stroke-width=\"3\" stroke-linecap=\"round\"/>
</svg>"""


@router.get("/health")
async def health_check():
    """Health check básico del backend."""
    return {
        "status": "healthy",
        "timestamp": dependencies.utcnow_iso(),
        "database": "connected",
    }


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Sirve favicon explicito para el Meta Analyzer."""
    return Response(content=_META_API_FAVICON, media_type="image/svg+xml")


@router.get("/dashboard")
async def get_dashboard():
    """Sirve el dashboard original."""
    dashboard_path = dependencies.output_file("meta-analyzer-dashboard.html")
    if not dashboard_path.exists():
        return {"error": "Dashboard no encontrado. Ejecuta: python scripts/setup_meta_analyzer.py"}
    return FileResponse(str(dashboard_path), media_type="text/html")


@router.get("/dashboard-enhanced")
async def get_dashboard_enhanced():
    """Sirve el dashboard mejorado con tabs avanzados."""
    dashboard_path = dependencies.output_file("meta-analyzer-dashboard-enhanced.html")
    if not dashboard_path.exists():
        return {"error": "Dashboard Enhanced no encontrado. Ejecuta: python scripts/generate_dashboard.py"}
    return FileResponse(str(dashboard_path), media_type="text/html")


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "LOLCLI Meta Analyzer API",
        "version": "1.0.0",
        "dashboards": {
            "original": "/dashboard",
            "enhanced": "/dashboard-enhanced (RECOMENDADO)",
        },
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@router.get("/api/v1/gaps")
async def get_global_gaps():
    """Obtiene la consola consolidada de todos los gaps del repositorio."""
    return gaps_registry.read_global_gaps()
