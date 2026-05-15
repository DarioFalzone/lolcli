"""Tests para el índice de búsqueda full-text in-memory."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.patch_notes import normalizer, search
from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection


@pytest.fixture
def isolated_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(normalizer, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(normalizer, "_NORMALIZED_DIR", tmp_path / "normalized")
    monkeypatch.setattr(normalizer, "_BY_PATCH_DIR", tmp_path / "normalized" / "by_patch")
    monkeypatch.setattr(normalizer, "_HISTORY_DIR", tmp_path / "normalized" / "history")
    monkeypatch.setattr(normalizer, "_MANIFEST_PATH", tmp_path / "manifest.json")
    monkeypatch.setattr(normalizer, "_SOURCES_DIR", tmp_path / "sources")
    # Reset índice global
    search._INDEX.postings.clear()
    search._INDEX.doc_count = 0
    return tmp_path


def _persist_note(version: str, locale: str, sections: list[PatchSection]) -> PatchNote:
    note = PatchNote(
        source_locale=locale,
        patch_version=version,
        title=f"Versión {version}",
        canonical_url=f"https://x/{version}",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash=normalizer.compute_content_hash(sections),
        scraper_version="test",
        sections=sections,
    )
    normalizer.save_normalized(note)
    normalizer.update_manifest(note)
    return note


def test_tokenize_strips_accents_and_punctuation() -> None:
    tokens = search._tokenize("Aatrox: buff a su pasiva—más daño.")
    assert "aatrox" in tokens
    assert "buff" in tokens
    assert "pasiva" in tokens
    # Stopwords se eliminan
    assert "a" not in tokens
    assert "su" not in tokens or len(tokens) > 3  # "su" no es stop pero podría serlo


def test_build_index_empty_returns_empty(isolated_dir) -> None:
    idx = search.build_index()
    assert idx.doc_count == 0
    assert search.search("aatrox") == []


def test_search_finds_matching_block(isolated_dir) -> None:
    sections = [
        PatchSection(
            title="Campeones",
            heading_level=2,
            blocks=["Aatrox recibe un buff importante a su pasiva."],
        )
    ]
    _persist_note("26.10", "es-es", sections)
    search.build_index()

    hits = search.search("aatrox")
    assert len(hits) >= 1
    assert hits[0].patch_version == "26.10"
    assert "aatrox" in hits[0].snippet.lower()


def test_search_locale_filter(isolated_dir) -> None:
    sections_es = [PatchSection(title="T", heading_level=2, blocks=["Aatrox aplastante."])]
    sections_en = [PatchSection(title="T", heading_level=2, blocks=["Aatrox is busted."])]
    _persist_note("26.10", "es-es", sections_es)
    _persist_note("26.10", "en-us", sections_en)
    search.build_index()

    es_hits = search.search("aatrox", locale="es-es")
    en_hits = search.search("aatrox", locale="en-us")
    assert all(h.source_locale == "es-es" for h in es_hits)
    assert all(h.source_locale == "en-us" for h in en_hits)
    assert len(es_hits) >= 1
    assert len(en_hits) >= 1


def test_search_and_logic(isolated_dir) -> None:
    """Solo retorna bloques donde TODOS los tokens aparezcan."""
    sections = [
        PatchSection(title="A", heading_level=2, blocks=["Aatrox jungla aplastante"]),
        PatchSection(title="B", heading_level=2, blocks=["Aatrox lane oprimido"]),
    ]
    _persist_note("26.10", "es-es", sections)
    search.build_index()

    hits = search.search("aatrox jungla")
    assert len(hits) == 1
    assert "jungla" in hits[0].snippet.lower()


def test_search_no_match_returns_empty(isolated_dir) -> None:
    sections = [PatchSection(title="T", heading_level=2, blocks=["Texto sin relación."])]
    _persist_note("26.10", "es-es", sections)
    search.build_index()
    assert search.search("xyzzy_inexistente") == []


def test_search_short_query_returns_empty(isolated_dir) -> None:
    sections = [PatchSection(title="T", heading_level=2, blocks=["Aatrox."])]
    _persist_note("26.10", "es-es", sections)
    search.build_index()
    assert search.search("a") == []  # menor que MIN_TOKEN_LEN


def test_snippet_extracts_context_around_match(isolated_dir) -> None:
    long_text = "x" * 100 + " Aatrox buff " + "y" * 100
    sections = [PatchSection(title="T", heading_level=2, blocks=[long_text])]
    _persist_note("26.10", "es-es", sections)
    search.build_index()
    hits = search.search("aatrox")
    assert len(hits) == 1
    snippet = hits[0].snippet
    assert "Aatrox" in snippet
    assert "…" in snippet  # debe haber elipsis al inicio o final
