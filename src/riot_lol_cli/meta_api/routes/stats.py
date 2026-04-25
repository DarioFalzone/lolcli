from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from riot_lol_cli.database.models import AnalysisLog, Anomaly, AnomalyTypeEnum, ChampionHourly, TierList
from riot_lol_cli.meta_api import dependencies

router = APIRouter(tags=["stats"])


@router.get("/api/v1/stats/latest")
async def get_latest_stats(limit: int = Query(50, ge=1, le=200)):
    """Obtiene las últimas estadísticas de campeones."""
    try:
        stats = dependencies.db.get_latest_stats(limit=limit)
        return {
            "success": True,
            "count": len(stats),
            "data": [stat.to_dict() for stat in stats],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting latest stats: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/stats/champion/{champion_name}")
async def get_champion_stats(champion_name: str, hours: int = Query(24, ge=1, le=72)):
    """Obtiene las estadísticas históricas de un campeón."""
    try:
        with dependencies.session_scope() as session:
            cutoff = dependencies.utcnow() - timedelta(hours=hours)
            stats = (
                session.query(ChampionHourly)
                .filter(
                    ChampionHourly.champion_name == champion_name,
                    ChampionHourly.hour_bucket >= cutoff,
                )
                .order_by(ChampionHourly.hour_bucket)
                .all()
            )

        if not stats:
            raise HTTPException(status_code=404, detail=f"No data for champion: {champion_name}")

        return {
            "success": True,
            "champion": champion_name,
            "period_hours": hours,
            "count": len(stats),
            "data": [stat.to_dict() for stat in stats],
            "timestamp": dependencies.utcnow_iso(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        dependencies.logger.error("Error getting champion stats: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/stats/top-tier")
async def get_top_tier_champions():
    """Obtiene los campeones más fuertes actualmente."""
    try:
        with dependencies.session_scope() as session:
            latest_tier = session.query(TierList).order_by(TierList.snapshot_at.desc()).first()

        if not latest_tier:
            return {
                "success": False,
                "message": "No tier list data available yet",
                "data": [],
            }

        tier_list = latest_tier.get_tier_list()
        tier_s = [champion for champion in tier_list if champion.get("tier") == "S"]
        tier_a = [champion for champion in tier_list if champion.get("tier") == "A"]

        return {
            "success": True,
            "snapshot_at": latest_tier.snapshot_at.isoformat(),
            "tier_s": tier_s,
            "tier_a": tier_a,
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting top tier: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/anomalies/high-confidence")
async def get_high_confidence_anomalies(
    min_confidence: float = Query(0.85, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
):
    """Obtiene anomalías de alta confianza."""
    try:
        with dependencies.session_scope() as session:
            anomalies = (
                session.query(Anomaly)
                .filter(Anomaly.confidence >= min_confidence)
                .order_by(Anomaly.detected_at.desc())
                .limit(limit)
                .all()
            )

        return {
            "success": True,
            "count": len(anomalies),
            "min_confidence": min_confidence,
            "data": [anomaly.to_dict() for anomaly in anomalies],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting anomalies: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/anomalies/champion/{champion_name}")
async def get_champion_anomalies(champion_name: str, hours: int = Query(24, ge=1, le=72)):
    """Obtiene las anomalías detectadas para un campeón."""
    try:
        with dependencies.session_scope() as session:
            cutoff = dependencies.utcnow() - timedelta(hours=hours)
            anomalies = (
                session.query(Anomaly)
                .filter(
                    Anomaly.champion_name == champion_name,
                    Anomaly.detected_at >= cutoff,
                )
                .order_by(Anomaly.detected_at.desc())
                .all()
            )

        return {
            "success": True,
            "champion": champion_name,
            "period_hours": hours,
            "count": len(anomalies),
            "data": [anomaly.to_dict() for anomaly in anomalies],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting champion anomalies: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/anomalies/types")
async def get_anomaly_types():
    """Obtiene los tipos de anomalías detectadas."""
    return {
        "success": True,
        "anomaly_types": [anomaly.value for anomaly in AnomalyTypeEnum],
        "count": len(AnomalyTypeEnum),
        "descriptions": {
            "WINRATE_SPIKE": "Winrate aumentó significativamente (>2σ)",
            "WINRATE_DROP": "Winrate disminuyó significativamente (>2σ)",
            "ITEM_EMERGENCE": "Nuevo item en el build",
            "ITEM_REPLACEMENT": "Cambio en items principales",
            "RUNE_CHANGE": "Cambio en runas",
            "PICKRATE_SURGE": "Pickrate aumentó >3%",
            "META_SHIFT": "Cambio general en el meta",
        },
    }


@router.get("/api/v1/tier-list/current")
async def get_current_tier_list():
    """Obtiene el tier list actual."""
    try:
        with dependencies.session_scope() as session:
            latest = session.query(TierList).order_by(TierList.snapshot_at.desc()).first()

        if not latest:
            return {
                "success": False,
                "message": "No tier list available yet",
                "data": [],
            }

        tier_list = latest.get_tier_list()
        tier_distribution = latest.get_tier_distribution()
        tier_data = {"S": [], "A": [], "B": [], "C": [], "D": []}

        for champion in tier_list:
            tier = champion.get("tier", "D")
            if tier in tier_data:
                tier_data[tier].append(champion)

        return {
            "success": True,
            "snapshot_at": latest.snapshot_at.isoformat(),
            "patch_version": latest.patch_version,
            "total_matches": latest.total_matches_in_window,
            "active_anomalies": latest.active_anomalies_count,
            "distribution": tier_distribution,
            "tier_s": tier_data["S"],
            "tier_a": tier_data["A"],
            "tier_b": tier_data["B"],
            "tier_c": tier_data["C"],
            "tier_d": tier_data["D"],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting tier list: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/tier-list/history")
async def get_tier_list_history(days: int = Query(7, ge=1, le=30)):
    """Obtiene el histórico de tier lists."""
    try:
        with dependencies.session_scope() as session:
            cutoff = dependencies.utcnow() - timedelta(days=days)
            history = (
                session.query(TierList)
                .filter(TierList.snapshot_at >= cutoff)
                .order_by(TierList.snapshot_at.desc())
                .all()
            )

        return {
            "success": True,
            "period_days": days,
            "count": len(history),
            "data": [tier.to_dict() for tier in history],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting tier list history: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/analysis/logs")
async def get_analysis_logs(limit: int = Query(50, ge=1, le=500), analysis_type: Optional[str] = None):
    """Obtiene los logs de análisis."""
    try:
        with dependencies.session_scope() as session:
            query = session.query(AnalysisLog)
            if analysis_type:
                query = query.filter(AnalysisLog.analysis_type == analysis_type)
            logs = query.order_by(AnalysisLog.created_at.desc()).limit(limit).all()

        return {
            "success": True,
            "count": len(logs),
            "data": [log.to_dict() for log in logs],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting analysis logs: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """Obtiene resumen del dashboard."""
    try:
        with dependencies.session_scope() as session:
            latest_tier = session.query(TierList).order_by(TierList.snapshot_at.desc()).first()
            high_conf = (
                session.query(Anomaly)
                .filter(Anomaly.confidence >= 0.85)
                .order_by(Anomaly.detected_at.desc())
                .limit(10)
                .all()
            )
            latest_stats = session.query(ChampionHourly).order_by(ChampionHourly.hour_bucket.desc()).limit(50).all()

        return {
            "success": True,
            "summary": {
                "last_tier_update": latest_tier.snapshot_at.isoformat() if latest_tier else None,
                "active_anomalies": len(high_conf),
                "champions_tracked": len({stat.champion_name for stat in latest_stats}),
                "total_matches": latest_tier.total_matches_in_window if latest_tier else 0,
            },
            "top_anomalies": [anomaly.to_dict() for anomaly in high_conf[:5]],
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting dashboard summary: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
