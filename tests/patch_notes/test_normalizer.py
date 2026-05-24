"""Tests del normalizer: hash estable, save_normalized, manifest, detect_change."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from riot_lol_cli.patch_notes import normalizer
from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection


def _make_note(
    *, version: str = "26.10", locale: str = "es-es", hash_val: str | None = None, sections: list[PatchSection] | None = None
) -> PatchNote:
    sections = sections or [PatchSection(title="Test", heading_level=2, blocks=["Bloque 1"], subsections=[])]
    if hash_val is None:
        hash_val = normalizer.compute_content_hash(sections)
    return PatchNote(
        source_locale=locale,
        patch_version=version,
        title=f"Versión {version}",
        canonical_url=f"https://x/{version}",
        fetched_at=datetime(2026, 5, 15, 18, 0, tzinfo=timezone.utc),
        content_hash=hash_val,
        scraper_version="test-v1",
        sections=sections,
    )


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(normalizer, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(normalizer, "_NORMALIZED_DIR", tmp_path / "normalized")
    monkeypatch.setattr(normalizer, "_BY_PATCH_DIR", tmp_path / "normalized" / "by_patch")
    monkeypatch.setattr(normalizer, "_HISTORY_DIR", tmp_path / "normalized" / "history")
    monkeypatch.setattr(normalizer, "_MANIFEST_PATH", tmp_path / "manifest.json")
    return tmp_path


def test_compute_content_hash_is_deterministic() -> None:
    sections = [PatchSection(title="A", heading_level=2, blocks=["x"])]
    h1 = normalizer.compute_content_hash(sections)
    h2 = normalizer.compute_content_hash(sections)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_content_hash_differs_when_text_changes() -> None:
    s1 = [PatchSection(title="A", heading_level=2, blocks=["original"])]
    s2 = [PatchSection(title="A", heading_level=2, blocks=["modificado"])]
    assert normalizer.compute_content_hash(s1) != normalizer.compute_content_hash(s2)


def test_save_normalized_writes_by_patch_and_history(isolated_data_dir) -> None:
    note = _make_note()
    path = normalizer.save_normalized(note)

    assert path.exists()
    assert path.name == "26.10_es-es.json"

    history_files = list((isolated_data_dir / "normalized" / "history").glob("*.json"))
    assert len(history_files) == 1

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["patch_version"] == "26.10"
    assert data["source_locale"] == "es-es"


def test_update_manifest_appends_and_updates(isolated_data_dir) -> None:
    note = _make_note()
    manifest = normalizer.update_manifest(note)
    assert manifest.available_patches == ["26.10"]
    assert manifest.locales == ["es-es"]
    assert len(manifest.entries) == 1

    note2 = _make_note(locale="en-us", hash_val="c" * 64)
    manifest2 = normalizer.update_manifest(note2)
    assert sorted(manifest2.locales) == ["en-us", "es-es"]
    assert len(manifest2.entries) == 2


def test_update_manifest_replaces_same_version_locale(isolated_data_dir) -> None:
    first = _make_note(hash_val="a" * 64)
    normalizer.update_manifest(first)
    second = _make_note(hash_val="b" * 64)
    manifest = normalizer.update_manifest(second)
    matching = [e for e in manifest.entries if e.patch_version == "26.10" and e.source_locale == "es-es"]
    assert len(matching) == 1
    assert matching[0].content_hash == "b" * 64


def test_detect_change_when_no_manifest(isolated_data_dir) -> None:
    assert normalizer.detect_change("26.10", "es-es", "a" * 64) is True


def test_detect_change_when_hash_same(isolated_data_dir) -> None:
    note = _make_note(hash_val="a" * 64)
    normalizer.save_normalized(note)
    normalizer.update_manifest(note)
    assert normalizer.detect_change("26.10", "es-es", "a" * 64) is False


def test_detect_change_when_hash_different(isolated_data_dir) -> None:
    note = _make_note(hash_val="a" * 64)
    normalizer.save_normalized(note)
    normalizer.update_manifest(note)
    assert normalizer.detect_change("26.10", "es-es", "b" * 64) is True


def test_version_sort_key_orders_correctly() -> None:
    versions = ["25.17", "26.10b", "26.10", "26.09"]
    ordered = sorted(versions, key=normalizer._version_sort_key, reverse=True)
    assert ordered == ["26.10b", "26.10", "26.09", "25.17"]
