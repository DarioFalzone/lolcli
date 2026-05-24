"""Tests del bridge esports → jungle.pro_presence (PR-C)."""

from __future__ import annotations

import json
from pathlib import Path

from riot_lol_cli.jungle_research.pipelines import pro_stage_bridge
from riot_lol_cli.jungle_research.pipelines.pro_stage_bridge import (
    load_pro_presence_from_esports,
)


def _write_comfort(dir_path: Path, name: str, entries: list[dict]) -> Path:
    target = dir_path / name
    target.write_text(json.dumps(entries), encoding="utf-8")
    return target


def test_gold_dir_inexistente_retorna_gap(tmp_path: Path):
    result = load_pro_presence_from_esports(gold_dir=tmp_path / "no_existe")
    assert result.pro_presence == {}
    assert any("no existe" in g for g in result.gaps)


def test_sin_archivos_comfort_retorna_gap(tmp_path: Path):
    tmp_path.mkdir(exist_ok=True)
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    assert result.pro_presence == {}
    assert any("sin archivos" in g for g in result.gaps)


def test_comfort_features_vacio_retorna_gap(tmp_path: Path):
    _write_comfort(tmp_path, "comfort_features_2026-05-24.json", [])
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    assert result.pro_presence == {}
    assert any("vacío" in g or "vacio" in g for g in result.gaps)


def test_agrega_max_por_champion_y_normaliza(tmp_path: Path, monkeypatch):
    # Sin champion_base mapping: usa champion_id como name.
    monkeypatch.setattr(
        pro_stage_bridge, "CHAMPION_BASE_FILE", tmp_path / "no_champion_base.json"
    )
    _write_comfort(
        tmp_path,
        "comfort_features_2026-05-24.json",
        [
            {"player_id": "Canyon", "champion_id": "Wukong", "comfort_score": 0.8},
            {"player_id": "Oner", "champion_id": "Wukong", "comfort_score": 0.6},
            {"player_id": "Canyon", "champion_id": "LeeSin", "comfort_score": 0.4},
        ],
    )
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    assert result.champion_count == 2
    # Wukong tiene max 0.8 (entre 0.8 y 0.6); LeeSin tiene 0.4.
    # Normalizado al max del pool (0.8 → 1.0, 0.4 → 0.5).
    assert result.pro_presence["Wukong"] == 1.0
    assert result.pro_presence["LeeSin"] == 0.5
    assert result.source_file == "comfort_features_2026-05-24.json"
    assert result.extracted_at == "2026-05-24"


def test_usa_archivo_mas_reciente(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        pro_stage_bridge, "CHAMPION_BASE_FILE", tmp_path / "no_base.json"
    )
    _write_comfort(
        tmp_path, "comfort_features_2026-05-20.json",
        [{"player_id": "A", "champion_id": "Old", "comfort_score": 1.0}],
    )
    _write_comfort(
        tmp_path, "comfort_features_2026-05-24.json",
        [{"player_id": "B", "champion_id": "New", "comfort_score": 1.0}],
    )
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    assert "New" in result.pro_presence
    assert "Old" not in result.pro_presence
    assert result.source_file == "comfort_features_2026-05-24.json"


def test_mapping_champion_id_a_name(tmp_path: Path, monkeypatch):
    """Si hay champion_base.json, champion_id se traduce a display_name."""
    base = tmp_path / "champion_base.json"
    base.write_text(json.dumps({
        "MonkeyKing": {"display_name": "Wukong"},
        "LeeSin": {"display_name": "Lee Sin"},
    }), encoding="utf-8")
    monkeypatch.setattr(pro_stage_bridge, "CHAMPION_BASE_FILE", base)
    _write_comfort(
        tmp_path, "comfort_features_2026-05-24.json",
        [
            {"player_id": "P1", "champion_id": "MonkeyKing", "comfort_score": 0.9},
            {"player_id": "P2", "champion_id": "LeeSin", "comfort_score": 0.7},
        ],
    )
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    # Key es display_name, no champion_id.
    assert "Wukong" in result.pro_presence
    assert "Lee Sin" in result.pro_presence
    assert "MonkeyKing" not in result.pro_presence


def test_unmapped_ids_aparecen_en_gaps(tmp_path: Path, monkeypatch):
    base = tmp_path / "champion_base.json"
    base.write_text(json.dumps({
        "Wukong": {"display_name": "Wukong"},
    }), encoding="utf-8")
    monkeypatch.setattr(pro_stage_bridge, "CHAMPION_BASE_FILE", base)
    _write_comfort(
        tmp_path, "comfort_features_2026-05-24.json",
        [
            {"player_id": "P1", "champion_id": "Wukong", "comfort_score": 1.0},
            {"player_id": "P2", "champion_id": "UnknownChamp", "comfort_score": 0.5},
        ],
    )
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    # Wukong mapeado normalmente; UnknownChamp pasa con ID como name.
    assert "Wukong" in result.pro_presence
    assert "UnknownChamp" in result.pro_presence
    assert any("UnknownChamp" in g or "sin mapping" in g for g in result.gaps)


def test_orchestrator_integra_pro_stage_alimenta_scoring(tmp_path: Path, monkeypatch):
    """PR-C E2E: STEP_PRO_STAGE en el orchestrator inyecta pro_presence al scoring."""
    from riot_lol_cli.jungle_research.orchestrator import (
        STEP_PRO_STAGE,
        STEP_SOLOQ,
        RefreshPlan,
        consolidate,
    )
    from riot_lol_cli.jungle_research.pipelines import meta_soloq, pro_stage_bridge

    # Mock del bridge: retorna pro_presence sintético para Wukong/LeeSin.
    monkeypatch.setattr(
        pro_stage_bridge, "ESPORTS_GOLD_DIR", tmp_path / "gold"
    )
    monkeypatch.setattr(
        pro_stage_bridge, "CHAMPION_BASE_FILE", tmp_path / "no_base.json"
    )
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    (gold_dir / "comfort_features_2026-05-24.json").write_text(
        json.dumps([
            {"player_id": "Canyon", "champion_id": "Wukong", "comfort_score": 0.9},
            {"player_id": "Oner", "champion_id": "LeeSin", "comfort_score": 0.6},
        ]),
        encoding="utf-8",
    )

    # Stub meta_soloq con 2 champions.
    fake_normalized = tmp_path / "fake.json"
    fake_normalized.write_text(
        json.dumps({
            "patch": "26.10",
            "champions": [
                {
                    "id": "Wukong", "display_name": "Wukong",
                    "source_breakdown": {
                        "ugg": {
                            "win_rate": 50.0, "games_analyzed": 5000,
                            "scraped_at": "2026-05-24T00:00:00Z",
                        }
                    },
                },
                {
                    "id": "LeeSin", "display_name": "LeeSin",
                    "source_breakdown": {
                        "ugg": {
                            "win_rate": 50.0, "games_analyzed": 5000,
                            "scraped_at": "2026-05-24T00:00:00Z",
                        }
                    },
                },
            ],
            "source_gaps": [],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(meta_soloq, "META_SCRAPER_NORMALIZED", fake_normalized)
    monkeypatch.setattr(meta_soloq, "JUNGLE_META_DIR", tmp_path / "absent_jungle_meta")

    # Aislar storage del orquestador.
    from riot_lol_cli.jungle_research import json_storage as jr_storage

    monkeypatch.setattr(jr_storage, "ROOT", tmp_path / "jr_storage")
    monkeypatch.setattr(jr_storage, "FINAL_TIERLIST_DIR", tmp_path / "jr_storage" / "tierlist")
    monkeypatch.setattr(jr_storage, "FINAL_TIERLIST_LATEST", tmp_path / "jr_storage" / "tierlist" / "latest.json")
    monkeypatch.setattr(jr_storage, "FINAL_TIERLIST_HISTORY", tmp_path / "jr_storage" / "tierlist" / "history")
    monkeypatch.setattr(jr_storage, "CHAMPION_SNAPSHOTS_DIR", tmp_path / "jr_storage" / "snapshots")
    monkeypatch.setattr(jr_storage, "CHAMPION_SNAPSHOTS_LATEST", tmp_path / "jr_storage" / "snapshots" / "latest.json")
    monkeypatch.setattr(jr_storage, "CHAMPION_SNAPSHOTS_BACKUPS", tmp_path / "jr_storage" / "snapshots" / "backups")
    monkeypatch.setattr(jr_storage, "CHAMPION_SNAPSHOTS_HISTORY", tmp_path / "jr_storage" / "snapshots" / "history")
    monkeypatch.setattr(jr_storage, "ASIA_PRESENCE_FILE", tmp_path / "jr_storage" / "asia.json")
    monkeypatch.setattr(jr_storage, "ADAPTER_RUNS_FILE", tmp_path / "jr_storage" / "runs.json")

    plan = RefreshPlan(steps={STEP_SOLOQ, STEP_PRO_STAGE}, queue="ranked_solo_5x5")
    result = consolidate(plan)
    assert result.success is True
    assert result.tierlist_summary["pro_presence_applied"] == 2
    assert result.tierlist_summary["pro_presence_source"] == "esports_bridge"
    assert result.tierlist_summary["pro_stage"]["champion_count"] == 2


def test_entries_invalidas_se_filtran(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        pro_stage_bridge, "CHAMPION_BASE_FILE", tmp_path / "no_base.json"
    )
    _write_comfort(
        tmp_path, "comfort_features_2026-05-24.json",
        [
            {"player_id": "P1", "champion_id": "Wukong", "comfort_score": 0.8},
            {"player_id": "P2"},  # sin champion_id
            {"champion_id": "Other", "comfort_score": None},  # sin valor
            "no_es_dict",  # ruido
        ],
    )
    result = load_pro_presence_from_esports(gold_dir=tmp_path)
    assert result.champion_count == 1
    assert result.pro_presence == {"Wukong": 1.0}
