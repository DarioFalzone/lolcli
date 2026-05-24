"""API-side loader: lee JSONs persistidos en `data/patch_notes/` y devuelve modelos.

Sigue el patrón de `jungle_meta/loader.py`: funciones puras sobre paths del módulo.
El server FastAPI lo usa para responder endpoints sin tocar el orchestrator.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .messages import DEFAULT_LOCALE, ENRICHMENT_SOURCES
from .normalizer import (
    _version_sort_key,
    attach_enrichments_to_note,
    get_data_dir,
    list_available_sources_for_patch,
    load_enrichment,
    load_manifest,
)
from .schema import PatchEnrichment, PatchManifest, PatchNote, PatchNoteIndex

logger = logging.getLogger(__name__)


def _by_patch_dir() -> Path:
    return get_data_dir() / "normalized" / "by_patch"


def load_manifest_safe() -> PatchManifest:
    """Wrapper que nunca lanza — devuelve manifest vacío si hay problemas."""
    return load_manifest()


def list_patches(locale: str | None = None) -> list[PatchNoteIndex]:
    """Lista los parches disponibles, ordenados por versión desc.

    Si `locale` es None, devuelve un patch por versión priorizando es-es,
    luego es-mx, luego en-us. Si `locale` se especifica, filtra solo ese.
    """
    manifest = load_manifest()
    if not manifest.entries:
        return []

    entries_by_version: dict[str, dict[str, PatchNoteIndex]] = {}
    for entry in manifest.entries:
        if locale and entry.source_locale != locale:
            continue
        version_bucket = entries_by_version.setdefault(entry.patch_version, {})
        try:
            patch = _read_patch_file(entry.patch_version, entry.source_locale)
            section_count = len(patch.sections) if patch else 0
            summary = patch.summary if patch else None
        except Exception as e:
            logger.warning(
                "[patch_notes/loader] No pude leer %s/%s para indexar: %s",
                entry.patch_version,
                entry.source_locale,
                e,
            )
            section_count = 0
            summary = None

        version_bucket[entry.source_locale] = PatchNoteIndex(
            patch_version=entry.patch_version,
            title=entry.title,
            published_at=entry.published_at,
            canonical_url=entry.canonical_url,
            source_locale=entry.source_locale,
            summary=summary,
            content_hash=entry.content_hash,
            section_count=section_count,
        )

    preferred_order = ("es-es", "es-mx", "en-us")
    chosen: list[PatchNoteIndex] = []
    for version in sorted(entries_by_version.keys(), key=_version_sort_key, reverse=True):
        bucket = entries_by_version[version]
        if locale:
            if locale in bucket:
                chosen.append(bucket[locale])
            continue
        for pref in preferred_order:
            if pref in bucket:
                chosen.append(bucket[pref])
                break
        else:
            chosen.append(next(iter(bucket.values())))
    return chosen


def load_patch(patch_version: str, locale: str = DEFAULT_LOCALE) -> PatchNote | None:
    """Carga un patch note completo desde disco. None si no existe.

    Hidrata `enrichments` desde `data/patch_notes/sources/` antes de devolver
    para que el cliente vea siempre el estado actualizado de fuentes adicionales.
    """
    note = _read_patch_file(patch_version, locale)
    if note is None:
        return None
    return attach_enrichments_to_note(note)


def load_patch_raw(patch_version: str, locale: str = DEFAULT_LOCALE) -> PatchNote | None:
    """Carga el patch sin hidratar enrichments (lectura directa del archivo)."""
    return _read_patch_file(patch_version, locale)


def list_enrichments_for_patch(patch_version: str) -> list[PatchEnrichment]:
    """Lista los enrichments disponibles para esta versión (per-patch + global)."""
    out: list[PatchEnrichment] = []
    for source in ENRICHMENT_SOURCES:
        per_patch = load_enrichment(source, patch_version)
        if per_patch is not None:
            out.append(per_patch)
            continue
        global_snap = load_enrichment(source, None)
        if global_snap is not None:
            out.append(global_snap)
    return out


def load_enrichment_for_patch(source: str, patch_version: str) -> PatchEnrichment | None:
    """Carga el enrichment específico de una fuente para un patch dado.

    Cae al snapshot global si no hay per-patch.
    """
    per_patch = load_enrichment(source, patch_version)
    if per_patch is not None:
        return per_patch
    return load_enrichment(source, None)


def list_sources_with_data(patch_version: str) -> list[str]:
    """Sources que tienen un archivo (per-patch o global) aplicable a este patch."""
    return list_available_sources_for_patch(patch_version)


def _read_patch_file(patch_version: str, locale: str) -> PatchNote | None:
    path = _by_patch_dir() / f"{patch_version}_{locale}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return PatchNote.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("[patch_notes/loader] Archivo corrupto %s: %s", path, e)
        return None


def patch_count() -> int:
    """Cantidad de versiones únicas conocidas."""
    return len(load_manifest().available_patches)


def available_locales() -> list[str]:
    """Locales registrados en el manifest."""
    return load_manifest().locales
