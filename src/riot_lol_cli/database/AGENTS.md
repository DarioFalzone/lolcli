# AGENTS.md — Database

## Propósito

Capa de persistencia para el subsistema **Meta Analyzer**. Define los modelos ORM con SQLAlchemy y el `DatabaseManager` para operaciones de alto nivel (init, cleanup, queries comunes).

**Stack:** SQLAlchemy 2.x (declarative_base), SQLite
**Archivo de BD:** `data/meta_analyzer.db` (~217 KB)

## Modelos (Tablas)

| Tabla | Modelo | Propósito | Indices |
|-------|--------|-----------|---------|
| `raw_matches` | `RawMatch` | Partidas crudas (ventana 48h) | match_id, timestamp, champion_name, summoner_name |
| `champion_hourly` | `ChampionHourly` | Agregaciones por hora (WR/PR/BR + stats avg + top 3 items) | hour_bucket, champion_name (compuesto único) |
| `anomalies` | `Anomaly` | Cambios detectados en meta con z-score y confidence | detected_at, champion_name, anomaly_type, confidence |
| `tier_lists` | `TierList` | Snapshots de tier lists (JSON serializado) | snapshot_at, patch_version |
| `champion_stats_historical` | `ChampionStatsHistorical` | Stats por día (último mes) con tier asignado y trend | date_bucket, champion_name |
| `meta_events` | `MetaEvent` | Eventos importantes en el meta (parches, hotfixes) | event_date, patch_version |
| `analysis_logs` | `AnalysisLog` | Auditoría de ejecuciones del meta analyzer | analysis_type, status |

### Enums (SQLEnum)

- `AnomalyTypeEnum` — `WINRATE_SPIKE`, `WINRATE_DROP`, `ITEM_EMERGENCE`, `ITEM_REPLACEMENT`, `RUNE_CHANGE`, `PICKRATE_SURGE`, `META_SHIFT`
- `SeverityEnum` — `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `TierEnum` — `S`, `A`, `B`, `C`, `D`
- `TrendEnum` — `RISING`, `STABLE`, `FALLING`

## Cómo Acceder a la BD

### Patrón estándar

```python
from src.riot_lol_cli.database import DatabaseManager, ChampionHourly

db = DatabaseManager(db_path="data/meta_analyzer.db")
db.init_db()  # Crea tablas si no existen

session = db.get_session()
try:
    stats = session.query(ChampionHourly).filter(
        ChampionHourly.champion_name == "Jinx"
    ).order_by(ChampionHourly.hour_bucket.desc()).limit(24).all()
finally:
    session.close()
```

### Helpers del DatabaseManager

| Método | Uso |
|--------|-----|
| `init_db()` | Crea todas las tablas |
| `get_session()` | Retorna nueva sesión SQLAlchemy |
| `cleanup_old_matches(hours=48)` | Borra partidas más viejas que N horas |
| `get_latest_stats(limit=50)` | Últimas stats horarias |
| `get_high_confidence_anomalies(min_confidence=0.85)` | Anomalías accionables |
| `get_tier_list_snapshot(limit=1)` | Último snapshot de tier list |

## Archivo de BD

- **Path:** `data/meta_analyzer.db` (relativo al repo root)
- **Tamaño actual:** ~217 KB (con datos demo)
- **Gitignored:** Sí — `*.db` está en `.gitignore`
- **Connection string:** `sqlite:///data/meta_analyzer.db` (engine creado en `DatabaseManager.__init__`)
- **Thread safety:** `connect_args={"check_same_thread": False}` permite uso desde múltiples threads (necesario para FastAPI)

## Schema SQL Standalone

Existe un `database/schema.sql` con el schema en SQL puro, generado a partir de los modelos SQLAlchemy. Útil para:
- Inspección rápida del schema
- Setup de BD sin Python
- Documentación

**No es la fuente de verdad** — los modelos SQLAlchemy en `models.py` son autoritativos.

## Migraciones

**Estado actual:** SIN migraciones implementadas.

- Las tablas se crean con `Base.metadata.create_all(engine)` en `init_db()`
- Cualquier cambio de schema requiere borrar `data/meta_analyzer.db` y regenerar

**TODO:** Si el schema empieza a cambiar con frecuencia, agregar Alembic (`pip install alembic && alembic init alembic`).

## Helpers de Serialización

Varios modelos tienen helpers para campos JSON (porque SQLite no tiene tipo JSON nativo):

| Modelo | Campo JSON | Helpers |
|--------|-----------|---------|
| `ChampionHourly` | `role_distribution` | `get_role_distribution()`, `set_role_distribution(dict)` |
| `Anomaly` | `details` | `get_details()`, `set_details(dict)` |
| `TierList` | `tier_list_json`, `tier_distribution` | `get_tier_list()`, `set_tier_list()`, `get_tier_distribution()`, `set_tier_distribution()` |
| `MetaEvent` | `affected_champions`, `affected_items` | `get_affected_champions()`, `set_affected_champions()`, etc. |

**Convención:** SIEMPRE usar los helpers, nunca asignar el campo raw directamente.

## Gotchas

1. **`check_same_thread=False`:** SQLite por defecto requiere acceso single-thread. La BD permite multi-thread por compatibilidad con FastAPI, pero **cuidado con writes concurrentes**.

2. **`Index('idx_hour_champion', 'hour_bucket', 'champion_name', unique=True)`:** Combinación única en `champion_hourly`. Si querés insertar duplicados, primero hacer DELETE.

3. **Onupdate timestamps:** `updated_at` en `RawMatch` y `TierList` tiene `onupdate=datetime.utcnow` — se actualiza automáticamente en cada UPDATE.

4. **Sin foreign keys:** Las tablas no tienen FKs explícitas entre `raw_matches` y `champion_hourly` aunque están relacionadas conceptualmente. Las relaciones son por `champion_name` (string).

5. **`DatabaseManager` directamente importable:** `from src.riot_lol_cli.database import DatabaseManager` funciona gracias al `__init__.py` que re-exporta.

6. **Test mode:** Correr `python -m src.riot_lol_cli.database.models` ejecuta `if __name__ == "__main__"` que inicializa la BD en su path por defecto. Útil para verificar que SQLAlchemy carga los modelos sin errores.
