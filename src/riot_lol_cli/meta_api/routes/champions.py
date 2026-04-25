from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from riot_lol_cli.database.models import Anomaly, ChampionHourly
from riot_lol_cli.meta_api import dependencies


router = APIRouter(tags=["champions"])


@router.get("/api/v1/champions/{champion_name}/matchups")
async def get_champion_matchups(
    champion_name: str,
    limit: int = Query(50, ge=1, le=500),
    hours: int = Query(24, ge=1, le=720),
):
    """Obtiene historial de matchups para un campeón."""
    try:
        with dependencies.session_scope() as session:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            stats = (
                session.query(ChampionHourly)
                .filter(
                    ChampionHourly.champion_name == champion_name,
                    ChampionHourly.hour_bucket >= cutoff,
                )
                .order_by(ChampionHourly.hour_bucket.desc())
                .limit(limit)
                .all()
            )

        matchups = [
            {
                "hour": stat.hour_bucket.isoformat(),
                "champion": stat.champion_name,
                "matches": stat.total_matches,
                "wins": stat.total_wins,
                "losses": stat.total_losses,
                "winrate": round(stat.winrate_pct, 2),
                "pickrate": round(stat.pickrate_pct, 2),
                "banrate": round(stat.banrate_pct, 2),
                "trend": "UP" if stat.winrate_pct > 50 else "DOWN" if stat.winrate_pct < 48 else "STABLE",
                "source": "data_dragon",
            }
            for stat in stats
        ]

        return {
            "success": True,
            "champion": champion_name,
            "hours": hours,
            "data": matchups,
            "total_records": len(matchups),
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting matchups: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/champions/{champion_name}/items")
async def get_champion_items(champion_name: str, limit: int = Query(20, ge=1, le=100)):
    """Obtiene items más usados por un campeón."""
    try:
        with dependencies.session_scope() as session:
            stats = (
                session.query(ChampionHourly)
                .filter(ChampionHourly.champion_name == champion_name)
                .order_by(ChampionHourly.hour_bucket.desc())
                .limit(limit)
                .all()
            )

        items_count = {}
        for stat in stats:
            if stat.item_1_id:
                items_count[stat.item_1_id] = items_count.get(stat.item_1_id, 0) + 1
            if stat.item_2_id:
                items_count[stat.item_2_id] = items_count.get(stat.item_2_id, 0) + 1
            if stat.item_3_id:
                items_count[stat.item_3_id] = items_count.get(stat.item_3_id, 0) + 1

        sorted_items = sorted(items_count.items(), key=lambda item: item[1], reverse=True)[:10]
        items = [
            {
                "item_id": item_id,
                "frequency": count,
                "build_path": f"Item {item_id}",
                "source": "data_dragon",
            }
            for item_id, count in sorted_items
        ]

        return {
            "success": True,
            "champion": champion_name,
            "data": items,
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting items: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/champions/{champion_name}/details")
async def get_champion_details(champion_name: str):
    """Obtiene detalles completos de un campeón."""
    try:
        with dependencies.session_scope() as session:
            latest_stat = (
                session.query(ChampionHourly)
                .filter(ChampionHourly.champion_name == champion_name)
                .order_by(ChampionHourly.hour_bucket.desc())
                .first()
            )
            anomalies = (
                session.query(Anomaly)
                .filter(Anomaly.champion_name == champion_name)
                .order_by(Anomaly.detected_at.desc())
                .limit(5)
                .all()
            )

        if not latest_stat:
            raise HTTPException(status_code=404, detail=f"No data for {champion_name}")

        anomalies_list = [
            {
                "type": anomaly.anomaly_type.value,
                "detected_at": anomaly.detected_at.isoformat(),
                "confidence": round(anomaly.confidence, 3),
                "description": anomaly.description,
                "severity": anomaly.severity.value,
            }
            for anomaly in anomalies
        ]

        return {
            "success": True,
            "champion": champion_name,
            "current_stats": {
                "winrate": round(latest_stat.winrate_pct, 2),
                "pickrate": round(latest_stat.pickrate_pct, 2),
                "banrate": round(latest_stat.banrate_pct, 2),
                "matches": latest_stat.total_matches,
                "wins": latest_stat.total_wins,
                "avg_kills": latest_stat.avg_kills,
                "avg_deaths": latest_stat.avg_deaths,
                "avg_assists": latest_stat.avg_assists,
                "avg_damage": latest_stat.avg_damage_dealt,
                "last_updated": latest_stat.hour_bucket.isoformat(),
            },
            "anomalies": anomalies_list,
            "source": "data_dragon",
            "timestamp": dependencies.utcnow_iso(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        dependencies.logger.error("Error getting champion details: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/champions/all/raw-data")
async def get_all_raw_data(limit: int = Query(100, ge=1, le=1000), champion: Optional[str] = None):
    """Obtiene datos raw de todos los campeones."""
    try:
        with dependencies.session_scope() as session:
            query = session.query(ChampionHourly)
            if champion:
                query = query.filter(ChampionHourly.champion_name == champion)
            records = query.order_by(ChampionHourly.hour_bucket.desc()).limit(limit).all()

        data = [
            {
                "hour_bucket": record.hour_bucket.isoformat(),
                "champion": record.champion_name,
                "matches": record.total_matches,
                "wins": record.total_wins,
                "losses": record.total_losses,
                "winrate": round(record.winrate_pct, 2),
                "pickrate": round(record.pickrate_pct, 2),
                "banrate": round(record.banrate_pct, 2),
                "items": [record.item_1_id, record.item_2_id, record.item_3_id],
                "avg_kills": round(record.avg_kills, 2) if record.avg_kills else None,
                "avg_deaths": round(record.avg_deaths, 2) if record.avg_deaths else None,
                "avg_assists": round(record.avg_assists, 2) if record.avg_assists else None,
                "avg_damage": record.avg_damage_dealt,
                "avg_gold": record.avg_gold_earned,
                "source": "data_dragon",
            }
            for record in records
        ]

        return {
            "success": True,
            "data": data,
            "total_records": len(data),
            "timestamp": dependencies.utcnow_iso(),
        }
    except Exception as exc:
        dependencies.logger.error("Error getting raw data: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
