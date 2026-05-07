# Meta Analyzer

Documento canonico del subsistema de deteccion de meta. Consolida la guia completa, el quickstart, la referencia tecnica de deteccion y el antiguo documento separado de ADC Tracker.

## Que es

Meta Analyzer detecta cambios en el meta de League of Legends a partir de partidas, agregaciones por hora y analisis estadistico. Su foco actual es ADC tracker/tier lists, con base SQLite local y API FastAPI.

## ADC Tracker

ADC Tracker no es un servicio separado: es una vista/dataset dentro del Meta Analyzer centrada en campeones ADC. Comparte la misma base SQLite, los mismos collectors, las mismas rutas FastAPI y el dashboard enhanced.

Archivos relacionados:

| Archivo | Uso |
|---------|-----|
| `data/adc_champions.json` | Lista de ADCs monitoreados |
| `data/meta_analyzer.db` | Stats y snapshots generados |
| `scripts/fetch_adc_champions.py` | Obtiene/cura lista de ADCs desde Data Dragon |
| `scripts/verify_adc_tracker.py` | Verifica presencia de ADCs en BD |

Flujo:

```text
data/adc_champions.json
  -> setup_meta_analyzer.py / collectors
  -> database.models.ChampionHourly
  -> tier_generator.py
  -> meta_api routes
  -> dashboard_enhanced.py
```

La lista historica documentada era de 31 ADCs trackeados. Verificar el conteo actual contra `data/adc_champions.json` antes de usarlo como contrato.

## Como levantar

```bash
# Crear BD, datos demo y dashboards
python scripts/setup_meta_analyzer.py

# Levantar API en puerto 8000
python scripts/run_api.py

# Generar dashboard standalone
python scripts/generate_dashboard.py
```

URLs:

- API: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- Dashboard enhanced: `http://localhost:8000/dashboard-enhanced`
- OpenAPI: `http://localhost:8000/docs`

## Arquitectura

```text
Riot API / datos demo
  -> meta_analyzer/data_collector_db.py
  -> database/models.py
  -> champion_hourly
  -> meta_analyzer/anomaly_detector.py
  -> anomalies
  -> meta_analyzer/tier_generator.py
  -> tier_lists
  -> meta_api/routes/*
  -> dashboard.py / dashboard_enhanced.py
```

Capas:

- `meta_analyzer/`: logica de recoleccion, agregacion, deteccion y tiering.
- `database/`: modelos SQLAlchemy y `DatabaseManager`.
- `meta_api/`: API HTTP moderna que expone datos y dashboards.
- `scripts/`: setup, generacion de dashboard y runner de API.

## Base de Datos

Archivo local: `data/meta_analyzer.db` (gitignored).

Modelos principales:

| Tabla | Proposito |
|-------|-----------|
| `raw_matches` | Partidas crudas en ventana reciente |
| `champion_hourly` | Agregaciones por campeon/hora |
| `anomalies` | Cambios estadisticos detectados |
| `tier_lists` | Snapshots de tier list |
| `champion_stats_historical` | Historico diario |
| `meta_events` | Parches/hotfixes/eventos |
| `analysis_logs` | Auditoria de ejecuciones |

No hay migraciones activas; `Base.metadata.create_all()` es el mecanismo actual. Cambios de schema requieren plan explicito.

## Deteccion de Anomalias

Tipos soportados por el modelo:

- `WINRATE_SPIKE`
- `WINRATE_DROP`
- `ITEM_EMERGENCE`
- `ITEM_REPLACEMENT`
- `RUNE_CHANGE`
- `PICKRATE_SURGE`
- `META_SHIFT`

Principios:

- Comparar ventanas temporales para detectar cambio.
- Usar umbrales estadisticos como z-score.
- Evitar falsos positivos con minimo de muestra.
- Guardar confidence/severity para priorizar.

## Tier Lists

El generador clasifica campeones en S/A/B/C/D usando WR, PR, BR, volumen y tendencia. Cada snapshot debe conservar patch/source cuando este disponible.

Tiers:

- **S:** dominante o must-pick.
- **A:** fuerte y consistente.
- **B:** viable.
- **C:** situacional.
- **D:** debil o riesgoso.

## API Principal

La API actual se define en `src/riot_lol_cli/meta_api/routes/`.

```text
GET /health
GET /dashboard
GET /dashboard-enhanced
GET /api/v1/stats/latest
GET /api/v1/stats/champion/{champion_name}
GET /api/v1/stats/top-tier
GET /api/v1/anomalies/high-confidence
GET /api/v1/anomalies/champion/{champion_name}
GET /api/v1/tier-list/current
GET /api/v1/tier-list/history
GET /api/v1/champions/{champion_name}/matchups
GET /api/v1/champions/{champion_name}/items
GET /api/v1/champions/{champion_name}/details
GET /api/v1/champions/all/raw-data
POST /api/v1/maintenance/cleanup
GET /api/v1/maintenance/status
```

## Datos Reales vs Demo

- Sin API key, `scripts/setup_meta_analyzer.py` permite trabajar con datos demo.
- Con API key en `.env`, los collectors pueden usar Riot API.
- Las dev keys de Riot expiran cada 24h.
- No hacer loops sin throttling contra Riot API.

## Archivos Clave

| Archivo | Rol |
|---------|-----|
| `src/riot_lol_cli/meta_analyzer/data_collector.py` | Collector legacy/JSON |
| `src/riot_lol_cli/meta_analyzer/data_collector_db.py` | Collector moderno hacia SQLite |
| `src/riot_lol_cli/meta_analyzer/anomaly_detector.py` | Deteccion estadistica |
| `src/riot_lol_cli/meta_analyzer/tier_generator.py` | Generacion de tier lists |
| `src/riot_lol_cli/meta_api/app.py` | FastAPI app |
| `src/riot_lol_cli/database/models.py` | Modelos ORM |
| `scripts/setup_meta_analyzer.py` | Setup y demo data |
| `scripts/run_api.py` | Runner API |

## Troubleshooting

- **`ModuleNotFoundError`:** instalar `pip install -r requirements.txt`.
- **Database locked:** cerrar procesos en puerto 8000 o conexiones abiertas.
- **Dashboard vacio:** correr setup para regenerar demo data.
- **Endpoints no coinciden con docs antiguas:** verificar `meta_api/routes`.

## Deuda Conocida

- `data_collector.py` JSON es legacy; preferir `data_collector_db.py`.
- Algunos documentos historicos describian estructura propuesta o rutas antiguas.
- No hay migraciones Alembic.
- La calidad del detector depende del volumen de muestra.
