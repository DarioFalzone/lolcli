"""HTTP router for Esports Research inside Meta Analyzer (:8000).

All endpoints return historical/post-game research data. If storage is missing,
the response stays 200 with visible `gaps`.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.pipelines.orchestrator import run_full_pipeline
from riot_lol_cli.esports_research.reports import coverage as coverage_report
from riot_lol_cli.esports_research.schemas import utcnow_iso
from riot_lol_cli.esports_research.source_registry import SourceRegistry

router = APIRouter(prefix="/api/v1/esports", tags=["esports-research"])


def _ok(**payload: Any) -> dict[str, Any]:
    return {"success": True, **payload, "timestamp": utcnow_iso()}


def _registry_payload() -> dict[str, Any]:
    try:
        registry = SourceRegistry.load()
    except Exception as exc:  # noqa: BLE001
        return {"summary": {}, "sources": [], "gaps": [f"sources registry unavailable: {exc}"]}
    return {
        "summary": registry.summary(),
        "sources": [source.model_dump(mode="json") for source in registry.all()],
        "gaps": [],
    }


def _collection(name: str) -> list[dict[str, Any]]:
    return json_storage.read_silver_collection(name)


def _entities(collection: str) -> list[dict[str, Any]]:
    return json_storage.list_json_rows(json_storage.SILVER_DIR / collection)


def _find(rows: list[dict[str, Any]], field: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if str(row.get(field)) == value), None)


def _limit_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 500))
    return rows[:safe_limit]


@router.get("/health")
async def health() -> dict[str, Any]:
    payload = _registry_payload()
    return _ok(status="ok", service="esports_research", sources=payload["summary"], gaps=payload["gaps"])


@router.get("/tournaments")
async def tournaments(league: str | None = None, season: str | None = None) -> dict[str, Any]:
    rows = _collection("tournaments")
    if league:
        rows = [row for row in rows if str(row.get("league", "")).lower() == league.lower()]
    if season:
        rows = [row for row in rows if season in str(row.get("start_date", ""))]
    return _ok(data=rows, total_records=len(rows), gaps=[] if rows else ["silver/tournaments.json no existe o esta vacio"])


@router.get("/tournaments/{tournament_id}")
async def tournament_detail(tournament_id: str) -> dict[str, Any]:
    row = _find(_collection("tournaments"), "tournament_id", tournament_id)
    return _ok(data=row, gaps=[] if row else [f"tournament not found: {tournament_id}"])


@router.get("/matches/{match_id}")
async def match_detail(match_id: str) -> dict[str, Any]:
    row = json_storage.read_silver_entity("matches", match_id) or _find(_entities("matches"), "match_id", match_id)
    return _ok(data=row, gaps=[] if row else [f"match not found: {match_id}"])


@router.get("/games/{game_id}")
async def game_detail(game_id: str) -> dict[str, Any]:
    row = json_storage.read_silver_entity("games", game_id) or _find(_entities("games"), "game_id", game_id)
    return _ok(data=row, gaps=[] if row else [f"game not found: {game_id}"])


@router.get("/games/{game_id}/draft")
async def game_draft(game_id: str) -> dict[str, Any]:
    rows = [row for row in _collection("draft_actions") if row.get("game_id") == game_id]
    return _ok(game_id=game_id, data=rows, total_records=len(rows), gaps=[] if rows else [f"draft not found: {game_id}"])


@router.get("/games/{game_id}/participants")
async def game_participants(game_id: str) -> dict[str, Any]:
    rows = [row for row in _collection("participants") if row.get("game_id") == game_id]
    return _ok(game_id=game_id, data=rows, total_records=len(rows), gaps=[] if rows else [f"participants not found: {game_id}"])


@router.get("/teams")
async def teams() -> dict[str, Any]:
    rows = _collection("teams")
    return _ok(data=rows, total_records=len(rows), gaps=[] if rows else ["silver/teams.json no existe o esta vacio"])


@router.get("/teams/{team_id}")
async def team_detail(team_id: str) -> dict[str, Any]:
    row = _find(_collection("teams"), "team_id", team_id)
    return _ok(data=row, gaps=[] if row else [f"team not found: {team_id}"])


@router.get("/teams/{team_id}/recent")
async def team_recent(team_id: str, limit: int = 20) -> dict[str, Any]:
    participants = [row for row in _collection("participants") if row.get("team_id") == team_id]
    game_ids = {row.get("game_id") for row in participants}
    games = [row for row in _entities("games") if row.get("game_id") in game_ids]
    return _ok(team_id=team_id, data=_limit_rows(games, limit), total_records=len(games), gaps=[] if games else [f"recent games not found: {team_id}"])


@router.get("/teams/{team_id}/champions")
async def team_champions(team_id: str) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in _collection("participants"):
        if row.get("team_id") == team_id and row.get("champion_id"):
            champion_id = str(row["champion_id"])
            counts[champion_id] = counts.get(champion_id, 0) + 1
    data = [{"champion_id": key, "games": value} for key, value in sorted(counts.items())]
    return _ok(team_id=team_id, data=data, total_records=len(data), gaps=[] if data else [f"champion distribution not found: {team_id}"])


@router.get("/players/{player_id}")
async def player_detail(player_id: str) -> dict[str, Any]:
    row = _find(_collection("players"), "player_id", player_id)
    return _ok(data=row, gaps=[] if row else [f"player not found: {player_id}"])


@router.get("/players/{player_id}/comfort")
async def player_comfort(player_id: str) -> dict[str, Any]:
    rows = _read_latest_comfort()
    data = [row for row in rows if row.get("player_id") == player_id]
    return _ok(player_id=player_id, data=data, total_records=len(data), gaps=[] if data else [f"comfort not found: {player_id}"])


@router.get("/players/{player_id}/games")
async def player_games(player_id: str, limit: int = 20) -> dict[str, Any]:
    rows = [row for row in _collection("participants") if row.get("player_id") == player_id]
    return _ok(player_id=player_id, data=_limit_rows(rows, limit), total_records=len(rows), gaps=[] if rows else [f"games not found: {player_id}"])


@router.get("/champions/{champion_id}/pro-stage")
async def champion_pro_stage(champion_id: str) -> dict[str, Any]:
    rows = [row for row in _collection("participants") if row.get("champion_id") == champion_id]
    return _ok(champion_id=champion_id, data=rows, total_records=len(rows), gaps=[] if rows else [f"pro-stage rows not found: {champion_id}"])


@router.get("/champions/{champion_id}/matchups")
async def champion_matchups(champion_id: str, patch: str | None = None) -> dict[str, Any]:
    rows = _read_counterpicks(patch)
    data = [row for row in rows if row.get("champion_id") == champion_id]
    return _ok(champion_id=champion_id, data=data, total_records=len(data), gaps=[] if data else [f"matchups not found: {champion_id}"])


@router.get("/counterpicks")
async def counterpicks(
    role: str | None = None,
    patch: str | None = None,
    region: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    rows = _read_counterpicks(patch)
    if role:
        rows = [row for row in rows if str(row.get("role", "")).upper() == role.upper()]
    if region:
        rows = [row for row in rows if str(row.get("region", "")).upper() == region.upper()]
    rows = sorted(rows, key=lambda row: (row.get("sample_confidence", 0), row.get("winrate_shrunken", 0)), reverse=True)
    return _ok(data=_limit_rows(rows, limit), total_records=len(rows), gaps=[] if rows else ["counterpick matrix no disponible"])


@router.get("/sources")
async def sources() -> dict[str, Any]:
    return _ok(**_registry_payload())


@router.get("/sources/{source_id}/last-run")
async def source_last_run(source_id: str) -> dict[str, Any]:
    registry = SourceRegistry.load()
    source_entry = registry.get(source_id)
    if source_entry is None:
        return _ok(source_id=source_id, data=None, gaps=[f"unknown source: {source_id}"])
    data = _source_last_run_payload(source_id, source_entry.status.value)
    return _ok(source_id=source_id, data=data, gaps=data.get("gaps", []))


@router.get("/coverage")
async def coverage() -> dict[str, Any]:
    report = coverage_report.generate()
    return _ok(data=report.model_dump(mode="json"), gaps=report.gaps)


@router.post("/refresh")
async def refresh(mode: str = "all", tournament: str | None = None) -> dict[str, Any]:
    if mode not in {"bronze", "silver", "gold", "all"}:
        return _ok(mode=mode, gaps=[f"unsupported mode: {mode}"], data=None)
    target_tournament = tournament or "all"
    if mode in {"gold", "all"}:
        result = run_full_pipeline(target_tournament)
        return _ok(mode=mode, data=result, gaps=result.get("gaps", []))
    return _ok(
        mode=mode,
        data={"status": "accepted", "tournament": target_tournament},
        gaps=[f"{mode} refresh requires source-specific ingest/normalize in V0"],
    )


@router.post("/ingest")
async def ingest(source: str, tournament: str | None = None) -> dict[str, Any]:
    registry = SourceRegistry.load()
    source_entry = registry.get(source)
    if source_entry is None:
        return _ok(source=source, data=None, gaps=[f"unknown source: {source}"])
    # NOTE V0: API-triggered external network ingest is reported as a dry run by
    # default to avoid accidental scraping from health/smoke flows. Operators can
    # run source-specific pipeline functions when they intentionally fetch data.
    return _ok(
        source=source,
        tournament=tournament,
        data={"status": "dry_run", "source_status": source_entry.status.value},
        gaps=["external ingest disabled by default in V0 API surface"],
    )


def _source_last_run_payload(source_id: str, source_status: str) -> dict[str, Any]:
    runs_payload = json_storage.read_adapter_runs()
    runs = runs_payload.get("runs", {}) if isinstance(runs_payload.get("runs"), dict) else {}
    run = runs.get(source_id)
    if not isinstance(run, dict):
        return {
            "source_id": source_id,
            "source_status": source_status,
            "status": "never_run",
            "last_attempted_at": None,
            "timestamp": None,
            "rows_ingested": 0,
            "gaps": [f"no run recorded for source: {source_id}"],
        }
    gaps = run.get("gaps", [])
    if isinstance(gaps, str):
        gaps = [gaps]
    if not isinstance(gaps, list):
        gaps = []
    reason = run.get("reason")
    if reason and not gaps:
        gaps = [str(reason)]
    timestamp = run.get("last_attempted_at") or run.get("timestamp") or run.get("updated_at")
    rows_ingested = run.get("rows_ingested", run.get("rows", run.get("row_count", 0)))
    return {
        "source_id": source_id,
        "source_status": source_status,
        "status": run.get("status", "unknown"),
        "last_attempted_at": timestamp,
        "timestamp": timestamp,
        "rows_ingested": rows_ingested,
        "gaps": gaps,
    }


def _read_counterpicks(patch: str | None) -> list[dict[str, Any]]:
    if patch:
        payload = json_storage.read_gold_feature(f"counterpick_matrix_{patch}.json")
        return payload if isinstance(payload, list) else []
    rows: list[dict[str, Any]] = []
    if not json_storage.GOLD_DIR.exists():
        return rows
    for path in sorted(json_storage.GOLD_DIR.glob("counterpick_matrix_*.json")):
        payload = json_storage.read_json(path)
        if isinstance(payload, list):
            rows.extend(row for row in payload if isinstance(row, dict))
    return rows


def _read_latest_comfort() -> list[dict[str, Any]]:
    if not json_storage.GOLD_DIR.exists():
        return []
    paths = sorted(json_storage.GOLD_DIR.glob("comfort_features_*.json"))
    if not paths:
        return []
    payload = json_storage.read_json(paths[-1])
    return payload if isinstance(payload, list) else []
