"""Pipeline meta_asia: orquesta 8 adapters V4 + produce asia_presence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import meta_asia


@pytest.fixture
def tmp_storage(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    monkeypatch.setattr(json_storage, "ADAPTER_RUNS_FILE", tmp_path / "adapter_runs.json")
    monkeypatch.setattr(json_storage, "ASIA_PRESENCE_FILE", tmp_path / "asia_presence.json")
    return tmp_path


class _StubOkAdapter:
    def __init__(self, source_id: str, champions: list[dict]):
        self.source_id = source_id
        self._champs = champions

    def fetch_jungle_tier_list(self, elo: str = "challenger") -> dict:
        return {
            "platform": self.source_id,
            "source_url": f"https://{self.source_id}.example",
            "patch": "26.10",
            "status": "ok",
            "champions": self._champs,
            "champion_count": len(self._champs),
            "scraped_at": "2026-05-12T10:00:00Z",
        }


class _StubNotImpl:
    def fetch_jungle_tier_list(self, elo: str = "challenger") -> dict:
        return {
            "platform": "stub",
            "source_url": "https://stub.example",
            "status": "not_implemented",
            "reason": "stub para tests",
            "champions": [],
            "champion_count": 0,
            "scraped_at": "2026-05-12T10:00:00Z",
        }


def test_default_adapters_all_not_implemented(tmp_storage):
    """Los 9 default adapters retornan not_implemented sin tocar red."""
    result = meta_asia.run(persist=False)
    assert len(result.snapshots) == 0
    assert result.asia_presence == {}
    assert len(result.runs) == 9  # 9 adapters en _default_adapters
    ids = {r.adapter_id for r in result.runs}
    assert ids == {
        "opgg_kr", "opgg_jp", "opgg_cn",
        "porogg_champions", "fow_kr", "lolps",
        "deeplol_kr_jungle", "tencent_101", "tencent_rank",
    }
    assert all(r.status == "not_implemented" for r in result.runs)


def test_ok_adapter_produces_asia_snapshots_with_region(tmp_storage):
    """Un adapter KR debe producir snapshots con region=KR (no GLOBAL)."""
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Wukong", "display_name": "Wukong", "win_rate": 54.0, "games": 3000},
        ]),
    }
    result = meta_asia.run(adapters=adapters, persist=False)
    assert len(result.snapshots) == 1
    assert result.snapshots[0].region == "KR"
    assert result.snapshots[0].source_id == "opgg_kr"


def test_asia_presence_pondera_por_region(tmp_storage):
    """KR (peso 1.0) > CN (0.8) > JP (0.5). Wukong en KR debe pesar mas que solo JP."""
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Wukong", "display_name": "Wukong", "win_rate": 55.0, "games": 3000},
        ]),
        "opgg_jp": _StubOkAdapter("opgg_jp", [
            {"id": "LeeSin", "display_name": "Lee Sin", "win_rate": 55.0, "games": 3000},
        ]),
    }
    result = meta_asia.run(adapters=adapters, persist=False)
    assert "Wukong" in result.asia_presence
    assert "Lee Sin" in result.asia_presence
    # Normalizado: Wukong (KR 1.0) > Lee Sin (JP 0.5)
    assert result.asia_presence["Wukong"] > result.asia_presence["Lee Sin"]
    # Maximo normalizado a 1.0
    assert max(result.asia_presence.values()) == 1.0


def test_asia_presence_pondera_por_winrate(tmp_storage):
    """WR>=53% (full) > WR 50-53% (medio) > WR<50% (bajo)."""
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Strong", "display_name": "Strong", "win_rate": 56.0},
            {"id": "Mid", "display_name": "Mid", "win_rate": 51.0},
            {"id": "Weak", "display_name": "Weak", "win_rate": 47.0},
        ]),
    }
    result = meta_asia.run(adapters=adapters, persist=False)
    assert result.asia_presence["Strong"] > result.asia_presence["Mid"]
    assert result.asia_presence["Mid"] > result.asia_presence["Weak"]


def test_mixed_implementations_only_ok_produce_presence(tmp_storage):
    """Stubs not_implemented no contaminan asia_presence."""
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Champ", "display_name": "Champ", "win_rate": 55.0},
        ]),
        "fow_kr": _StubNotImpl(),
    }
    result = meta_asia.run(adapters=adapters, persist=False)
    assert "Champ" in result.asia_presence
    assert len(result.snapshots) == 1


def test_persist_writes_asia_presence_cache(tmp_storage):
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Wukong", "display_name": "Wukong", "win_rate": 55.0},
        ]),
    }
    meta_asia.run(adapters=adapters, persist=True)
    assert json_storage.ASIA_PRESENCE_FILE.exists()
    payload = json.loads(json_storage.ASIA_PRESENCE_FILE.read_text(encoding="utf-8"))
    assert payload["snapshot_count"] == 1
    assert payload["asia_presence"]["Wukong"] == 1.0


def test_read_cached_asia_presence_returns_empty_if_no_cache(tmp_storage):
    assert meta_asia.read_cached_asia_presence() == {}


def test_read_cached_asia_presence_returns_dict_after_persist(tmp_storage):
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "Wukong", "display_name": "Wukong", "win_rate": 55.0},
        ]),
    }
    meta_asia.run(adapters=adapters, persist=True)
    cached = meta_asia.read_cached_asia_presence()
    assert cached == {"Wukong": 1.0}


def test_compute_asia_presence_handles_no_winrate(tmp_storage):
    """WR None debe usar boost 0.5 (no fallar)."""
    adapters = {
        "opgg_kr": _StubOkAdapter("opgg_kr", [
            {"id": "X", "display_name": "X"},  # sin win_rate
        ]),
    }
    result = meta_asia.run(adapters=adapters, persist=False)
    assert "X" in result.asia_presence
