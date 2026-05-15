"""pipeline pro_accounts: gaps controlados, mock RiotBridge."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import pro_accounts
from riot_lol_cli.jungle_research.riot_bridge import ResolutionResult, RiotBridge


@pytest.fixture
def tmp_seed(tmp_path: Path, monkeypatch) -> Path:
    seed_file = tmp_path / "pro_players_seed.json"
    accounts_file = tmp_path / "pro_accounts.json"
    seed_file.write_text(
        json.dumps(
            {
                "players": [
                    {
                        "player_name": "Canyon",
                        "priority_tier": "S",
                        "riot_id": "DK Canyon#KR1",
                        "server": "KR",
                    },
                    {
                        "player_name": "Oner",
                        "priority_tier": "S",
                        # sin riot_id — debe quedar como needs_account_resolution
                    },
                    {
                        "player_name": "Kanavi",
                        "priority_tier": "A",
                        "riot_id": {"game_name": "JDG Kanavi", "tagline": "1234"},
                        "server": "CN",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(json_storage, "PRO_PLAYERS_SEED_FILE", seed_file)
    monkeypatch.setattr(json_storage, "PRO_ACCOUNTS_FILE", accounts_file)
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    return tmp_path


class _StubBridge(RiotBridge):
    """Bridge sin tocar Riot: devuelve PUUIDs determinísticos."""

    def __init__(self, has_key: bool = True, results: dict | None = None):
        self._has_key = has_key
        self._results = results or {}

    def has_key(self) -> bool:  # type: ignore[override]
        return self._has_key

    def resolve_riot_id(self, game_name: str, tagline: str, server: str):  # type: ignore[override]
        key = (game_name, tagline, server)
        if key in self._results:
            return self._results[key]
        return ResolutionResult(
            riot_id_game_name=game_name,
            riot_id_tagline=tagline,
            server=server,
            puuid=f"PUUID-{game_name.replace(' ', '')}",
        )


def test_no_riot_key_marks_all_as_no_riot_key(tmp_seed):
    bridge = _StubBridge(has_key=False)
    result = pro_accounts.run(bridge=bridge, persist=False)
    assert result.resolved_count == 0
    flags = {a.gap_flag for a in result.accounts}
    assert "no_riot_key" in flags
    assert "needs_account_resolution" in flags  # Oner sin riot_id


def test_resolution_succeeds_when_bridge_returns_puuid(tmp_seed):
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.run(bridge=bridge, persist=False)
    by_player = {a.pro_player_id: a for a in result.accounts}
    assert by_player["Canyon"].puuid == "PUUID-DKCanyon"
    assert by_player["Oner"].gap_flag == "needs_account_resolution"
    assert by_player["Kanavi"].puuid == "PUUID-JDGKanavi"
    assert result.resolved_count == 2


def test_persists_to_pro_accounts_file(tmp_seed):
    bridge = _StubBridge(has_key=True)
    pro_accounts.run(bridge=bridge, persist=True)
    payload = json.loads(json_storage.PRO_ACCOUNTS_FILE.read_text(encoding="utf-8"))
    assert payload["total_count"] == 3
    assert payload["resolved_count"] == 2


def test_parse_riot_id_string_format():
    assert pro_accounts._parse_riot_id("Foo#TAG") == ("Foo", "TAG")
    assert pro_accounts._parse_riot_id("Foo#") is None
    assert pro_accounts._parse_riot_id("#TAG") is None
    assert pro_accounts._parse_riot_id("no_separator") is None


def test_parse_riot_id_dict_format():
    assert pro_accounts._parse_riot_id({"game_name": "X", "tagline": "TAG"}) == ("X", "TAG")
    assert pro_accounts._parse_riot_id({"game_name": "X"}) is None
    assert pro_accounts._parse_riot_id({}) is None
    assert pro_accounts._parse_riot_id(None) is None


def test_real_seed_loads_without_riot_id(monkeypatch, tmp_path: Path):
    """El seed shipped no trae riot_id; todos deben quedar needs_account_resolution."""
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    monkeypatch.setattr(json_storage, "PRO_ACCOUNTS_FILE", tmp_path / "pro_accounts.json")
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.run(bridge=bridge, persist=False)
    assert result.resolved_count == 0  # nadie tiene riot_id en el seed real
    assert all(a.gap_flag == "needs_account_resolution" for a in result.accounts)
    assert len(result.accounts) == 11  # 11 pros del seed shipped


# ---------------------------------------------------------------------------
# V2: set_pro_account — upsert puntual desde endpoint
# ---------------------------------------------------------------------------


def test_set_pro_account_invalid_riot_id_format(tmp_seed):
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.set_pro_account(
        "Canyon", riot_id="no_separator", server="KR", bridge=bridge
    )
    assert result["updated"] is False
    assert "formato" in result["error"].lower()


def test_set_pro_account_riot_id_without_server(tmp_seed):
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.set_pro_account(
        "Canyon", riot_id="DK Canyon#KR1", server=None, bridge=bridge
    )
    assert result["updated"] is False
    assert "server" in result["error"].lower()


def test_set_pro_account_unknown_player(tmp_seed):
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.set_pro_account(
        "FakerJungla", riot_id="X#Y", server="KR", bridge=bridge
    )
    assert result["updated"] is False
    assert "no está en el seed" in result["error"]


def test_set_pro_account_clears_when_riot_id_none(tmp_seed):
    """Pasar riot_id=None debe limpiar la cuenta del seed."""
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.set_pro_account(
        "Canyon", riot_id=None, server=None, bridge=bridge
    )
    assert result["updated"] is True
    assert result["gap_flag"] == "needs_account_resolution"
    # Verificar que el seed quedó actualizado.
    raw = json.loads(json_storage.PRO_PLAYERS_SEED_FILE.read_text(encoding="utf-8"))
    canyon = next(p for p in raw["players"] if p["player_name"] == "Canyon")
    assert canyon["riot_id"] is None
    assert canyon["server"] is None


def test_set_pro_account_resolves_when_key_present(tmp_seed):
    bridge = _StubBridge(has_key=True)
    result = pro_accounts.set_pro_account(
        "Oner", riot_id="T1 Oner#KR1", server="KR", bridge=bridge
    )
    assert result["updated"] is True
    assert result["resolved"] is True
    assert result["puuid"] == "PUUID-T1Oner"
    # El seed debe reflejar el cambio.
    raw = json.loads(json_storage.PRO_PLAYERS_SEED_FILE.read_text(encoding="utf-8"))
    oner = next(p for p in raw["players"] if p["player_name"] == "Oner")
    assert oner["riot_id"] == "T1 Oner#KR1"
    assert oner["server"] == "KR"
    # pro_accounts.json se actualizó.
    accounts_payload = json.loads(json_storage.PRO_ACCOUNTS_FILE.read_text(encoding="utf-8"))
    oner_acc = next(a for a in accounts_payload["accounts"] if a["pro_player_id"] == "Oner")
    assert oner_acc["puuid"] == "PUUID-T1Oner"


def test_set_pro_account_no_key_marks_pending(tmp_seed):
    bridge = _StubBridge(has_key=False)
    result = pro_accounts.set_pro_account(
        "Oner", riot_id="T1 Oner#KR1", server="KR", bridge=bridge
    )
    assert result["updated"] is True
    assert result["resolved"] is False
    assert result["gap_flag"] == "no_riot_key"
