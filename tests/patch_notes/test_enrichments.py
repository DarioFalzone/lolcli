"""Tests para save_enrichment + load_enrichment + attach_enrichments_to_note."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.patch_notes import normalizer
from riot_lol_cli.patch_notes.messages import (
    ENRICHMENT_SOURCES,
    SOURCE_DDRAGON,
    SOURCE_RIOT_CALENDAR,
    SOURCE_UGG_PATCH,
)
from riot_lol_cli.patch_notes.schema import PatchEnrichment, PatchNote, PatchSection


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(normalizer, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(normalizer, "_NORMALIZED_DIR", tmp_path / "normalized")
    monkeypatch.setattr(normalizer, "_BY_PATCH_DIR", tmp_path / "normalized" / "by_patch")
    monkeypatch.setattr(normalizer, "_HISTORY_DIR", tmp_path / "normalized" / "history")
    monkeypatch.setattr(normalizer, "_MANIFEST_PATH", tmp_path / "manifest.json")
    monkeypatch.setattr(normalizer, "_SOURCES_DIR", tmp_path / "sources")
    return tmp_path


def _make_note(version: str = "26.10", locale: str = "es-es") -> PatchNote:
    sections = [PatchSection(title="Test", heading_level=2, blocks=["Bloque 1"])]
    return PatchNote(
        source_locale=locale,
        patch_version=version,
        title=f"Versión {version}",
        canonical_url=f"https://x/{version}",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash=normalizer.compute_content_hash(sections),
        scraper_version="test-v2",
        sections=sections,
    )


def test_save_enrichment_per_patch(isolated_data_dir) -> None:
    path, enrichment = normalizer.save_enrichment(
        SOURCE_UGG_PATCH,
        patch_version="26.10",
        payload={"rows_count": 42, "rows": [{"name": "Aatrox"}]},
        source_url="https://u.gg/lol/tier-list",
    )
    assert path.exists()
    assert path.name == "26.10.json"
    assert enrichment.source == SOURCE_UGG_PATCH
    assert enrichment.payload["rows_count"] == 42
    assert enrichment.error is None
    assert len(enrichment.content_hash) == 64


def test_save_enrichment_global_snapshot(isolated_data_dir) -> None:
    path, enrichment = normalizer.save_enrichment(
        SOURCE_DDRAGON,
        patch_version=None,
        payload={"versions": ["26.10.1"], "latest": "26.10.1"},
    )
    assert path.exists()
    assert path.name == "snapshot.json"
    assert enrichment.source == SOURCE_DDRAGON


def test_save_enrichment_with_error_persists(isolated_data_dir) -> None:
    path, enrichment = normalizer.save_enrichment(
        SOURCE_UGG_PATCH,
        patch_version="26.10",
        payload={},
        error="timeout while loading SPA",
    )
    assert path.exists()
    assert enrichment.error == "timeout while loading SPA"
    assert enrichment.payload == {}


def test_load_enrichment_roundtrip(isolated_data_dir) -> None:
    normalizer.save_enrichment(SOURCE_UGG_PATCH, "26.10", {"key": "value"})
    loaded = normalizer.load_enrichment(SOURCE_UGG_PATCH, "26.10")
    assert loaded is not None
    assert loaded.payload == {"key": "value"}


def test_load_enrichment_returns_none_when_missing(isolated_data_dir) -> None:
    assert normalizer.load_enrichment(SOURCE_UGG_PATCH, "99.99") is None


def test_attach_enrichments_falls_back_to_global(isolated_data_dir) -> None:
    note = _make_note("26.10", "es-es")
    normalizer.save_enrichment(SOURCE_DDRAGON, patch_version=None, payload={"latest": "26.10.1"})
    normalizer.save_enrichment(SOURCE_UGG_PATCH, "26.10", {"rows_count": 5})

    hydrated = normalizer.attach_enrichments_to_note(note)
    sources = {e.source for e in hydrated.enrichments}
    assert SOURCE_DDRAGON in sources
    assert SOURCE_UGG_PATCH in sources


def test_update_source_status_records_success(isolated_data_dir) -> None:
    normalizer.update_source_status(SOURCE_DDRAGON, success=True, patch_version=None)
    raw = normalizer._read_manifest_raw()
    status = raw["sources_status"][SOURCE_DDRAGON]
    assert status["last_success"] is not None
    assert status["last_error"] is None


def test_update_source_status_records_error(isolated_data_dir) -> None:
    normalizer.update_source_status(SOURCE_UGG_PATCH, success=False, error="timeout")
    raw = normalizer._read_manifest_raw()
    status = raw["sources_status"][SOURCE_UGG_PATCH]
    assert status["last_error"] == "timeout"
    assert status["last_success"] is None


def test_enrichment_sources_constant_complete() -> None:
    """Las 8 fuentes de enrichment están registradas (V2.3 agrega mobalytics_breakdown)."""
    assert len(ENRICHMENT_SOURCES) == 8
    assert SOURCE_DDRAGON in ENRICHMENT_SOURCES
    assert SOURCE_RIOT_CALENDAR in ENRICHMENT_SOURCES


def test_patch_note_accepts_enrichments_field() -> None:
    enrichment = PatchEnrichment(
        source=SOURCE_DDRAGON,
        fetched_at=datetime.now(timezone.utc),
        content_hash="a" * 64,
        payload={"versions": []},
    )
    sections = [PatchSection(title="T", heading_level=2, blocks=["b"])]
    note = PatchNote(
        source_locale="es-es",
        patch_version="26.10",
        title="Test",
        canonical_url="https://x",
        fetched_at=datetime.now(timezone.utc),
        content_hash="b" * 64,
        scraper_version="t",
        sections=sections,
        enrichments=[enrichment],
    )
    assert len(note.enrichments) == 1
    assert note.enrichments[0].source == SOURCE_DDRAGON
