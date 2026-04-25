from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import text

from riot_lol_cli.meta_api import dependencies


router = APIRouter(tags=["maintenance"])


@router.post("/api/v1/maintenance/cleanup")
async def trigger_cleanup(background_tasks: BackgroundTasks):
    """Dispara limpieza de datos antiguos."""
    background_tasks.add_task(dependencies.db.cleanup_old_matches, hours=48)
    return {
        "success": True,
        "message": "Cleanup triggered in background",
        "timestamp": dependencies.utcnow_iso(),
    }


@router.get("/api/v1/maintenance/status")
async def get_maintenance_status():
    """Obtiene estado del sistema."""
    try:
        with dependencies.session_scope() as session:
            session.execute(text("SELECT 1"))

        return {
            "success": True,
            "status": "healthy",
            "database": "connected",
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "degraded",
            "database": "disconnected",
            "error": str(exc),
            "timestamp": dependencies.utcnow_iso(),
        }
