# Jungle Research - Hoja de ruta

Roadmap evolutivo para `src/riot_lol_cli/jungle_research/`. Esta es la fuente
de verdad de **lo que falta** y en qué orden encararlo. Se actualiza al cierre
de cada PR, marcando lo hecho y reordenando si cambian prioridades.

> Esta doc complementa `docs/meta_analyzer/README.md` (sección "Jungla 360").
> El README cuenta el estado actual; este archivo cuenta lo que viene.

## Audit-driven fixes Tier 1 + Tier 2 (cerrados 2026-05-24)

Round de saneamiento despues del audit de Codex sobre V1-V4. Cerrados los
8 fixes (5 Tier 1 + 3 Tier 2) en un solo PR.

| Fix | Estado | Notas |
|-----|--------|-------|
| **T1.1** `trend_score` neutralizado a 0.5 constante | OK Done [2026-05-24] | Bug activo: formula `0.5 + (prev - 0.5)` no medía trend, replicaba el score previo. Trend real queda para V10 |
| **T1.2** TTL 48h en cache `asia_presence` con gap visible si stale | OK Done [2026-05-24] | `read_cached_asia_presence_with_metadata()` + warning `asia_presence_stale` en tier list |
| **T1.3** `_compute_asia_presence` sample-aware (penaliza games bajos) | OK Done [2026-05-24] | `_games_boost` + warnings `asia_sample_low`/`asia_sample_unknown` inyectados al tier list entry |
| **T1.4** `_timestamp_slug` con microsegundos + UUID corto | OK Done [2026-05-24] | Previene colisiones cuando V9 scheduler corra cron |
| **T1.5** Guard anti-mojibake cubre `data/meta_analyzer`, `data/draft_advisor`, `data/jungle_meta` | OK Done [2026-05-24] | NO cubre `data/meta_scraper/` (snapshots externos pueden tener mojibake genuino) |
| **T2.6** `_consolidate_and_save` extraido a `orchestrator.py` con `RefreshPlan` | OK Done [2026-05-24] | Router queda como adaptador HTTP delgado. Compat wrapper retroactivo para tests externos |
| **T2.7** `mode=asia` ya NO regenera tier list por default | OK Done [2026-05-24] | UX honesta: solo cachea + telemetría. Para regenerar: `?modes=asia&modes=soloq&regenerate_tierlist=true` |
| **T2.8** `modes=list[str]` con compat de `mode` legacy | OK Done [2026-05-24] | Composicion libre via `?modes=soloq&modes=asia`. Validación 400 si inválido |
| Bonus | `flake8-bugbear` configurado con `extend-immutable-calls` para FastAPI | OK Done [2026-05-24] | Ruff B008 ya no warning sobre `Query()`/`Depends()` defaults |

**Verificación**: `pytest -q` → 529 passed; `ruff check src tests scripts`
→ All checks passed; smoke API confirma `modes=list` compone, `mode=asia`
no regenera por default, `regenerate_tierlist=true` fuerza regeneración.

## Pre-V4 fixes (cerrados 2026-05-12)

Round de saneamiento antes de encarar V4. Cerrado el `[2026-05-12]`:

| Fix | Estado | Notas |
|-----|--------|-------|
| Bug: `_consolidate_and_save` no mergeaba `meta_soloq_extra` al consenso | ✅ Done | Ahora acepta `include_extra=True` (default), mergea snapshots V3 + reporta `extra_snapshots` y `runs` en la respuesta. `mode=all` ya incluye extras. `mode=soloq` mantiene compat (solo Meta Scraper + Jungle Meta) |
| `mode=all` corría `meta_soloq_extra` dos veces (en `_consolidate_and_save` extendido y luego suelto) | ✅ Done | Endpoint refactored a if/elif. Cada modo invoca lo suyo una sola vez |
| `high_elo_presence_score` hardcoded a 0 en scoring | ✅ Done | Scoring acepta nuevo param `asia_presence: dict[str, float]`. Si vacío (V1 sin pipeline meta_asia) sigue siendo 0; cuando V4 alimente el dict, activa el peso 0.10 |
| `FinalJungleTierEntry.asia_score` siempre `None` | ✅ Done | Se llena desde `asia_presence` cuando > 0 |
| Sin tests del flow merged | ✅ Done | 2 tests nuevos en `test_routes.py`: mergea V3 al tier list, mode=soloq NO invoca extras |
| `UTF8JSONResponse` en los 5 servidores FastAPI no Meta Analyzer | ✅ Verificado | Draft Advisor, Meta Scraper, Jungle Meta, Items Browser y Home Hub ya lo aplican. Cierra punto del incidente encoding 2026-05-15 |

Con esto V4 puede arrancar con la confianza de que cualquier nuevo pipeline
`meta_asia` que alimente `asia_presence` impactará directo al `final_score`
sin tocar el orquestador.

## Gaps acumulados (snapshot post-V4, 2026-05-12)

Inventario único de todo lo pendiente, agrupado por categoría operativa.
Cuando un gap se cierra, se tacha y queda como referencia histórica con la
fecha de cierre.

> **Última actualización**: post-cierre de V4 (chasis). El estado de cada
> fase vive en su sección dedicada más abajo; acá solo el rollup ejecutivo.

### Done en esta sesión (referencia histórica)

| Capa | Item | Cierre |
|------|------|--------|
| V1 | Backend foundation completo | 2026-05-12 |
| V1 | ~~`high_elo_presence_score` hardcoded a 0~~ | Pre-V4 fix — scoring acepta `asia_presence` |
| V2 | docs formato riot_id + endpoint POST account + UI form (4/7 done) | 2026-05-12 |
| V2 | Bug visual sub-tabs anidados | Helper `jrActivateView` |
| V3 | Chasis 4 adapters + pipeline + telemetría | Modo chasis cerrado |
| V3 | ~~`_consolidate_and_save` no mergeaba snapshots V3~~ | Pre-V4 fix — `include_extra=True` |
| V4 | Chasis 9 adapters + pipeline + `asia_presence` end-to-end + columna UI | Modo chasis cerrado |
| Encoding | `UTF8JSONResponse` verificado en los 6 servidores FastAPI | Incidente 2026-05-15 cerrado |

### 🔴 Gaps alta prioridad — activación de extracts reales

Mismo patrón: cada adapter stub tiene `note` con instrucciones precisas.
Reemplazar `_stub_response()` por `parse_html()` / Playwright real.

| ID | Adapter | Esfuerzo | Por qué importa |
|----|---------|----------|-----------------|
| ~~**V3.7** METAsrc~~ | ✅ Done [2026-05-24] | Parser real con 3 estrategias (embedded JSON, table, data-attrs) + 14 tests con fixture sintético. PR-B cerrado |
| **V4.13** | OP.GG KR | ~3-4h | Reusa `opgg.py` con locale. KR Challenger = fuente predictiva top |
| **V3.8** | LeagueOfGraphs | ~3h | HTML estático; redundancia SoloQ |
| **V4.14** | PORO.GG (KR) | ~3-4h | Stats KR via `__NEXT_DATA__` JSON embebido |
| V3.9 | Mobalytics (Playwright SPA) | ~4-6h | Tier curado externo además de stats |
| V4.15 | DEEPLOL KR jungle | ~3-4h | Rankings KR jungle específicos |
| V4.16 | OP.GG CN/JP | ~3-4h | Cobertura regional asiática |
| V4.17 | FOW KR + LOLPS | ~4-6h | Encoding mixto (FOW EUC-KR), LOLPS SPA |
| V3.10 | Tracker.gg | ~5-8h | Mayor fricción, valor incremental marginal |
| V4.18 | Tencent 101 + rank (CN) | ~6-10h | Geolock CN, encoding GB18030, opcional |

### 🟠 Gaps diferidos por bloqueador externo

Necesitan decisión del operador o infraestructura previa.

| Gap | Bloqueador | Fase destino |
|-----|------------|--------------|
| **V2.5** auto-refresh `match_history` cuentas resueltas | Necesita scheduler (V9.5) + `RIOT_API_KEY` estable | V9 |
| **V2.6** caché `pro_recent_picks` agregado en `final_jungle_tierlist` | Falta diseño de invalidación | V2.b |
| **V2.7** sub-vista Pros: últimos N picks reales por jugador | Depende de V2.6 + cuentas resueltas | V2.b |
| Sin seed real de Riot IDs (descartado en V2.2) | Operador debe cargar via UI o endpoint | Operacional |
| ~~`pro_presence_score` queda en 0 para todos en repo limpio~~ | ✅ Done [2026-05-24] (PR-C) | Bridge `pro_stage_bridge.py` alimenta desde `esports_research/gold/comfort_features_*.json`. Sin depender de Riot API. `mode=pro_stage` o `?modes=soloq&modes=pro_stage` activa la integración cruzada |

### ⚪ Fases enteras no encaradas

| Fase | Items | Foco | Cuándo encarar |
|------|-------|------|----------------|
| **V5** Pro stage / esports | 7 | Picks competitivos vía Riot Esports Data + GOL | Cuando V3 + V4 tengan 2 extracts reales cada uno |
| **V6** OTP rankings | 7 | Onetricks + LoG summoners + PORO Masters | Cuando haya campeones meta detectados |
| **V7** Matchups / counters | 5 | CounterStats + LoLalytics matchups | Cuando tier list base sea estable |
| **V8** Migración SQLite/PG | 6 | Trigger: `history/` > 500 archivos | Cuando JSON realmente duela (no urgente) |
| **V9** Jobs programados | 11 | APScheduler — desbloquea V2.5-V2.7 + autonomía | Después de 1-2 extracts reales para tener qué automatizar |
| **V10** Calidad / observabilidad | 4 | Logs, métricas, alertas, sparklines | Cuando haya operación continua para monitorear |

### 🟡 Decisiones globales pendientes

Afectan múltiples fases. Sin tomarlas, varios gaps quedan en limbo.

| # | Decisión | Bloquea | Recomendación inicial |
|---|----------|---------|----------------------|
| 1 | **Storage final**: JSON / SQLite / Postgres | V8 | SQLite cuando dispare crecimiento; PG solo si se sube a host compartido |
| 2 | **Playwright para SPA asia + Mobalytics** (V3.9 + V4 SPA) | V3.9, V4.17, V4.18 | Sí, con rate limit estricto y respetar robots.txt. Meta Scraper ya lo usa |
| 3 | **`RIOT_API_KEY`**: dev rotada vs prod permanente | V2.5-V2.7, V9.5 | Dev por ahora; aplicar prod cuando V2.b estabilice |
| 4 | **Localización UI**: bilingüe técnico vs español puro | Drift de microcopy | Mantener canónicos en inglés (Riot ID, PUUID, jungle), copy en español rioplatense |
| 5 | **Home Hub `:8080` → `#jungle-research`**: link directo | UX descubrimiento | Sí, agregar al grid del Home Hub como acceso directo |

### 🔵 Mejoras oportunas / deuda menor

No bloquean fases pero conviene anotarlas para no perderlas.

| Gap | Severidad | Origen | Cuándo resolver |
|-----|-----------|--------|-----------------|
| `final_jungle_tierlist` sin scheduler — envejece silenciosa | Alta | V1 — solo se regenera con `POST /refresh` | V9.7 |
| ~~`trend_score` siempre 0.5 — no se pasa `previous_scores`~~ | ✅ Done [2026-05-24] | T1.1: neutralizado a 0.5 constante con docstring "no-op hasta V10 (trend real desde backups)" |
| Tier cuts hardcoded `(0.85, 0.70, 0.50, 0.30)` en `TIER_CUTS` | Baja | V1 — imposible afinar sin editar código | V10 (config externa) |
| Scoring pesos hardcoded (`WEIGHTS_FINAL`, `WEIGHTS_CONFIDENCE`, `REGION_WEIGHT`) | Baja | V1/V4 — idem tier cuts | V10 |
| `_normalize_iso` no valida timezone ≠ UTC | Baja | V1 — solo afecta si fuente externa reporta `+03:00` (no observado) | Hardening defensivo oportuno |
| Tabla Consenso ya tiene 10 columnas — responsividad va a doler | Media | V4 — agregó "Asia (V4)" | Revisión de diseño cuando se agreguen más layers (V5 pro_stage, V6 otp) |
| HTML embebido en `dashboard_enhanced.py` crece (~80% en estas iteraciones) | Media | UI — string raw Python | Extraer a `meta_api/static/dashboard-enhanced/` cuando el dolor sea evidente |
| Sub-vista Fuentes: tooltip `last_run_reason` truncado a 200 chars sin indicador | Baja | V3.6 | UI mejora cuando se active al menos 1 adapter real |
| Sub-vista Pros: si Riot bridge devuelve `error` (no `gap_flag`), misma card que `no_riot_key` | Baja | V2.4 | UI distinguir modos de fallo |
| Endpoint `GET /pros` no pagina (hoy 11, sin urgencia) | Baja | V2.3b | V8 cuando crezca |
| Telemetría adapter_runs no expone series temporales (solo `last_attempted_at`) | Baja | V3.5 — imposible ver "falló 5 veces seguidas" | V10.3 (alertas) |
| Filtro por region en Consenso | Baja | V4.12 — cuando datos reales por region existan | Después de activar V4.13+ |
| Bug latente cerrado pero no validado en producción: `_consolidate_and_save` mergea extras+asia, pero sin extract real no hay validación end-to-end | Media | Pre-V4 fix | Se cierra automáticamente cuando V3.7 o V4.13 estén activos |

### 📋 Ranking propuesto (qué encarar siguiente)

Por **impacto / esfuerzo**:

1. **V3.7 METAsrc real** — primer extract real, valida cadena V3 end-to-end. ~2-3h. Bajo riesgo (HTML SSR estable).
2. **V4.13 OP.GG KR real** — primer dato asia real, activa `asia_score` con datos. ~3-4h. Alto valor predictivo.
3. **Decisión `RIOT_API_KEY`** — desbloquea V2.5-V2.7. Decisión binaria, no requiere código.
4. **V9.7 + V9.8** (calculate_tierlist_every_6h + generate_daily_report) — empieza operación autónoma. ~4-6h con APScheduler.
5. **Home Hub link a `#jungle-research`** — quick win UX. ~30 min.

**Lo que está bien diferir**:
- V5/V6/V7 (más fuentes) hasta que V3 + V4 tengan al menos 2 extracts reales cada uno
- V8 hasta que `history/` supere 500 archivos (sin presión hoy)
- V10 hasta que haya operación continua que monitorear

---

## 🛣 Caminos propuestos para el próximo PR

Los items del "Ranking propuesto" arriba se pueden agrupar en 3 caminos
coherentes. Cada uno tiene un foco distinto y trade-offs distintos. Esta
sección documenta cuándo encarar cuál, para que la próxima vez que se abra
el roadmap no haya que re-derivar el razonamiento.

### Camino A — Tier 3: deuda estructural (~5-6h)

Pagar deuda de UI **antes** de que V5/V6 hagan el archivo insostenible.

**Items**:
1. Extraer `dashboard_enhanced.py` HTML a `static/dashboard-enhanced/`
   (~4-6h). Hoy son 1390 líneas de raw string en `.py`; cada feature que
   se agrega lo infla más.
2. Mini-router hash único reemplaza el monkey-patch `jrActivateView`
   (~2h). Solución limpia para navegación `#tab/subtab`.
3. División del roadmap en 3 archivos: `status.md` / `roadmap.md` /
   `decisions.md` (~30 min).
4. Drill-down expandible en tabla Consenso (~2-3h). Reducir 10 columnas
   a 5 prioritarias + click expande detalle.

**Pros**: desbloquea V5+ sin que cada feature haga el `.py` insostenible.
Quita un patrón frágil (monkey-patch).

**Contras**: cero valor visible al usuario final (pura ingeniería).
Si V5/V6 quedan en planned por meses, este trabajo se ve menos.

**Cuándo encararlo**: ANTES de cualquier feature que agregue más vistas
al cockpit (V5 Pro Stage, V6 OTPs, surface Esports Research).

### Camino B — Activación de extracts reales V3/V4 (~3-8h por adapter)

Pasar adapters de stub a datos reales. Cada uno es un PR aislado.

**Items priorizados por ROI**:

| Adapter | Esfuerzo | Por qué primero |
|---------|----------|-----------------|
| **V3.7 METAsrc** | ~2-3h | HTML SSR, el más barato. Primer extract real del set V3 — valida cadena `meta_soloq_extra → orchestrator → tier list` con datos reales |
| **V4.13 OP.GG KR** | ~3-4h | Reusa `opgg.py` con locale. KR Challenger = mejor señal predictiva. Primer dato `asia_presence` real |
| **V3.8 LeagueOfGraphs** | ~3h | HTML estático, rate limit ya configurado a 8s. Redundancia SoloQ |
| **V4.14 PORO.GG** | ~3-4h | Stats KR vía `__NEXT_DATA__` JSON embebido. Buen ratio esfuerzo/cobertura |

**Pros**: valor visible inmediato (tier list con datos reales). Cada
adapter es un PR aislado. El chasis ya está testeado — solo hay que
reemplazar `_stub_response()` por `parse_html()`.

**Contras**: requiere acceso a las páginas en vivo para validar
selectores. Si una página cambió markup, se demora. Cada extract abre
superficie de bugs operativos (encoding, rate limit real, captchas).

**Cuándo encararlo**: cuando hay tiempo para iteración rápida + validación
browser. Idealmente con un patch fresco de LoL para tener datos relevantes.

### Camino C — Esports Research V0 (~3-5 días, scope grande)

Ejecutar el plan ya aprobado para el subsistema nuevo `esports_research/`:
pro stage + drafts + counterpicks + comfort jugador-campeón.

**Referencia**: el plan completo vive en
`C:\Users\Dario Falzone\.claude\plans\cuddly-sprouting-newell.md` y cubre:

- Subsistema autónomo `src/riot_lol_cli/esports_research/` separado de
  `jungle_research`.
- 4 adapters activos V0 (Leaguepedia API, Oracle's Elixir CSV, Gol.gg
  HTML, Data Dragon) + 6 stubs (Riot Tournament, GRID, PandaScore, Abios,
  VODs metadata, Game Client local).
- Pipelines bronze/silver/gold + analytics (counterpick matrix + comfort
  jugador-campeón).
- Surface dedicada `/esports` con tokens Pattern Library v2.
- ~110 tests nuevos.

**Pros**: salto cualitativo grande — cubre el caso de uso original del
proyecto (análisis competitivo de drafting). Subsistema autónomo, no
rompe nada de jungle_research.

**Contras**: scope grande. Riesgo de scraping ciego sin validar con
páginas en vivo. Decisión pendiente sobre quién ejecuta: Claude (sesión
larga) o Codex (como se planeó originalmente).

**Cuándo encararlo**: cuando se quiera empezar a usar drafts profesionales
como input al sistema. Es el camino con mayor inversión pero mayor cambio
cualitativo.

### Tabla de decisión: si querés X → encarar Y

| Si querés... | Encarar |
|--------------|---------|
| Sangrado-cero y UI mantenible para meses | **Camino A — Tier 3** |
| Datos reales en pantalla esta semana | **Camino B — V3.7 + V4.13** (1 sprint) |
| Cubrir la pregunta original del proyecto (drafts pro) | **Camino C — Esports Research V0** |
| Compromiso intermedio: poco código nuevo, mucho valor | **Camino B — solo V3.7** (~3h) → validamos cadena con datos reales, después decidimos |

### Recomendación (si hay que elegir uno solo)

**Camino B con foco en V3.7 (METAsrc)**. Razones:

1. Bajo riesgo (~2-3h), cero bloqueos de decisiones globales.
2. Valida que todo el chasis V1+V2+V3+V4+Tier1+Tier2 funcione end-to-end
   con datos reales (no solo stubs).
3. Si rompe algo, lo encontramos con scope chico antes de invertir en
   Camino A o C.
4. Después de V3.7 las opciones A y C quedan más informadas (sabemos qué
   patrones reales necesita la UI, qué datos asia entran al scoring).

### Anti-patrones a evitar

- ❌ **Encarar V5/V6 antes que A**: cualquier feature que agregue tab al
  cockpit antes de extraer HTML va a inflar más el `.py` y dificultar la
  extracción posterior.
- ❌ **Encarar Camino C sin al menos 1 extract real del Camino B**: el
  riesgo de scraping ciego se acumula. Mejor validar el patrón en V3.7
  primero.
- ❌ **Mezclar caminos en un solo PR**: cada uno tiene foco distinto y se
  audita distinto. Mantener atomicidad.

---

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

## V4 - Asia meta (chasis cerrado, extracts pendientes)

Foco: **detectar tendencias antes que el meta global**. Las regiones asiáticas
históricamente se anticipan al cambio meta por 1-2 patches.

Cerrado en `[2026-05-12]` modo chasis: 9 adapters como stubs, pipeline
`meta_asia` calcula `asia_presence` con heuristica WR + region weight,
scoring engine lo aplica al `high_elo_presence_score`, UI muestra columna
"Asia (V4)". Cuando se active el extract real de algun adapter, el flujo
end-to-end ya funciona.

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| V4.1 | Adapter `opgg_kr` (locale ko) | ✅ Stub [2026-05-12] | `meta_scraper/adapters/asia.py:OpGgKrAdapter`. Activar = reusar `opgg.py` con locale |
| V4.2 | Adapter `opgg_jp` (locale ja) | ✅ Stub [2026-05-12] | `OpGgJpAdapter` |
| V4.3 | Adapter `opgg_cn` (locale zh-cn) | ✅ Stub [2026-05-12] | `OpGgCnAdapter`. Cuidado: posibles diferencias de payload por dataset Tencent |
| V4.4 | Adapter `porogg_champions` (KR) | ✅ Stub [2026-05-12] | `PoroGgAdapter`. Activar = parse `<script id=__NEXT_DATA__>` |
| V4.5 | Adapter `fow_kr` | ✅ Stub [2026-05-12] | `FowKrAdapter`. CUIDADO: encoding mixto UTF-8/EUC-KR — validar con `tests/test_no_mojibake.py` |
| V4.6 | Adapter `lolps` | ✅ Stub [2026-05-12] | `LolPsAdapter`. SPA, sospechar XHR antes de Playwright |
| V4.7 | Adapter `deeplol_kr_jungle` | ✅ Stub [2026-05-12] | `DeepLolKrAdapter` |
| V4.8 | Adapter `tencent_101` + `tencent_rank` | ✅ Stub [2026-05-12] | `Tencent101Adapter` + `TencentRankAdapter`. Encoding GB18030 + geolock |
| V4.9 | Pipeline `meta_asia` orienta los 9 adapters | ✅ Done [2026-05-12] | `jungle_research/pipelines/meta_asia.py` + `asia_presence` heuristica + cache JSON |
| V4.10 | Scoring: `high_elo_presence_score` real (era 0 hardcoded) | ✅ Done [2026-05-12] | Resuelto en pre-V4 fixes. `score_snapshots(asia_presence=...)` activa el peso 0.10 |
| V4.11 | Sub-vista Consenso: columna "Asia score" | ✅ Done [2026-05-12] | Columna entre SoloQ y Pro presence; boton "↻ Asia (V4)" en header |
| V4.12 | Filtro por region en Consenso (opcional) | ⏳ Pendiente | Hoy todo es "GLOBAL"; cuando V4 tenga datos reales por region, agregar filtro |

**Próximas activaciones de extract real** (1 PR por adapter, similar a V3.7+):

| # | Tarea | Estado |
|---|-------|--------|
| V4.13 | Activar `opgg_kr` (mas alto ROI: KR challenger es la fuente predictiva top) | ⏳ Pendiente |
| V4.14 | Activar `porogg_champions` (KR alto valor) | ⏳ Pendiente |
| V4.15 | Activar `deeplol_kr_jungle` (rankings KR jungle) | ⏳ Pendiente |
| V4.16 | Activar `opgg_cn` / `opgg_jp` (cobertura regional) | ⏳ Pendiente |
| V4.17 | Activar `fow_kr` / `lolps` | ⏳ Pendiente |
| V4.18 | Activar `tencent_101` / `tencent_rank` (opcional, geolock CN) | ⏳ Pendiente |

**Riesgo**: muchas fuentes asiáticas cambian markup sin aviso o requieren
cookies de sesión. Implementar con `playwright` (Mobalytics-style) y
guardar raw HTML como fallback en `champion_meta_snapshots/raw/<source>/`.

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
