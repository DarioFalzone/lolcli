# 🎯 Meta Analyzer - Sistema de Detección de Meta en Tiempo Real

Módulo para detectar cambios en el meta de League of Legends **desde el Día 1**, no esperar a la Semana 3.

## 📊 Características

### ✅ Recolección de Datos
- Descarga partidas en tiempo real vía Riot API
- Procesa items, runas, stats de cada partida
- Almacenamiento en base de datos con rolling window (últimas 48h)

### ✅ Análisis Estadístico
- Calcula winrate, pickrate, banrate por campeón
- Agregación por hora, rol, elo
- Historial de 7 días para comparación

### ✅ Detección de Anomalías
- **WINRATE_SPIKE**: Winrate sube 2σ+ (95% confianza)
- **WINRATE_DROP**: Winrate baja significativamente
- **ITEM_EMERGENCE**: Nuevo item popular aparece
- **ITEM_REPLACEMENT**: Cambio en build core
- **RUNE_CHANGE**: Nuevas runas por campeón
- **PICKRATE_SURGE**: Popularidad sube de golpe
- **META_SHIFT**: Cambio general en el meta

### ✅ Generación de Tier Lists
- Ranking automático de campeones (S/A/B/C/D)
- Tendencias detectadas (RISING/STABLE/FALLING)
- Razones contextuales por tier
- HTML + JSON output

## 🏗️ Arquitectura

```
meta_analyzer/
├── data_collector.py      # Recolecta partidas de Riot API
├── anomaly_detector.py    # Detecta cambios estadísticos
├── tier_generator.py      # Genera tier lists
└── __init__.py
```

## 🚀 Uso

### 1. Recolectar Datos

```python
from src.riot_lol_cli.meta_analyzer.data_collector import MetaDataCollector

collector = MetaDataCollector(
    api_key="RGAPI-xxxxxxxx",
    platform="la2",
    regional="americas"
)

# Recolectar matches de jugadores
matches = collector.collect_matches_batch(
    summoners=["Deshu#LAS", "OtroJugador#LAS"],
    count_per_summoner=20
)

# Guardar
collector.save_matches(matches)

# Obtener estadísticas agregadas
stats = collector.get_hourly_stats(matches)
```

### 2. Detectar Anomalías

```python
from src.riot_lol_cli.meta_analyzer.anomaly_detector import MetaAnomalyDetector

detector = MetaAnomalyDetector()

# Detectar cambios
anomalies = detector.detect_anomalies(
    current_stats=current_hour_stats,
    historical_stats=last_7_days_stats
)

# Filtrar por confianza alta
high_confidence = detector.get_high_confidence_anomalies(anomalies)

# Guardar
detector.save_anomalies(high_confidence)
```

### 3. Generar Tier List

```python
from src.riot_lol_cli.meta_analyzer.tier_generator import TierListGenerator

generator = TierListGenerator()

# Generar tier list
tier_list = generator.generate_tier_list(
    stats=current_stats,
    anomalies=anomalies
)

# Guardar JSON
generator.save_tier_list(tier_list)

# Generar HTML
html = generator.get_tier_list_html(tier_list)
with open("tier_list.html", "w") as f:
    f.write(html)
```

## 📈 Ejemplo: Detección de Ekko (Día 1)

**Escenario:** Nuevo parche con items nuevos. Ekko consigue nueva itemización.

### Timeline:

```
00:00 - Parche aplicado
  └─ Ekko: WR 49.2%, PR 4.5% (histórico)

06:00 - Primeros datos
  └─ Ekko: WR 49.8%, PR 5.1%
  └─ "Hollow Radiance" en 38% de builds
  └─ Status: OBSERVACIÓN (n=45 matches)

12:00 - Datos confirmados ✅
  └─ Ekko: WR 51.2%, PR 6.8%
  └─ Z-score: 2.4 (95% confianza)
  └─ Item-specific WR: 53.5%
  └─ Status: 🔔 ANOMALÍA DETECTADA
  └─ Tier Update: B → A (TENDENCIA AL ALZA)

18:00 - Confirmación ✅
  └─ Ekko: WR 52.1%, PR 7.5%
  └─ Confidence: 0.92
  └─ Status: TIER A (CONFIRMED)
  └─ vs. Semana 3: DETECTADO 18 DÍAS ANTES

Resultado: ✅ Cambio detectado en 12 horas
```

## 🔧 Umbrales de Detección

```python
WINRATE_SPIKE_THRESHOLD = 2.0σ        # z-score para detectar spike
PICKRATE_SURGE_THRESHOLD = 3.0%       # aumento absoluto en 6h
ITEM_EMERGENCE_THRESHOLD = 15%        # aumento en pickrate de item
MIN_SAMPLE_SIZE = 50                  # mínimo matches para validez
CONFIDENCE_HIGH = 0.85                # confianza mínima para acción
```

## 📊 Output de Anomalías

Formato JSON:
```json
{
  "detected_at": "2025-01-11T14:30:00",
  "count": 3,
  "anomalies": [
    {
      "timestamp": "2025-01-11T14:30:00",
      "champion": "Ekko",
      "type": "WINRATE_SPIKE",
      "magnitude": 2.0,
      "confidence": 0.92,
      "z_score": 2.4,
      "details": {
        "current_wr": 51.2,
        "historical_avg": 49.2,
        "change_percent": 2.0,
        "matches": 120
      }
    }
  ]
}
```

## 📊 Output de Tier List

Formato JSON:
```json
{
  "generated_at": "2025-01-11T14:30:00",
  "count": 169,
  "tier_list": [
    {
      "champion": "Ekko",
      "tier": "A",
      "winrate": 51.2,
      "pickrate": 6.8,
      "banrate": 5.2,
      "matches": 120,
      "trend": "RISING",
      "reason": "Muy fuerte ahora (WR: 51.2%) ↗ (Tendencia al alza)",
      "best_role": "MIDDLE"
    }
  ]
}
```

## 🗄️ Base de Datos

Tablas SQLite:

### `raw_matches` (últimas 48h)
- match_id, timestamp, champion_id, role, result, items, runes, elo, region, etc.

### `champion_hourly` (agregaciones por hora)
- timestamp, champion_id, role, elo_tier
- matches_count, wins, losses, pickrate, winrate, banrate
- top_items, top_runes

### `anomalies` (detectadas)
- id, timestamp, champion_id, anomaly_type
- magnitude, confidence, details

### `tier_lists` (snapshots históricos)
- timestamp, snapshot_id
- tier_list (JSONB), meta_shift_indicators

## 📅 Próximas Mejoras

- [ ] Machine Learning para predicción
- [ ] Correlación items ↔ champions ↔ winrate
- [ ] Regional comparison (LAS vs EUW vs KR)
- [ ] Professional Play tracking (LEC/LCK)
- [ ] Cause-effect analysis (qué causó el cambio)
- [ ] Real-time notifications/webhooks
- [ ] Dashboard interactivo con D3.js

## 🛠️ Desarrollo

### Tests
```bash
python -m pytest tests/test_meta_analyzer.py -v
```

### Lint
```bash
python -m pylint src/riot_lol_cli/meta_analyzer/
```

### Type checking
```bash
python -m mypy src/riot_lol_cli/meta_analyzer/
```

---

**Versión:** 1.0.0
**Última actualización:** 11 de enero de 2026
**Estado:** MVP funcional ✅
