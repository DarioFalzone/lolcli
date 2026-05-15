"""SourceRegistry sobre el JSON real del repo y casos sintéticos."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.schemas import SourceStatus, SourceType
from riot_lol_cli.jungle_research.source_registry import SourceRegistry


def test_load_real_sources_json_validates():
    """Debe poder validar el sources.json shipped en data/."""
    registry = SourceRegistry.load()
    assert len(registry.all()) > 0


def test_real_sources_have_required_fields():
    registry = SourceRegistry.load()
    for source in registry.all():
        assert source.id
        assert source.name
        assert source.base_url.startswith("http")
        assert source.created_at
        assert source.updated_at


def test_real_sources_have_active_layer():
    """V1 requiere al menos 1 fuente active de SOLOQ_META y 1 OFFICIAL_API."""
    registry = SourceRegistry.load()
    soloq_active = [
        s for s in registry.active() if s.source_type == SourceType.SOLOQ_META
    ]
    api_active = [
        s for s in registry.active() if s.source_type == SourceType.OFFICIAL_API
    ]
    assert soloq_active, "Falta al menos una fuente soloq_meta activa"
    assert api_active, "Falta al menos una fuente official_api activa"


def test_curated_local_present():
    """Jungle Meta :8003 debe estar registrada como curated_local."""
    registry = SourceRegistry.load()
    curated = registry.by_type(SourceType.CURATED_LOCAL)
    assert any(s.id == "jungle_meta_local" for s in curated)


def test_summary_sums_to_total():
    registry = SourceRegistry.load()
    summary = registry.summary()
    total = summary.pop("total")
    assert sum(summary.values()) == total


def test_load_synthetic(tmp_path: Path, monkeypatch):
    """SourceRegistry.load() debe respetar el path canónico vía json_storage."""
    fake = tmp_path / "sources.json"
    fake.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "x",
                        "name": "X",
                        "base_url": "https://x.example",
                        "source_type": "soloq_meta",
                        "status": "active",
                        "created_at": "2026-05-11T20:00:00Z",
                        "updated_at": "2026-05-11T20:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(json_storage, "SOURCES_FILE", fake)
    registry = SourceRegistry.load()
    assert len(registry.all()) == 1
    assert registry.get("x").status == SourceStatus.ACTIVE


def test_invalid_source_raises(tmp_path: Path, monkeypatch):
    fake = tmp_path / "sources.json"
    fake.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "x",
                        "name": "X",
                        "base_url": "https://x",
                        "source_type": "INVALID_TYPE_BAD",
                        "created_at": "2026-05-11T20:00:00Z",
                        "updated_at": "2026-05-11T20:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(json_storage, "SOURCES_FILE", fake)
    with pytest.raises(ValueError):
        SourceRegistry.load()


def test_filter_active_only_returns_active():
    registry = SourceRegistry.load()
    all_ids = [s.id for s in registry.all()]
    filtered = registry.filter_active(all_ids)
    assert all(s.status == SourceStatus.ACTIVE for s in filtered)
