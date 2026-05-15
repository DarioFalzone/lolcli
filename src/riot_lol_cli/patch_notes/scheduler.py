"""APScheduler hooks opcionales para el subsistema patch_notes.

Solo se inicia si `LOLCLI_PATCH_NOTES_CRON_ENABLED=1`. El scheduler vive
dentro del proceso uvicorn (BackgroundScheduler) y se apaga al shutdown.

Jobs:
- Daily 12:00 UTC — `run_full_scrape(max_patches=5)`: pickup de parches nuevos.
- Weekly Monday 03:00 UTC — refresh de enrichments globales (calendar + ddragon).
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


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
    scheduler.start()
    logger.info("[scheduler] APScheduler iniciado (2 jobs)")
    return scheduler


def shutdown_scheduler(scheduler: BackgroundScheduler | None) -> None:
    if scheduler is None:
        return
    try:
        scheduler.shutdown(wait=False)
        logger.info("[scheduler] APScheduler detenido")
    except Exception as e:
        logger.warning("[scheduler] Error al apagar scheduler: %s", e)
