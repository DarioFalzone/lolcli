"""APScheduler hooks opcionales para el subsistema patch_notes.

Solo se inicia si `LOLCLI_PATCH_NOTES_CRON_ENABLED=1`. El scheduler vive
dentro del proceso uvicorn (BackgroundScheduler) y se apaga al shutdown.

Jobs:
- Daily 12:00 UTC — `run_full_scrape(max_patches=5)`: pickup de parches nuevos.
- Weekly Monday 03:00 UTC — refresh de enrichments globales (calendar + ddragon).
- Daily 12:30 UTC (opcional) — export a MongoDB Atlas. Solo si
  `LOLCLI_MONGO_EXPORT_CRON_ENABLED=1` y `LOLCLI_MONGO_URI` esta configurado.
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from riot_lol_cli import settings

logger = logging.getLogger(__name__)


def _load_mongo_export() -> Callable[..., int] | None:
    """Carga `run_export` desde scripts/export_patch_notes_to_mongo.py.

    Usa importlib porque `scripts/` no es un package Python. Devuelve None si
    el archivo no existe o falla la carga (ej: pymongo no instalado).
    """
    script_path = (
        Path(__file__).resolve().parents[3] / "scripts" / "export_patch_notes_to_mongo.py"
    )
    if not script_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "export_patch_notes_to_mongo", script_path
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.run_export
    except Exception as e:
        logger.warning("[scheduler] Fallo cargar Mongo export: %s", e)
        return None


def setup_scheduler(orchestrator) -> BackgroundScheduler:
    """Crea y arranca el scheduler. El caller guarda la referencia para shutdown."""
    scheduler = BackgroundScheduler(timezone="UTC")

    def _daily_job() -> None:
        logger.info("[scheduler] Iniciando job diario de scraping")
        try:
            orchestrator.run_full_scrape(max_patches=5)
        except Exception as e:
            logger.error("[scheduler] Job diario falló: %s", e, exc_info=True)

    def _weekly_refresh_job() -> None:
        logger.info("[scheduler] Iniciando refresh semanal de enrichments globales")
        try:
            orchestrator.refresh_global_enrichments()
        except Exception as e:
            logger.error("[scheduler] Refresh semanal falló: %s", e, exc_info=True)

    scheduler.add_job(
        _daily_job,
        "cron",
        hour=12,
        minute=0,
        id="patch_notes_daily_scrape",
        replace_existing=True,
    )
    scheduler.add_job(
        _weekly_refresh_job,
        "cron",
        day_of_week="mon",
        hour=3,
        minute=0,
        id="patch_notes_weekly_global_refresh",
        replace_existing=True,
    )

    jobs_count = 2

    # Job opcional: export a MongoDB Atlas tras el scrape diario.
    if settings.get_mongo_export_cron_enabled() and settings.get_mongo_uri():
        run_export = _load_mongo_export()
        if run_export is None:
            logger.warning(
                "[scheduler] No se pudo cargar scripts/export_patch_notes_to_mongo.py; "
                "Mongo export job desactivado"
            )
        else:
            def _mongo_export_job() -> None:
                logger.info("[scheduler] Iniciando export a MongoDB Atlas")
                try:
                    run_export(dry_run=False)
                except Exception as e:
                    logger.error("[scheduler] Mongo export falló: %s", e, exc_info=True)

            scheduler.add_job(
                _mongo_export_job,
                "cron",
                hour=12,
                minute=30,
                id="patch_notes_mongo_export",
                replace_existing=True,
            )
            jobs_count += 1
            logger.info("[scheduler] Mongo export job registrado (daily 12:30 UTC)")

    scheduler.start()
    logger.info("[scheduler] APScheduler iniciado (%d jobs)", jobs_count)
    return scheduler


def shutdown_scheduler(scheduler: BackgroundScheduler | None) -> None:
    if scheduler is None:
        return
    try:
        scheduler.shutdown(wait=False)
        logger.info("[scheduler] APScheduler detenido")
    except Exception as e:
        logger.warning("[scheduler] Error al apagar scheduler: %s", e)
