"""Tests para diff_patches — matching de secciones + change_type."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from riot_lol_cli.patch_notes import normalizer
from riot_lol_cli.patch_notes.diff import diff_patches
from riot_lol_cli.patch_notes.schema import PatchNote, PatchSection


def _make_note(version: str, sections: list[PatchSection], locale: str = "es-es") -> PatchNote:
    return PatchNote(
        source_locale=locale,
        patch_version=version,
        title=f"Versión {version}",
        canonical_url=f"https://x/{version}",
        fetched_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        content_hash=normalizer.compute_content_hash(sections),
        scraper_version="test",
        sections=sections,
    )


def test_diff_rejects_mixed_locales() -> None:
    a = _make_note("26.10", [], locale="es-es")
    b = _make_note("26.09", [], locale="en-us")
    with pytest.raises(ValueError):
        diff_patches(a, b)


def test_diff_unchanged_when_identical() -> None:
    sections = [PatchSection(title="Campeones", heading_level=2, blocks=["Igual"])]
    a = _make_note("26.10", sections)
    b = _make_note("26.10", sections)
    diff = diff_patches(a, b)
    assert all(s.change_type == "unchanged" for s in diff.sections)
    assert diff.summary["unchanged"] >= 1


def test_diff_modified_when_blocks_change() -> None:
    a = _make_note("26.10", [PatchSection(title="Campeones", heading_level=2, blocks=["Buff Aatrox"])])
    b = _make_note("26.11", [PatchSection(title="Campeones", heading_level=2, blocks=["Nerf Aatrox"])])
    diff = diff_patches(a, b)
    assert len(diff.sections) == 1
    assert diff.sections[0].change_type == "modified"
    assert diff.summary["modified"] == 1


def test_diff_added_when_section_only_in_b() -> None:
    a = _make_note("26.10", [PatchSection(title="Campeones", heading_level=2, blocks=["X"])])
    b = _make_note(
        "26.11",
        [
            PatchSection(title="Campeones", heading_level=2, blocks=["X"]),
            PatchSection(title="Ítems", heading_level=2, blocks=["Nuevo ítem"]),
        ],
    )
    diff = diff_patches(a, b)
    types = {s.title: s.change_type for s in diff.sections}
    assert types["Campeones"] == "unchanged"
    assert types["Ítems"] == "added"


def test_diff_removed_when_section_only_in_a() -> None:
    a = _make_note(
        "26.10",
        [
            PatchSection(title="Campeones", heading_level=2, blocks=["X"]),
            PatchSection(title="Bots", heading_level=2, blocks=["Vapps"]),
        ],
    )
    b = _make_note("26.11", [PatchSection(title="Campeones", heading_level=2, blocks=["X"])])
    diff = diff_patches(a, b)
    types = {s.title: s.change_type for s in diff.sections}
    assert types["Bots"] == "removed"


def test_diff_normalizes_titles_for_matching() -> None:
    """Misma sección con tildes diferentes debe matchear."""
    a = _make_note("26.10", [PatchSection(title="Ítems", heading_level=2, blocks=["A"])])
    b = _make_note("26.11", [PatchSection(title="Items", heading_level=2, blocks=["A"])])
    diff = diff_patches(a, b)
    assert len(diff.sections) == 1
    assert diff.sections[0].change_type == "unchanged"


def test_diff_recurses_into_subsections() -> None:
    a = _make_note(
        "26.10",
        [
            PatchSection(
                title="Campeones",
                heading_level=2,
                blocks=[],
                subsections=[PatchSection(title="Aatrox", heading_level=3, blocks=["Old"])],
            )
        ],
    )
    b = _make_note(
        "26.11",
        [
            PatchSection(
                title="Campeones",
                heading_level=2,
                blocks=[],
                subsections=[PatchSection(title="Aatrox", heading_level=3, blocks=["New"])],
            )
        ],
    )
    diff = diff_patches(a, b)
    assert diff.sections[0].change_type == "modified"
    assert diff.sections[0].sub_diffs[0].change_type == "modified"


def test_diff_summary_counts_all_change_types() -> None:
    a = _make_note(
        "26.10",
        [
            PatchSection(title="A", heading_level=2, blocks=["x"]),
            PatchSection(title="B", heading_level=2, blocks=["y"]),
        ],
    )
    b = _make_note(
        "26.11",
        [
            PatchSection(title="A", heading_level=2, blocks=["x"]),
            PatchSection(title="C", heading_level=2, blocks=["z"]),
        ],
    )
    diff = diff_patches(a, b)
    assert diff.summary["unchanged"] == 1
    assert diff.summary["removed"] == 1
    assert diff.summary["added"] == 1
