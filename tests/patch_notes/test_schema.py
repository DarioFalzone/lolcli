"""Tests del schema Pydantic V2 del subsistema patch_notes."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from riot_lol_cli.patch_notes.schema import (
    PatchAsset,
    PatchManifest,
    PatchNote,
    PatchNoteIndex,
    PatchSection,
)


def _valid_note_payload(**overrides) -> dict:
    base = {
        "source_locale": "es-es",
        "patch_version": "26.10",
        "title": "Notas de la versión 26.10",
        "canonical_url": "https://www.leagueoflegends.com/es-es/news/game-updates/patch-26-10-notes",
        "fetched_at": datetime(2026, 5, 15, 18, 0, tzinfo=timezone.utc),
        "content_hash": "a" * 64,
        "scraper_version": "patch_notes_v1.0.0",
        "sections": [],
        "assets": [],
    }
    base.update(overrides)
    return base


def test_patch_note_minimal_valid() -> None:
    note = PatchNote.model_validate(_valid_note_payload())
    assert note.publisher == "riot"
    assert note.game == "lol"
    assert note.channel == "site"
    assert note.patch_version == "26.10"


def test_patch_note_rejects_short_hash() -> None:
    with pytest.raises(ValidationError):
        PatchNote.model_validate(_valid_note_payload(content_hash="short"))


def test_patch_note_rejects_invalid_publisher() -> None:
    with pytest.raises(ValidationError):
        PatchNote.model_validate({**_valid_note_payload(), "publisher": "blizzard"})


def test_patch_section_recursive() -> None:
    section = PatchSection(
        title="Campeones",
        heading_level=2,
        blocks=["Cambios generales."],
        subsections=[
            PatchSection(
                title="Aatrox",
                heading_level=3,
                blocks=["Pasiva — algo cambia."],
                subsections=[],
            )
        ],
    )
    assert len(section.subsections) == 1
    assert section.subsections[0].title == "Aatrox"
    dumped = section.model_dump()
    rebuilt = PatchSection.model_validate(dumped)
    assert rebuilt.subsections[0].title == "Aatrox"


def test_patch_asset_image_and_link() -> None:
    image = PatchAsset(asset_type="image", src="https://example.com/img.png", alt="Splash")
    link = PatchAsset(asset_type="link", src="https://example.com", text="Ver más")
    assert image.asset_type == "image"
    assert link.asset_type == "link"

    with pytest.raises(ValidationError):
        PatchAsset(asset_type="video", src="x")


def test_patch_note_index_compact() -> None:
    idx = PatchNoteIndex(
        patch_version="26.10",
        title="Notas",
        canonical_url="https://x",
        source_locale="es-es",
        content_hash="b" * 64,
        section_count=3,
    )
    assert idx.section_count == 3
    assert idx.summary is None


def test_patch_manifest_empty_default() -> None:
    manifest = PatchManifest(scraper_version="patch_notes_v1.0.0")
    assert manifest.entries == []
    assert manifest.locales == []
    assert manifest.available_patches == []
