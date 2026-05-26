"""
JSON storage para Jungle Research.

Storage v1: snapshots inmutables bajo `data/meta_analyzer/jungle_research/`.
Cada escritura de `latest.json` rota la versión previa a `backups/` con
timestamp, y opcionalmente agrega a `history/` para análisis de tendencias.

Estructura:

    data/meta_analyzer/jungle_research/
        sources.json
        pro_players_seed.json
        pro_accounts.json
        champion_meta_snapshots/
            latest.json
            backups/<YYYY-MM-DDTHH-MM-SS>.json
            history/<YYYY-MM-DDTHH-MM-SS>_merged.json
            raw/<source>/<YYYY-MM-DDTHH-MM-SS>.json
        match_history/<puuid>/<YYYY-MM-DDTHH-MM-SS>.json
        otp_rankings/<champion_id>/<YYYY-MM-DDTHH-MM-SS>.json
        final_jungle_tierlist/
            latest.json
            history/<YYYY-MM-DDTHH-MM-SS>.json
        daily_reports/<YYYY-MM-DD>.json

Migración futura a SQLite/Postgres: los nombres de directorios coinciden con
tablas; cada JSON es un row set. La rotación a `backups/` simula `created_at`
para snapshots.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from riot_lol_cli import paths

ROOT = paths.DATA_DIR / "meta_analyzer" / "jungle_research"

SOURCES_FILE = ROOT / "sources.json"
PRO_PLAYERS_SEED_FILE = ROOT / "pro_players_seed.json"
PRO_ACCOUNTS_FILE = ROOT / "pro_accounts.json"
ADAPTER_RUNS_FILE = ROOT / "adapter_runs.json"
ASIA_PRESENCE_FILE = ROOT / "asia_presence.json"

CHAMPION_SNAPSHOTS_DIR = ROOT / "champion_meta_snapshots"
CHAMPION_SNAPSHOTS_LATEST = CHAMPION_SNAPSHOTS_DIR / "latest.json"
CHAMPION_SNAPSHOTS_BACKUPS = CHAMPION_SNAPSHOTS_DIR / "backups"
CHAMPION_SNAPSHOTS_HISTORY = CHAMPION_SNAPSHOTS_DIR / "history"
CHAMPION_SNAPSHOTS_RAW = CHAMPION_SNAPSHOTS_DIR / "raw"

MATCH_HISTORY_DIR = ROOT / "match_history"
OTP_RANKINGS_DIR = ROOT / "otp_rankings"

FINAL_TIERLIST_DIR = ROOT / "final_jungle_tierlist"
FINAL_TIERLIST_LATEST = FINAL_TIERLIST_DIR / "latest.json"
FINAL_TIERLIST_HISTORY = FINAL_TIERLIST_DIR / "history"

DAILY_REPORTS_DIR = ROOT / "daily_reports"


def _timestamp_slug() -> str:
    """Slug ISO seguro para nombres de archivo: 2026-05-11T20-15-30."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0, tzinfo=None)
        .isoformat()
        .replace(":", "-")
    )


def ensure_directories() -> None:
    """Crea todos los subdirectorios canónicos (idempotente)."""
    for path in (
        ROOT,
        CHAMPION_SNAPSHOTS_DIR,
        CHAMPION_SNAPSHOTS_BACKUPS,
        CHAMPION_SNAPSHOTS_HISTORY,
        CHAMPION_SNAPSHOTS_RAW,
        MATCH_HISTORY_DIR,
        OTP_RANKINGS_DIR,
        FINAL_TIERLIST_DIR,
        FINAL_TIERLIST_HISTORY,
        DAILY_REPORTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    """Lee un JSON. Devuelve None si no existe."""
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: Path, payload: Any) -> None:
    """Escribe JSON UTF-8 sin BOM de forma atómica (tmp + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    tmp.replace(path)


def write_latest_with_backup(latest_path: Path, backups_dir: Path, payload: Any) -> Path | None:
    """
    Escribe `payload` en `latest_path`, rotando la versión previa a
    `backups_dir/<timestamp>.json` si existía.

    Devuelve la ruta del backup creado, o None si no había versión previa.
    """
    backup_path: Path | None = None
    if latest_path.exists():
        backups_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backups_dir / f"{_timestamp_slug()}.json"
        backup_path.write_bytes(latest_path.read_bytes())
    _write_json_atomic(latest_path, payload)
    return backup_path


def append_history(history_dir: Path, payload: Any, suffix: str = "") -> Path:
    """Escribe un snapshot append-only en `history_dir/<timestamp><suffix>.json`."""
    history_dir.mkdir(parents=True, exist_ok=True)
    name = f"{_timestamp_slug()}{suffix}.json"
    target = history_dir / name
    _write_json_atomic(target, payload)
    return target


def save_raw_payload(source_id: str, payload: Any) -> Path:
    """Guarda un raw payload por fuente para debugging/trazabilidad."""
    source_dir = CHAMPION_SNAPSHOTS_RAW / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    target = source_dir / f"{_timestamp_slug()}.json"
    _write_json_atomic(target, payload)
    return target


def save_champion_snapshots(payload: Any) -> tuple[Path, Path | None, Path]:
    """
    Persiste un snapshot consolidado: pisa latest (con backup) + history.

    Devuelve `(latest_path, backup_path | None, history_path)`.
    """
    ensure_directories()
    backup = write_latest_with_backup(
        CHAMPION_SNAPSHOTS_LATEST, CHAMPION_SNAPSHOTS_BACKUPS, payload
    )
    history = append_history(CHAMPION_SNAPSHOTS_HISTORY, payload, suffix="_merged")
    return CHAMPION_SNAPSHOTS_LATEST, backup, history


def save_final_tierlist(payload: Any) -> tuple[Path, Path | None, Path]:
    """Persiste tier list final consolidada: latest (con backup) + history."""
    ensure_directories()
    backup = write_latest_with_backup(
        FINAL_TIERLIST_LATEST, FINAL_TIERLIST_DIR / "backups", payload
    )
    history = append_history(FINAL_TIERLIST_HISTORY, payload)
    return FINAL_TIERLIST_LATEST, backup, history


def save_daily_report(report_date: str, payload: Any) -> Path:
    """Persiste reporte diario por fecha calendario."""
    ensure_directories()
    target = DAILY_REPORTS_DIR / f"{report_date}.json"
    _write_json_atomic(target, payload)
    return target


def save_match_history(puuid: str, payload: Any) -> Path:
    """Persiste match history snapshot por PUUID."""
    ensure_directories()
    puuid_dir = MATCH_HISTORY_DIR / puuid
    puuid_dir.mkdir(parents=True, exist_ok=True)
    target = puuid_dir / f"{_timestamp_slug()}.json"
    _write_json_atomic(target, payload)
    return target


def save_otp_ranking(champion_id: str, payload: Any) -> Path:
    """Persiste un ranking OTP por campeón."""
    ensure_directories()
    champ_dir = OTP_RANKINGS_DIR / champion_id
    champ_dir.mkdir(parents=True, exist_ok=True)
    target = champ_dir / f"{_timestamp_slug()}.json"
    _write_json_atomic(target, payload)
    return target


def save_pro_accounts(payload: Any) -> Path:
    """Persiste el roster mutable de cuentas pro (sin rotación)."""
    ensure_directories()
    _write_json_atomic(PRO_ACCOUNTS_FILE, payload)
    return PRO_ACCOUNTS_FILE


def read_adapter_runs() -> dict[str, Any]:
    """Lee la telemetría de runs por adapter. Devuelve {} si no existe."""
    data = read_json(ADAPTER_RUNS_FILE)
    return data if isinstance(data, dict) else {}


def save_adapter_runs(payload: dict[str, Any]) -> Path:
    """Persiste telemetría de adapter runs (mutable, sin rotación)."""
    ensure_directories()
    _write_json_atomic(ADAPTER_RUNS_FILE, payload)
    return ADAPTER_RUNS_FILE


def read_sources() -> list[dict[str, Any]]:
    """Lee el registry de fuentes; devuelve [] si el archivo no existe."""
    data = read_json(SOURCES_FILE)
    if not data:
        return []
    return data.get("sources", []) if isinstance(data, dict) else data


def read_pro_players_seed() -> list[dict[str, Any]]:
    """Lee el seed de pros; devuelve [] si el archivo no existe."""
    data = read_json(PRO_PLAYERS_SEED_FILE)
    if not data:
        return []
    return data.get("players", []) if isinstance(data, dict) else data


def save_asia_presence(payload: Any) -> Path:
    """Persiste la presencia de Asia cacheada (sin rotación)."""
    ensure_directories()
    _write_json_atomic(ASIA_PRESENCE_FILE, payload)
    return ASIA_PRESENCE_FILE


def read_asia_presence() -> dict[str, Any]:
    """Lee la presencia de Asia cacheada. Devuelve {} si no existe."""
    data = read_json(ASIA_PRESENCE_FILE)
    return data if isinstance(data, dict) else {}
