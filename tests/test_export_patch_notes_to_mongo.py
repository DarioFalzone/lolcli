"""Tests para scripts/export_patch_notes_to_mongo.py.

No requiere Mongo real ni pymongo. Cubre:
- Dry-run sin URI configurada (exit 0).
- Builders puros: forma del doc, _id, champions_mentioned, sufijo GLOBAL.
- Manejo de URI faltante en modo live (exit 2).
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "export_patch_notes_to_mongo.py"

# Asegurar src/ en path para imports del modulo a testear.
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _load_export_module():
    """Carga el script como modulo Python para tests directos de sus funciones."""
    spec = importlib.util.spec_from_file_location("export_patch_notes_to_mongo", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        pytest.fail(f"No se pudo cargar {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_patch_note():
    """Crea un PatchNote minimal con seccion 'Campeones' para testear extraccion."""
    from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection

    return PatchNote(
        source_locale="es-es",
        patch_version="99.99",
        title="Test patch",
        canonical_url="https://example.com/patch",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash="a" * 64,
        sections=[
            PatchSection(
                title="Campeones",
                heading_level=2,
                subsections=[
                    PatchSection(title="Aatrox", heading_level=3),
                    PatchSection(title="Ahri", heading_level=3),
                ],
            ),
            PatchSection(title="Otra seccion", heading_level=2),
        ],
        scraper_version="patch_notes_v2.0.0",
    )


def _make_enrichment(source: str = "mobalytics_breakdown"):
    from riot_lol_cli.patch_notes.schema import PatchEnrichment

    return PatchEnrichment(
        source=source,
        source_url="https://example.com",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash="b" * 64,
        payload={"foo": "bar"},
        error=None,
    )


# ---------- Tests ----------


def test_build_patch_doc_id_and_shape():
    """_build_patch_doc devuelve _id compuesto y champions_mentioned."""
    module = _load_export_module()
    note = _make_patch_note()
    doc = module._build_patch_doc(note)

    assert doc["_id"] == "99.99__es-es"
    assert doc["patch_version"] == "99.99"
    assert doc["source_locale"] == "es-es"
    assert doc["champions_mentioned"] == ["Aatrox", "Ahri"]
    assert "synced_at" in doc
    # Mantiene los campos del modelo
    assert doc["title"] == "Test patch"
    assert doc["content_hash"] == "a" * 64


def test_build_patch_doc_no_champions_section():
    """Si no hay seccion 'Campeones', champions_mentioned es lista vacia."""
    from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection

    module = _load_export_module()
    note = PatchNote(
        source_locale="es-es",
        patch_version="1.0",
        title="x",
        canonical_url="https://example.com",
        fetched_at=datetime.now(timezone.utc),
        content_hash="c" * 64,
        sections=[PatchSection(title="Item changes", heading_level=2)],
        scraper_version="test",
    )
    doc = module._build_patch_doc(note)
    assert doc["champions_mentioned"] == []


def test_build_enrichment_doc_per_patch_id():
    """Enrichment per-patch tiene _id con versión."""
    module = _load_export_module()
    enrichment = _make_enrichment("mobalytics_breakdown")
    doc = module._build_enrichment_doc(enrichment, "26.10")

    assert doc["_id"] == "mobalytics_breakdown__26.10"
    assert doc["patch_version_indexed"] == "26.10"
    assert doc["source"] == "mobalytics_breakdown"
    assert "synced_at" in doc


def test_build_enrichment_doc_global_suffix():
    """Enrichment global (patch_version=None) usa sufijo __GLOBAL."""
    module = _load_export_module()
    enrichment = _make_enrichment("ddragon")
    doc = module._build_enrichment_doc(enrichment, None)

    assert doc["_id"] == "ddragon__GLOBAL"
    assert doc["patch_version_indexed"] is None


def test_dry_run_without_uri_does_not_fail(monkeypatch, capsys):
    """`--dry-run` con env vacia retorna 0 sin tocar Mongo."""
    monkeypatch.delenv("LOLCLI_MONGO_URI", raising=False)
    monkeypatch.delenv("LOLCLI_MONGO_DB", raising=False)

    module = _load_export_module()
    exit_code = module.main(["--dry-run"])
    assert exit_code == module.EXIT_OK


def test_missing_uri_in_live_mode_exits_with_code_2(monkeypatch):
    """Sin URI y sin --dry-run, exit code 2."""
    monkeypatch.delenv("LOLCLI_MONGO_URI", raising=False)

    module = _load_export_module()
    exit_code = module.main([])  # No --dry-run
    assert exit_code == module.EXIT_MISSING_URI


def test_only_flag_restricts_collection(monkeypatch):
    """`--only manifest --dry-run` solo procesa manifest."""
    monkeypatch.delenv("LOLCLI_MONGO_URI", raising=False)

    module = _load_export_module()
    exit_code = module.main(["--dry-run", "--only", "manifest"])
    assert exit_code == module.EXIT_OK


def test_collection_constants_match_plan():
    """Las constantes coinciden con el contrato del plan."""
    module = _load_export_module()
    assert module.COLLECTION_PATCHES == "patches"
    assert module.COLLECTION_ENRICHMENTS == "enrichments"
    assert module.COLLECTION_MANIFEST == "manifest"
    assert module.MANIFEST_DOC_ID == "current"
    assert module.GLOBAL_PATCH_TOKEN == "GLOBAL"
