# AGENTS.md — Meta Analyzer

## Qué es este subsistema

Sistema de detección de meta de League of Legends en tiempo real. Analiza datos de partidas para detectar **anomalías estadísticas** (cambios significativos en win rate, pick rate, builds de ítems, runas) y genera **tier lists S/A/B/C/D** con tendencias (RISING/STABLE/FALLING).

**Estado:** Activo / Producción
**Stack:** Python 3.9+, SQLAlchemy, estadísticas (z-score)
**Versión interna:** 1.0.0

## Cómo correr

```bash
# Setup inicial (crea BD + datos demo)
python scripts/setup_meta_analyzer.py

# Levantar API (FastAPI consume meta_analyzer)
python scripts/run_api.py
# → http://localhost:8000/dashboard-enhanced

# Generar dashboard standalone (sin API)
python scripts/generate_dashboard.py
```

## Estructura de Archivos

```
meta_analyzer/
├── AGENTS.md             # Este archivo
├── __init__.py           # Package init (versión 1.0.0)
├── data_collector.py     # Recolecta partidas desde Riot API → JSON files
├── data_collector_db.py  # Recolecta partidas desde Riot API → SQLite DB
├── anomaly_detector.py   # Detecta cambios significativos en el meta
└── tier_generator.py     # Genera tier lists S/A/B/C/D
```

## Pipeline de Datos

```
┌─────────────────┐
│ Riot API (V5)   │
│ Match-V5        │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐    ┌─────────────────────┐
│ data_collector.py   │ or │ data_collector_db.py│
│ → JSON files        │    │ → SQLite (RawMatch) │
└────────┬────────────┘    └──────────┬──────────┘
         │                            │
         └──────────┬─────────────────┘
                    ▼
         ┌─────────────────────┐
         │  ChampionHourly     │ ← agregaciones por hora
         │  (tabla SQLite)     │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │ anomaly_detector.py │ ← compara ventanas (z-score)
         │ → Anomaly records   │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │ tier_generator.py   │ ← clasifica por WR/PR/BR
         │ → TierList snapshot │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │ dashboard / API     │
         └─────────────────────┘
```

## Algoritmos Clave

### Detección de Anomalías (`anomaly_detector.py`)

7 tipos de anomalías detectables:

| Tipo | Descripción | Threshold |
|------|-------------|-----------|
| `WINRATE_SPIKE` | Win rate sube significativamente | Z-score >= 2.0 |
| `WINRATE_DROP` | Win rate baja significativamente | Z-score >= 2.0 |
| `ITEM_EMERGENCE` | Nuevo ítem se vuelve popular | +15% en pickrate |
| `ITEM_REPLACEMENT` | Cambio en ítem core | Comparación builds |
| `RUNE_CHANGE` | Cambio en runas predominantes | Comparación distribución |
| `PICKRATE_SURGE` | Pickrate sube mucho en 6h | +3% absoluto |
| `META_SHIFT` | Cambio general en meta | Múltiples señales |

**Constantes clave:**
- `MIN_SAMPLE_SIZE = 50` — mínimo de partidas para validez estadística
- `CONFIDENCE_HIGH = 0.85` — umbral para considerar la anomalía accionable

### Tier List Generator (`tier_generator.py`)

Clasifica campeones en tiers según WR/PR/BR:
- **S** — OP, must pick
- **A** — Muy bueno, pick frecuente
- **B** — Bueno, viable
- **C** — Aceptable
- **D** — Débil, evitar

Cada `ChampionTierInfo` incluye trend (`RISING`/`STABLE`/`FALLING`) y reason explicativa.

## Base de Datos

Tablas usadas (definidas en `src/riot_lol_cli/database/models.py`):

| Tabla | Propósito |
|-------|-----------|
| `raw_matches` | Partidas crudas (ventana 48h) |
| `champion_hourly` | Agregaciones por hora (WR, PR, BR, items top 3, stats avg) |
| `anomalies` | Anomalías detectadas con z-score y confidence |
| `tier_lists` | Snapshots de tier lists |
| `champion_stats_historical` | Stats por día (último mes) |
| `meta_events` | Eventos importantes en el meta (parches, etc.) |
| `analysis_logs` | Auditoría de ejecuciones |

Ver [database/AGENTS.md](../database/AGENTS.md) para detalles de cada modelo.

## Dependencias Externas

- **Riot Games API:** Match-V5, Account-V1 (vía `src.riot_lol_cli.api.RiotClient`)
- **SQLite:** `data/meta_analyzer.db` (vía `database.DatabaseManager`)
- **Variables de entorno:** `RIOT_API_KEY` requerida para data collection real
- **Sin variables:** Funciona con datos demo generados por `scripts/setup_meta_analyzer.py`

## Gotchas

1. **`data_collector.py` (JSON) vs `data_collector_db.py` (SQLite):** Hay dos collectors. El JSON es legacy/standalone, el DB es el moderno. Usar el DB para nuevos desarrollos.

2. **Path raro a `data/meta/`:** `data_collector.py` y `anomaly_detector.py` hacen `Path(__file__).parent.parent.parent.parent / "data" / "meta"`. Es `BASE_DIR/data/meta/`, no confundir con `data/meta_analyzer.db`.

3. **Demo data:** `scripts/setup_meta_analyzer.py --demo` genera datos sintéticos para los ~30 ADCs del archivo `data/adc_champions.json`.

4. **Cleanup de partidas viejas:** `DatabaseManager.cleanup_old_matches(hours=48)` borra partidas más viejas que 48h. Importante para mantener la BD chica.

5. **`MIN_SAMPLE_SIZE = 50`:** Si tenés menos de 50 partidas para un campeón en una hora, las anomalías no se calculan (evita falsos positivos por sample chico).

6. **Sin tests:** No hay tests unitarios del scoring, anomaly detection ni tier generation. Ver `_analysis/TESTING_AUDIT.md` para el plan.
