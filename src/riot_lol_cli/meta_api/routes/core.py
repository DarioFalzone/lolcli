from fastapi import APIRouter
from fastapi.responses import FileResponse

from riot_lol_cli.meta_api import dependencies

router = APIRouter(tags=["core"])


@router.get("/health")
async def health_check():
    """Health check básico del backend."""
    return {
        "status": "healthy",
        "timestamp": dependencies.utcnow_iso(),
        "database": "connected",
    }


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
