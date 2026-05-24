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
    monkeypatch.setattr(json_storage, "ASIA_PRESENCE_FILE", tmp_path / "asia_presence.json")
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
    assert "riot_pros" in body["steps"]
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


def test_refresh_soloq_extra_returns_runs(client: TestClient, monkeypatch):
    """POST /refresh?mode=soloq_extra invoca los 4 adapters V3 y devuelve runs.

    Tras V3.7 [2026-05-24]: metasrc ya no es stub, intenta fetch real. Para
    aislar este test de network, mockeamos el adapter real con uno stub.
    Los otros 3 (mobalytics, leagueofgraphs, tracker_gg) siguen siendo stubs.
    """
    from riot_lol_cli.jungle_research.pipelines import meta_soloq_extra
    from riot_lol_cli.meta_scraper.adapters.leagueofgraphs import LeagueOfGraphsAdapter
    from riot_lol_cli.meta_scraper.adapters.mobalytics import MobalyticsAdapter
    from riot_lol_cli.meta_scraper.adapters.tracker_gg import TrackerGgAdapter

    # Adapter stub para metasrc que NO toca network y retorna not_implemented.
    class _MetaSrcStubForTest:
        def fetch_jungle_tier_list(self, elo="emerald_plus"):
            return {
                "platform": "metasrc",
                "source_url": "https://x",
                "status": "not_implemented",
                "reason": "stub: aislado de network para test",
                "champions": [],
                "champion_count": 0,
                "scraped_at": "2026-05-24T00:00:00Z",
            }

    monkeypatch.setattr(
        meta_soloq_extra,
        "_default_adapters",
        lambda: {
            "metasrc_jungle": _MetaSrcStubForTest(),
            "mobalytics_jungle_tierlist": MobalyticsAdapter(),
            "leagueofgraphs_jungle": LeagueOfGraphsAdapter(),
            "tracker_gg_lol": TrackerGgAdapter(),
        },
    )

    resp = client.post("/api/v1/jungle-research/refresh?mode=soloq_extra")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "extra" in body["steps"]
    assert body["extra"]["extra_snapshots"] == 0  # todos retornan not_implemented o gap
    assert len(body["extra"]["runs"]) == 4
    statuses = {r["adapter_id"]: r["status"] for r in body["extra"]["runs"]}
    # 3 stubs + 1 metasrc mockeado: todos not_implemented en este test.
    assert all(v == "not_implemented" for v in statuses.values())
    # mode=soloq_extra NO regenera tier list (default).
    assert body["regenerate_tierlist"] is False


def test_sources_enriched_with_telemetry_after_refresh(client: TestClient, monkeypatch):
    """Tras un refresh, GET /sources debe incluir last_attempted_at + status.

    Tras V3.7: metasrc ahora intenta network. Mockeamos para validar el
    enriquecimiento del registry con telemetría.
    """
    from riot_lol_cli.jungle_research.pipelines import meta_soloq_extra
    from riot_lol_cli.meta_scraper.adapters.leagueofgraphs import LeagueOfGraphsAdapter
    from riot_lol_cli.meta_scraper.adapters.mobalytics import MobalyticsAdapter
    from riot_lol_cli.meta_scraper.adapters.tracker_gg import TrackerGgAdapter

    class _MetaSrcStubForTest:
        def fetch_jungle_tier_list(self, elo="emerald_plus"):
            return {
                "platform": "metasrc",
                "source_url": "https://x",
                "status": "not_implemented",
                "reason": "stub: aislado de network para test",
                "champions": [],
                "champion_count": 0,
                "scraped_at": "2026-05-24T00:00:00Z",
            }

    monkeypatch.setattr(
        meta_soloq_extra,
        "_default_adapters",
        lambda: {
            "metasrc_jungle": _MetaSrcStubForTest(),
            "mobalytics_jungle_tierlist": MobalyticsAdapter(),
            "leagueofgraphs_jungle": LeagueOfGraphsAdapter(),
            "tracker_gg_lol": TrackerGgAdapter(),
        },
    )

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


def test_refresh_asia_mode_returns_runs_y_presence(client: TestClient):
    """POST /refresh?mode=asia invoca los 9 adapters V4 y devuelve runs + presence."""
    resp = client.post("/api/v1/jungle-research/refresh?mode=asia")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "asia" in body["steps"]
    # Stubs default = 0 snapshots, asia_presence vacio.
    assert body["asia"]["asia_snapshots"] == 0
    assert body["asia"]["asia_presence_size"] == 0
    assert len(body["asia"]["runs"]) == 9
    statuses = {r["adapter_id"]: r["status"] for r in body["asia"]["runs"]}
    assert all(v == "not_implemented" for v in statuses.values())
    # mode=asia NO regenera tier list por default (T2.7).
    assert body["regenerate_tierlist"] is False


def test_refresh_modes_param_compose_steps(client: TestClient):
    """V2.8: modes=list[str] permite composición libre."""
    resp = client.post("/api/v1/jungle-research/refresh?modes=asia&modes=riot_pros")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["steps"]) == {"asia", "riot_pros"}
    assert "asia" in body and body["asia"]["asia_snapshots"] == 0
    assert "pros" in body
    # Sin soloq/extra → no regenera.
    assert body["regenerate_tierlist"] is False


def test_refresh_modes_invalid_returns_400(client: TestClient):
    resp = client.post("/api/v1/jungle-research/refresh?modes=invalid_mode")
    assert resp.status_code == 400


def test_refresh_asia_can_regenerate_with_explicit_flag(
    client: TestClient, monkeypatch, tmp_path: Path
):
    """T2.7: mode=asia con regenerate_tierlist=true regenera con cache asia."""
    from riot_lol_cli.jungle_research.pipelines import meta_soloq

    # Necesitamos al menos 1 snapshot para que regenere algo.
    base = tmp_path / "base.json"
    base.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": "Wukong",
                        "display_name": "Wukong",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50.0,
                                "games_analyzed": 5000,
                                "scraped_at": "2026-05-12T10:00:00Z",
                            }
                        },
                    }
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", base)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent")
    # Necesitamos soloq también para que haya snapshots; modes=asia,soloq + regenerate=true.
    resp = client.post(
        "/api/v1/jungle-research/refresh"
        "?modes=asia&modes=soloq&regenerate_tierlist=true"
    )
    body = resp.json()
    assert body["success"] is True
    assert body["regenerate_tierlist"] is True
    assert body["tierlist"]["success"] is True


def test_refresh_all_includes_asia_y_alimenta_scoring(
    client: TestClient, monkeypatch, tmp_path: Path
):
    """mode=all debe correr meta_asia y aplicar asia_presence al scoring."""
    from riot_lol_cli.jungle_research.pipelines import meta_asia, meta_soloq

    base = tmp_path / "base.json"
    base.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": "Wukong",
                        "display_name": "Wukong",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50.0,
                                "games_analyzed": 5000,
                                "scraped_at": "2026-05-12T10:00:00Z",
                            }
                        },
                    }
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", base)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent")

    class _OkAsia:
        def fetch_jungle_tier_list(self, elo="challenger"):
            return {
                "platform": "opgg_kr",
                "source_url": "https://opgg.example",
                "patch": "26.10",
                "status": "ok",
                "champions": [
                    {"id": "Wukong", "display_name": "Wukong", "win_rate": 56.0},
                ],
                "champion_count": 1,
                "scraped_at": "2026-05-12T10:00:00Z",
            }

    monkeypatch.setattr(meta_asia, "_default_adapters", lambda: {"opgg_kr": _OkAsia()})

    resp = client.post("/api/v1/jungle-research/refresh?mode=all")
    body = resp.json()
    assert body["success"] is True
    assert body["asia"]["asia_snapshots"] == 1
    assert body["asia"]["asia_presence_size"] == 1
    assert body["tierlist"]["asia_presence_applied"] == 1

    # Verificar que el tier list final tiene asia_score poblado.
    current = client.get("/api/v1/jungle-research/current").json()
    wukong = next(e for e in current["data"] if e["champion_name"] == "Wukong")
    assert wukong["asia_score"] == 1.0  # max normalizado


def test_refresh_all_mergea_soloq_extra_en_tier_list(
    client: TestClient, monkeypatch, tmp_path: Path
):
    """Bug fix: mode=all debe mergear snapshots V3 al final tier list."""
    from riot_lol_cli.jungle_research.pipelines import meta_soloq, meta_soloq_extra

    base = tmp_path / "base.json"
    base.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": f"Base{i}",
                        "display_name": f"Base{i}",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50.0,
                                "pick_rate": 5.0,
                                "ban_rate": 1.0,
                                "games_analyzed": 5000,
                                "tier": "A",
                                "scraped_at": "2026-05-12T10:00:00Z",
                            }
                        },
                    }
                    for i in range(3)
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", base)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent")

    class _StubOkAdapter:
        def fetch_jungle_tier_list(self, elo="emerald_plus"):
            return {
                "platform": "metasrc",
                "source_url": "https://metasrc.example",
                "patch": "26.10",
                "status": "ok",
                "champions": [
                    {"id": "Extra1", "display_name": "Extra1", "win_rate": 55.0, "games": 3000},
                    {"id": "Extra2", "display_name": "Extra2", "win_rate": 48.0, "games": 2500},
                ],
                "champion_count": 2,
                "scraped_at": "2026-05-12T10:00:00Z",
            }

    monkeypatch.setattr(
        meta_soloq_extra,
        "_default_adapters",
        lambda: {"metasrc_jungle": _StubOkAdapter()},
    )

    resp = client.post("/api/v1/jungle-research/refresh?mode=all")
    body = resp.json()
    assert body["success"] is True
    assert body["tierlist"]["success"] is True
    assert body["tierlist"]["entries"] == 5
    assert "metasrc_jungle" in body["tierlist"]["sources_used"]
    assert body["extra"]["extra_snapshots"] == 2

    current = client.get("/api/v1/jungle-research/current").json()
    names = {e["champion_name"] for e in current["data"]}
    assert names == {"Base0", "Base1", "Base2", "Extra1", "Extra2"}


def test_refresh_soloq_no_incluye_extras_por_default(
    client: TestClient, monkeypatch, tmp_path: Path
):
    """mode=soloq mantiene compat: solo Meta Scraper + Jungle Meta curated."""
    from riot_lol_cli.jungle_research.pipelines import meta_soloq, meta_soloq_extra

    base = tmp_path / "base.json"
    base.write_text(
        json.dumps(
            {
                "patch": "26.10",
                "champions": [
                    {
                        "id": "Base1",
                        "display_name": "Base1",
                        "source_breakdown": {
                            "ugg": {
                                "win_rate": 50.0,
                                "games_analyzed": 5000,
                                "scraped_at": "2026-05-12T10:00:00Z",
                            }
                        },
                    }
                ],
                "source_gaps": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", base)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent")

    def _fail_extras():
        raise AssertionError("meta_soloq_extra no debe invocarse en mode=soloq")

    monkeypatch.setattr(meta_soloq_extra, "_default_adapters", _fail_extras)

    resp = client.post("/api/v1/jungle-research/refresh?mode=soloq")
    assert resp.status_code == 200


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
    assert rbody["tierlist"]["success"] is True
    assert rbody["tierlist"]["entries"] == 8

    overview = client.get("/api/v1/jungle-research/overview").json()
    assert overview["entry_count"] == 8
    assert overview["patch"] == "26.10"

    current = client.get("/api/v1/jungle-research/current").json()
    assert len(current["data"]) == 8
