"""Tests del loader: list_patches y load_patch desde disco."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.patch_notes import loader, normalizer
from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection


@pytest.fixture
def isolated_dir(tmp_path, monkeypatch):
    """Aísla el almacenamiento del normalizer + loader a tmp_path."""
    monkeypatch.setattr(normalizer, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(normalizer, "_NORMALIZED_DIR", tmp_path / "normalized")
    monkeypatch.setattr(normalizer, "_BY_PATCH_DIR", tmp_path / "normalized" / "by_patch")
    monkeypatch.setattr(normalizer, "_HISTORY_DIR", tmp_path / "normalized" / "history")
    monkeypatch.setattr(normalizer, "_MANIFEST_PATH", tmp_path / "manifest.json")
    return tmp_path


def _persist_note(version: str, locale: str, title: str = "Versión X") -> PatchNote:
    sections = [PatchSection(title="Campeones", heading_level=2, blocks=["Buff a Aatrox"], subsections=[])]
    note = PatchNote(
        source_locale=locale,
        patch_version=version,
        title=title,
        canonical_url=f"https://x/{version}",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash=normalizer.compute_content_hash(sections),
        scraper_version="test-v1",
        sections=sections,
        summary="Buff a Aatrox y nerf a Lulu.",
    )
    normalizer.save_normalized(note)
    normalizer.update_manifest(note)
    return note


def test_list_patches_empty_returns_empty(isolated_dir) -> None:
    assert loader.list_patches() == []


def test_list_patches_returns_descending_versions(isolated_dir) -> None:
    _persist_note("25.17", "es-es")
    _persist_note("26.10", "es-es")
    _persist_note("26.09", "es-es")

    items = loader.list_patches()
    versions = [i.patch_version for i in items]
    assert versions == ["26.10", "26.09", "25.17"]


def test_list_patches_filters_by_locale(isolated_dir) -> None:
    _persist_note("26.10", "es-es")
    _persist_note("26.10", "en-us")

    es_only = loader.list_patches(locale="es-es")
    en_only = loader.list_patches(locale="en-us")

    assert len(es_only) == 1
    assert es_only[0].source_locale == "es-es"
    assert len(en_only) == 1
    assert en_only[0].source_locale == "en-us"


def test_list_patches_prefers_es_es_when_no_filter(isolated_dir) -> None:
    _persist_note("26.10", "es-es", title="Es ES")
    _persist_note("26.10", "en-us", title="En US")

    items = loader.list_patches()
    assert len(items) == 1
    assert items[0].source_locale == "es-es"
    assert items[0].title == "Es ES"


def test_load_patch_returns_full_note(isolated_dir) -> None:
    _persist_note("26.10", "es-es", title="Notas 26.10")
    note = loader.load_patch("26.10", locale="es-es")
    assert note is not None
    assert note.patch_version == "26.10"
    assert note.title == "Notas 26.10"
    assert len(note.sections) == 1


def test_load_patch_returns_none_when_missing(isolated_dir) -> None:
    assert loader.load_patch("99.99", locale="es-es") is None
