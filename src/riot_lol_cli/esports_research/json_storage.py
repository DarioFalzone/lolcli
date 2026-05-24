"""JSON storage helpers for Esports Research.

V0 uses immutable bronze snapshots and table-like silver/gold JSON files.
Writes are UTF-8 without BOM and atomic via `.tmp` plus replace.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from riot_lol_cli import paths

ROOT = paths.DATA_DIR / "esports_research"
SOURCES_FILE = ROOT / "sources.json"

BRONZE_DIR = ROOT / "bronze"
SILVER_DIR = ROOT / "silver"
GOLD_DIR = ROOT / "gold"
REPORTS_DIR = ROOT / "reports"

SILVER_TOURNAMENTS_FILE = SILVER_DIR / "tournaments.json"
SILVER_TEAMS_FILE = SILVER_DIR / "teams.json"
SILVER_PLAYERS_FILE = SILVER_DIR / "players.json"
SILVER_PATCHES_FILE = SILVER_DIR / "patches.json"
SILVER_MATCHES_DIR = SILVER_DIR / "matches"
SILVER_GAMES_DIR = SILVER_DIR / "games"


def _timestamp_slug() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0, tzinfo=None)
        .isoformat()
        .replace(":", "-")
    )


def ensure_directories() -> None:
    for directory in (
        ROOT,
        BRONZE_DIR,
        SILVER_DIR,
        GOLD_DIR,
        REPORTS_DIR,
        SILVER_MATCHES_DIR,
        SILVER_GAMES_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
    tmp.replace(path)
    return path


def write_text_atomic(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    tmp.replace(path)
    return path


def read_sources() -> list[dict[str, Any]]:
    data = read_json(SOURCES_FILE)
    if not data:
        return []
    if isinstance(data, dict):
        return data.get("sources", [])
    return data


def save_bronze_json(source_id: str, partition: str, name: str, payload: Any) -> Path:
    ensure_directories()
    target = BRONZE_DIR / source_id / partition / f"{name}_{_timestamp_slug()}.json"
    return write_json_atomic(target, payload)


def save_bronze_text(source_id: str, partition: str, name: str, text: str, suffix: str) -> Path:
    ensure_directories()
    clean_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    target = BRONZE_DIR / source_id / partition / f"{name}_{_timestamp_slug()}{clean_suffix}"
    return write_text_atomic(target, text)


def read_collection(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    if payload is None:
        return []
    if isinstance(payload, dict):
        for key in ("data", "items", "rows", "sources"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return payload if isinstance(payload, list) else []


def save_silver_collection(name: str, rows: list[dict[str, Any]]) -> Path:
    ensure_directories()
    return write_json_atomic(SILVER_DIR / f"{name}.json", rows)


def read_silver_collection(name: str) -> list[dict[str, Any]]:
    return read_collection(SILVER_DIR / f"{name}.json")


def save_silver_entity(collection: str, entity_id: str, payload: dict[str, Any]) -> Path:
    ensure_directories()
    return write_json_atomic(SILVER_DIR / collection / f"{entity_id}.json", payload)


def read_silver_entity(collection: str, entity_id: str) -> dict[str, Any] | None:
    payload = read_json(SILVER_DIR / collection / f"{entity_id}.json")
    return payload if isinstance(payload, dict) else None


def save_gold_feature(name: str, payload: Any) -> Path:
    ensure_directories()
    return write_json_atomic(GOLD_DIR / name, payload)


def read_gold_feature(name: str) -> Any:
    return read_json(GOLD_DIR / name)


def save_report(name: str, payload: Any) -> Path:
    ensure_directories()
    return write_json_atomic(REPORTS_DIR / name, payload)


def list_json_rows(path: Path) -> list[dict[str, Any]]:
    if path.is_file():
        return read_collection(path)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(path.glob("*.json")):
        payload = read_json(child)
        if isinstance(payload, dict):
            rows.append(payload)
        elif isinstance(payload, list):
            rows.extend(row for row in payload if isinstance(row, dict))
    return rows
