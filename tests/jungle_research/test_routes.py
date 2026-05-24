"""Endpoints HTTP de jungle_research: 200 sin Riot key, gaps visibles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.meta_api.app import create_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    """Crea TestClient con storage aislado y sin RIOT_API_KEY."""
    monkeypatch.delenv("RIOT_API_KEY", raising=False)
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    csd = tmp_path / "champion_meta_snapshots"
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_DIR", csd)
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_LATEST", csd / "latest.json")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_BACKUPS", csd / "backups")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_HISTORY", csd / "history")
    monkeypatch.setattr(json_storage, "CHAMPION_SNAPSHOTS_RAW", csd / "raw")
    monkeypatch.setattr(json_storage, "MATCH_HISTORY_DIR", tmp_path / "match_history")
    monkeypatch.setattr(json_storage, "OTP_RANKINGS_DIR", tmp_path / "otp_rankings")
    ftd = tmp_path / "final_jungle_tierlist"
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_DIR", ftd)
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_LATEST", ftd / "latest.json")
    monkeypatch.setattr(json_storage, "FINAL_TIERLIST_HISTORY", ftd / "history")
    monkeypatch.setattr(json_storage, "DAILY_REPORTS_DIR", tmp_path / "daily_reports")
    monkeypatch.setattr(json_storage, "PRO_ACCOUNTS_FILE", tmp_path / "pro_accounts.json")
    monkeypatch.setattr(json_storage, "ADAPTER_RUNS_FILE", tmp_path / "adapter_runs.json")
    return TestClient(create_app())


def test_overview_no_data_returns_gap_visible(client: TestClient):
    resp = client.get("/api/v1/jungle-research/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["riot_api_key_present"] is False
    assert body["freshness"] is None
    assert any("no existe" in g for g in body["gaps"])


def test_sources_returns_registry(client: TestClient):
    resp = client.get("/api/v1/jungle-research/sources")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["summary"]["total"] > 0
    assert any(s["id"] == "meta_scraper_local" for s in body["sources"])


def test_current_no_data_returns_empty(client: TestClient):
    resp = client.get("/api/v1/jungle-research/current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert any("no existe" in g for g in body["gaps"])


def test_pros_recent_picks_no_riot_key(client: TestClient):
    resp = client.get("/api/v1/jungle-research/pros/recent-picks")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert "no_riot_key" in body["gaps"]


def test_pro_matches_unknown_player(client: TestClient):
    resp = client.get("/api/v1/jungle-research/pros/Faker/matches")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["gaps"]


def test_otp_endpoint_planned_gap(client: TestClient):
    resp = client.get("/api/v1/jungle-research/champions/LeeSin/otp")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert any("planned" in g for g in body["gaps"])


def test_consensus_no_data(client: TestClient):
    resp = client.get("/api/v1/jungle-research/consensus")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []


def test_emerging_no_data(client: TestClient):
    resp = client.get("/api/v1/jungle-research/emerging")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []


def test_daily_report_no_data(client: TestClient):
    resp = client.get("/api/v1/jungle-research/daily-report?date=2026-05-11")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] is None
    assert any("sin tier list" in g for g in body["gaps"])


def test_champion_history_no_data(client: TestClient):
    resp = client.get("/api/v1/jungle-research/champions/Wukong/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []


def test_refresh_riot_pros_without_key_completes_with_gaps(client: TestClient):
    resp = client.post("/api/v1/jungle-research/refresh?mode=riot_pros")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["mode"] == "riot_pros"
    assert "pros" in body
    assert body["pros"]["resolved"] == 0  # sin key, todo gap
    assert body["pros"]["gaps"]


def test_list_pros_returns_seed_and_state(client: TestClient):
    """GET /pros lista el seed real con estado de resolución."""
    resp = client.get("/api/v1/jungle-research/pros")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["total"] == 11  # 11 pros en el seed shipped
    assert body["resolved"] == 0  # ninguno tiene riot_id por default
    assert body["riot_api_key_present"] is False
    names = [p["player_name"] for p in body["data"]]
    assert "Canyon" in names
    assert "Oner" in names


def test_set_pro_account_invalid_format(client: TestClient, tmp_path: Path, monkeypatch):
    """POST con formato inválido devuelve success=False con error claro."""
    # Copiar el seed real al tmp para no contaminar.
    seed_src = Path("data/meta_analyzer/jungle_research/pro_players_seed.json")
    seed_dst = tmp_path / "pro_players_seed.json"
    seed_dst.write_text(seed_src.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(json_storage, "PRO_PLAYERS_SEED_FILE", seed_dst)

    resp = client.post(
        "/api/v1/jungle-research/pros/Canyon/account",
        json={"riot_id": "no_separator", "server": "KR"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "formato" in body["error"].lower()


def test_set_pro_account_unknown_player(client: TestClient, tmp_path: Path, monkeypatch):
    seed_src = Path("data/meta_analyzer/jungle_research/pro_players_seed.json")
    seed_dst = tmp_path / "pro_players_seed.json"
    seed_dst.write_text(seed_src.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(json_storage, "PRO_PLAYERS_SEED_FILE", seed_dst)

    resp = client.post(
        "/api/v1/jungle-research/pros/FakerJungla/account",
        json={"riot_id": "X#Y", "server": "KR"},
    )
    body = resp.json()
    assert body["success"] is False
    assert "seed" in body["error"]


def test_refresh_soloq_extra_returns_runs(client: TestClient):
    """POST /refresh?mode=soloq_extra invoca los 4 adapters stub y devuelve runs."""
    resp = client.post("/api/v1/jungle-research/refresh?mode=soloq_extra")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["mode"] == "soloq_extra"
    assert "soloq_extra" in body
    assert body["soloq_extra"]["extra_snapshots"] == 0  # stubs
    assert len(body["soloq_extra"]["runs"]) == 4
    statuses = {r["adapter_id"]: r["status"] for r in body["soloq_extra"]["runs"]}
    assert all(v == "not_implemented" for v in statuses.values())


def test_sources_enriched_with_telemetry_after_refresh(client: TestClient):
    """Tras un refresh, GET /sources debe incluir last_attempted_at + status."""
    client.post("/api/v1/jungle-research/refresh?mode=soloq_extra")
    resp = client.get("/api/v1/jungle-research/sources")
    body = resp.json()
    metasrc = next(s for s in body["sources"] if s["id"] == "metasrc_jungle")
    assert "last_attempted_at" in metasrc
    assert metasrc["last_run_status"] == "not_implemented"
    assert "stub" in metasrc["last_run_reason"].lower()


def test_set_pro_account_no_key_marks_pending(client: TestClient, tmp_path: Path, monkeypatch):
    seed_src = Path("data/meta_analyzer/jungle_research/pro_players_seed.json")
    seed_dst = tmp_path / "pro_players_seed.json"
    seed_dst.write_text(seed_src.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(json_storage, "PRO_PLAYERS_SEED_FILE", seed_dst)

    resp = client.post(
        "/api/v1/jungle-research/pros/Canyon/account",
        json={"riot_id": "DK Canyon#KR1", "server": "KR"},
    )
    body = resp.json()
    assert body["success"] is True
    assert body["updated"] is True
    assert body["resolved"] is False
    assert body["gap_flag"] == "no_riot_key"
    # Verificar que el seed quedó actualizado en disco.
    persisted = json.loads(seed_dst.read_text(encoding="utf-8"))
    canyon = next(p for p in persisted["players"] if p["player_name"] == "Canyon")
    assert canyon["riot_id"] == "DK Canyon#KR1"
    assert canyon["server"] == "KR"


def test_overview_after_refresh_with_real_data(client: TestClient, monkeypatch, tmp_path: Path):
    """Si Meta Scraper tiene snapshot real, refresh produce tier list."""
    # Apuntar al fixture sintético del Meta Scraper.
    from riot_lol_cli.jungle_research.pipelines import meta_soloq

    fake = tmp_path / "fake.json"
    fake.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": f"C{i}",
                        "display_name": f"C{i}",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50 + i * 0.3,
                                "pick_rate": 5 + i * 0.1,
                                "ban_rate": 1.0,
                                "games_analyzed": 5000,
                                "tier": "A",
                                "scraped_at": "2026-05-11T10:00:00Z",
                            }
                        },
                    }
                    for i in range(8)
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", fake)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent")

    refresh = client.post("/api/v1/jungle-research/refresh?mode=soloq")
    assert refresh.status_code == 200
    rbody = refresh.json()
    assert rbody["soloq"]["success"] is True
    assert rbody["soloq"]["entries"] == 8

    overview = client.get("/api/v1/jungle-research/overview").json()
    assert overview["entry_count"] == 8
    assert overview["patch"] == "26.10"

    current = client.get("/api/v1/jungle-research/current").json()
    assert len(current["data"]) == 8
