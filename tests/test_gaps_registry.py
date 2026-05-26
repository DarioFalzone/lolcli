"""Tests unitarios para el Registro Global de Gaps (gaps_registry)."""

from __future__ import annotations

from pathlib import Path

import pytest

from riot_lol_cli import gaps_registry


@pytest.fixture
def tmp_gaps_file(tmp_path: Path, monkeypatch) -> Path:
    target = tmp_path / "global_gaps.json"
    monkeypatch.setattr(gaps_registry, "GAPS_FILE", target)
    return target


def test_read_global_gaps_returns_empty_when_no_file(tmp_gaps_file):
    assert gaps_registry.read_global_gaps() == []


def test_register_gap_creates_file_with_correct_payload(tmp_gaps_file):
    gaps_registry.register_gap(
        source="test_source",
        gap_id="test_gap",
        description="Brecha de prueba",
        severity="info",
        action_required="Ninguna acción",
    )

    assert tmp_gaps_file.exists()
    gaps = gaps_registry.read_global_gaps()
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap["source"] == "test_source"
    assert gap["gap_id"] == "test_gap"
    assert gap["description"] == "Brecha de prueba"
    assert gap["severity"] == "info"
    assert gap["action_required"] == "Ninguna acción"
    assert "detected_at" in gap


def test_register_gap_overwrites_existing(tmp_gaps_file):
    gaps_registry.register_gap("test_source", "test_gap", "Primera descripción")
    gaps_registry.register_gap("test_source", "test_gap", "Segunda descripción")

    gaps = gaps_registry.read_global_gaps()
    assert len(gaps) == 1
    assert gaps[0]["description"] == "Segunda descripción"


def test_clear_gap_removes_correct_record(tmp_gaps_file):
    gaps_registry.register_gap("src1", "gap1", "Desc1")
    gaps_registry.register_gap("src2", "gap2", "Desc2")

    gaps_registry.clear_gap("src1", "gap1")
    gaps = gaps_registry.read_global_gaps()
    assert len(gaps) == 1
    assert gaps[0]["source"] == "src2"


def test_clear_source_gaps_removes_all_records(tmp_gaps_file):
    gaps_registry.register_gap("src1", "gap1", "Desc1")
    gaps_registry.register_gap("src1", "gap2", "Desc2")
    gaps_registry.register_gap("src2", "gap3", "Desc3")

    gaps_registry.clear_source_gaps("src1")
    gaps = gaps_registry.read_global_gaps()
    assert len(gaps) == 1
    assert gaps[0]["source"] == "src2"


def test_utf8_no_bom_in_written_file(tmp_gaps_file):
    gaps_registry.register_gap("src", "gap", "Tilde á é í ó ú ñ")
    assert tmp_gaps_file.exists()

    # Leer en binario para verificar que no empiece con los bytes del BOM EF BB BF
    raw = tmp_gaps_file.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
