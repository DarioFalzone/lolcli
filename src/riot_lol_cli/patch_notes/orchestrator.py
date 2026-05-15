"""Orquestador del pipeline de patch notes — V2 multi-source.

Flujo por ejecución (`run_full_scrape`):
1. **Phase 1 — Canonical**: corre `lol_official.discover(locale)` + `extract(url, locale)`
   para cada URL nueva por locale; persiste el `PatchNote` en `by_patch/`.
2. **Phase 2 — Enrichments globales**: corre `ddragon` y `riot_calendar` una sola vez
   (no dependen de patch específico) — `snapshot.json` por cada fuente.
3. **Phase 3 — Enrichments per-patch**: para cada patch persistido en phase 1,
   corre `lol_dev`, `ugg_patch`, `opgg_patch`, `lolalytics_patch`, `mobalytics_patch`.
   Cada fuente persiste un `{patch}.json` o falla con `error`.
4. **Phase 4 — Manifest update**: actualiza `manifest.json` con `sources_status`.

Tolerancia: si un adapter falla, su `enrichment` queda con `error` y el flujo sigue.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from .adapters.base import PatchNotesAdapterBase
from .messages import (
    SCRAPER_VERSION,
    SOURCE_DDRAGON,
    SOURCE_LOL_DEV,
    SOURCE_LOL_OFFICIAL,
    SOURCE_LOLALYTICS_PATCH,
    SOURCE_MOBALYTICS_BREAKDOWN,
    SOURCE_MOBALYTICS_PATCH,
    SOURCE_OPGG_PATCH,
    SOURCE_RIOT_CALENDAR,
    SOURCE_UGG_PATCH,
    SUPPORTED_LOCALES,
)
from .normalizer import (
    compute_content_hash,
    detect_change,
    save_enrichment,
    save_normalized,
    update_manifest,
    update_source_status,
)
from .schema import PatchNote, PatchSection

logger = logging.getLogger(__name__)

# Sources que no dependen de un patch específico — un único snapshot global.
_GLOBAL_SOURCES = (SOURCE_DDRAGON, SOURCE_RIOT_CALENDAR)
# Sources que adjuntan datos por patch — corren después de phase 1.
_PER_PATCH_SOURCES = (
    SOURCE_LOL_DEV,
    SOURCE_UGG_PATCH,
    SOURCE_OPGG_PATCH,
    SOURCE_LOLALYTICS_PATCH,
    SOURCE_MOBALYTICS_PATCH,
    SOURCE_MOBALYTICS_BREAKDOWN,
)


class PatchNotesOrchestrator:
    """Coordina canonical scraping + enrichments multi-source."""

    def __init__(
        self,
        adapter: PatchNotesAdapterBase | None = None,
        enrichment_adapters: dict[str, PatchNotesAdapterBase] | None = None,
    ) -> None:
        self.adapter = adapter
        self.enrichment_adapters: dict[str, PatchNotesAdapterBase] = enrichment_adapters or {}
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def register_enrichment_adapter(self, source: str, adapter: PatchNotesAdapterBase) -> None:
        self.enrichment_adapters[source] = adapter

    def run_full_scrape(
        self,
        locales: tuple[str, ...] = SUPPORTED_LOCALES,
        max_patches: int = 6,
    ) -> dict[str, Any]:
        """Pipeline completo: canonical → globals → per-patch enrichments."""
        if self.adapter is None:
            raise RuntimeError("No hay adapter canónico registrado.")
        if self._is_running:
            raise RuntimeError("Ya hay un scraping de patch notes en curso.")

        self._is_running = True
        summary: dict[str, Any] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "locales": list(locales),
            "max_patches": max_patches,
            "canonical": {},
            "global_enrichments": {},
            "per_patch_enrichments": {},
            "errors": [],
        }

        patches_to_enrich: set[str] = set()

        try:
            # Phase 1 — Canonical
            summary["canonical"] = self._scrape_canonical(locales, max_patches, patches_to_enrich)
            # Importante: cerrar el adapter canonical YA para liberar el slot Playwright
            # del thread. Sync Playwright solo admite UNA instancia activa por thread.
            try:
                if self.adapter is not None:
                    self.adapter.close()
            except Exception as e:
                logger.warning("[orchestrator] cierre temprano canonical: %s", e)

            # Phase 2 — Global enrichments (independientes del patch)
            summary["global_enrichments"] = self._scrape_global_enrichments()

            # Phase 3 — Per-patch enrichments
            if patches_to_enrich:
                summary["per_patch_enrichments"] = self._scrape_per_patch_enrichments(
                    sorted(patches_to_enrich)
                )

        finally:
            self._close_all_adapters()
            self._is_running = False

        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        return summary

    def run_source_scrape(
        self,
        source: str,
        patch_version: str | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        """Dispara un único source en background. patch_version requerido para per-patch."""
        if source == SOURCE_LOL_OFFICIAL:
            return self._scrape_canonical(
                (locale,) if locale else SUPPORTED_LOCALES,
                max_patches=3,
                tracked_patches=set(),
            )
        if source in _GLOBAL_SOURCES:
            return self._scrape_one_global(source)
        if source in _PER_PATCH_SOURCES:
            if patch_version is None:
                raise ValueError(f"source {source} requiere patch_version")
            return self._scrape_one_per_patch(source, patch_version)
        raise ValueError(f"source desconocido: {source}")

    def refresh_global_enrichments(self) -> dict[str, Any]:
        """Refresca solo los snapshots globales (ddragon, calendar)."""
        return self._scrape_global_enrichments()

    # ---- Phases ----

    def _scrape_canonical(
        self,
        locales: tuple[str, ...],
        max_patches: int,
        tracked_patches: set[str],
    ) -> dict[str, Any]:
        results: dict[str, Any] = {}
        adapter = self.adapter
        if adapter is None:
            return results

        for locale in locales:
            entry = {"discovered": 0, "saved": 0, "unchanged": 0, "errors": []}
            try:
                urls = adapter.discover(locale, max_patches=max_patches)
                entry["discovered"] = len(urls)
            except Exception as e:
                logger.error("[orchestrator] discover %s falló: %s", locale, e, exc_info=True)
                entry["errors"].append({"stage": "discover", "reason": str(e)})
                update_source_status(SOURCE_LOL_OFFICIAL, success=False, error=f"discover:{e}")
                results[locale] = entry
                continue

            for url in urls:
                try:
                    raw = adapter.extract(url, locale)
                    note = _build_patch_note(raw)
                    if not detect_change(note.patch_version, note.source_locale, note.content_hash):
                        entry["unchanged"] += 1
                        tracked_patches.add(note.patch_version)
                        continue
                    save_normalized(note)
                    update_manifest(note)
                    entry["saved"] += 1
                    tracked_patches.add(note.patch_version)
                except Exception as e:
                    logger.error("[orchestrator] extract %s falló: %s", url, e, exc_info=True)
                    entry["errors"].append({"url": url, "reason": str(e)})

            results[locale] = entry

        update_source_status(
            SOURCE_LOL_OFFICIAL,
            success=any(e["saved"] > 0 or e["unchanged"] > 0 for e in results.values()),
            error=None,
        )
        return results

    def _scrape_global_enrichments(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for source in _GLOBAL_SOURCES:
            out[source] = self._scrape_one_global(source)
        return out

    def _scrape_one_global(self, source: str) -> dict[str, Any]:
        adapter = self.enrichment_adapters.get(source)
        if adapter is None:
            update_source_status(source, success=False, error="adapter no registrado")
            return {"status": "missing_adapter"}
        try:
            urls = adapter.discover(locale="es-es", max_patches=1)
            url = urls[0] if urls else None
            if url is None:
                raise RuntimeError("discover devolvió 0 URLs")
            payload = adapter.extract(url, locale="es-es")
            save_enrichment(source, patch_version=None, payload=payload, source_url=url)
            update_source_status(source, success=True)
            result = {"status": "ok", "source_url": url}
        except Exception as e:
            logger.error("[orchestrator] global %s falló: %s", source, e, exc_info=True)
            save_enrichment(source, patch_version=None, payload={}, error=str(e))
            update_source_status(source, success=False, error=str(e))
            result = {"status": "error", "reason": str(e)}

        # Cierre temprano del adapter (liberar Playwright si lo abrió).
        try:
            adapter.close()
        except Exception as e:
            logger.warning("[orchestrator] cierre %s falló: %s", source, e)
        return result

    def _scrape_per_patch_enrichments(self, patches: list[str]) -> dict[str, Any]:
        out: dict[str, dict[str, Any]] = {}
        for patch_version in patches:
            patch_results: dict[str, Any] = {}
            for source in _PER_PATCH_SOURCES:
                patch_results[source] = self._scrape_one_per_patch(source, patch_version)
            out[patch_version] = patch_results
        return out

    def _scrape_one_per_patch(self, source: str, patch_version: str) -> dict[str, Any]:
        adapter = self.enrichment_adapters.get(source)
        if adapter is None:
            update_source_status(source, success=False, patch_version=patch_version, error="adapter no registrado")
            return {"status": "missing_adapter"}
        try:
            urls = adapter.discover(locale="es-es", max_patches=1)
            url = urls[0] if urls else None
            if url is None:
                raise RuntimeError("discover devolvió 0 URLs")
            # extract() acepta patch_version como kwarg en adapters comunitarios
            try:
                payload = adapter.extract(url, locale="es-es", patch_version=patch_version)
            except TypeError:
                payload = adapter.extract(url, locale="es-es")
            save_enrichment(source, patch_version=patch_version, payload=payload, source_url=url)
            update_source_status(source, success=True, patch_version=patch_version)
            result = {"status": "ok", "source_url": url}
        except Exception as e:
            logger.error("[orchestrator] %s/%s falló: %s", source, patch_version, e, exc_info=True)
            save_enrichment(source, patch_version=patch_version, payload={}, error=str(e))
            update_source_status(source, success=False, patch_version=patch_version, error=str(e))
            result = {"status": "error", "reason": str(e)}

        # Cerrar el adapter después de cada extracción para liberar Playwright.
        # Esto permite que el siguiente adapter sync abra su propio chromium en el mismo thread.
        try:
            adapter.close()
        except Exception as e:
            logger.warning("[orchestrator] cierre %s falló: %s", source, e)
        return result

    def _close_all_adapters(self) -> None:
        if self.adapter is not None:
            try:
                self.adapter.close()
            except Exception as e:
                logger.warning("[orchestrator] cierre canónico falló: %s", e)
        for source, adapter in self.enrichment_adapters.items():
            try:
                adapter.close()
            except Exception as e:
                logger.warning("[orchestrator] cierre %s falló: %s", source, e)


def _build_patch_note(raw: dict[str, Any]) -> PatchNote:
    sections = [PatchSection.model_validate(s) for s in raw.get("sections", [])]
    content_hash = compute_content_hash(sections)
    return PatchNote.model_validate(
        {
            **raw,
            "sections": [s.model_dump() for s in sections],
            "content_hash": content_hash,
            "scraper_version": SCRAPER_VERSION,
        }
    )


def create_default_orchestrator() -> PatchNotesOrchestrator | None:
    """Factory: registra el adapter canónico + todos los enrichment adapters disponibles."""
    canonical_adapter: PatchNotesAdapterBase | None = None
    try:
        from .adapters.lol_official import LolOfficialAdapter

        canonical_adapter = LolOfficialAdapter()
    except ImportError as e:
        logger.warning("[orchestrator] LolOfficialAdapter no disponible: %s", e)

    if canonical_adapter is None:
        return None

    orchestrator = PatchNotesOrchestrator(adapter=canonical_adapter)

    enrichment_factories = [
        (SOURCE_DDRAGON, "ddragon", "DDragonAdapter"),
        (SOURCE_RIOT_CALENDAR, "riot_calendar", "RiotCalendarAdapter"),
        (SOURCE_LOL_DEV, "lol_dev", "LolDevAdapter"),
        (SOURCE_LOLALYTICS_PATCH, "lolalytics_patch", "LolalyticsPatchAdapter"),
        (SOURCE_UGG_PATCH, "ugg_patch", "UggPatchAdapter"),
        (SOURCE_OPGG_PATCH, "opgg_patch", "OpggPatchAdapter"),
        (SOURCE_MOBALYTICS_PATCH, "mobalytics_patch", "MobalyticsPatchAdapter"),
    ]

    for source_id, module_name, class_name in enrichment_factories:
        try:
            module = __import__(
                f"riot_lol_cli.patch_notes.adapters.{module_name}",
                fromlist=[class_name],
            )
            cls = getattr(module, class_name)
            orchestrator.register_enrichment_adapter(source_id, cls())
        except (ImportError, AttributeError) as e:
            logger.warning("[orchestrator] adapter %s no disponible: %s", source_id, e)

    return orchestrator
