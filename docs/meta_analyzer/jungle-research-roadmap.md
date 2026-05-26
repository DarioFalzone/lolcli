# Jungle Research — Roadmap (V5+)

Visión a futuro del subsistema `jungle_research/`. Este archivo cubre **qué viene después de V3.7**.  
El estado actual vive en [`jungle-research-status.md`](jungle-research-status.md).  
Las decisiones de diseño viven en [`jungle-research-decisions.md`](jungle-research-decisions.md).

> **Estado actual**: V3.7 (METAsrc extraído, esports integrado, HTML/CSS/JS separado)  
> **Última actualización**: 2026-05-25 (PR-D cerrado)

---

## 🔄 Fases completadas (referencia)

| Fase | Foco | Status |
|------|------|--------|
| **V1** | Scoring + registry + endpoints base | ✅ Cerrada [2026-05-12] |
| **V2** | Pro players seed + account resolution | ✅ Cerrada [2026-05-12] |
| **V3** | Adapter chasis + METAsrc V3.7 real | ✅ Cerrada [2026-05-25] |
| **V4** | Asia meta (KR/CN/JP) | ⏳ Planned |

Ver [`jungle-research-status.md`](jungle-research-status.md) para detalles V1-V3.

## Estado actual (V1)

Cerrado en `[2026-05-12]` con 3 PRs por fases. Ver bitácora.

| Capa | Estado |
|------|--------|
| Schemas Pydantic V2 | OK 8 modelos compatibles SQL |
| Storage JSON inmutable + rotación | OK escritura atómica via `.tmp` |
| Source registry (35 fuentes) | OK 7 active, 28 planned |
| Scoring engine (percentil + consenso) | OK 7 pesos final + 4 confidence |
| Riot bridge (RiotClient + SERVER_ROUTING) | OK gap controlado sin key |
| Pipeline `meta_soloq` | OK Meta Scraper + Jungle Meta curated |
| Pipeline `pro_accounts` | OK manual seed, sin scrape |
| Pipeline `match_history` | OK match-v5 si hay PUUID + key |
| Reporte diario | OK risers/fallers/contradictions |
| 11 endpoints HTTP `/api/v1/jungle-research/*` | OK |
| Tab `Jungla 360` en `/dashboard-enhanced` | OK 5 sub-vistas |
| Tests | OK 79 nuevos, 280 totales en suite |

## V2 - Apertura del registry de pros (parcialmente cerrada)

Foco: **resolución real de cuentas pro**. Hoy todos los pros del seed quedan
en `needs_account_resolution` porque no se trae ningún Riot ID. Esto bloquea
todo el resto de la cadena (`pro_presence` en scoring, picks recientes,
match history). Es la mayor brecha entre "datos de demo" y "datos reales".

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V2.1 | Documentar formato `riot_id` + `server` en `pro_players_seed.json` | ✅ Done [2026-05-12] | Campo `_format_help` en el seed con ejemplos + servers válidos |
| V2.2 | Cargar Riot IDs públicos verificables al seed | ⊘ Descartado | Datos volátiles. UI da el form para que cada uno cargue lo que conoce/verifica |
| V2.3 | Endpoint `POST /api/v1/jungle-research/pros/{name}/account` | ✅ Done [2026-05-12] | Body `{riot_id, server}`. Valida formato, persiste atómico, dispara resolución |
| V2.3b | Endpoint `GET /api/v1/jungle-research/pros` | ✅ Done [2026-05-12] | Lista seed + estado real (puuid, gap_flag, last_seen_at) |
| V2.4 | UI sub-vista Pros: form para agregar Riot ID + server por pro | ✅ Done [2026-05-12] | Cards con `<details>` expandible, input + select de 14 servers, mensajes inline |
| V2.5 | Auto-refresh `match_history` para cuentas resueltas | ⏳ V2.b | Requiere scheduler — sale con V9.5 |
| V2.6 | Persistir `pro_recent_picks` agregado en `final_jungle_tierlist` | ⏳ V2.b | Cachear para evitar re-llamar Riot en cada scoring |
| V2.7 | Sub-vista Pros: mostrar últimos N champion picks reales por jugador | ⏳ V2.b | Lee `match_history/<puuid>/*.json` |

**Bloqueador**: `RIOT_API_KEY` válida (dev keys expiran cada 24h). Para V2.5-V2.7
hay que decidir si se asume key local o se aplica para prod key permanente.

**Bug fix lateral (mismo PR V2)**: el hash hook anidado del cockpit
(`#jungle-research/jr-sources`) fallaba al activar el primary tab. Refactor a
helper `jrActivateView` que setea state directo sin simular clicks anidados.

## V3 - Adapters de SoloQ extra (chasis cerrado, extracts pendientes)

Foco: **redundancia de fuentes**. Hoy si Meta Scraper falla en U.GG/LoLalytics,
todo el sistema queda con 1 fuente o 0. Agregar adapters propios para no
depender solo de la pipeline existente.

Cerrado en `[2026-05-12]` modo chasis: los 4 adapters existen como módulos
en `meta_scraper/adapters/`, el pipeline los invoca, la telemetría se
persiste y se visualiza. Los extracts reales quedan como activaciones
manuales por adapter (1 PR por adapter cuando se valide markup en vivo).

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V3.1 | Adapter `mobalytics_jungle` (SPA, requiere Playwright) | ✅ Stub [2026-05-12] | Rate limit 5-10s; `meta_scraper/adapters/mobalytics.py`. Activar = reemplazar `_stub_response()` con Playwright + extract |
| V3.2 | Adapter `metasrc_jungle` (HTML parseable) | ✅ Stub [2026-05-12] | `meta_scraper/adapters/metasrc.py`. Activar = parse del HTML SSR con BeautifulSoup |
| V3.3 | Adapter `leagueofgraphs_jungle` (HTML, rate limit estricto) | ✅ Stub [2026-05-12] | Min_delay 8s configurado. `meta_scraper/adapters/leagueofgraphs.py` |
| V3.4 | Adapter `tracker_gg_lol` (SPA, posibles XHR) | ✅ Stub [2026-05-12] | `meta_scraper/adapters/tracker_gg.py`. Inspeccionar XHR antes de Playwright |
| V3.5 | Pipeline `meta_soloq_extra` que orqueste los adapters | ✅ Done [2026-05-12] | `jungle_research/pipelines/meta_soloq_extra.py` + merge histórico de telemetría |
| V3.6 | Sub-vista Fuentes: `last_attempted_at` por fuente + razón del último gap | ✅ Done [2026-05-12] | Columna "Último run" con badges coloreados; botón "Probar adapters V3" |

**Decisión tomada**: viven en `meta_scraper/adapters/` siguiendo el patrón
existente (LoLalytics/OP.GG/U.GG). El pipeline orquestador vive en
`jungle_research/pipelines/` porque es Jungle Research quien los consume.

**Próximas tareas opcionales** (V3.7+, una por adapter cuando se priorice):

| # | Tarea | Estado |
|---|-------|--------|
| V3.7 | Activar extract real de `metasrc_jungle` | ⏳ Pendiente — bajo costo, empezar por acá |
| V3.8 | Activar extract real de `leagueofgraphs_jungle` | ⏳ Pendiente |
| V3.9 | Activar extract real de `mobalytics_jungle` (requiere Playwright) | ⏳ Pendiente |
| V3.10 | Activar extract real de `tracker_gg_lol` | ⏳ Pendiente — opcional, alta fricción |

## V4 - Asia meta (señal temprana KR/CN/JP)

Foco: **detectar tendencias antes que el meta global**. Las regiones asiáticas
históricamente se anticipan al cambio meta por 1-2 patches. Necesario para
el caso de uso "campeones emergentes".

| # | Tarea | Tipo | Notas técnicas |
|---|-------|------|----------------|
| V4.1 | Adapter `opgg_kr` | adapter | Misma estructura que opgg_jungle, distinto locale `/ko/` |
| V4.2 | Adapter `opgg_jp` | adapter | Idem `/ja/` |
| V4.3 | Adapter `opgg_cn` | adapter | Idem `/zh-cn/`; verificar geolock |
| V4.4 | Adapter `porogg_champions` (KR) | adapter | Stats KR, requiere parsing JSON dentro del HTML |
| V4.5 | Adapter `fow_kr` | adapter | Stats históricos KR; encoding mixto UTF-8/EUC-KR (cuidado con `tests/test_no_mojibake.py`) |
| V4.6 | Adapter `lolps` | adapter | SPA, lang=ko forzado |
| V4.7 | Adapter `deeplol_kr_jungle` | adapter | Ranking KR |
| V4.8 | Adapter `tencent_101` + `tencent_rank` | adapter | CN; encoding GB18030, geolock probable |
| V4.9 | Pipeline `meta_asia` que oriente todos los adapters asiáticos | pipeline | Activa la columna `asia_score` del scoring (hoy = 0) |
| V4.10 | Scoring: integrar `high_elo_presence_score` real (hoy = 0) usando KR Challenger como pivot | scoring | Requiere cohorte separada `(patch, region=KR, elo=CHALLENGER)` |
| V4.11 | Sub-vista Consenso: columna "Asia score" + filtro region | UI | baja |

**Riesgo**: muchas de estas fuentes asiáticas pueden cambiar su markup sin
aviso o requerir cookies de sesión. Implementar con `playwright` y guardar
raw HTML como fallback.

## V5 - Pro stage / esports

Foco: **picks competitivos**. Los pros en stage hacen drafts curados, no SoloQ.
Distinguir entre meta SoloQ y meta stage es clave para el cuadrante "fuerte
en SoloQ pero débil en pro" (y viceversa).

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V5.1 | Adapter `riot_esports_data` (datos oficiales) | adapter | Posible login/auth; verificar terms |
| V5.2 | Adapter `gol_gg` (fallback público) | adapter | HTML parseable; estable históricamente |
| V5.3 | Adapter `gol_picks_of_the_week` | adapter | URL patrón `/champion/picks-of-the-week/selectdate-LAST/` |
| V5.4 | Pipeline `pro_stage` que genere `pro_stage_score` por campeón | pipeline | Pondera por torneo (Worlds > regionals > playoffs) |
| V5.5 | Endpoint `GET /api/v1/jungle-research/pro-stage/recent` | endpoint | Filtros por tournament, days_back |
| V5.6 | Sub-vista nueva "Pro Stage" en Jungla 360 | UI | Tabla de picks/bans por torneo, jugador |
| V5.7 | Reporte diario: agregar sección "diferencia SoloQ vs Pro Stage" | report | Usa `soloq_vs_pro_diff` que ya está en `DailyReport` schema |

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
es S tier" de "Lee Sin es S tier salvo contra Karthus". Para draft real,
matchups importan tanto como el tier.

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V7.1 | Adapter `counterstats` (matchups jungla) | adapter | HTML; usa SOLO para matchups, no como ranking maestro |
| V7.2 | Adapter `lolalytics` extendido para extraer matchup tables | adapter | Reusa estructura existente |
| V7.3 | Schema `ChampionMatchupSnapshot` (champion vs opponent, win_rate, sample, source) | schema | Pareja ordenada |
| V7.4 | Endpoint `GET /api/v1/jungle-research/champions/{id}/matchups` | endpoint | Filtro por opponent o por win_rate < 45% |
| V7.5 | Sub-vista nueva "Matchups jungla" o columna en Consenso | UI | Cuando picks Lee Sin, mostrar 3 worst matchups |

## V8 - Migración a SQLite/PostgreSQL

Foco: **escala y consultas analíticas**. Cuando los snapshots crezcan
(>1000 archivos `history/`), JSON deja de servir para queries cross-snapshot
del estilo "dame el WR promedio de Wukong en los últimos 30 patches en KR".

| # | Tarea | Tipo | Notas |
|---|-------|------|-------|
| V8.1 | Decidir DB target (SQLite local vs PostgreSQL) | decision | SQLite alcanza si stays single-machine; PG necesario si Home Hub se sube a un host |
| V8.2 | DDL inicial mapeando los 8 schemas a tablas | migration | Todos los campos ya están en `schemas.py` |
| V8.3 | Repositorio `jungle_research/repository/` con interfaz común | refactor | Inyectable para permitir tests con SQLite in-memory |
| V8.4 | Migrador `scripts/jungle_research_migrate_json_to_db.py` | script | Lee history/ + latest.json y popula DB |
| V8.5 | Index strategies: `(champion_name, generated_at, region, elo)` para queries de evolución | index | |
| V8.6 | Endpoint `GET /api/v1/jungle-research/champions/{id}/timeseries?from=&to=` | endpoint | Imposible/lento sobre JSON, trivial sobre SQL |

**Trigger**: cuando `data/meta_analyzer/jungle_research/champion_meta_snapshots/history/`
supere los 500 archivos, encarar V8.

## V9 - Operación: jobs programados y reportes

Foco: **automatización**. Hoy refresh es manual desde el cockpit. Para que
el sistema sea útil sin intervención, necesita correr periódicamente.

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

## Decisiones globales pendientes

Cosas que afectan a múltiples fases y vale la pena decidir antes de avanzar:

1. **Storage final**: ¿JSON eternamente, o SQLite cuando crezca, o PostgreSQL? - **Mi recomendación**: SQLite cuando V8 se dispare, PG solo si se sube a host.
2. **Scraping con Playwright**: ¿permitir? Hoy Meta Scraper ya lo usa. - **Recomendación**: sí, con rate limit estricto y respetando robots.txt.
3. **`RIOT_API_KEY` en producción**: ¿dev key rotada manualmente, o aplicar a prod key permanente? - **Recomendación**: dev por ahora, solicitar prod cuando V2 estabilice.
4. **Localizar UI**: el cockpit está mezclado español/inglés. ¿Migrar todo a español, o mantener bilingüe técnico? - **Recomendación**: mantener nombres canónicos (Riot ID, PUUID, jungle, etc.) en inglés y copy en español rioplatense.
5. **Visibilidad**: ¿el Home Hub (`:8080`) debería linkear directamente al tab `#jungle-research`? - **Recomendación**: sí, agregar al grid del Home Hub como acceso directo.

## Cómo se prioriza el siguiente PR

Cuando quieras arrancar el próximo, leer este archivo y elegir 1-3 ítems
**de la fase más temprana sin terminar**. Las fases están ordenadas por
impacto (V2 desbloquea pros, V3 reduce dependencia de Meta Scraper, V4 da
señal temprana asiática). No saltear fases sin justificación.

Reglas heredadas que aplican a todo PR de Jungle Research:

- Cero scraping agresivo. Respetar `Retry-After` y rate limits.
- Cero datos inventados; gap controlado siempre que falte fuente.
- Snapshots inmutables; rotar a `backups/` antes de pisar `latest`.
- UTF-8 sin BOM (test `tests/test_no_mojibake.py` rompe build si entra mojibake).
- Smoke visual obligatorio para cualquier cambio en el tab del cockpit.
- Bitácora actualizada en el mismo PR.
