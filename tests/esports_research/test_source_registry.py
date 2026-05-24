from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.schemas import SourceStatus, SourceType
from riot_lol_cli.esports_research.source_registry import SourceRegistry


def test_load_real_sources_json_validates():
    registry = SourceRegistry.load()
    assert len(registry.all()) == 12


def test_summary_expected_v0_counts():
    summary = SourceRegistry.load().summary()
    assert summary["active"] == 4
    assert summary["stub"] == 6
    assert summary["restricted"] == 1
    assert summary["planned"] == 1
    assert summary["total"] == 12


def test_active_sources_include_public_v0():
    ids = {source.id for source in SourceRegistry.load().active()}
    assert {"leaguepedia", "oracles_elixir", "gol_gg", "data_dragon"} <= ids


def test_by_type_finds_community_html():
    html_sources = SourceRegistry.load().by_type(SourceType.COMMUNITY_HTML)
    assert [source.id for source in html_sources] == ["gol_gg"]


def test_filter_active_drops_stub():
    registry = SourceRegistry.load()
    filtered = registry.filter_active(["leaguepedia", "pandascore"])
    assert [source.id for source in filtered] == ["leaguepedia"]


def test_status_accessors():
    registry = SourceRegistry.load()
    assert len(registry.stubs()) == 6
    assert len(registry.planned()) == 1
    assert len(registry.restricted()) == 1


def test_invalid_source_raises(tmp_path: Path, monkeypatch):
    fake = tmp_path / "sources.json"
    fake.write_text(json.dumps({"sources": [{"id": "bad"}]}), encoding="utf-8")
    monkeypatch.setattr(json_storage, "SOURCES_FILE", fake)
    with pytest.raises(ValueError):
        SourceRegistry.load()


def test_get_unknown_returns_none():
    assert SourceRegistry.load().get("missing") is None


def test_source_status_enum_has_compliance_states():
    assert SourceStatus.STUB.value == "stub"
    assert SourceStatus.RESTRICTED.value == "restricted"
