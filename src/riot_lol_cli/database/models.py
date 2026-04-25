"""
ORM Models para Meta Analyzer
Usando SQLAlchemy para abstracción de BD
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, String, Text, create_engine
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class AnomalyTypeEnum(str, Enum):
    WINRATE_SPIKE = "WINRATE_SPIKE"
    WINRATE_DROP = "WINRATE_DROP"
    ITEM_EMERGENCE = "ITEM_EMERGENCE"
    ITEM_REPLACEMENT = "ITEM_REPLACEMENT"
    RUNE_CHANGE = "RUNE_CHANGE"
    PICKRATE_SURGE = "PICKRATE_SURGE"
    META_SHIFT = "META_SHIFT"


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TierEnum(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class TrendEnum(str, Enum):
    RISING = "RISING"
    STABLE = "STABLE"
    FALLING = "FALLING"


# ============================================================================
# MODELS
# ============================================================================

class RawMatch(Base):
    """Partidas crudas - ventana 48h"""
    __tablename__ = "raw_matches"

    id = Column(Integer, primary_key=True)
    match_id = Column(String(255), unique=True, nullable=False, index=True)
    platform_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Información general
    match_duration_seconds = Column(Integer, nullable=False)
    game_mode = Column(String(50), nullable=False)
    game_type = Column(String(50), nullable=False)
    
    # Participantes
    champion_id = Column(Integer, nullable=False)
    champion_name = Column(String(100), nullable=False, index=True)
    summoner_name = Column(String(100), nullable=False, index=True)
    summoner_id = Column(String(255), nullable=False)
    
    # Stats
    role = Column(String(50))
    team_id = Column(Integer)
    
    # Resultados
    win = Column(Boolean, nullable=False)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    damage_dealt = Column(Float)
    damage_taken = Column(Float)
    gold_earned = Column(Float)
    minions_killed = Column(Integer)
    vision_score = Column(Float)
    
    # Items
    item_0 = Column(Integer)
    item_1 = Column(Integer)
    item_2 = Column(Integer)
    item_3 = Column(Integer)
    item_4 = Column(Integer)
    item_5 = Column(Integer)
    item_6 = Column(Integer)
    
    # Runas
    rune_primary = Column(Integer)
    rune_secondary = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "champion_name": self.champion_name,
            "summoner_name": self.summoner_name,
            "win": self.win,
            "role": self.role,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class ChampionHourly(Base):
    """Estadísticas agregadas por hora"""
    __tablename__ = "champion_hourly"

    id = Column(Integer, primary_key=True)
    hour_bucket = Column(DateTime, nullable=False, index=True)
    champion_name = Column(String(100), nullable=False, index=True)
    
    # Agregaciones
    total_matches = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    
    # Porcentajes
    winrate_pct = Column(Float)
    pickrate_pct = Column(Float)
    banrate_pct = Column(Float)
    
    # Items principales
    item_1_id = Column(Integer)
    item_2_id = Column(Integer)
    item_3_id = Column(Integer)
    
    # Stats promedio
    avg_kills = Column(Float)
    avg_deaths = Column(Float)
    avg_assists = Column(Float)
    avg_damage_dealt = Column(Float)
    avg_damage_taken = Column(Float)
    avg_gold_earned = Column(Float)
    avg_minions_killed = Column(Float)
    avg_vision_score = Column(Float)
    avg_game_duration_seconds = Column(Float)
    
    # Por rol (JSON)
    role_distribution = Column(Text)  # JSON string
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_hour_champion', 'hour_bucket', 'champion_name', unique=True),
    )

    def to_dict(self) -> dict:
        return {
            "hour_bucket": self.hour_bucket.isoformat() if self.hour_bucket else None,
            "champion_name": self.champion_name,
            "total_matches": self.total_matches,
            "winrate": self.winrate_pct,
            "pickrate": self.pickrate_pct,
            "banrate": self.banrate_pct,
            "avg_damage": self.avg_damage_dealt,
            "items_top3": [self.item_1_id, self.item_2_id, self.item_3_id],
        }

    def get_role_distribution(self) -> dict[str, float]:
        """Parsea role_distribution JSON"""
        if not self.role_distribution:
            return {}
        return json.loads(self.role_distribution)

    def set_role_distribution(self, dist: dict[str, float]):
        """Serializa role_distribution"""
        self.role_distribution = json.dumps(dist)


class Anomaly(Base):
    """Cambios detectados en el meta"""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    champion_name = Column(String(100), nullable=False, index=True)
    
    # Tipo
    anomaly_type = Column(SQLEnum(AnomalyTypeEnum), nullable=False, index=True)
    
    # Valores
    previous_value = Column(Float)
    current_value = Column(Float)
    change_pct = Column(Float)
    z_score = Column(Float)
    
    # Confianza
    confidence = Column(Float, nullable=False, index=True)  # 0.0 a 1.0
    severity = Column(SQLEnum(SeverityEnum))
    
    # Detalles
    description = Column(Text)
    details = Column(Text)  # JSON
    
    # Seguimiento
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "champion": self.champion_name,
            "type": self.anomaly_type.value if self.anomaly_type else None,
            "confidence": self.confidence,
            "z_score": self.z_score,
            "current_value": self.current_value,
            "change_pct": self.change_pct,
            "description": self.description,
            "severity": self.severity.value if self.severity else None,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    def get_details(self) -> dict:
        """Parsea details JSON"""
        if not self.details:
            return {}
        return json.loads(self.details)

    def set_details(self, details: dict):
        """Serializa details"""
        self.details = json.dumps(details)


class TierList(Base):
    """Snapshots de tier lists"""
    __tablename__ = "tier_lists"

    id = Column(Integer, primary_key=True)
    snapshot_at = Column(DateTime, nullable=False, index=True)
    
    # Info del snapshot
    patch_version = Column(String(50), index=True)
    total_matches_in_window = Column(Integer)
    
    # Tier list completa (JSON)
    tier_list_json = Column(Text, nullable=False)  # JSON array
    
    # Summary (JSON)
    tier_distribution = Column(Text)  # JSON: {"S": 5, "A": 12, ...}
    
    # Anomalies activas
    active_anomalies_count = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "snapshot_at": self.snapshot_at.isoformat() if self.snapshot_at else None,
            "patch_version": self.patch_version,
            "total_matches": self.total_matches_in_window,
            "active_anomalies": self.active_anomalies_count,
            "tier_distribution": json.loads(self.tier_distribution) if self.tier_distribution else {},
        }

    def get_tier_list(self) -> list[dict]:
        """Parsea tier_list_json"""
        return json.loads(self.tier_list_json)

    def set_tier_list(self, tier_list: list[dict]):
        """Serializa tier list"""
        self.tier_list_json = json.dumps(tier_list)

    def get_tier_distribution(self) -> dict[str, int]:
        """Parsea tier_distribution"""
        if not self.tier_distribution:
            return {}
        return json.loads(self.tier_distribution)

    def set_tier_distribution(self, dist: dict[str, int]):
        """Serializa tier_distribution"""
        self.tier_distribution = json.dumps(dist)


class ChampionStatsHistorical(Base):
    """Stats históricos por día (último mes)"""
    __tablename__ = "champion_stats_historical"

    id = Column(Integer, primary_key=True)
    date_bucket = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    champion_name = Column(String(100), nullable=False, index=True)
    
    # Stats del día
    matches = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    winrate_pct = Column(Float)
    pickrate_pct = Column(Float)
    banrate_pct = Column(Float)
    
    # Trending
    tier_assigned = Column(SQLEnum(TierEnum))
    trend = Column(SQLEnum(TrendEnum))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_date_champion', 'date_bucket', 'champion_name', unique=True),
    )

    def to_dict(self) -> dict:
        return {
            "date": self.date_bucket,
            "champion": self.champion_name,
            "matches": self.matches,
            "winrate": self.winrate_pct,
            "pickrate": self.pickrate_pct,
            "banrate": self.banrate_pct,
            "tier": self.tier_assigned.value if self.tier_assigned else None,
            "trend": self.trend.value if self.trend else None,
        }


class MetaEvent(Base):
    """Eventos importantes en meta"""
    __tablename__ = "meta_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    patch_version = Column(String(50), index=True)
    
    # Cambios
    description = Column(Text, nullable=False)
    affected_champions = Column(Text)  # JSON
    affected_items = Column(Text)      # JSON
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def get_affected_champions(self) -> list[str]:
        if not self.affected_champions:
            return []
        return json.loads(self.affected_champions)

    def set_affected_champions(self, champs: list[str]):
        self.affected_champions = json.dumps(champs)

    def get_affected_items(self) -> list[int]:
        if not self.affected_items:
            return []
        return json.loads(self.affected_items)

    def set_affected_items(self, items: list[int]):
        self.affected_items = json.dumps(items)


class AnalysisLog(Base):
    """Logs de análisis para auditoría"""
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True)
    analysis_type = Column(String(50), nullable=False, index=True)
    
    # Ejecución
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(20), index=True)
    
    # Resultados
    matches_processed = Column(Integer)
    anomalies_detected = Column(Integer)
    tier_list_generated = Column(Boolean)
    
    # Logs
    log_message = Column(Text)
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "analysis_type": self.analysis_type,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "matches_processed": self.matches_processed,
            "anomalies_detected": self.anomalies_detected,
        }


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manager para conexiones y operaciones DB"""
    
    def __init__(self, db_path: str = "data/meta_analyzer.db"):
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Inicializa la BD con el schema"""
        Base.metadata.create_all(self.engine)
        logger.info("Base de datos inicializada: %s", self.db_path)

    def get_session(self) -> Session:
        """Retorna una sesión de BD"""
        return self.SessionLocal()

    def cleanup_old_matches(self, hours: int = 48):
        """Limpia matches más antiguas que N horas"""
        from datetime import timedelta
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            deleted = session.query(RawMatch).filter(
                RawMatch.timestamp < cutoff
            ).delete()
            session.commit()
            logger.info("Eliminadas %d partidas antiguas (>%dh)", deleted, hours)
        finally:
            session.close()

    def get_latest_stats(self, limit: int = 50) -> list[ChampionHourly]:
        """Obtiene las últimas stats de campeones"""
        session = self.get_session()
        try:
            return session.query(ChampionHourly).order_by(
                ChampionHourly.hour_bucket.desc()
            ).limit(limit).all()
        finally:
            session.close()

    def get_high_confidence_anomalies(self, min_confidence: float = 0.85) -> list[Anomaly]:
        """Obtiene anomalías de alta confianza"""
        session = self.get_session()
        try:
            return session.query(Anomaly).filter(
                Anomaly.confidence >= min_confidence
            ).order_by(Anomaly.detected_at.desc()).all()
        finally:
            session.close()

    def get_tier_list_snapshot(self, limit: int = 1) -> Optional[TierList]:
        """Obtiene el último snapshot de tier list"""
        session = self.get_session()
        try:
            return session.query(TierList).order_by(
                TierList.snapshot_at.desc()
            ).first()
        finally:
            session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = DatabaseManager()
    db.init_db()
    logger.info("Models y DatabaseManager listos")
