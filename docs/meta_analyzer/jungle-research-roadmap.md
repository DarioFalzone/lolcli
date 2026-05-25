# Jungle Research - Roadmap (fases futuras)

Lo **que viene** en `src/riot_lol_cli/jungle_research/`. Fuente de verdad
para elegir el próximo PR. Se actualiza al cierre de cada PR, marcando lo
hecho (que migra a [jungle-research-status.md](jungle-research-status.md))
y reordenando si cambian prioridades.

> Documentos hermanos:
> - [jungle-research-status.md](jungle-research-status.md) — lo que ya está done.
> - [jungle-research-decisions.md](jungle-research-decisions.md) — ADRs y decisiones globales.

## V2.b - Cierre del registry de pros

Tareas que quedaron de V2 al estar bloqueadas por scheduler / cache de
matches.

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V2.5 | Auto-refresh `match_history` para cuentas resueltas | ⏳ V2.b | Requiere scheduler — sale con V9.5 |
| V2.6 | Persistir `pro_recent_picks` agregado en `final_jungle_tierlist` | ⏳ V2.b | Cachear para evitar re-llamar Riot en cada scoring |
| V2.7 | Sub-vista Pros: mostrar últimos N champion picks reales por jugador | ⏳ V2.b | Lee `match_history/<puuid>/*.json` |

**Bloqueador**: `RIOT_API_KEY` válida. Ver [ADR-3](jungle-research-decisions.md#adr-3-riot_api_key).

## V3.8+ - Activación de adapters V3 restantes

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V3.8 | Activar extract real de `leagueofgraphs_jungle` | ⏳ Pendiente — siguiente lógico tras V3.7 |
| V3.9 | Activar extract real de `mobalytics_jungle` (requiere Playwright) | ⏳ Pendiente |
| V3.10 | Activar extract real de `tracker_gg_lol` | ⏳ Pendiente — opcional, alta fricción |

**Patrón a seguir**: V3.7 (METAsrc) en `feat/metasrc-real-v37`. 3 estrategias
en cascada (embedded_json / table / data_attrs), fixture HTML guardado,
tests aislados de red. Reusar el mismo esquema.

## V4 - Asia meta (señal temprana KR/CN/JP)

Foco: **detectar tendencias antes que el meta global**. Las regiones asiáticas
históricamente se anticipan al cambio meta por 1-2 patches.

| # | Tarea | Tipo | Notas técnicas |
|---|-------|------|----------------|
| V4.1 | Adapter `opgg_kr` | adapter | Misma estructura que opgg_jungle, distinto locale `/ko/` |
| V4.2 | Adapter `opgg_jp` | adapter | Idem `/ja/` |
| V4.3 | Adapter `opgg_cn` | adapter | Idem `/zh-cn/`; verificar geolock |
| V4.4 | Adapter `porogg_champions` (KR) | adapter | Stats KR, requiere parsing JSON dentro del HTML |
| V4.5 | Adapter `fow_kr` | adapter | Stats históricos KR; encoding mixto UTF-8/EUC-KR ([ADR-8](jungle-research-decisions.md#adr-8-encoding-utf-8-sin-bom)) |
| V4.6 | Adapter `lolps` | adapter | SPA, lang=ko forzado |
| V4.7 | Adapter `deeplol_kr_jungle` | adapter | Ranking KR |
| V4.8 | Adapter `tencent_101` + `tencent_rank` | adapter | CN; encoding GB18030, geolock probable |
| V4.9 | Pipeline `meta_asia` que oriente todos los adapters asiáticos | pipeline | Activa la columna `asia_score` del scoring (hoy = 0) |
| V4.10 | Scoring: integrar `high_elo_presence_score` real (hoy = 0) usando KR Challenger como pivot | scoring | Requiere cohorte separada `(patch, region=KR, elo=CHALLENGER)` |
| V4.11 | Sub-vista Consenso: columna "Asia score" + filtro region | UI | baja |

**Riesgo**: muchas fuentes asiáticas pueden cambiar markup sin aviso o
requerir cookies de sesión. Implementar con Playwright ([ADR-2](jungle-research-decisions.md#adr-2-scraping-con-playwright)) y guardar
raw HTML como fallback.

## V5 - Pro stage / esports (mayormente cubierto por esports_research)

Foco: **picks competitivos**. Distinguir meta SoloQ de meta stage es clave
para el cuadrante "fuerte en SoloQ pero débil en pro" (y viceversa).

**Nota cross-subsystem**: PR-C [2026-05-24] cerró el flujo `esports comfort
→ jungle.pro_presence_score` vía bridge. Los items V5.x restantes son
incrementales sobre esa base.

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V5.4 | Pipeline `pro_stage` que pondere por torneo (Worlds > regionals > playoffs) | pipeline | Hoy bridge usa max(comfort) sin ponderar |
| V5.5 | Endpoint `GET /api/v1/jungle-research/pro-stage/recent` | endpoint | Filtros por tournament, days_back |
| V5.6 | Sub-vista nueva "Pro Stage" en Jungla 360 | UI | Tabla de picks/bans por torneo, jugador |
| V5.7 | Reporte diario: agregar sección "diferencia SoloQ vs Pro Stage" | report | Usa `soloq_vs_pro_diff` que ya está en `DailyReport` schema |

V5.1-V5.3 (adapters esports) cubiertos por `esports_research/` (Codex V0).

## V6 - OTP rankings y descubrimiento

Foco: **mejores jugadores por campeón**. Para campeones meta, encontrar a los
top players de ese campeón ayuda a estudiar builds, runas, matchups.

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V6.1 | Adapter `onetricks` (rankings + builds por campeón) | adapter | Path `/champions/ranking/<champion>` y `/champions/builds/<champion>` |
| V6.2 | Adapter `leagueofgraphs_summoners` por (campeón, región) | adapter | Path `/rankings/summoners/<champion>/<region>/jungle` |
| V6.3 | Adapter `porogg_masters` por campeón KR | adapter | Path `/leaderboards/champions/<champion>` |
| V6.4 | Pipeline `otp_rankings` que oriente los 3 adapters | pipeline | Para cada campeón meta detectado, busca top OTPs en las 3 fuentes |
| V6.5 | Implementar `GET /api/v1/jungle-research/champions/{id}/otp` con datos reales (hoy es gap) | endpoint | Usa `OtpRankingEntry` schema ya definido |
| V6.6 | Sub-vista OTPs: reemplazar el banner "planned" por tabla con top N por fuente | UI | Click en summoner abre cuenta resuelta vía Riot bridge |
| V6.7 | Cross-reference: si un OTP es también un pro tracked, marcar con badge | feature | Match por Riot ID |

## V7 - Matchups y counters

Foco: **datos de matchup específicos**. Hoy el scoring no diferencia "Lee Sin
es S tier" de "Lee Sin es S tier salvo contra Karthus".

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V7.1 | Adapter `counterstats` (matchups jungla) | adapter | HTML; usa SOLO para matchups, no como ranking maestro |
| V7.2 | Adapter `lolalytics` extendido para extraer matchup tables | adapter | Reusa estructura existente |
| V7.3 | Schema `ChampionMatchupSnapshot` (champion vs opponent, win_rate, sample, source) | schema | Pareja ordenada |
| V7.4 | Endpoint `GET /api/v1/jungle-research/champions/{id}/matchups` | endpoint | Filtro por opponent o por win_rate < 45% |
| V7.5 | Sub-vista nueva "Matchups jungla" o columna en Consenso | UI | Cuando picks Lee Sin, mostrar 3 worst matchups |

## V8 - Migración a SQLite/PostgreSQL

Foco: **escala y consultas analíticas**. Disparada por trigger de snapshots
(ver [ADR-1](jungle-research-decisions.md#adr-1-storage-final)).

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V8.1 | Decidir DB target (SQLite local vs PostgreSQL) | decision | Ya decidido en [ADR-1](jungle-research-decisions.md#adr-1-storage-final): SQLite |
| V8.2 | DDL inicial mapeando los 8 schemas a tablas | migration | Todos los campos ya están en `schemas.py` |
| V8.3 | Repositorio `jungle_research/repository/` con interfaz común | refactor | Inyectable para permitir tests con SQLite in-memory |
| V8.4 | Migrador `scripts/jungle_research_migrate_json_to_db.py` | script | Lee history/ + latest.json y popula DB |
| V8.5 | Index strategies: `(champion_name, generated_at, region, elo)` para queries de evolución | index | |
| V8.6 | Endpoint `GET /api/v1/jungle-research/champions/{id}/timeseries?from=&to=` | endpoint | Imposible/lento sobre JSON, trivial sobre SQL |

**Trigger**: cuando `champion_meta_snapshots/history/` supere los 500 archivos.

## V9 - Operación: jobs programados y reportes

Foco: **automatización**. Hoy refresh es manual desde el cockpit.

| # | Tarea | Tipo | Frecuencia sugerida |
|---|-------|------|---------------------|
| V9.1 | Job `sync_data_dragon_daily` | job | 1x/día |
| V9.2 | Job `scrape_soloq_meta_every_6h` (corre `mode=soloq`) | job | cada 6h |
| V9.3 | Job `scrape_asia_meta_every_6h` (corre `meta_asia` cuando exista) | job | cada 6h, post-V4 |
| V9.4 | Job `update_pro_accounts_daily` | job | 1x/día |
| V9.5 | Job `fetch_pro_matches_every_3h` | job | cada 3h, post-V2 |
| V9.6 | Job `fetch_otp_rankings_daily` (post-V6) | job | 1x/día |
| V9.7 | Job `calculate_tierlist_every_6h` | job | cada 6h, dispara reporte |
| V9.8 | Job `generate_daily_report` | job | 1x/día a las 09:00 ART |
| V9.9 | Implementar via APScheduler dentro de Meta API o crontab + endpoint trigger | infra | APScheduler es más simple si todo vive en :8000 |
| V9.10 | Endpoint `GET /api/v1/jungle-research/jobs/status` con last run + next run | endpoint | |
| V9.11 | UI: pequeño widget de "next refresh in" en el header del tab | UI | |

## V10 - Calidad y observabilidad

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V10.1 | Logs estructurados (JSON) por pipeline run con `correlation_id` | infra | |
| V10.2 | Métricas Prometheus opcionales (snapshots/h, gaps/h, latencia API) | infra | Solo si se sube a host con Prom |
| V10.3 | Alertas en `daily_report` si una fuente lleva > 24h en `gap` | feature | Genera entrada con flag `alert:source_down` |
| V10.4 | Dashboard "salud del sistema" en sub-vista Fuentes con sparklines | UI | |

## Cómo se prioriza el siguiente PR

Cuando arranques el próximo, leer este archivo y elegir 1-3 ítems
**de la fase más temprana sin terminar**. Las fases están ordenadas por
impacto (V2.b desbloquea pros, V3.8+ reduce dependencia de Meta Scraper,
V4 da señal temprana asiática). No saltear fases sin justificación.

Reglas heredadas que aplican a todo PR de Jungle Research:

- Cero scraping agresivo. Respetar `Retry-After` y rate limits ([ADR-2](jungle-research-decisions.md#adr-2-scraping-con-playwright)).
- Cero datos inventados; gap controlado siempre que falte fuente ([ADR-7](jungle-research-decisions.md#adr-7-gap-controlado-vs-error), [ADR-9](jungle-research-decisions.md#adr-9-cero-datos-inventados)).
- Snapshots inmutables; rotar a `backups/` antes de pisar `latest` ([ADR-6](jungle-research-decisions.md#adr-6-snapshots-inmutables--rotación)).
- UTF-8 sin BOM ([ADR-8](jungle-research-decisions.md#adr-8-encoding-utf-8-sin-bom)).
- Smoke visual obligatorio para cualquier cambio en el tab del cockpit.
- Bitácora actualizada en el mismo PR.
