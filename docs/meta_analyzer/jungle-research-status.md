# Jungle Research - Estado actual

Snapshot de lo **hecho** y lo **gap** en `src/riot_lol_cli/jungle_research/`.
Este archivo es read-mostly: se actualiza al cierre de cada PR para marcar
nuevos items done.

> Documentos hermanos:
> - [jungle-research-roadmap.md](jungle-research-roadmap.md) — lo que viene (fases futuras).
> - [jungle-research-decisions.md](jungle-research-decisions.md) — ADRs y decisiones globales.

## V1 - Base cerrada [2026-05-12]

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

Cerrada la mitad: el form para cargar Riot IDs existe y persiste, pero la
cadena `pro_accounts → match_history → pro_presence` queda bloqueada por
`RIOT_API_KEY` y por las tareas V2.b.

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V2.1 | Documentar formato `riot_id` + `server` en `pro_players_seed.json` | ✅ Done [2026-05-12] | Campo `_format_help` con ejemplos + servers válidos |
| V2.2 | Cargar Riot IDs públicos verificables al seed | ⊘ Descartado | Datos volátiles. UI da el form para que cada uno cargue lo que conoce/verifica |
| V2.3 | Endpoint `POST /api/v1/jungle-research/pros/{name}/account` | ✅ Done [2026-05-12] | Body `{riot_id, server}`. Valida formato, persiste atómico, dispara resolución |
| V2.3b | Endpoint `GET /api/v1/jungle-research/pros` | ✅ Done [2026-05-12] | Lista seed + estado real (puuid, gap_flag, last_seen_at) |
| V2.4 | UI sub-vista Pros: form para agregar Riot ID + server por pro | ✅ Done [2026-05-12] | Cards con `<details>` expandible, input + select de 14 servers, mensajes inline |

**Bug fix lateral (mismo PR V2)**: el hash hook anidado del cockpit
(`#jungle-research/jr-sources`) fallaba al activar el primary tab. Refactor a
helper `jrActivateView` que setea state directo sin simular clicks anidados.

## V3 - Adapters de SoloQ extra (chasis cerrado, extracts parciales)

Cerrado en `[2026-05-12]` modo chasis: los 4 adapters existen como módulos
en `meta_scraper/adapters/`, el pipeline los invoca, la telemetría se
persiste y se visualiza. Los extracts reales se activan 1 PR por adapter
cuando se valide markup en vivo.

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V3.1 | Adapter `mobalytics_jungle` (SPA, requiere Playwright) | ✅ Stub [2026-05-12] | Rate limit 5-10s; `meta_scraper/adapters/mobalytics.py` |
| V3.2 | Adapter `metasrc_jungle` (HTML parseable) | ✅ Stub [2026-05-12] | `meta_scraper/adapters/metasrc.py` |
| V3.3 | Adapter `leagueofgraphs_jungle` (HTML, rate limit estricto) | ✅ Stub [2026-05-12] | Min_delay 8s configurado |
| V3.4 | Adapter `tracker_gg_lol` (SPA, posibles XHR) | ✅ Stub [2026-05-12] | `meta_scraper/adapters/tracker_gg.py` |
| V3.5 | Pipeline `meta_soloq_extra` que orqueste los adapters | ✅ Done [2026-05-12] | `jungle_research/pipelines/meta_soloq_extra.py` + merge histórico de telemetría |
| V3.6 | Sub-vista Fuentes: `last_attempted_at` por fuente + razón del último gap | ✅ Done [2026-05-12] | Columna "Último run" con badges coloreados; botón "Probar adapters V3" |
| V3.7 | Activar extract real de `metasrc_jungle` | ✅ Done [2026-05-24] | PR-B/`feat/metasrc-real-v37`. 3 estrategias en cascada (embedded_json / table / data_attrs). Degrada a gap si markup cambia |

## PR-A/B/C [2026-05-24] - Integraciones cross-subsystem

Cerrados sobre el commit V0 de `esports_research` (Codex, `f9faa77`):

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| PR-A | Audit `esports_research` V0 read-only | ✅ Done [2026-05-24] | `docs/esports_research/audit_2026-05-24.md`. 6 dimensiones, top 5 issues, no bloquea merge |
| PR-B | V3.7 METAsrc real (ver tabla V3 arriba) | ✅ Done [2026-05-24] | Marca V3.7 como done |
| PR-C | Bridge esports → jungle.pro_presence | ✅ Done [2026-05-24] | Cierra gap `pro_presence_score=0` sin Riot API. STEP_PRO_STAGE + badge "ES" en UI |

## Gaps abiertos (snapshot)

Estos gaps actuales fueron auditados y no están bloqueados:

- `pro_presence_score=0` cuando no hay `RIOT_API_KEY` y no se corre
  `STEP_PRO_STAGE`. Mitigado parcialmente por PR-C (bridge esports).
- `high_elo_presence_score=0` cuando no hay datos KR Challenger. Requiere
  V4.10 (pivot KR Challenger).
- `asia_score=0` cuando no hay pipeline `meta_asia`. Requiere V4.9.
- Adapters V3.8-V3.10 todavía stubs (LeagueOfGraphs, Mobalytics, Tracker.gg).

Detalle de qué falta: ver [jungle-research-roadmap.md](jungle-research-roadmap.md).
