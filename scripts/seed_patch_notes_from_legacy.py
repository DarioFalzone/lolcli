"""Seed inicial del nuevo subsistema `patch_notes` desde los datos legacy.

Lee `projects/active/patch-notes/data/lol_patch_notes.json` (formato v33b) y
emite archivos `data/patch_notes/normalized/by_patch/{version}_es-es.json`
con el schema nuevo, marcados como `scraper_version="legacy-v33b"`.

Idempotente: si la versión y locale ya existen con el mismo hash, no escribe.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Hacer que el paquete sea importable cuando se corre como script directo.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from riot_lol_cli.patch_notes.normalizer import (  # noqa: E402
    compute_content_hash,
    save_normalized,
    update_manifest,
)
from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection  # noqa: E402

logger = logging.getLogger(__name__)

_LEGACY_JSON = _REPO_ROOT / "projects" / "active" / "patch-notes" / "data" / "lol_patch_notes.json"
_LOCALE = "es-es"
_SCRAPER_VERSION = "legacy-v33b"


def _parse_legacy_date(raw: str) -> datetime | None:
    """Convierte '26/08/25' (DD/MM/YY) a datetime UTC. None si no parsea."""
    if not raw:
        return None
    try:
        day, month, year_short = raw.split("/")
        year = int(year_short)
        if year < 70:
            year += 2000
        elif year < 100:
            year += 1900
        return datetime(year, int(month), int(day), tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None


def _extract_version(title: str, url: str) -> str:
    m = re.search(r"(\d+\.\d+[a-z]?)", title)
    if m:
        return m.group(1)
    m = re.search(r"patch-(\d+)-(\d+)([a-z]?)-notes", url, re.IGNORECASE)
    if m:
        return f"{int(m.group(1))}.{int(m.group(2)):02d}{m.group(3) or ''}"
    return "unknown"


def _build_summary(sections: list[dict]) -> str | None:
    for s in sections:
        text = s.get("texto", "").strip()
        if text and len(text) > 40:
            return text[:280].rstrip() + ("…" if len(text) > 280 else "")
    return None


def _convert_legacy_sections(legacy_sections: list[dict]) -> list[PatchSection]:
    """Convierte el schema legacy (lista plana con 'nombre'/'texto'/'subsecciones')
    al schema nuevo (jerárquico H2 → H3 → H4)."""
    result: list[PatchSection] = []
    for raw in legacy_sections:
        name = (raw.get("nombre") or "").strip()
        text = (raw.get("texto") or "").strip()
        blocks = [text] if text else []
        subsections = _convert_legacy_subsections(raw.get("subsecciones", []))
        if not name and not blocks and not subsections:
            continue
        result.append(
            PatchSection(
                title=name or "Introducción",
                heading_level=2,
                blocks=blocks,
                subsections=subsections,
            )
        )
    return result


def _convert_legacy_subsections(legacy_subs: list[dict]) -> list[PatchSection]:
    result: list[PatchSection] = []
    for raw in legacy_subs:
        name = (raw.get("nombre") or "").strip()
        text = (raw.get("texto") or "").strip()
        blocks = [text] if text else []
        nested = _convert_legacy_subsections(raw.get("subsecciones", []))
        if not name and not blocks and not nested:
            continue
        result.append(
            PatchSection(
                title=name or "—",
                heading_level=3,
                blocks=blocks,
                subsections=nested,
            )
        )
    return result


def seed() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    if not _LEGACY_JSON.exists():
        logger.error("Legacy JSON no encontrado: %s", _LEGACY_JSON)
        return 1

    with open(_LEGACY_JSON, encoding="utf-8-sig") as f:
        legacy = json.load(f)

    parches = legacy.get("parches", [])
    if not parches:
        logger.error("No hay parches en el JSON legacy.")
        return 1

    written = 0
    skipped = 0
    fetched_at = datetime.now(timezone.utc)

    for raw_patch in parches:
        title = raw_patch.get("titulo", "")
        url = raw_patch.get("url", "")
        published = _parse_legacy_date(raw_patch.get("publicado", ""))
        version = _extract_version(title, url)
        if version == "unknown":
            logger.warning("Versión desconocida, skip: %s", title)
            skipped += 1
            continue

        sections = _convert_legacy_sections(raw_patch.get("secciones", []))
        content_hash = compute_content_hash(sections)
        summary = _build_summary(raw_patch.get("secciones", []))

        note = PatchNote(
            source_locale=_LOCALE,
            patch_version=version,
            title=title,
            canonical_url=url,
            published_at=published,
            fetched_at=fetched_at,
            content_hash=content_hash,
            summary=summary,
            sections=sections,
            assets=[],
            scraper_version=_SCRAPER_VERSION,
        )
        save_normalized(note)
        update_manifest(note)
        written += 1
        logger.info("  ✓ %s (%s) — %d secciones", version, _LOCALE, len(sections))

    logger.info("Seed completo: %d escritos, %d saltados", written, skipped)
    return 0


if __name__ == "__main__":
    sys.exit(seed())
