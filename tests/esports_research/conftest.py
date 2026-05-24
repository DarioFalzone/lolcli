from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from riot_lol_cli.esports_research import json_storage

FIXTURES = Path(__file__).parent / "fixtures"


def load_json_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_text_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture
def esports_tmp_root(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(json_storage, "ROOT", tmp_path)
    monkeypatch.setattr(json_storage, "SOURCES_FILE", tmp_path / "sources.json")
    monkeypatch.setattr(json_storage, "BRONZE_DIR", tmp_path / "bronze")
    monkeypatch.setattr(json_storage, "SILVER_DIR", tmp_path / "silver")
    monkeypatch.setattr(json_storage, "GOLD_DIR", tmp_path / "gold")
    monkeypatch.setattr(json_storage, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(json_storage, "SILVER_TOURNAMENTS_FILE", tmp_path / "silver" / "tournaments.json")
    monkeypatch.setattr(json_storage, "SILVER_TEAMS_FILE", tmp_path / "silver" / "teams.json")
    monkeypatch.setattr(json_storage, "SILVER_PLAYERS_FILE", tmp_path / "silver" / "players.json")
    monkeypatch.setattr(json_storage, "SILVER_PATCHES_FILE", tmp_path / "silver" / "patches.json")
    monkeypatch.setattr(json_storage, "SILVER_MATCHES_DIR", tmp_path / "silver" / "matches")
    monkeypatch.setattr(json_storage, "SILVER_GAMES_DIR", tmp_path / "silver" / "games")
    json_storage.ensure_directories()
    real_sources = Path("data/esports_research/sources.json")
    json_storage.SOURCES_FILE.write_text(real_sources.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


@pytest.fixture
def esports_client(esports_tmp_root: Path) -> TestClient:
    from riot_lol_cli.meta_api.app import create_app

    return TestClient(create_app())
