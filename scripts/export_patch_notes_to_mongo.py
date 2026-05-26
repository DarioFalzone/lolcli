"""Export idempotente de patch_notes a MongoDB Atlas.

Lee los JSON persistidos en `data/patch_notes/` y los upserta en 3 colecciones
de MongoDB Atlas (free tier). El JSON local sigue siendo source of truth;
MongoDB es read-only para exploracion desde MongoDB Compass.

Uso:
    python scripts/export_patch_notes_to_mongo.py [--dry-run] [--only {patches,enrichments,manifest}] [--verbose]

Pre-requisitos:
    pip install -r requirements.txt
    setx LOLCLI_MONGO_URI "mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
    setx LOLCLI_MONGO_DB  "lolcli_patch_notes"

Ver docs/patch_notes_mongo_export.md para setup paso a paso.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Asegurar que `src/` esté en el path cuando se corre via `python scripts/...`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from riot_lol_cli import settings  # noqa: E402
from riot_lol_cli.patch_notes import loader, normalizer  # noqa: E402
from riot_lol_cli.patch_notes.messages import ENRICHMENT_SOURCES  # noqa: E402
from riot_lol_cli.patch_notes.schema import PatchEnrichment, PatchNote  # noqa: E402

logger = logging.getLogger(__name__)

COLLECTION_PATCHES = "patches"
COLLECTION_ENRICHMENTS = "enrichments"
COLLECTION_MANIFEST = "manifest"
MANIFEST_DOC_ID = "current"
GLOBAL_PATCH_TOKEN = "GLOBAL"

# Exit codes
EXIT_OK = 0
EXIT_MISSING_URI = 2
EXIT_PYMONGO_NOT_INSTALLED = 3
EXIT_MONGO_CONNECTION_FAILED = 4


# ---------- Builders (puros, testeables sin Mongo) ----------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_champions_mentioned(note: PatchNote) -> list[str]:
    """Heuristica simple: titulos de subsecciones de la seccion 'Campeones'.

    En las notas Riot es-es, la seccion 'Campeones' tiene subsecciones nombradas
    con el champion (ej: 'Aatrox', 'Ahri'). Esto permite filtrar en Compass via
    `{ champions_mentioned: 'Aatrox' }` sin necesidad de full-text search.
    """
    out: list[str] = []
    for section in note.sections:
        title_norm = (section.title or "").strip().lower()
        if title_norm in {"campeones", "champions"}:
            for sub in section.subsections:
                name = (sub.title or "").strip()
                if name and len(name) < 40:
                    out.append(name)
    return out


def _build_patch_doc(note: PatchNote) -> dict[str, Any]:
    """Convierte un PatchNote en doc BSON listo para MongoDB.

    `_id` compuesto `{patch_version}__{source_locale}` garantiza idempotencia:
    re-ejecuciones del export upsertan el mismo doc.
    """
    payload = note.model_dump(mode="json")
    payload["_id"] = f"{note.patch_version}__{note.source_locale}"
    payload["synced_at"] = _now_iso()
    payload["champions_mentioned"] = _extract_champions_mentioned(note)
    return payload


def _build_enrichment_doc(enrichment: PatchEnrichment, patch_version: str | None) -> dict[str, Any]:
    """Convierte un PatchEnrichment en doc BSON.

    `_id` = `{source}__{patch_version or 'GLOBAL'}`. Los snapshots globales
    (ddragon, riot_calendar) usan el sufijo `GLOBAL`.
    """
    payload = enrichment.model_dump(mode="json")
    version_token = patch_version if patch_version else GLOBAL_PATCH_TOKEN
    payload["_id"] = f"{enrichment.source}__{version_token}"
    payload["patch_version_indexed"] = patch_version  # None para globales
    payload["synced_at"] = _now_iso()
    return payload


def _build_manifest_doc() -> dict[str, Any]:
    """Lee el manifest raw y le agrega `_id` + `synced_at`."""
    raw = normalizer._read_manifest_raw()
    raw["_id"] = MANIFEST_DOC_ID
    raw["synced_at"] = _now_iso()
    return raw


# ---------- Collectors (recorren disco) ----------


def collect_patch_docs() -> list[dict[str, Any]]:
    """Itera todos los patches en disco y construye sus docs Mongo."""
    docs: list[dict[str, Any]] = []
    for index in loader.list_patches(locale=None):
        note = loader.load_patch_raw(index.patch_version, index.source_locale)
        if note is None:
            logger.warning("Patch ilegible en disco: %s/%s", index.patch_version, index.source_locale)
            continue
        docs.append(_build_patch_doc(note))
    return docs


def collect_enrichment_docs() -> list[dict[str, Any]]:
    """Itera todos los enrichments (per-patch + globales) y construye sus docs."""
    docs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Per-patch: cruza ENRICHMENT_SOURCES contra patches conocidos.
    manifest = loader.load_manifest_safe()
    patch_versions = list(manifest.available_patches)

    for source in ENRICHMENT_SOURCES:
        # Per-patch
        for version in patch_versions:
            enrichment = loader.load_enrichment_for_patch(source, version)
            if enrichment is None:
                continue
            # `load_enrichment_for_patch` cae a global si no hay per-patch, asi que
            # solo guardamos como per-patch si la fuente tiene archivo per-patch real.
            per_patch_file = (
                normalizer.get_data_dir() / "sources" / source / f"{version}.json"
            )
            if per_patch_file.exists():
                doc = _build_enrichment_doc(enrichment, version)
                if doc["_id"] not in seen_ids:
                    docs.append(doc)
                    seen_ids.add(doc["_id"])

        # Global snapshot
        snapshot_file = normalizer.get_data_dir() / "sources" / source / "snapshot.json"
        if snapshot_file.exists():
            try:
                raw = json.loads(snapshot_file.read_text(encoding="utf-8"))
                enrichment = PatchEnrichment.model_validate(raw)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("Snapshot ilegible para %s: %s", source, e)
                continue
            doc = _build_enrichment_doc(enrichment, None)
            if doc["_id"] not in seen_ids:
                docs.append(doc)
                seen_ids.add(doc["_id"])

    return docs


# ---------- Mongo upserts ----------


def _bulk_upsert(collection, docs: list[dict[str, Any]]) -> dict[str, int]:
    """Bulk write con UpdateOne(upsert=True). Devuelve {scanned, upserted, modified}."""
    from pymongo import UpdateOne

    if not docs:
        return {"scanned": 0, "upserted": 0, "modified": 0}

    operations = [
        UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True) for doc in docs
    ]
    result = collection.bulk_write(operations, ordered=False)
    return {
        "scanned": len(docs),
        "upserted": result.upserted_count,
        "modified": result.modified_count,
    }


def _ensure_indexes(db) -> None:
    """Crea indexes idempotentes en las 3 colecciones."""
    patches = db[COLLECTION_PATCHES]
    patches.create_index([("patch_version", -1)], background=True)
    patches.create_index([("source_locale", 1)], background=True)
    patches.create_index([("content_hash", 1)], background=True)
    patches.create_index([("champions_mentioned", 1)], background=True)
    patches.create_index([("published_at", -1)], background=True)

    enrichments = db[COLLECTION_ENRICHMENTS]
    enrichments.create_index([("source", 1), ("patch_version_indexed", -1)], background=True)
    enrichments.create_index([("content_hash", 1)], background=True)


# ---------- Main flow ----------


def run_export(
    dry_run: bool = False,
    only: str | None = None,
    verbose: bool = False,
) -> int:
    """Ejecuta el export. Devuelve exit code (0 OK).

    Args:
        dry_run: si True, NO conecta a Mongo. Solo imprime el plan de docs.
        only: si se especifica, solo procesa esa coleccion (patches/enrichments/manifest).
        verbose: log nivel DEBUG.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")

    started = time.time()
    summary: dict[str, Any] = {"started_at": _now_iso()}

    # Recoleccion (siempre, incluso en dry-run para imprimir counts).
    if only in (None, COLLECTION_PATCHES):
        patches = collect_patch_docs()
        summary[COLLECTION_PATCHES] = {"collected": len(patches)}
    else:
        patches = []

    if only in (None, COLLECTION_ENRICHMENTS):
        enrichments = collect_enrichment_docs()
        summary[COLLECTION_ENRICHMENTS] = {"collected": len(enrichments)}
    else:
        enrichments = []

    if only in (None, COLLECTION_MANIFEST):
        manifest_doc = _build_manifest_doc()
        summary[COLLECTION_MANIFEST] = {"collected": 1}
    else:
        manifest_doc = None

    if dry_run:
        summary["mode"] = "dry-run"
        summary["duration_s"] = round(time.time() - started, 2)
        logger.info("Dry-run summary: %s", json.dumps(summary, indent=2, default=str))
        return EXIT_OK

    # Validar config
    uri = settings.get_mongo_uri()
    if not uri:
        logger.error(
            "LOLCLI_MONGO_URI no esta configurada. "
            "Setear via `setx LOLCLI_MONGO_URI \"mongodb+srv://...\"` y reabrir la terminal. "
            "Para chequear sin Mongo: --dry-run."
        )
        return EXIT_MISSING_URI

    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError
    except ImportError:
        logger.error(
            "pymongo no esta instalado. Correr: pip install -r requirements.txt"
        )
        return EXIT_PYMONGO_NOT_INSTALLED

    db_name = settings.get_mongo_db_name()
    logger.info("Conectando a MongoDB Atlas (db=%s)...", db_name)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        client.admin.command("ping")
    except PyMongoError as e:
        logger.error("Conexion a MongoDB fallo: %s", e)
        return EXIT_MONGO_CONNECTION_FAILED

    try:
        db = client[db_name]
        _ensure_indexes(db)

        if only in (None, COLLECTION_PATCHES):
            res = _bulk_upsert(db[COLLECTION_PATCHES], patches)
            summary[COLLECTION_PATCHES].update(res)
            logger.info("patches: %s", res)

        if only in (None, COLLECTION_ENRICHMENTS):
            res = _bulk_upsert(db[COLLECTION_ENRICHMENTS], enrichments)
            summary[COLLECTION_ENRICHMENTS].update(res)
            logger.info("enrichments: %s", res)

        if only in (None, COLLECTION_MANIFEST):
            res = _bulk_upsert(db[COLLECTION_MANIFEST], [manifest_doc])
            summary[COLLECTION_MANIFEST].update(res)
            logger.info("manifest: %s", res)
    finally:
        client.close()

    summary["duration_s"] = round(time.time() - started, 2)
    summary["mode"] = "live"
    logger.info("Export summary: %s", json.dumps(summary, indent=2, default=str))
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No conecta a Mongo; solo imprime los counts del plan.",
    )
    parser.add_argument(
        "--only",
        choices=[COLLECTION_PATCHES, COLLECTION_ENRICHMENTS, COLLECTION_MANIFEST],
        default=None,
        help="Procesar solo una coleccion (por defecto: las 3).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log nivel DEBUG.",
    )
    args = parser.parse_args(argv)
    return run_export(dry_run=args.dry_run, only=args.only, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
