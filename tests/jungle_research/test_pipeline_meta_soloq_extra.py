"""Pipeline meta_soloq_extra: orquesta los 4 adapters V3."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import meta_soloq_extra


@pytest.fixture
def tmp_storage(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    monkeypatch.setattr(json_storage, "ADAPTER_RUNS_FILE", tmp_path / "adapter_runs.json")
    return tmp_path


class _StubOkAdapter:
    """Adapter falso que retorna data ok para tests."""

    def __init__(self, source_id: str, champion_count: int = 3):
        self.source_id = source_id
        self._count = champion_count

    def fetch_jungle_tier_list(self, elo: str = "emerald_plus") -> dict:
        return {
            "platform": self.source_id,
            "source_url": f"https://{self.source_id}.example",
            "role": "jungle",
            "patch": "26.10",
            "elo": elo,
            "status": "ok",
            "champions": [
                {"id": f"C{i}", "display_name": f"C{i}", "win_rate": 50.0 + i, "pick_rate": 5.0, "games": 1000}
                for i in range(self._count)
            ],
            "champion_count": self._count,
            "scraped_at": "2026-05-12T10:00:00Z",
        }


class _StubNotImplementedAdapter:
    def fetch_jungle_tier_list(self, elo: str = "emerald_plus") -> dict:
        return {
            "platform": "stub",
            "source_url": "https://stub.example",
            "status": "not_implemented",
            "reason": "stub para tests",
            "champions": [],
            "champion_count": 0,
            "scraped_at": "2026-05-12T10:00:00Z",
        }


class _StubRaisingAdapter:
    def fetch_jungle_tier_list(self, elo: str = "emerald_plus") -> dict:
        raise RuntimeError("conexion timeout")


def test_default_adapters_all_not_implemented(tmp_storage):
    """Los 4 default adapters retornan not_implemented sin tocar red."""
    result = meta_soloq_extra.run(persist=False)
    assert len(result.snapshots) == 0
    assert len(result.runs) == 4
    ids = {r.adapter_id for r in result.runs}
    assert ids == {
        "metasrc_jungle",
        "mobalytics_jungle_tierlist",
        "leagueofgraphs_jungle",
        "tracker_gg_lol",
    }
    assert all(r.status == "not_implemented" for r in result.runs)


def test_ok_adapter_produces_snapshots(tmp_storage):
    adapters = {"metasrc_jungle": _StubOkAdapter("metasrc", champion_count=5)}
    result = meta_soloq_extra.run(adapters=adapters, persist=False)
    assert len(result.snapshots) == 5
    assert result.runs[0].status == "ok"
    assert result.runs[0].champion_count == 5
    assert result.snapshots[0].source_id == "metasrc_jungle"
    assert result.snapshots[0].role == "jungle"


def test_raising_adapter_caught_and_logged_as_error(tmp_storage):
    adapters = {"failing": _StubRaisingAdapter()}
    result = meta_soloq_extra.run(adapters=adapters, persist=False)
    assert result.snapshots == []
    assert result.runs[0].status == "error"
    assert "conexion timeout" in result.runs[0].reason


def test_persist_writes_adapter_runs_json(tmp_storage):
    adapters = {
        "metasrc_jungle": _StubOkAdapter("metasrc"),
        "mobalytics_jungle_tierlist": _StubNotImplementedAdapter(),
    }
    meta_soloq_extra.run(adapters=adapters, persist=True)
    assert json_storage.ADAPTER_RUNS_FILE.exists()
    payload = json.loads(json_storage.ADAPTER_RUNS_FILE.read_text(encoding="utf-8"))
    runs = payload["runs"]
    assert "metasrc_jungle" in runs
    assert "mobalytics_jungle_tierlist" in runs
    assert runs["metasrc_jungle"]["status"] == "ok"
    assert runs["mobalytics_jungle_tierlist"]["status"] == "not_implemented"


def test_persist_merges_with_previous_runs(tmp_storage):
    # Primer run: metasrc ok
    meta_soloq_extra.run(
        adapters={"metasrc_jungle": _StubOkAdapter("metasrc")},
        persist=True,
    )
    # Segundo run: solo tracker_gg, metasrc no se ejecuta — su telemetría debe persistir.
    meta_soloq_extra.run(
        adapters={"tracker_gg_lol": _StubNotImplementedAdapter()},
        persist=True,
    )
    payload = json.loads(json_storage.ADAPTER_RUNS_FILE.read_text(encoding="utf-8"))
    runs = payload["runs"]
    assert "metasrc_jungle" in runs  # preservado del run anterior
    assert "tracker_gg_lol" in runs


def test_mixed_results_only_ok_produce_snapshots(tmp_storage):
    adapters = {
        "ok1": _StubOkAdapter("ok1", champion_count=2),
        "not_impl": _StubNotImplementedAdapter(),
        "ok2": _StubOkAdapter("ok2", champion_count=3),
    }
    result = meta_soloq_extra.run(adapters=adapters, persist=False)
    assert len(result.snapshots) == 5  # 2 + 0 + 3
    statuses = {r.adapter_id: r.status for r in result.runs}
    assert statuses == {"ok1": "ok", "not_impl": "not_implemented", "ok2": "ok"}
