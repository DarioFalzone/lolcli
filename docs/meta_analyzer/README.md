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

## Jungla 360 - fuentes y consenso

Capa de investigacion de jungla integrada al Meta Analyzer. Vive en
`src/riot_lol_cli/jungle_research/` y se visualiza como tab dentro de
`/dashboard-enhanced` (`#jungle-research`). Corre dentro del mismo proceso
FastAPI `:8000` y comparte el lifecycle.

### Arquitectura

```text
src/riot_lol_cli/jungle_research/
  schemas.py          Pydantic V2: Source, ChampionMetaSnapshot, ProPlayer,
                      ProAccount, MatchHistoryEntry, OtpRankingEntry,
                      FinalJungleTierEntry, FinalJungleTierList, DailyReport
  source_registry.py  Read-only sobre data/.../sources.json (35 fuentes)
  json_storage.py     Snapshots inmutables, rotacion a backups/, escritura
                      atomica via .tmp
  scoring_engine.py   Percentiles por cohorte (patch, region, elo, queue) +
                      consenso multi-fuente + warning_flags
  riot_bridge.py      Wrapper sobre RiotClient (api.py) con SERVER_ROUTING
                      KR/JP/CN/EUW/NA/BR/etc. + gap si falta RIOT_API_KEY
  pipelines/
    meta_soloq.py     V1 active. Lee Meta Scraper local + Jungle Meta curated
    pro_accounts.py   V1 active. Resuelve PUUID solo si seed tiene riot_id
    match_history.py  V1 active. Descarga ultimas N partidas via match-v5
    meta_asia.py      Planned (KR/CN/JP)
    pro_stage.py      Planned (Riot Esports Data + GOL)
    otp_rankings.py   Planned (Onetricks, LeagueOfGraphs, PORO Masters)
  reports/
    daily_report.py   Top junglers + risers/fallers + contradictions
```

### Storage canonico

```text
data/meta_analyzer/jungle_research/
  sources.json                                  # registry de fuentes
  pro_players_seed.json                         # seed manual de pros
  pro_accounts.json                             # cuentas resueltas
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
```

Storage v1 = JSON. Migracion futura a SQLite/PostgreSQL queda preparada por
nombres de campos compatibles. **Snapshots inmutables**: nunca se pisa
`latest.json` sin antes rotar a `backups/`.

### Endpoints

Bajo `/api/v1/jungle-research/*`:

| Endpoint | Funcion |
|----------|---------|
| `GET overview` | Resumen agregado: top tiers, conteo de fuentes, freshness, riot_api_key_present |
| `GET current?limit=` | Tier list final consolidada |
| `GET sources` | Registry con estado de cada fuente |
| `GET champions/{id}/history` | Evolucion del campeon en backups historicos |
| `GET champions/{id}/otp` | OTPs (V1: gap visible) |
| `GET pros/recent-picks?hours=` | Picks pros ultimas N horas |
| `GET pros/{name}/matches` | Match history persistido |
| `GET emerging` | Mayor subida de score vs ultimo backup |
| `GET consensus` | Mayor acuerdo entre fuentes |
| `GET daily-report?date=` | Reporte diario; genera al vuelo si no existe |
| `POST refresh?mode=soloq\|riot_pros\|all` | Dispara pipelines disponibles |

Regla central: si una capa de datos no esta disponible, los endpoints
devuelven 200 con `gaps` visible. Nunca 500. Nunca inventan datos.

### Refresh: que hace cada modo

- `mode=soloq`: lee `data/meta_scraper/normalized/latest_jungle_tier.json` +
  `data/jungle_meta/patch_*.json`, consolida, persiste tier list.
- `mode=riot_pros`: solo si `RIOT_API_KEY` esta presente, resuelve cuentas
  pro con Riot ID conocido en el seed. Cero scraping.
- `mode=all`: ejecuta lo activo + registra gaps de lo planned.

### Fuentes activas vs planned (V1)

Active (5): Riot API + Data Dragon + Meta Scraper local + Jungle Meta local
+ adapters U.GG/LoLalytics/OP.GG via Meta Scraper.

Planned (28): Mobalytics, METAsrc, League of Graphs, Tracker.gg, PORO.GG,
FOW, LOL.PS, DEEPLOL, Tencent 101, OP.GG KR/JP/CN, TrackingThePros,
DPM.LOL, ProbuildStats, Games of Legends, Riot Esports Data, Onetricks,
CounterStats. Cada una tiene URL en el registry; se activan agregando
adapter cuando se decida implementar.

### Resolucion de cuentas pro

V1 = manual. El seed shipped (`pro_players_seed.json`) trae 11 pros con
URLs publicas pero sin Riot ID. Para resolver cuentas:

1. Editar el seed y agregar `riot_id` (formato `"GameName#TAG"`) y `server`
   (KR, EUW, NA, etc.) por jugador.
2. Exportar `RIOT_API_KEY` (dev keys expiran cada 24h).
3. `POST /api/v1/jungle-research/refresh?mode=riot_pros`.

Si `riot_id` falta -> `gap_flag: needs_account_resolution`. Si falta key ->
`gap_flag: no_riot_key`. Cero scraping de TrackingThePros/DPM.

### Cockpit visual

Tab `Jungla 360` (icono pino) en `/dashboard-enhanced`. 5 sub-vistas:

- **Consenso**: tier list final con score, confidence, WR/PR/BR/games,
  source_count, warnings, explicacion.
- **Fuentes**: registry con estado coloreado (active/planned/gap) y URLs.
- **Pros**: cards por jugador del seed con su flag de resolucion.
- **OTPs**: state-block warning indicando "planned" en V1.
- **Reporte diario**: top junglers + risers + fallers + contradictions
  entre fuentes (spread WR > 5pp).

Header del tab: freshness, patch reportado por fuentes, estado Riot API
(verde si presente, warning si ausente), conteo total de gaps, botones
Refrescar SoloQ / Riot Pros.

URL hash hook: `/dashboard-enhanced#jungle-research` activa el tab al
cargar (util para smoke visual reproducible).

## Deuda Conocida

- `data_collector.py` JSON es legacy; preferir `data_collector_db.py`.
- Algunos documentos historicos describian estructura propuesta o rutas antiguas.
- No hay migraciones Alembic.
- La calidad del detector depende del volumen de muestra.
- Jungle Research V1: 28 de 33 fuentes externas estan en estado `planned` (registry-only). Pipelines `meta_asia`, `pro_stage`, `otp_rankings` no implementados.
- Resolucion automatica de cuentas pro queda fuera de V1 (requiere editar seed manualmente).
