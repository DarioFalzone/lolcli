"""pipeline match_history: gaps, parse de payload match-v5, fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import match_history
from riot_lol_cli.jungle_research.riot_bridge import RiotBridge
from riot_lol_cli.jungle_research.schemas import ProAccount


@pytest.fixture
def tmp_storage(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    monkeypatch.setattr(json_storage, "MATCH_HISTORY_DIR", tmp_path / "match_history")
    return tmp_path


class _StubBridge(RiotBridge):
    def __init__(self, has_key: bool, match_ids=None, match_detail=None):
        self._has_key = has_key
        self._match_ids = match_ids or []
        self._match_detail = match_detail

    def has_key(self) -> bool:  # type: ignore[override]
        return self._has_key

    def fetch_recent_match_ids(self, puuid, server, count=20):  # type: ignore[override]
        return list(self._match_ids)

    def fetch_match_detail(self, match_id, server):  # type: ignore[override]
        return self._match_detail


def _account(**overrides) -> ProAccount:
    base = {
        "pro_player_id": "Canyon",
        "source": "manual_seed",
        "puuid": "PUUID-X",
        "server": "KR",
    }
    base.update(overrides)
    return ProAccount(**base)


def test_no_riot_key_returns_gap(tmp_storage):
    bridge = _StubBridge(has_key=False)
    entries, gaps = match_history.run_for_account(_account(), bridge=bridge, persist=False)
    assert entries == []
    assert any(g["reason"] == "RIOT_API_KEY ausente" for g in gaps)


def test_account_without_puuid_returns_gap(tmp_storage):
    bridge = _StubBridge(has_key=True)
    entries, gaps = match_history.run_for_account(
        _account(puuid=None), bridge=bridge, persist=False
    )
    assert entries == []
    assert any("PUUID" in g["reason"] for g in gaps)


def test_zero_matches_returns_gap(tmp_storage):
    bridge = _StubBridge(has_key=True, match_ids=[])
    entries, gaps = match_history.run_for_account(_account(), bridge=bridge, persist=False)
    assert entries == []
    assert any("0 partidas" in g["reason"] for g in gaps)


def test_parses_match_detail_and_persists(tmp_storage):
    fake_match = {
        "metadata": {"matchId": "KR_7000000001"},
        "info": {
            "queueId": 420,
            "gameVersion": "14.10.450.1234",
            "gameStartTimestamp": 1715000000000,
            "gameDuration": 1800,
            "participants": [
                {
                    "puuid": "PUUID-X",
                    "championName": "Wukong",
                    "teamPosition": "JUNGLE",
                    "win": True,
                    "kills": 5,
                    "deaths": 2,
                    "assists": 8,
                    "totalMinionsKilled": 30,
                    "neutralMinionsKilled": 120,
                    "goldEarned": 14000,
                    "totalDamageDealtToChampions": 22000,
                    "visionScore": 25,
                }
            ],
        },
    }
    bridge = _StubBridge(has_key=True, match_ids=["KR_7000000001"], match_detail=fake_match)
    entries, gaps = match_history.run_for_account(
        _account(), bridge=bridge, count=1, persist=True
    )
    assert len(entries) == 1
    e = entries[0]
    assert e.champion_name == "Wukong"
    assert e.win is True
    assert e.cs == 150
    assert e.detected_role == "JUNGLE"
    assert gaps == []
    # Persistencia
    puuid_dir = tmp_storage / "match_history" / "PUUID-X"
    assert puuid_dir.exists()
    files = list(puuid_dir.glob("*.json"))
    assert files


def test_run_iterates_multiple_accounts(tmp_storage):
    fake_match = {
        "metadata": {"matchId": "KR_7000000002"},
        "info": {
            "queueId": 420,
            "gameStartTimestamp": 1715000000000,
            "participants": [
                {"puuid": "PUUID-X", "championName": "LeeSin", "win": False}
            ],
        },
    }
    bridge = _StubBridge(has_key=True, match_ids=["KR_7000000002"], match_detail=fake_match)
    accounts = [_account(), _account(pro_player_id="Oner", puuid="PUUID-X")]
    out = match_history.run(accounts, bridge=bridge, count=1, persist=False)
    assert out.total_entries() == 2


def test_recent_pro_picks_no_key_returns_empty():
    bridge = _StubBridge(has_key=False)
    assert match_history.recent_pro_picks([_account()], bridge=bridge) == {}
