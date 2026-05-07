"""
Anomaly Detector - Detecta cambios significativos en el meta
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Tipos de anomalías detectables"""

    WINRATE_SPIKE = "WINRATE_SPIKE"  # Winrate sube significativamente
    WINRATE_DROP = "WINRATE_DROP"  # Winrate baja significativamente
    ITEM_EMERGENCE = "ITEM_EMERGENCE"  # Nuevo item popular
    ITEM_REPLACEMENT = "ITEM_REPLACEMENT"  # Cambio en item core
    RUNE_CHANGE = "RUNE_CHANGE"  # Cambio en runas
    PICKRATE_SURGE = "PICKRATE_SURGE"  # Pickrate sube mucho
    META_SHIFT = "META_SHIFT"  # Cambio general en meta


@dataclass
class Anomaly:
    """Representa una anomalía detectada"""

    timestamp: datetime
    champion: str
    anomaly_type: AnomalyType
    magnitude: float  # Cuánto cambió (e.g., +2.5 para +2.5%)
    confidence: float  # 0-1, qué tan seguro estamos
    z_score: Optional[float] = None  # Z-score estadístico
    details: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "champion": self.champion,
            "type": self.anomaly_type.value,
            "magnitude": round(self.magnitude, 2),
            "confidence": round(self.confidence, 3),
            "z_score": round(self.z_score, 2) if self.z_score else None,
            "details": self.details or {},
        }


class MetaAnomalyDetector:
    """Detecta anomalías en estadísticas de campeones"""

    # Umbrales de detección
    WINRATE_SPIKE_THRESHOLD = 2.0  # Z-score para detectar spike
    PICKRATE_SURGE_THRESHOLD = 3.0  # % aumento en pickrate en 6h
    ITEM_EMERGENCE_THRESHOLD = 15  # % aumento en pickrate de item
    MIN_SAMPLE_SIZE = 50  # Mínimo matches para validez estadística
    CONFIDENCE_HIGH = 0.85  # Confidence mínimo para acción

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "meta"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def detect_anomalies(self, current_stats: dict[str, Any], historical_stats: dict[str, Any]) -> list[Anomaly]:
        """
        Detecta anomalías comparando estadísticas actuales con históricas

        Args:
            current_stats: Estadísticas del período actual
            historical_stats: Estadísticas históricas (últimos 7 días)

        Returns:
            Lista de anomalías detectadas
        """

        anomalies = []

        for champion, current_data in current_stats.items():
            if champion not in historical_stats:
                continue  # Sin datos históricos

            historical_data = historical_stats[champion]

            # 1. DETECCIÓN DE SPIKE DE WINRATE
            anomaly = self._detect_winrate_spike(champion, current_data, historical_data)
            if anomaly:
                anomalies.append(anomaly)

            # 2. DETECCIÓN DE CAMBIO DE ITEMIZACIÓN
            item_anomalies = self._detect_item_changes(champion, current_data, historical_data)
            anomalies.extend(item_anomalies)

            # 3. DETECCIÓN DE CAMBIO DE RUNAS
            # (Futura implementación)

            # 4. DETECCIÓN DE SPIKE DE PICKRATE
            anomaly = self._detect_pickrate_surge(champion, current_data, historical_data)
            if anomaly:
                anomalies.append(anomaly)

        return sorted(anomalies, key=lambda x: x.confidence, reverse=True)

    def _detect_winrate_spike(
        self, champion: str, current: dict[str, Any], historical: dict[str, Any]
    ) -> Optional[Anomaly]:
        """Detecta si winrate subió significativamente"""

        # Validar sample size
        if current.get("matches", 0) < self.MIN_SAMPLE_SIZE:
            return None

        current_wr = current.get("winrate", 0)
        historical_avg = historical.get("avg_winrate_7d", 0)
        historical_std = historical.get("std_winrate_7d", 1)

        if historical_std == 0:
            return None

        # Calcular Z-score
        z_score = (current_wr - historical_avg) / historical_std
        magnitude = current_wr - historical_avg

        # Detección: > 2σ (95% confianza)
        if z_score > self.WINRATE_SPIKE_THRESHOLD:
            confidence = min(0.95, 0.50 + (z_score * 0.15))  # 0.50 base + ajuste

            return Anomaly(
                timestamp=datetime.now(),
                champion=champion,
                anomaly_type=AnomalyType.WINRATE_SPIKE,
                magnitude=magnitude,
                confidence=confidence,
                z_score=z_score,
                details={
                    "current_wr": round(current_wr, 2),
                    "historical_avg": round(historical_avg, 2),
                    "change_percent": round(magnitude, 2),
                    "matches": current["matches"],
                },
            )

        # Detección de drop
        elif z_score < -self.WINRATE_SPIKE_THRESHOLD:
            confidence = min(0.95, 0.50 + (abs(z_score) * 0.15))

            return Anomaly(
                timestamp=datetime.now(),
                champion=champion,
                anomaly_type=AnomalyType.WINRATE_DROP,
                magnitude=magnitude,
                confidence=confidence,
                z_score=z_score,
                details={
                    "current_wr": round(current_wr, 2),
                    "historical_avg": round(historical_avg, 2),
                    "change_percent": round(magnitude, 2),
                    "matches": current["matches"],
                },
            )

        return None

    def _detect_item_changes(self, champion: str, current: dict[str, Any], historical: dict[str, Any]) -> list[Anomaly]:
        """Detecta cambios en itemización"""

        anomalies = []
        current_items = set(current.get("items_top3", []))
        historical_items = set(historical.get("items_top3", []))

        # Detectar items nuevos en top 3
        new_items = current_items - historical_items

        for item_id in new_items:
            # Item emergente
            anomalies.append(
                Anomaly(
                    timestamp=datetime.now(),
                    champion=champion,
                    anomaly_type=AnomalyType.ITEM_EMERGENCE,
                    magnitude=0,  # Placeholder
                    confidence=0.80,
                    details={
                        "item_id": item_id,
                        "position": "TOP_3",
                        "historical_position": "NOT_TOP_3",
                    },
                )
            )

        # Detectar items reemplazados
        replaced_items = historical_items - current_items
        if replaced_items:
            for item_id in replaced_items:
                anomalies.append(
                    Anomaly(
                        timestamp=datetime.now(),
                        champion=champion,
                        anomaly_type=AnomalyType.ITEM_REPLACEMENT,
                        magnitude=0,
                        confidence=0.75,
                        details={
                            "old_item": item_id,
                            "new_items": list(new_items),
                        },
                    )
                )

        return anomalies

    def _detect_pickrate_surge(
        self, champion: str, current: dict[str, Any], historical: dict[str, Any]
    ) -> Optional[Anomaly]:
        """Detecta si pickrate subió significativamente"""

        current_pr = current.get("pickrate", 0)
        historical_pr = historical.get("avg_pickrate_7d", 0)

        # Cambio absoluto en pickrate
        pr_change = current_pr - historical_pr

        # Detección: > 3% aumento
        if pr_change > self.PICKRATE_SURGE_THRESHOLD:
            # Confidence basado en magnitud
            confidence = min(0.90, 0.60 + (pr_change * 0.05))

            return Anomaly(
                timestamp=datetime.now(),
                champion=champion,
                anomaly_type=AnomalyType.PICKRATE_SURGE,
                magnitude=pr_change,
                confidence=confidence,
                details={
                    "current_pr": round(current_pr, 2),
                    "historical_pr": round(historical_pr, 2),
                    "change_percent": round(pr_change, 2),
                },
            )

        return None

    def save_anomalies(self, anomalies: list[Anomaly], timestamp: Optional[str] = None) -> Path:
        """Guarda anomalías detectadas"""

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        filepath = self.data_dir / f"anomalies_{timestamp}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "detected_at": datetime.now().isoformat(),
                    "count": len(anomalies),
                    "anomalies": [a.to_dict() for a in anomalies],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info("%d anomalías guardadas en %s", len(anomalies), filepath)
        return filepath

    def get_high_confidence_anomalies(self, anomalies: list[Anomaly]) -> list[Anomaly]:
        """Filtra anomalías de alta confianza para tier list"""
        return [a for a in anomalies if a.confidence >= self.CONFIDENCE_HIGH]


if __name__ == "__main__":
    # Ejemplo de uso
    detector = MetaAnomalyDetector()

    # Mock data
    current = {"Ekko": {"matches": 150, "winrate": 53.5, "pickrate": 8.5, "items_top3": [3089, 3156, 3001]}}

    historical = {
        "Ekko": {
            "avg_winrate_7d": 49.2,
            "std_winrate_7d": 1.5,
            "avg_pickrate_7d": 4.5,
            "items_top3": [3089, 3156, 3135],
        }
    }

    anomalies = detector.detect_anomalies(current, historical)
    for anomaly in anomalies:
        logger.info(
            "%s - %s | Confidence: %.2f%% | Details: %s",
            anomaly.anomaly_type.value,
            anomaly.champion,
            anomaly.confidence * 100,
            anomaly.details,
        )
