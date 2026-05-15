"""Hash, persistencia y change detection para patch notes.

Sigue el patrón de `meta_scraper/normalizer.py`: funciones puras + paths
canónicos resueltos al import. Toda escritura va a disco y actualiza el manifest.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .schema import ManifestEntry, PatchEnrichment, PatchManifest, PatchNote, PatchSection

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _BASE_DIR / "data" / "patch_notes"
_NORMALIZED_DIR = _DATA_DIR / "normalized"
_BY_PATCH_DIR = _NORMALIZED_DIR / "by_patch"
_HISTORY_DIR = _NORMALIZED_DIR / "history"
_MANIFEST_PATH = _DATA_DIR / "manifest.json"
_SOURCES_DIR = _DATA_DIR / "sources"


def get_data_dir() -> Path:
    """Path absoluto a `data/patch_notes/`. Útil para tests con monkeypatch."""
    return _DATA_DIR


def compute_content_hash(sections: list[PatchSection]) -> str:
    """SHA-256 estable sobre el JSON canónico de las secciones.

    Usado para detectar cambios entre revisiones del mismo `(patch_version, locale)`.
    Si el hash difiere, hay una revisión nueva que merece persistirse en history.
    """
    payload = [s.model_dump() for s in sections]
    stable = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _patch_file_path(patch_version: str, locale: str) -> Path:
    return _BY_PATCH_DIR / f"{patch_version}_{locale}.json"


def _history_file_path(patch_version: str, locale: str, fetched_at: datetime) -> Path:
    stamp = fetched_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    return _HISTORY_DIR / f"{stamp}_{patch_version}_{locale}.json"


def save_normalized(note: PatchNote) -> Path:
    """Persiste la nota en `by_patch/` y guarda una copia en `history/`.

    Devuelve el path del archivo canónico (`by_patch/{version}_{locale}.json`).
    """
    _BY_PATCH_DIR.mkdir(parents=True, exist_ok=True)
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    canonical_path = _patch_file_path(note.patch_version, note.source_locale)
    history_path = _history_file_path(note.patch_version, note.source_locale, note.fetched_at)

    payload = note.model_dump(mode="json")

    canonical_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    history_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info(
        "[patch_notes/normalizer] %s/%s persistido (sections=%d, hash=%s...)",
        note.patch_version,
        note.source_locale,
        len(note.sections),
        note.content_hash[:8],
    )
    return canonical_path


def load_manifest() -> PatchManifest:
    """Carga el manifest desde disco. Si no existe, devuelve uno vacío."""
    from .messages import SCRAPER_VERSION  # local import to avoid cycle

    if not _MANIFEST_PATH.exists():
        return PatchManifest(scraper_version=SCRAPER_VERSION)

    try:
        data = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        return PatchManifest.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("[patch_notes/normalizer] Manifest corrupto, regenerando: %s", e)
        return PatchManifest(scraper_version=SCRAPER_VERSION)


def update_manifest(note: PatchNote) -> PatchManifest:
    """Inserta o actualiza la entrada del manifest para `(patch_version, locale)`.

    Mantiene `available_patches` desc por version. Idempotente: si la entrada ya
    existe con el mismo hash, no cambia nada salvo el `last_scrape`.
    """
    manifest = load_manifest()

    canonical_rel = _patch_file_path(note.patch_version, note.source_locale).relative_to(_DATA_DIR)

    new_entry = ManifestEntry(
        patch_version=note.patch_version,
        source_locale=note.source_locale,
        file=str(canonical_rel).replace("\\", "/"),
        content_hash=note.content_hash,
        fetched_at=note.fetched_at,
        published_at=note.published_at,
        title=note.title,
        canonical_url=note.canonical_url,
    )

    existing_idx = next(
        (
            i
            for i, e in enumerate(manifest.entries)
            if e.patch_version == note.patch_version and e.source_locale == note.source_locale
        ),
        None,
    )
    if existing_idx is None:
        manifest.entries.append(new_entry)
    else:
        manifest.entries[existing_idx] = new_entry

    if note.source_locale not in manifest.locales:
        manifest.locales = sorted({*manifest.locales, note.source_locale})

    versions = sorted({e.patch_version for e in manifest.entries}, key=_version_sort_key, reverse=True)
    manifest.available_patches = versions

    manifest.last_scrape = datetime.now(timezone.utc)

    _MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _MANIFEST_PATH.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest


def get_sources_dir() -> Path:
    """Path a `data/patch_notes/sources/`. Útil para tests con monkeypatch."""
    return _SOURCES_DIR


def compute_enrichment_hash(payload: dict, error: str | None = None) -> str:
    """SHA-256 estable del payload + error. Permite detectar cambios en enrichments."""
    stable = json.dumps(
        {"payload": payload, "error": error},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _enrichment_path(source: str, patch_version: str | None) -> Path:
    """Ubicación canónica de un payload por source.

    Si `patch_version` es None → snapshot global (calendar, ddragon).
    """
    if patch_version is None:
        return _SOURCES_DIR / source / "snapshot.json"
    return _SOURCES_DIR / source / f"{patch_version}.json"


def save_enrichment(
    source: str,
    patch_version: str | None,
    payload: dict,
    source_url: str | None = None,
    error: str | None = None,
) -> tuple[Path, PatchEnrichment]:
    """Persiste un enrichment en `data/patch_notes/sources/{source}/...`.

    Devuelve el path absoluto + el modelo `PatchEnrichment` listo para attachear.
    """
    target = _enrichment_path(source, patch_version)
    target.parent.mkdir(parents=True, exist_ok=True)

    content_hash = compute_enrichment_hash(payload, error)
    enrichment = PatchEnrichment(
        source=source,
        source_url=source_url,
        fetched_at=datetime.now(timezone.utc),
        content_hash=content_hash,
        payload=payload,
        error=error,
    )
    target.write_text(
        json.dumps(enrichment.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(
        "[patch_notes/normalizer] enrichment %s/%s persistido (error=%s, hash=%s...)",
        source,
        patch_version or "global",
        bool(error),
        content_hash[:8],
    )
    return target, enrichment


def load_enrichment(source: str, patch_version: str | None) -> PatchEnrichment | None:
    """Lee un enrichment del disco. None si no existe."""
    target = _enrichment_path(source, patch_version)
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return PatchEnrichment.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("[patch_notes/normalizer] enrichment corrupto %s: %s", target, e)
        return None


def list_available_sources_for_patch(patch_version: str) -> list[str]:
    """Lista sources que tienen un payload para este patch (o un global aplicable)."""
    available: list[str] = []
    if not _SOURCES_DIR.exists():
        return available
    for source_dir in _SOURCES_DIR.iterdir():
        if not source_dir.is_dir():
            continue
        per_patch = source_dir / f"{patch_version}.json"
        global_snapshot = source_dir / "snapshot.json"
        if per_patch.exists() or global_snapshot.exists():
            available.append(source_dir.name)
    return sorted(available)


def attach_enrichments_to_note(note: PatchNote) -> PatchNote:
    """Hidrata `note.enrichments` desde disco para esta version.

    Devuelve una copia del note con `enrichments` actualizado.
    """
    from .messages import ENRICHMENT_SOURCES  # local import

    fresh: list[PatchEnrichment] = []
    for source in ENRICHMENT_SOURCES:
        # Probar primero per-patch, luego global
        per_patch = load_enrichment(source, note.patch_version)
        if per_patch is not None:
            fresh.append(per_patch)
            continue
        global_snap = load_enrichment(source, None)
        if global_snap is not None:
            fresh.append(global_snap)

    return note.model_copy(update={"enrichments": fresh})


def update_source_status(
    source: str,
    success: bool,
    patch_version: str | None = None,
    error: str | None = None,
) -> None:
    """Actualiza el `sources_status` del manifest (campo extra V2)."""
    raw = _read_manifest_raw()
    sources_status = raw.setdefault("sources_status", {})
    entry = sources_status.setdefault(
        source,
        {"last_scrape": None, "last_success": None, "last_error": None, "available_patches": []},
    )
    now_iso = datetime.now(timezone.utc).isoformat()
    entry["last_scrape"] = now_iso
    if success:
        entry["last_success"] = now_iso
        entry["last_error"] = None
        if patch_version and patch_version not in entry["available_patches"]:
            entry["available_patches"] = sorted(
                {*entry["available_patches"], patch_version}, key=_version_sort_key, reverse=True
            )
    else:
        entry["last_error"] = error or "unknown"

    raw["sources_status"] = sources_status
    _write_manifest_raw(raw)


def _read_manifest_raw() -> dict:
    """Lee el manifest como dict crudo (para extensión V2 sin romper Pydantic)."""
    if not _MANIFEST_PATH.exists():
        from .messages import SCRAPER_VERSION

        return {
            "schema_version": "1.0",
            "scraper_version": SCRAPER_VERSION,
            "locales": [],
            "available_patches": [],
            "entries": [],
            "sources_status": {},
        }
    try:
        return json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        from .messages import SCRAPER_VERSION

        return {
            "schema_version": "1.0",
            "scraper_version": SCRAPER_VERSION,
            "locales": [],
            "available_patches": [],
            "entries": [],
            "sources_status": {},
        }


def _write_manifest_raw(data: dict) -> None:
    _MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _MANIFEST_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def detect_change(patch_version: str, locale: str, new_hash: str) -> bool:
    """True si la nueva versión difiere de lo persistido (o no había nada)."""
    manifest = load_manifest()
    for entry in manifest.entries:
        if entry.patch_version == patch_version and entry.source_locale == locale:
            return entry.content_hash != new_hash
    return True


def _version_sort_key(version: str) -> tuple[int, int, str]:
    """Convierte '26.10b' → (26, 10, 'b') para sort estable."""
    parts = version.split(".")
    if len(parts) < 2:
        return (0, 0, version)
    major = _safe_int(parts[0])
    minor_raw = parts[1]
    suffix = ""
    minor_digits = ""
    for ch in minor_raw:
        if ch.isdigit():
            minor_digits += ch
        else:
            suffix += ch
    minor = _safe_int(minor_digits)
    return (major, minor, suffix)


def _safe_int(raw: str) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0
