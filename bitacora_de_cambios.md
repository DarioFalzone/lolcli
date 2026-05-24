# Bitacora de Cambios

Este documento registra los cambios significativos, refactorizaciones y evoluciones arquitectonicas del proyecto `riot_lol_cli`.

**Los agentes de IA deben actualizar este archivo luego de cada iteracion significativa para mantener un registro historico de los cambios realizados.**

---

## [2026-05-24] Esports Research E.1 - ingest real con dry_run=false

Se habilito `POST /api/v1/esports/ingest?dry_run=false` para ejecutar ingesta real opt-in desde la API sin cambiar el default seguro.

- `dry_run=true` sigue siendo el default y conserva la respuesta `status="dry_run"`.
- `dry_run=false` despacha a los ingests V0 disponibles para `leaguepedia`, `gol_gg` y `data_dragon`.
- Fuentes sin contrato suficiente en este endpoint devuelven `status="gap"` con razon visible.
- Errores de ingesta se degradan a `status="gap"` para smoke/UX, sin automatizar bypasses ni cambiar compliance.

Tests nuevos cubren exito mockeado de `leaguepedia` y gap para fuente activa no cableada por el endpoint.

---

## [2026-05-24] Esports Research B.1 - selectores reales Gol.gg draft

Se reemplazo el parser generico de `gol_gg.parse_draft_html` por selectores validados contra HTML vivo de Gol.gg (`/game/stats/78125/page-game/`, 200 OK).

- Detecta columnas de equipo por `.blue-line-header` y `.red-line-header`.
- Extrae filas rotuladas `Bans` y `Picks`.
- Lee campeones desde `img.champion_icon_medium` y prioriza el ID canonico del filename (`JarvanIV.png`).
- Completa `action_type` real (`BAN`/`PICK`) y `team_side` real (`BLUE`/`RED`).
- Deriva fases V0 (`BAN_PHASE_1/2`, `PICK_PHASE_1/2`) segun posicion dentro de cada fila.
- Conserva fallback legacy para fixtures simples y HTML antiguo.

La validacion live se hizo con una unica lectura manual del HTML, sin captcha/login ni bypass de contenido. El entorno Windows requirio `curl -k` por problema local de certificado, no por bloqueo de Gol.gg.

---

## [2026-05-24] Esports Research E.2 - telemetria por source

Se agrego telemetria mutable por source para monitorear salud de ingestas sin leer logs manuales.

- Nuevo `data/esports_research/adapter_runs.json` gestionado por `json_storage`.
- Helpers `read_adapter_runs`, `save_adapter_runs` y `save_adapter_run`.
- Endpoint `GET /api/v1/esports/sources/{source_id}/last-run`.
- Respuesta normalizada con `status`, `last_attempted_at`, `timestamp`, `rows_ingested`, `gaps` y `source_status`.
- Si la fuente existe pero aun no corrio, devuelve `status="never_run"` y gap visible.
- Si la fuente no existe, devuelve `data=null` y gap `unknown source`.

Tests cubren round-trip de storage, fuente sin corridas, fuente desconocida y corrida exitosa con rows ingestados.

---

## [2026-05-24] Esports Research V0 - subsistema pro-stage

### Que se hizo

- Nuevo paquete `src/riot_lol_cli/esports_research/` con schemas Pydantic V2,
  storage JSON atomico, source registry, analytics de counterpicks, comfort y
  sinergias, reports y pipelines bronze/silver/gold.
- Nuevos adapters en `src/riot_lol_cli/meta_scraper/adapters/esports/`:
  Leaguepedia, Oracle's Elixir, Gol.gg y Data Dragon activos; Riot Tournament
  V5, GRID, PandaScore, Abios, LoL Esports VODs y Game Client Local como stubs.
- Nuevo router `src/riot_lol_cli/meta_api/routes/esports.py` bajo
  `/api/v1/esports/*`, integrado al Meta API `:8000`, con regla de `200 + gaps`
  si falta storage o fuente.
- Nueva surface `/esports/` con 6 paginas vanilla usando Pattern Library v2:
  overview, drafts, teams, players, counterpicks y tournaments.
- Home Hub actualizado para abrir Esports Research como surface del Meta API.
- Documentacion nueva en `docs/esports_research/` y mapas actualizados en
  `AGENTS.md`, `docs/README.md`, `projects/README.md` y
  `docs/meta_analyzer/README.md`.

### Compliance

- Sin endpoints de asistencia en vivo.
- VODs solo metadata; no descarga ni rehosting.
- Gol.gg respeta robots.txt y `min_delay >= 4s`; Leaguepedia usa
  User-Agent identificable con email de contacto y `min_delay >= 2s`.
- Stubs comerciales/oficiales quedan desactivados hasta contrato, token o
  production key.

### Verificacion

- `pytest tests/esports_research -q` -> 126 passed.
- Ruff parcial de archivos nuevos ejecutado durante implementacion y corregido.

---

## [2026-05-15] Patch Notes — Mobalytics Breakdown + hardening UTF-8

### Que se hizo

**1. Mobalytics Patch Notes Breakdown como nueva fuente de enrichment:**
- Adapter nuevo: `src/riot_lol_cli/patch_notes/adapters/mobalytics_breakdown.py`
  (Playwright, scrapea `mobalytics.gg/lol/guides/patch-notes-breakdown`)
- Constante `SOURCE_MOBALYTICS_BREAKDOWN` agregada a `messages.py` y a
  `_PER_PATCH_SOURCES` en `orchestrator.py` (corre como enrichment por patch).
- Seed del breakdown 26.10 desde markdown ingerido en
  `data/patch_notes/sources/mobalytics_breakdown/26.10.json` y adjunto al
  `PatchNote` canónico via `enrichments[]`. Script: `scripts/seed_mobalytics_breakdown.py`.
- UI: `buildSourceCard()` en `static/app.js` ahora detecta `content_markdown`
  en el payload y lo renderiza como texto formateado en lugar de JSON crudo.

**2. Formato de fechas en UI:**
- `formatDate()` y `timeAgo()` en `static/app.js` reemplazados por formato
  corto `DD mmm, HH:MM` (ej: `15 may, 09:54`). Aplica a card hero, freshness
  chip y meta de cada source. Reemplaza el viejo "Actualizado hace X días".

**3. Hardening UTF-8 (incidente y fix):**

Mojibake apareció en el frontend ("o-con-tilde" se rompía en pantalla). Root
cause fueron 3 fallos simultáneos:

1. PowerShell `Out-File -Encoding UTF8` agregó BOM a JSON intermedios.
2. PowerShell legacy leyó strings UTF-8 como Latin-1 y re-codificó →
   doble-encoding en disco (bytes UTF-8 de un caracter terminaron como bytes
   UTF-8 de la representacion Latin-1 de ese caracter, 4 bytes en lugar de 2).
3. FastAPI por defecto sirve `application/json` sin `charset=utf-8`, navegador
   asume Latin-1.

Fix aplicado:
- `UTF8JSONResponse` class en `patch_notes/server.py` con
  `media_type = "application/json; charset=utf-8"`, usada como
  `default_response_class` en `create_app()`.
- Script `scripts/fix_double_encoding.py` con tabla de reemplazos para
  revertir mojibake (no usa `latin-1.encode()` porque rompe con caracteres
  Unicode legítimos como `⇒`).
- Tests preventivos en `tests/patch_notes/test_encoding.py` (5 tests):
  no BOM en JSON, no doble-encoding, charset en headers HTTP, payload
  Mobalytics intacto, respuestas sin bytes corruptos.

**4. Documentación:**
- `.agent/rules/engineering-standards.md` § "Encoding y mojibake" expandido
  con los 3 modos de fallo, soluciones y guards.
- `AGENTS.md` § "Reglas de Codificación (JSON, UTF-8)" nueva.
- Memoria `feedback_utf8_no_bom.md` actualizada con incidente y patrones.

### Verificación

- `pytest tests/patch_notes/test_encoding.py -v` → 5 passed.
- `python scripts/visual_smoke.py http://localhost:8005/#patch/26.10
  --width 1920` → screenshot HD muestra tildes correctas en todo el patch.
- Servidor responde `Content-Type: application/json; charset=utf-8`.

---

## [2026-05-15] Patch Notes — V3 roadmap documentado, stand-by hasta nuevo aviso

### Que se hizo

Creado `projects/active/patch-notes/V3_ROADMAP.md` con las próximas iteraciones
planificadas para el subsistema. El documento agrupa 19 items en 6 prioridades:

- **P1 Cierre V2** (4 items): disclaimer legal Riot, cron UI, markdown.new
  fallback, inline champion enrichment.
- **P2 Features visuales** (4 items): item icons inline, rune icons, patch
  impact score, filtros en diff.
- **P3 Integración cross-subsistema** (3 items): cross-link a draft_advisor,
  tier shift indicator, pro picks tracker (reusa jungle_research).
- **P4 Stitch-driven design** (3 items): mobile refinement, patch summary
  view, "what's new" digest.
- **P5 Infraestructura** (3 items): audit log, métricas de salud, migración
  async Playwright.
- **P6 Exploratorias** (5 items): push notifications, voice search, export
  PDF, light mode, video walkthroughs.

Cada item incluye problema que resuelve, alcance (XS/S/M/L/XL), dependencias,
risk y ROI estimado. Propone dos sprints concretos (V3.0 "Iconografía completa"
y V3.1 "Operabilidad") para cuando se reactive.

Cross-links agregados en `projects/active/patch-notes/README.md` para que el
roadmap aparezca junto a `DESIGN.md` y `deep-research-report.md`.

### Estado al cierre

- V2.5 corriendo en `:8005` con `version: "2.2.0"` visible en el hero.
- 16 patches scrapeados (26.10 al 25.12, es-es).
- 7 adapters operativos.
- 65 tests verdes, ruff clean.
- Documentación completa: README, DESIGN.md, V3_ROADMAP.md, deep-research-report.md.

**Stand-by hasta nuevo aviso.** Cuando se reactive, abrir `V3_ROADMAP.md`,
elegir item, ejecutar.

---

## [2026-05-15] Patch Notes V2.5 — version pill UI + lifespan + riot_calendar Playwright

### Que se hizo

Tres fixes que cerraban los items pendientes del roadmap V2.5:

**1. Version pill en el hero**
- `SUBSYSTEM_VERSION = "2.2.0"` declarado en `server.py`, expuesto por `/health`.
- `index.html`: agregado `<span class="version-pill" data-bind="app_version">` en el
  hero junto al texto "FUENTE OFICIAL".
- `app.js`: nuevo `loadHealth()` que cachea la respuesta de `/health` y lo binde
  al pill como `v2.2.0`. Se carga en paralelo a `loadList()`.
- `styles.css`: nueva clase `.version-pill` con border arc-gold-dark, tint gold 10%,
  font-mono caption — discreto pero visible.
- Cache buster: `?v=4` en `app.js` y `styles.css`.

**2. Migración `on_event` → `lifespan` (FastAPI)**
- FastAPI marca `@app.on_event("startup"|"shutdown")` como deprecated.
- Reemplazado por `@asynccontextmanager async def _lifespan(app)` que ejecuta:
  - Pre-yield: `build_index()` + APScheduler opcional.
  - Post-yield: `shutdown_scheduler(_scheduler)`.
- `create_app()` pasa `lifespan=_lifespan` al constructor de `FastAPI()`.
- Resultado: `taskkill` ya no muestra `DeprecationWarning` al arrancar.

**3. Fix `riot_calendar` 403 con Playwright**
- El Zendesk de `support.leagueoflegends.com` rechazaba httpx incluso con UA real.
- Cambiado el adapter a `Playwright` (mismo patrón que `lol_official`):
  - `_ensure_playwright()` lazy + `service_workers="block"`.
  - `page.goto(_CALENDAR_URL)` + `page.wait_for_timeout(2000)`.
  - `page.evaluate()` que extrae texto de `tr/li/p` con regex de versión+fecha.
- Como ya está integrado en el orchestrator con cierre temprano por adapter,
  esto no rompe el slot Playwright para los demás enrichments.

### Verificación visual

**Smoke #1 — Overview**: hero muestra `FUENTE OFICIAL` + pill `v2.2.0` + freshness
chip cyan + 16 patches cards. Search bar visible, sin locale toggle (V2.2 lo eliminó).

**Smoke #2 — Detail 26.10**: pills `VERSIÓN 26.10` + `12 DE MAY DE 2026` +
`FUENTE OFICIAL ↗` + `7 FUENTES`. Tab bar Hextech con "Notas oficiales" / "Por fuente".
TOC sticky con anchors funcionales (fix de slug consistente aplicado en V2.2).

**Smoke #3 — Search "aatrox"**: 2 resultados con highlighting `<mark>` gold sobre
fondo dorado tenue. Cards con version + locale pills + section path + snippet
+ CTA "Ver parche →".

**Smoke #4 — Diff 26.10 vs 26.9**: pills `26.10` vs `26.9` + summary `+83 / −55 / ~28`.
Legend chips + cards con border-left color-coded (verde añadido, rojo eliminado,
gold modificado). Columnas "Antes" / "Después" lado a lado.

### Tests + lint

- Ruff: clean en `src/riot_lol_cli/patch_notes`.
- 65 tests V2 pasan.
- Server startup output **sin warnings de `on_event`** (migración limpia).
- Health endpoint reporta `version: "2.2.0"` correctamente.

---

## [2026-05-15] Patch Notes V2.2 — español-only + scroll-to-top transversal + visual enrichment + DESIGN.md Stitch

### Que se hizo

**1. Eliminación multi-locale (español-only)**
- La fuente de verdad pasa a ser **únicamente `es-es`** de `leagueoflegends.com`.
- Removido del UI: `locale-toggle` (botones ES-ES/ES-MX/EN-US), tab "Comparar locales".
- `messages.py`: `SUPPORTED_LOCALES = ("es-es",)`.
- `app.js`: removido `state.locale`, `setLocale`, `LOCALES`, `LOCALE_LABELS`, `fillLocalesPanel`, `buildLocaleColumn`. Constante `LOCALE = "es-es"` global.
- `parseRoute()` acepta legacy hash `#patch/26.10|es-es` por compatibilidad pero genera links nuevos sin locale (`#patch/26.10`).
- `styles.css`: removidos `.locale-toggle`, `.locale-btn`, `.locales-grid`, `.locale-col*`.

**2. Fix bug TOC anchors**
- Bug reportado: clicks en links de tabla de contenidos no scrolleaban a la sección.
- Causa: el slug generado por `fillOfficialPanel` para subsecciones (`${idx}-sub-${sIdx}`) no coincidía con el slug generado por `buildSectionNode` (`${parentSlug}-${idx}`).
- Fix: usar el mismo formato `${slug}-${sIdx}` en ambas funciones.

**3. Visual enrichment con Data Dragon**
- Champion icons inyectados en H3 cuando el título matchea un champion canónico
  (Aatrox, Anivia, Bel'Veth, K'Sante, etc.). Mapping por normalización
  (lowercase + sin acentos/apóstrofes/espacios).
- Ability icons (P/Q/W/E/R) inyectados en H3/H4 que empiezan con "Q -", "W -", etc.
  Fetch lazy del JSON de spells del campeón (`champion/{id}.json`).
- Fetch directo desde `ddragon.leagueoflegends.com` CDN (CORS-friendly).
- Clases nuevas: `.champion-heading`, `.champion-heading__icon` (56x56),
  `.ability-heading`, `.ability-heading__icon` (36x36).

**4. Scroll-to-top transversal**
- Nuevo componente del design system canónico:
  - `src/riot_lol_cli/draft_advisor/static/design-system/scroll-to-top.js`
    — auto-init, aparece al scrollear > 320px, expone `window.LOLCLI_ScrollToTop.refresh()`.
  - `components.css` extendido con clases `.scroll-to-top` + `.scroll-to-top--visible`.
- Integrado en `patch_notes/static/index.html` (cargado vía
  `<script src="/design-system/scroll-to-top.js">`).
- **Pattern transversal**: queda disponible para integrarse en todos los
  frontends del repo. Para roll-out completo agregar el `<script>` en
  jungle_meta, items_browser, meta_scraper, draft_advisor y home/static.

**5. DESIGN.md para Google Stitch**
- Nuevo archivo `projects/active/patch-notes/DESIGN.md` siguiendo la guía
  `Google_Stitch_DESIGNmd_Guia.pdf` provista por el usuario.
- Estructura: YAML frontmatter con tokens (colors, typography, spacing, rounded,
  elevation, motion, layout, components) + body markdown con Overview, Colors,
  Typography, Layout, Elevation, Shapes, Components, Do's/Don'ts, plantillas de
  prompts para Stitch (nueva pantalla / refinar / consistencia).
- Hereda todos los tokens canónicos de `tokens.css`. Documenta los componentes
  V2.2 (`champion-heading`, `ability-heading`, `scroll-to-top`, freshness chips).
- Sirve como **fuente de verdad reutilizable** para que Stitch genere propuestas
  alineadas con el lenguaje Hextech del repo.

### Verificación

- Ruff: clean en `src/riot_lol_cli/patch_notes` + `tests/patch_notes`.
- Tests V2 patch_notes: **65 passed** en 0.59s.
- Server V2.2 levantado en :8005 con health response que reporta `version: "2.0.0"`,
  `patch_count: 16`, `scraper_available: true`.
- Visual smoke overview: confirma ausencia de locale toggle, search bar visible.
- Visual smoke detail 26.10: tab bar muestra solo "Notas oficiales" y "Por fuente";
  H3 "Ambessa" arranca con placeholder del icon de Data Dragon (carga async — en
  browser real ya carga el icon completo).
- Curl a `ddragon.leagueoflegends.com/cdn/16.9.1/img/champion/Ambessa.png` → 200 OK 20KB.

---

## [2026-05-15] Patch Notes V2.1 — fix regex URL para parches >= 26.4

### Que se hizo

Detectado que Riot cambió el slug de los URLs de patch notes a partir de la
versión 26.4: antes era `/news/game-updates/patch-26-3-notes`, ahora es
`/news/game-updates/league-of-legends-patch-26-10-notes` (con prefijo
`league-of-legends-`).

Mi regex `_PATCH_URL_PATTERN` en `adapters/lol_official.py` solo matcheaba el
formato viejo, así que el discover encontraba 12 URLs en el DOM pero filtraba
las 7 nuevas (26.4-26.10) y solo retornaba 3 (26.1-26.3).

### Fix aplicado

```python
_PATCH_URL_PATTERN = re.compile(
    r"/news/game-updates/(?:league-of-legends-)?patch-(\d+)-(\d+)([a-z]?)-notes",
    re.IGNORECASE,
)
```

El `(?:league-of-legends-)?` opcional acepta ambos formatos sin romper compat con los parches viejos ya en disco.

### Verificación

Tras re-scrape con `max_patches=10&locales=es-es`:
- Descubrió **10 URLs** (antes 3).
- Persistió 26.10 (14 secciones), 26.9, 26.8, etc.
- Patch 26.10 confirmado por el usuario como el actual en producción.

---

## [2026-05-15] Patch Notes V2 — multi-source + búsqueda + diff + cron + tabs UI

### Que se hizo

Expansión completa V2 del subsistema `patch_notes`:

**Backend multi-source (7 adapters):**
- `lol_official` (canónico, Playwright) — existente.
- `lol_dev.py` (Playwright) — scraping del dev blog.
- `riot_calendar.py` (httpx + BeautifulSoup) — calendario oficial.
- `ddragon.py` (httpx puro) — versiones técnicas.
- `ugg_patch.py`, `opgg_patch.py`, `lolalytics_patch.py`, `mobalytics_patch.py` (Playwright)
  — snapshots por patch de los sitios comunitarios.

**Schema V2 extendido:**
- `PatchEnrichment` — payload por fuente con `content_hash` + `error` opcional.
- `SearchHit` — resultado FTS con `section_path`, `snippet`, `score`, `section_anchor`.
- `DiffSection` + `PatchDiff` — comparación recursiva sección-por-sección.
- `PatchNote.enrichments[]` agregado (backwards-compatible via `extra="ignore"`).

**Nuevos módulos:**
- `search.py` — índice in-memory TF-IDF simple sin dependencias, AND lógico, snippet ±80 chars.
- `diff.py` — matching por título normalizado (NFD + lowercase), recursivo, taggea added/removed/modified/unchanged.
- `scheduler.py` — APScheduler opcional vía `LOLCLI_PATCH_NOTES_CRON_ENABLED=1`.

**Orchestrator multi-fase:**
1. Phase 1 — canonical scraping del oficial multi-locale.
2. Phase 2 — enrichments globales (calendar + ddragon).
3. Phase 3 — enrichments per-patch (dev + 4 comunidad).
4. Phase 4 — manifest `sources_status` update.
- Tolerancia a fallos: cada error queda en `PatchEnrichment.error` sin bloquear el flujo.

**Server V2 — 10 endpoints REST:**
- `/health` ahora incluye `version`, `search_index`, `cron_enabled`.
- Nuevos: `/sources/registry`, `/{v}/sources`, `/{v}/sources/{src}`, `/search`, `/diff/{a}/{b}`, `/scrape/{source}`.
- Startup hook reconstruye el índice. Scheduler opcional.
- **Fix importante**: el scrape se ejecuta en `threading.Thread`, no en `BackgroundTask` de FastAPI, porque Playwright sync API no tolera el event loop asyncio activo.

**Frontend V2 (SPA con design system):**
- Hero con freshness chip ("Actualizado hace X días") con 3 niveles (fresh/stale/cold).
- Multi-locale toggle persistido en `localStorage` (es-es/es-mx/en-us).
- Search input visible en overview con submit → ruta `#search?q=`.
- Tab bar en detail: `[Notas oficiales] [Por fuente] [Comparar locales]`.
- Tab "Por fuente": accordion `<details>` con payload pretty-printed + error chip.
- Tab "Comparar locales": grid de 3 columnas con preview de cada locale.
- Vista diff (`#diff/{a}/{b}`): columnas Antes/Después con badges color-coded.
- Vista search (`#search?q=`): cards con snippets + `<mark>` highlighting + locale pill.

**Calidad:**
- `requirements.txt`: agregadas `apscheduler>=3.10` y `beautifulsoup4>=4.12`.
- 65 tests V2 en `tests/patch_notes/` (schema + normalizer + loader + search + diff + enrichments + adapters_smoke).
- Suite completa: 367 tests pasan sin regresiones.
- Ruff: clean.

### Limitaciones documentadas (V2.5)

1. **DDragon `versions.json`**: tiene entradas legacy (`lolpatch_7`, `lolpatch_3.10`)
   que no parsean como float — el adapter ahora las skipea con try/except (corregido durante el scrape real).

2. **Riot Calendar 403**: el Zendesk de support.leagueoflegends.com bloquea con
   user-agents minimalistas. Mitigado agregando UA real + Referer en el adapter.
   Si sigue fallando, usar `markdown.new` como fallback V2.5.

3. **Playwright sync en asyncio**: FastAPI `BackgroundTasks` mantienen el loop
   activo aunque la función sea sync, y Playwright sync detecta el loop y rechaza
   el segundo `start()`. **Fix aplicado**: cambiar a `threading.Thread(daemon=True)`
   en los endpoints `/scrape` y `/scrape/{source}` para que el scrape corra en su
   propio thread con su propio event loop limpio.

4. **Adapters comunitarios y markup volátil**: U.GG/OP.GG/Mobalytics no exponen
   URLs históricas por patch — scrapeamos el snapshot actual y lo tageamos con
   `patch_label_active`. Si el sitio cambia DOM, `payload={}` + `error` y el
   patch sigue mostrando lo que sí funcione.

5. **`on_event` deprecated**: FastAPI sugiere migrar a `lifespan` context manager.
   No es crítico ahora; queda para V3.

### Scrape end-to-end

Disparado `POST /api/v1/patch-notes/scrape?max_patches=3&locales=es-es` con éxito:
- Canónico: 3 patches nuevos (26.1, 26.2, 26.3) + 6 seedeados (25.12-25.17) = 9 patches en total.
- DDragon, Riot Calendar y comunitarios funcionan en el thread separado tras el fix.
- Índice FTS reconstruido: ~5000 tokens, ~1400 bloques indexados post-scrape.

---

## [2026-05-15] Patch Notes — rediseño completo a subsistema activo del paquete

### Que se hizo

Implementé el rediseño completo del proyecto Patch Notes siguiendo el `deep-research-report.md`
en `projects/active/patch-notes/`. El subsistema ahora vive como módulo Python en
`src/riot_lol_cli/patch_notes/` y comparte el design system canónico del repo.

**Nuevo módulo `src/riot_lol_cli/patch_notes/`**:
- `schema.py` — Pydantic V2: `PatchNote`, `PatchSection` (recursiva), `PatchAsset`, `PatchNoteIndex`, `PatchManifest`.
- `normalizer.py` — `compute_content_hash()` (sha256 estable), `save_normalized()`, `update_manifest()`, `detect_change()`. Persistencia en `data/patch_notes/normalized/by_patch/{version}_{locale}.json` + `history/`.
- `loader.py` — API-side: `list_patches(locale)`, `load_patch(version, locale)`, `load_manifest()`.
- `adapters/base.py` — `PatchNotesAdapterBase` con rate limit humanizado, user-agent pool, retries.
- `adapters/lol_official.py` — Playwright sync: discovery vía índice por tags + click en "Ver más"; extracción vía `page.evaluate()` con JS recursivo que arma H2 → H3 → H4 + bloques P/LI + imágenes + links.
- `orchestrator.py` — pipeline discover → extract → hash → detect_change → persist + update manifest.
- `server.py` — FastAPI factory canónico en **puerto 8005**, monta `/design-system`, expone `/health`, `/api/v1/patch-notes/list`, `/{version}`, `/manifest`, `/scrape`.
- `static/index.html + app.js + styles.css + favicon.svg` — SPA con hash router (`#overview`, `#patch/{version}|{locale}`), templates clonables, design system canónico (`hero --dual`, cards, pills, TOC sticky).

**Integración**:
- `settings.py`: agregadas funciones `get_patch_notes_host/port()` con env vars `LOLCLI_PATCH_NOTES_*`.
- `home/server.py`: registrado en `SERVICES` y `_LAUNCH_CMDS` con icono 📝 y accent gold.

**Datos iniciales**:
- `scripts/seed_patch_notes_from_legacy.py` convierte los 6 parches del JSON v33b legacy
  al nuevo schema (es-es). El frontend arranca con contenido visible desde el primer commit.

**Tests** (`tests/patch_notes/`): 22 tests unitarios cubriendo schema, hash determinístico,
save_normalized + history, update_manifest (idempotente y replace-same-key), detect_change,
list_patches con orden desc, filtros por locale, preferencia es-es cuando no hay filtro.

### Verificación

- `pytest tests/patch_notes -q` → 22 passed
- `pytest tests/` → 324 passed (sin regresiones)
- `ruff check` → all clean
- `python scripts/seed_patch_notes_from_legacy.py` → 6 parches escritos
- `python -m riot_lol_cli.patch_notes.server` + `curl http://localhost:8005/health` →
  `{"status":"ok","patch_count":6,"locales":["es-es"],"scraper_available":true}`
- Visual smoke: overview muestra hero gold "PATCH NOTES" + grid de 6 cards con versión, fecha y resumen. Detalle muestra TOC sticky + jerarquía H2 (gold) / H3 (cyan).
- Home Hub `/api/v1/home/status` reporta `patch_notes` como `online` en `:8005`.

### Por que

El prototipo legacy era PowerShell standalone + HTML aislado. El deep research propuso
una arquitectura robusta: Playwright + DOM semántico + hash de cambios + schema normalizado.
Movimos todo al paquete Python para tener tests, Pydantic, FastAPI y reutilización del
design system canónico (`tokens.css` + `patterns.css`), siguiendo el patrón de `jungle_meta`.

### V2 pendiente (data ya disponible)

- UI multi-locale toggle (es-es/es-mx/en-us — backend ya scrapea los 3).
- Búsqueda full-text sobre `sections.blocks`.
- Vista diff entre versiones usando `content_hash` y schema completo.
- Cron automático para disparar `/scrape` periódicamente.
- Disclaimer legal de Riot en el footer (TODO V1.5 antes de publicar externamente).

---

## [2026-05-15] Reactivación de proyectos legacy: Patch Notes Viewer y CLI Match History

### Que se hizo

**Patch Notes Viewer** — reactivado desde dos carpetas legacy:
- `projects/legacy/patch-notes-scraper-v33a/` y `projects/legacy/patch-notes-web-v33b/`
  fueron unificados en `projects/active/patch-notes/` con estructura limpia:
  `scraper/`, `web/`, `data/`, `logs/`.
- Se copió el scraper PowerShell (v33b, versión con mejor manejo de errores),
  el frontend HTML y el JSON de datos.
- README completo escrito cubriendo: estructura, cómo ejecutar, formato de datos,
  fuentes scrapeadas, deuda técnica y roadmap de refactor con opciones abiertas
  (scraping Python vs PS, JSON estático vs FastAPI, standalone vs integrado al Hub).

**CLI Match History** — reactivado con README exhaustivo:
- `projects/active/cli-match-history/README.md` reescrito completamente.
- Cubre: APIs externas (Account-V1, Summoner-V4, Match-V5, Data Dragon), rutas runtime,
  flujo de datos, comandos, plataformas soportadas, deuda técnica y roadmap de refactor
  con opciones abiertas (HTML estático vs FastAPI, cache JSON vs SQLite, separación de capas).

**Documentación sincronizada:**
- `projects/README.md`: Patch Notes Viewer agregado a la tabla de proyectos activos;
  legacies actualizados como "referencia histórica supersedida".
- `AGENTS.md`: Patch Notes Viewer agregado al mapa de proyectos; descripción de legacy actualizada.

### Por que

Ambos proyectos tenían código funcional y una idea clara pero estaban enterrados en
`legacy/` sin documentación que permita retomarlo. El objetivo es dejarlos listos para
una sesión de refactorización de estrategia y visual sin tener que redescubrir el estado.

---

## [2026-05-12] Docs — inventario de fuentes externas de datos en AGENTS.md

### Que se hizo

Agregada sección "Fuentes Externas de Datos" en `AGENTS.md` con el inventario
consolidado de todas las URLs y fuentes web que el proyecto consume o planea
consumir:

- **APIs Oficiales Riot**: Developer Portal, Platform/Regional endpoints, Data Dragon CDN, Riot Static Content — con los endpoints DDragon específicos que usa `api.py`.
- **Meta Scraper — Fuentes Activas (V1)**: OP.GG, LoLalytics, U.GG, con URLs exactas, roles scrapeados, técnica y archivo adapter.
- **Meta Scraper — Fuentes Planeadas (Stubs)**: METAsrc, Mobalytics, League of Graphs, Tracker.gg, con prioridad y notas operativas.

### Por que

No había un punto único donde un agente (o desarrollador) pudiera ver de un vistazo qué fuentes web usa el proyecto. La información estaba dispersa entre docstrings de adapters, comentarios de código y README de subsistemas.

---

## [2026-05-12] Jungle Research V3 - Adapters SoloQ extra (chasis + telemetria)

### Que se hizo

Capa de redundancia de fuentes SoloQ. Hoy si Meta Scraper falla en
U.GG/LoLalytics, el sistema queda con 1 fuente. V3 entrega los 4 adapters
nuevos del set (METAsrc, Mobalytics, League of Graphs, Tracker.gg) como
**chasis completo + telemetria funcional**, pero el extract real de cada
adapter queda como activacion manual por adapter cuando el operador haya
verificado el markup actual contra la pagina en vivo.

**Razon del approach**: implementar scraping ciego sin validar contra cada
sitio es invitar bugs silenciosos, banear cuentas o pisar markup que cambio.
Mejor entregar la interfaz lista, los logs visibles, y dejar la activacion
como decision explicita.

V3.1-V3.4: 4 adapters nuevos en `src/riot_lol_cli/meta_scraper/adapters/`:

- `metasrc.py` (HTML estatico, complejidad baja) - estrategia parse del SSR.
- `mobalytics.py` (SPA, requiere Playwright) - rate limit conservador 5-10s.
- `leagueofgraphs.py` (HTML estatico, rate limit estricto) - min_delay 8s.
- `tracker_gg.py` (SPA + XHR posibles) - prioridad mas baja del set V3.

Cada adapter hereda de `BaseAdapter`, expone `platform_name` y las 3 fetches
canonicas. Hoy retornan `status=not_implemented` con razon clara (instrucciones
exactas para activar cada uno). Cero llamadas de red en V1.

V3.5: pipeline `jungle_research/pipelines/meta_soloq_extra.py` que orquesta
los 4 adapters. Por cada uno: invoca, captura excepciones (mark como `error`),
agrega snapshots si `status=ok`, persiste telemetria en
`data/meta_analyzer/jungle_research/adapter_runs.json` con merge historico
(no pisa runs de adapters que no se invocaron en esta corrida).

V3.6: telemetria expuesta:

- `GET /api/v1/jungle-research/sources` ahora enriquece cada source con
  `last_attempted_at`, `last_run_status`, `last_run_reason`,
  `last_run_champion_count` cuando hay datos en `adapter_runs.json`.
- Sub-vista Fuentes del cockpit: nueva columna "Ultimo run" con badge de
  status colored (ok=verde, not_implemented=gris, error=rojo), timestamp
  local, tooltip con la razon completa. Boton "Probar adapters V3" en el
  header dispara `POST /refresh?mode=soloq_extra`.

Endpoint `POST /api/v1/jungle-research/refresh` acepta nuevo modo
`soloq_extra` (solo adapters V3) y `all` los incluye automaticamente.

V3 cerrado parcialmente: el chasis esta completo, los 4 extracts reales
quedan como activaciones futuras 1 a 1. Cuando se active uno (ej. METAsrc),
solo hay que reemplazar `_stub_response()` por `parse_html()` real; toda
la cadena (pipeline, telemetria, UI) ya consume el output.

### Verificacion

- `pytest -q` -> 302 passed (12 nuevos del V3: 6 pipeline + 4 adapter
  sanity + 2 routes).
- `ruff check src tests scripts` -> All checks passed.
- Smoke API:
  - `POST /api/v1/jungle-research/refresh?mode=soloq_extra` -> 200
    con `extra_snapshots=0` (stubs) + 4 runs con `status=not_implemented`.
  - `GET /api/v1/jungle-research/sources` despues del refresh -> los 4
    adapters V3 traen `last_attempted_at` + `last_run_status: not_implemented`.
- Smoke visual `#jungle-research/jr-sources` -> tabla con columna "Ultimo
  run" mostrando la telemetria de los 4 adapters V3 en gris, resto del
  registry vacio (sin invocaciones).

### Decisiones clave

- **Stubs en lugar de scraping ciego**: cada adapter expone `_stub_response`
  con instrucciones exactas en `_NOT_IMPLEMENTED_NOTE` para activar.
  Trade-off: V3 no agrega snapshots reales hoy, pero deja el camino limpio
  y testeado para hacerlo seguro.
- **Telemetria con merge historico**: una corrida que solo invoca a
  Mobalytics no debe pisar el last_run de METAsrc.
- **Pipeline import lazy**: `_default_adapters()` importa solo cuando se
  llama (no en import del modulo) para que los tests del pipeline puedan
  mockear sin tocar Playwright.

### Archivos creados

- `src/riot_lol_cli/meta_scraper/adapters/metasrc.py`
- `src/riot_lol_cli/meta_scraper/adapters/mobalytics.py`
- `src/riot_lol_cli/meta_scraper/adapters/leagueofgraphs.py`
- `src/riot_lol_cli/meta_scraper/adapters/tracker_gg.py`
- `src/riot_lol_cli/jungle_research/pipelines/meta_soloq_extra.py`
- `tests/jungle_research/test_pipeline_meta_soloq_extra.py` (6 tests)
- `tests/jungle_research/test_adapters_v3.py` (4 tests)

### Archivos modificados

- `src/riot_lol_cli/jungle_research/json_storage.py` -> agrega
  `ADAPTER_RUNS_FILE` + `read_adapter_runs()` + `save_adapter_runs()`.
- `src/riot_lol_cli/meta_api/routes/jungle_research.py` -> modo
  `soloq_extra` en `/refresh` + enriquecimiento de `/sources` con
  telemetria.
- `src/riot_lol_cli/dashboard_enhanced.py` -> nueva columna "Ultimo run"
  en sub-vista Fuentes + boton "Probar adapters V3" + render con badges
  coloreados.
- `outputs/meta-analyzer-dashboard-enhanced.html` -> regenerado.
- `tests/jungle_research/test_routes.py` -> 2 tests nuevos
  (refresh soloq_extra + sources con telemetria) + mock de
  ADAPTER_RUNS_FILE en fixture.
- `docs/meta_analyzer/jungle-research-roadmap.md` -> marca V3 done en
  modo chasis.
- `bitacora_de_cambios.md` -> esta entrada.

---

## [2026-05-12] Jungle Research V2 - Apertura del registry de pros + fix bug sub-tabs

### Que se hizo

V2.1+V2.2: documentacion del formato `riot_id` (`"GameName#TAG"`) + lista
canonica de servers en `pro_players_seed.json` via campo `_format_help`.
**No** se cargaron Riot IDs hardcoded — son volatiles y publicos pero no
verificables sin contacto directo. El usuario los carga via UI o endpoint.

V2.3: nuevo endpoint `POST /api/v1/jungle-research/pros/{name}/account` con
body `{riot_id, server}`. Valida formato, persiste el seed con escritura
atomica preservando el resto del JSON, y dispara resolucion via `RiotBridge`
si hay `RIOT_API_KEY`. Si no hay key, marca `gap_flag: no_riot_key` y queda
listo para resolver al rotar la key.

V2.3 lateral: nuevo endpoint `GET /api/v1/jungle-research/pros` que devuelve
seed + estado por jugador (riot_id, server, puuid, gap_flag, last_seen_at).
Reemplaza el approach previo de inferir desde `pro_accounts.json` solo.

V2.4: sub-vista Pros del cockpit reescrita. Cards muestran resolucion real
(verde si PUUID, amarillo si pendiente, rojo si error). Cada card tiene un
`<details>` con form para editar Riot ID + select de servers (KR/EUW/NA/...).
Botones "Guardar" y "Limpiar". Mensajes inline de exito/error sin recargar.

Bug fix lateral: hash hook anidado (`#jungle-research/jr-sources`) no
activaba el primary tab correctamente. Causa raiz: el handler `switchTab`
original usa `document.querySelectorAll('.tab')` que tambien matchea los
sub-tabs internos (.tab dentro de #jungle-research), generando state cruzado.
El simulado `subBtn.click()` posterior ejecutaba `jrSwitchSubtab` cuyo
`event.currentTarget.classList.add('active')` daba la apariencia de
sub-tab activo, pero quedaba con primary tab "Dashboard" highlighted.

Fix: nuevo helper `jrActivateView(primaryTabId, subtabId)` que setea state
directamente sobre los elementos correctos sin pasar por handlers de click.
Limita el scope de las queries (`.container > .tabs` para primary, dentro
del container para sub) y elimina race conditions. El hash hook lo usa.

V2.5+V2.6+V2.7 (auto-refresh, persist pro_recent_picks, ultimos picks por
jugador) quedan para V2.b — requieren cron/scheduler, primero conviene
estabilizar el camino manual de V2 y validar con uso real.

### Verificacion

- `pytest -q` -> 290 passed (10 nuevos tests del V2: 6 de set_pro_account
  + 4 de endpoints).
- `ruff check src tests scripts` -> All checks passed.
- Smoke API:
  - `GET /api/v1/jungle-research/pros` -> 200, 11 jugadores, 0 resolved.
  - `POST /api/v1/jungle-research/pros/Canyon/account` con
    `{"riot_id": "DK Canyon#KR1", "server": "KR"}` -> 200,
    `updated: true`, `gap_flag: no_riot_key` (sin key).
  - Re-`GET /pros` muestra el campo riot_id persistido.
- Smoke visual `http://localhost:8000/dashboard-enhanced#jungle-research/jr-pros`
  -> tab principal "Jungla 360" activo (bug fixed), sub-tab Pros activo,
  banner key absent visible, 11 cards con form colapsable + tier badges
  S/A/B + estado pendiente.

### Archivos modificados

- `src/riot_lol_cli/jungle_research/pipelines/pro_accounts.py` -> agrega
  `set_pro_account()` con upsert atomico y trigger de resolucion.
- `src/riot_lol_cli/meta_api/routes/jungle_research.py` -> 2 endpoints
  nuevos (`GET /pros`, `POST /pros/{name}/account`) + Pydantic body schema.
- `src/riot_lol_cli/dashboard_enhanced.py` -> helper `jrActivateView`
  + reescritura de `jrLoadPros` con cards interactivos + funciones
  `jrSavePro`/`jrClearPro`. Hash hook ahora usa el helper directo.
- `data/meta_analyzer/jungle_research/pro_players_seed.json` -> agrega
  `_format_help` con docs de formato y opciones de resolucion.
- `outputs/meta-analyzer-dashboard-enhanced.html` -> regenerado.
- `tests/jungle_research/test_pipeline_pro_accounts.py` -> 6 tests nuevos
  para `set_pro_account` (validaciones + upsert + clear + no-key).
- `tests/jungle_research/test_routes.py` -> 4 tests nuevos para los
  endpoints de pros.
- `docs/meta_analyzer/jungle-research-roadmap.md` -> marca V2 partially
  done; V2.5-V2.7 quedan en V2.b.
- `bitacora_de_cambios.md` -> esta entrada.

---

## [2026-05-12] Jungle Meta Knowledge Base — capa `jungle_research` en Meta Analyzer

### Que se hizo

Sistema completo para investigar y consolidar el meta de jungla. Vive como
capa nueva dentro de Meta Analyzer (`:8000`). Reusa Meta Scraper (`:8002`)
y Jungle Meta (`:8003`) como fuentes activas, persiste en JSON versionado
bajo `data/meta_analyzer/jungle_research/`, y expone endpoints + tab visual
en `/dashboard-enhanced`.

Implementado en 3 PRs por fases (mergeables independientemente):

**PR1 - backend foundation (storage + registry + scoring + tests):**

- `src/riot_lol_cli/jungle_research/`: modulo nuevo con `schemas.py` (8 modelos
  Pydantic V2 con campos compatibles para migracion futura a SQL),
  `source_registry.py` (read-only sobre `sources.json`), `json_storage.py`
  (snapshots inmutables con rotacion a `backups/` y escritura atomica via
  `.tmp`), `scoring_engine.py` (percentiles por cohorte + 7 pesos del
  `final_score` + 4 pesos del `confidence` + warnings sample_size_low,
  stale_>72h, outlier:metric), `riot_bridge.py` (wrapper sobre `RiotClient`
  con SERVER_ROUTING + gap controlado si falta `RIOT_API_KEY`).
- `data/meta_analyzer/jungle_research/sources.json`: 35 fuentes registradas
  del prompt original. 7 active (Riot API + Data Dragon + Meta Scraper local
  + Jungle Meta local + adapters U.GG/LoLalytics/OP.GG). 28 planned
  (Mobalytics, METAsrc, PORO.GG, FOW, DEEPLOL, Tencent, OP.GG KR/JP/CN,
  TrackingThePros, DPM, Onetricks, GOL, etc.).
- `data/meta_analyzer/jungle_research/pro_players_seed.json`: 11 pros del
  prompt (Canyon, Oner, Peanut, Kanavi, Jankos, XUN, Tian, Blaber, Wei,
  Pyosik, Tarzan) con URLs publicas. `riot_id: null` con flag implicito
  `needs_account_resolution`. La resolucion requiere agregar Riot ID + server
  manualmente al seed antes de correr el pipeline.
- `tests/jungle_research/`: 43 tests (schemas, storage, registry, scoring).

**PR2 - API + V1 pipelines (SoloQ + Riot pros + reportes):**

- `pipelines/meta_soloq.py`: lee `data/meta_scraper/normalized/latest_jungle_tier.json`
  (descompone `source_breakdown` en snapshots por fuente individual) +
  `data/jungle_meta/patch_*.json` (capa `curated_local`). Persiste con rotacion.
- `pipelines/pro_accounts.py`: resuelve PUUID solo si seed tiene `riot_id` +
  `RIOT_API_KEY`. Cero scraping de TrackingThePros/DPM en V1.
- `pipelines/match_history.py`: descarga ultimas N partidas via Riot match-v5
  para cuentas resueltas. Funcion `recent_pro_picks()` alimenta `pro_presence`
  en scoring.
- `reports/daily_report.py`: top junglers + risers/fallers (compara `latest`
  vs ultimo backup) + contradictions (spread WR > 5pp entre fuentes).
- `meta_api/routes/jungle_research.py`: 11 endpoints bajo
  `/api/v1/jungle-research/*`. Regla central: si una capa de datos no esta
  disponible, devolver 200 con `gaps` visible. Nunca 500 ni inventar datos.
- `meta_api/app.py`: registra `jungle_research_router`.
- 36 tests adicionales (pipelines, daily_report, routes con FastAPI TestClient).

**PR3 - cockpit UI: tab `Jungla 360` en `/dashboard-enhanced`:**

- `src/riot_lol_cli/dashboard_enhanced.py`: tab nuevo en la barra principal con
  5 sub-vistas (Consenso, Fuentes, Pros, OTPs, Reporte diario) + header con
  freshness + patch + estado Riot API + conteo de gaps + botones "Refrescar
  SoloQ" / "Riot Pros". JS llama solo endpoints `/api/v1/jungle-research/*`.
  Hook de URL hash para auto-activar tab desde `#jungle-research` (util para
  smoke visual).
- Fix lateral: comillas tipograficas (U+201D right-double-quote) que alguien
  habia reemplazado en los `class="tab"` de los 4 tabs originales,
  corregidas a comillas rectas para que el HTML las parsee correctamente.
- Regenerado `outputs/meta-analyzer-dashboard-enhanced.html`.

### Causa raiz / decisiones clave

- **Decision: tab dentro del dashboard existente**, no surface nueva. Mantiene
  el cockpit unificado sin sumar puertos. Costo: el `.py` con HTML embebido
  crece, pero cualquier refactor visual de Meta Analyzer ya planea extraer
  esto a static.
- **Decision: Jungle Meta `:8003` coexiste como `curated_local`**. No se
  deprecio. Sigue siendo fuente de fallback del Draft Advisor. Ahora tambien
  es una capa de consenso para Jungle Research.
- **Decision: cero scraping en V1**. TrackingThePros/DPM/Onetricks quedan
  como `planned`. Resolucion de cuentas pro requiere edicion manual del seed
  para agregar `riot_id` + `server` (no se evade nada, no se inventa).
- **Decision: storage JSON versionado, no PostgreSQL todavia**. Los nombres
  de schemas y campos son compatibles con migracion futura a SQL.
- **Decision: `final_score` por percentil dentro de `(patch, role, region,
  elo, queue)`**. No copia ninguna tier list externa. Outliers se conservan
  con `warning_flags`, no se eliminan.

### Verificacion

- `pytest -q` -> 280 passed (79 nuevos en `tests/jungle_research/`).
- `ruff check src tests scripts` -> All checks passed.
- `tests/test_no_mojibake.py` -> verde para todo el path nuevo.
- API smoke end-to-end levantando `:8000`:
  - `GET /api/v1/jungle-research/sources` -> 200, 35 fuentes, 7 active.
  - `POST /api/v1/jungle-research/refresh?mode=soloq` -> 200, consolido 36
    entries de 3 fuentes (lolalytics + ugg + jungle_meta_local), patch 26.9.
  - `GET /api/v1/jungle-research/overview` -> 200, 36 entries, distribucion
    por tier, freshness, riot_api_key_present.
- Smoke visual `python scripts/visual_smoke.py
  http://localhost:8000/dashboard-enhanced#jungle-research` -> PNG mostrando
  tab activo con header (freshness + patch + Riot API gap warning), 5
  sub-tabs y tabla de consenso renderizada.

### Archivos creados

- `src/riot_lol_cli/jungle_research/__init__.py`
- `src/riot_lol_cli/jungle_research/schemas.py`
- `src/riot_lol_cli/jungle_research/source_registry.py`
- `src/riot_lol_cli/jungle_research/json_storage.py`
- `src/riot_lol_cli/jungle_research/scoring_engine.py`
- `src/riot_lol_cli/jungle_research/riot_bridge.py`
- `src/riot_lol_cli/jungle_research/pipelines/__init__.py`
- `src/riot_lol_cli/jungle_research/pipelines/meta_soloq.py`
- `src/riot_lol_cli/jungle_research/pipelines/pro_accounts.py`
- `src/riot_lol_cli/jungle_research/pipelines/match_history.py`
- `src/riot_lol_cli/jungle_research/reports/__init__.py`
- `src/riot_lol_cli/jungle_research/reports/daily_report.py`
- `src/riot_lol_cli/meta_api/routes/jungle_research.py`
- `data/meta_analyzer/jungle_research/sources.json` (35 fuentes)
- `data/meta_analyzer/jungle_research/pro_players_seed.json` (11 pros)
- `tests/jungle_research/__init__.py`
- `tests/jungle_research/test_schemas.py` (12 tests)
- `tests/jungle_research/test_source_registry.py` (8 tests)
- `tests/jungle_research/test_json_storage.py` (12 tests)
- `tests/jungle_research/test_scoring_engine.py` (11 tests)
- `tests/jungle_research/test_pipeline_meta_soloq.py` (7 tests)
- `tests/jungle_research/test_pipeline_pro_accounts.py` (7 tests)
- `tests/jungle_research/test_pipeline_match_history.py` (6 tests)
- `tests/jungle_research/test_daily_report.py` (5 tests)
- `tests/jungle_research/test_routes.py` (12 tests)

### Archivos modificados

- `src/riot_lol_cli/meta_api/app.py` -> registra router nuevo.
- `src/riot_lol_cli/dashboard_enhanced.py` -> tab Jungla 360 + JS + fix de
  smart quotes en tabs originales.
- `outputs/meta-analyzer-dashboard-enhanced.html` -> regenerado.
- `AGENTS.md` -> agrega `jungle_research` al mapa de subsistemas + endpoints
  a la seccion Meta API.
- `docs/meta_analyzer/README.md` -> seccion "Jungla 360 - fuentes y consenso".
- `bitacora_de_cambios.md` -> esta entrada.

---

## [2026-05-11] Guardrails anti-mojibake + smoke visual + minimizacion de rules

### Que se hizo

Sesion nacida de un bug visual del dashboard enhanced que **no se atrapo**
auditando solo HTML/JS/CSS. Fueron necesarias capturas headless de Chrome para
verlo. Resultado: tres cambios estructurales ademas del fix puntual.

**Fix puntual `dashboard_enhanced.py`:**

- Modal siempre visible. Outer div tenia `class="modal"` y `patterns.css` define
  `.modal { display: flex }` siempre, asumiendo que el toggle lo hace
  `.modal-overlay`. Como `patterns.css` carga despues del CSS local, gano la
  cascada y el modal nunca se ocultaba. Fix: outer -> `class="modal-overlay"`,
  inner queda como `.modal-content` (estilos locales).
- 14 mojibake por doble-encoding UTF-8 <-> cp1252 acumulado a traves de
  sesiones de agentes que reescribian el archivo con encoding inconsistente.
  El sintoma visible era texto en espanol y algunos iconos renderizados con
  secuencias corruptas. Fix con script Python que reencodea cada secuencia
  (`segment.encode("latin-1").decode("utf-8")`) mas replacements manuales de
  los emojis 4-byte que el algoritmo no atrapo.
- `row.hour` -> `Invalid Date` en tabla Raw Data; la API devuelve
  `hour_bucket`. Fix: rename de la referencia en el JS.

**Guardrail automatico contra mojibake** (`tests/test_no_mojibake.py`):

- Escanea `src/`, `templates/`, `scripts/`, `docs/`, `outputs/`,
  `projects/active/`, `.agent/rules/` y archivos root relevantes por
  marcadores conocidos de doble-encoding y por BOM en archivos `.py`.
- En esta iteracion tambien se hizo barrido manual read-only sobre
  `projects/legacy/` y `projects/dev-scratch/`; no quedaron hits.
- Forma parte de la suite default de pytest; cualquier regresion rompe CI.

**Helper de smoke visual** (`scripts/visual_smoke.py`):

- Wrapper sobre Chrome `--headless=new --screenshot=...`.
- Maneja path absoluto, user-data-dir aislado, no-first-run.
- Output a `outputs/visual-smoke/<page>.png` lista para abrir con Read tool.
- Uso: `python scripts/visual_smoke.py <URL>`.

**Minimizacion de las 4 rules de `.agent/rules/`:**

- Reducidas a la minima expresion accionable, sin duplicar `AGENTS.md`.
- Agregada seccion "Encoding y mojibake (regla dura)" en
  `engineering-standards.md` con referencia al guard test.
- Agregada seccion "Verificacion visual obligatoria" en
  `engineering-standards.md` y reflejada en checklist de cierre de
  `agent-workflow.md`. Mensaje central: auditar HTML/JS/CSS no es
  suficiente para frontend; siempre cerrar con captura.
- `CLAUDE.md` corregido (decia 3 servidores FastAPI, son 6) + nota sobre
  smoke visual obligatorio para cambios visuales.

### Causa raiz

1. **Modal**: el dashboard nunca actualizo su estructura cuando se aplico
   Pattern Library v2 (la migracion del PR especifico no incluyo este surface
   embebido en `dashboard_enhanced.py`).
2. **Mojibake**: PowerShell `Set-Content -Encoding UTF8` agrega BOM, lecturas
   con encoding equivocado en sesiones anteriores reescribieron el archivo
   con caracteres ya corruptos. **Impide volver a ocurrir**:
   `tests/test_no_mojibake.py` rompe el build ante cualquier regresion.
3. **Proceso**: revisar HTML/JS/CSS en codigo no atrapa cascadas rotas ni
   modales fantasma. **Impide volver a ocurrir**: regla escrita en
   `engineering-standards.md` y `agent-workflow.md`, helper `visual_smoke.py`
   listo para usar, mencion en `CLAUDE.md`.

### Verificacion

- `pytest tests/test_no_mojibake.py -q` -> 2 passed.
- `python scripts/visual_smoke.py http://localhost:8000/dashboard-enhanced`
  -> PNG con hero "META ANALYZER" Anton italic, stat-strip 31/100/9, tier list
  cargada con 23 ADCs en Tier A, **modal cerrado**.

### Archivos creados

- `tests/test_no_mojibake.py` -> guardrail anti-mojibake/BOM.
- `scripts/visual_smoke.py` -> captura headless Chrome para smoke visual.

## [2026-05-11] Draft Advisor - rol Jungla con Jungle Meta como fuente primaria

### Que se hizo
- Se extendio `target_role` con `jungle` y el front de `/draft` ahora permite elegir `Jungla` sin cambiar el default `ADC`.
- Se agrego `jungle_meta_provider.py`: primero consulta `http://localhost:8003/api/v1/jungle/tier-list` y, si Jungle Meta esta offline, cae a `data/jungle_meta/patch_26.09.json` usando el loader local.
- El scoring de Jungla v1 usa Jungle Meta como fuente principal: `S/A` pueden ser top, `B` queda como fallback y `C` solo puede ser top en `pool_only` sin mejores opciones.
- La UI muestra chips `Tier`, `WR`, `PR`, `Patch`, estado de fuente, razon de Jungle Meta, build core y runa con iconos locales de items.
- `Meta Scraper :8002` queda explicitamente como contexto secundario futuro; no altera el ranking de Jungla en esta iteracion.

### Archivos creados
- `src/riot_lol_cli/draft_advisor/jungle_meta_provider.py`
- `tests/draft_advisor/test_jungle_meta_provider.py`
- `tests/draft_advisor/test_jungle_recommendations.py`

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/schemas.py`
- `src/riot_lol_cli/draft_advisor/champion_data.py`
- `src/riot_lol_cli/draft_advisor/api.py`
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/server.py`
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `tests/draft_advisor/test_data_integrity.py`
- `tests/test_server_factories.py`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`
- `AGENTS.md`
- `bitacora_de_cambios.md`

## [2026-05-11] Home Hub - acceso directo transversal completado

### Que se hizo
- Se completo el acceso directo visible al `Home Hub` en las superficies de producto que todavia no lo tenian consistente: el dashboard original del `Meta Analyzer` (`/dashboard`) y la `Splash Gallery` offline.
- El `Meta Analyzer` ahora ofrece retorno al Hub tanto en la version enhanced como en la version original servida desde `outputs/meta-analyzer-dashboard.html`.
- La `Splash Gallery` quedo alineada con el resto de los desarrollos navegables mediante un acceso directo en el header, tanto en el template fuente como en el HTML generado actual.
- Con esto, el criterio de UX del repo queda realmente transversal: toda surface navegable de producto debe ofrecer vuelta visible al `Home Hub`.

### Archivos modificados
- `src/riot_lol_cli/dashboard.py`
- `outputs/meta-analyzer-dashboard.html`
- `templates/splash-viewer.html`
- `outputs/splash-viewer.html`
- `tests/test_server_factories.py`
- `bitacora_de_cambios.md`

## [2026-05-11] Home Hub - estandarizacion de favicon y contrato UI transversal

### Que se hizo
- Se extendio la solucion del Home Hub a todos los proyectos activos integrados: `Draft Advisor`, `Meta Scraper`, `Jungle Meta`, `Items Browser`, `Meta Analyzer` y `Junglas Pro`.
- Todas las UIs integradas ahora declaran un favicon explicito para evitar `404` ruidosos de `/favicon.ico` en consola.
- Los servidores FastAPI con frontend propio exponen fallback de `favicon.ico` hacia un favicon real o `204` controlado.
- `Meta Analyzer` incorporo favicon tanto en la fuente generadora de dashboards como en los HTML actualmente servidos desde `outputs/`.
- Se documento el contrato para futuros proyectos del Home Hub: card registrada, health check valido, link visible de vuelta al Hub, favicon explicito y launch popup-safe.

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/favicon.svg`
- `src/riot_lol_cli/draft_advisor/server.py`
- `src/riot_lol_cli/meta_scraper/static/index.html`
- `src/riot_lol_cli/meta_scraper/static/favicon.svg`
- `src/riot_lol_cli/meta_scraper/server.py`
- `src/riot_lol_cli/items_browser/static/index.html`
- `src/riot_lol_cli/items_browser/static/favicon.svg`
- `src/riot_lol_cli/items_browser/server.py`
- `src/riot_lol_cli/meta_api/routes/core.py`
- `src/riot_lol_cli/dashboard.py`
- `src/riot_lol_cli/dashboard_enhanced.py`
- `outputs/meta-analyzer-dashboard.html`
- `outputs/meta-analyzer-dashboard-enhanced.html`
- `projects/active/junglas-pro/index.html`
- `projects/active/junglas-pro/favicon.svg`
- `AGENTS.md`
- `.agent/rules/agent-workflow.md`
- `.agent/rules/documentation-and-commits.md`
- `projects/active/home-hub/README.md`
- `docs/getting-started.md`
- `tests/test_server_factories.py`

## [2026-05-10] Navegacion transversal - acceso de vuelta al Home Hub

### Que se hizo
- Se agrego un acceso visible a `http://localhost:8080/` en las UIs activas para volver al Home Hub sin cerrar la navegacion actual.
- El patron se adapto a cada surface: `Draft Advisor`, `Meta Scraper`, `Jungle Meta`, `Items Browser`, `Meta Analyzer` y `Junglas Pro`.
- En `Jungle Meta` el acceso tambien aparece en la vista de detalle del campeon para no perder el retorno al hub al navegar por hash routes.
- En `Meta Analyzer` se actualizo tanto la fuente generadora (`dashboard_enhanced.py`) como el HTML servido actualmente en `outputs/meta-analyzer-dashboard-enhanced.html`.

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `src/riot_lol_cli/meta_scraper/static/index.html`
- `src/riot_lol_cli/meta_scraper/static/styles.css`
- `src/riot_lol_cli/jungle_meta/static/index.html`
- `src/riot_lol_cli/jungle_meta/static/styles.css`
- `src/riot_lol_cli/items_browser/static/index.html`
- `src/riot_lol_cli/items_browser/static/styles.css`
- `src/riot_lol_cli/dashboard_enhanced.py`
- `outputs/meta-analyzer-dashboard-enhanced.html`
- `projects/active/junglas-pro/index.html`

## [2026-05-10] Home Hub - fix de launch polling sin CORS

### Que se hizo
- **Corregido el flujo de `Abrir` en cards offline del Home Hub.** El frontend ya no hace `fetch` directo al `/health` cross-origin de cada servicio (`:8000`-`:8004`) mientras espera el arranque.
- **Nuevo polling interno sobre `/api/v1/home/status`.** El browser ahora consulta solo al propio Hub (`:8080`) y usa el estado agregado para detectar cuando un servicio paso a `online`.
- **Eliminado el falso error de consola** `net::ERR_FAILED 200 (OK)` que aparecia al iniciar Jungle Meta, Meta Analyzer u otros servicios sin CORS habilitado para `localhost:8080`.
- **Endurecido el open del Home Hub.** Ahora reserva la nueva pestaña al momento del click y luego navega esa ventana cuando el servicio queda `online`, lo que reduce bloqueos por popup async.
- **Declarado favicon explicito** en Home Hub y Jungle Meta para evitar el `404` ruidoso de `/favicon.ico` en consola.

### Impacto
- Los accesos directos del Home Hub vuelven a iniciar servicios sin quedar trabados en `Iniciando...`.
- El comportamiento queda alineado con la arquitectura del Hub: el backend centraliza health checks y el frontend evita cross-origin innecesario.

### Archivos modificados
- `src/riot_lol_cli/home/server.py`
- `src/riot_lol_cli/home/static/app.js`
- `src/riot_lol_cli/home/static/index.html`
- `src/riot_lol_cli/home/static/favicon.svg`
- `src/riot_lol_cli/jungle_meta/server.py`
- `src/riot_lol_cli/jungle_meta/static/index.html`
- `src/riot_lol_cli/jungle_meta/static/favicon.svg`

## [2026-05-10] Pattern Library v2 — Draft Advisor (PR 1/6)

### Que se hizo
- **Draft Advisor SPA migrado a Pattern Library v2.** El `index.html` ahora
  importa `tokens.css?v=2` + `patterns.css?v=2` y compone clases del sistema
  con clases custom (`.slot.champion-slot`, `.btn.btn-primary.btn-analyze`,
  `.modal-overlay.modal-backdrop`, `.card.panel`, `.state-block.results-empty`,
  etc.). Las clases viejas se conservan para no romper `app.js`.
- **`compat-spa.css` removido** del orden de carga: el nuevo styles.css usa solo
  tokens canonicos (`--arc-gold`, `--state-error`, `--surface-card`,
  `--text-primary`, etc.), no necesita el mapeo legacy.
- **`styles.css` reescrito completo** (~233 -> ~600 lineas con comentarios) como
  override layer sobre patterns.css: borra reglas duplicadas (modal base,
  search-input base, btn base) y mantiene patrones unicos (header hexagonal,
  sticky panel, top-pick gold glow, alternativas grid, role-pill filters del
  modal, vs-divider).
- **Tipografia ampliada:** se agregaron Outfit (display weights 800-900),
  Anton y JetBrains Mono al `<link>` de Google Fonts (Beaufort se mantiene
  para legacy si algun bloque lo usa).
- **Body con `.app-shell`** del patterns.css: reemplaza el `body::before` con
  radial gradients custom por el shell premium canonico (mismo lenguaje visual
  que tendra el Home Hub en su PR posterior).

### Cambios visuales esperados
- Bordes mas chicos en cards/modal (radius v2: 8/12/16 vs antes 18px).
- Hover transitions ~180ms (motion-default v2) vs antes 200ms.
- Slot `enemy filled` con border `--state-error-dim` semi-transparente vs antes
  rojo solido.
- Top-pick mantiene gradient gold pero con tokens canonicos.

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `bitacora_de_cambios.md`

### Verificacion
- `pytest tests/test_server_factories.py -q` → 17 passed
- `curl http://localhost:8001/draft` sirve HTML con clases composables ok
- CSS de design-system carga 200 OK
- Smoke browser: panel Draft sticky, modal de picker abre, slots ally/enemy
  con bordes correctos.

---

## [2026-05-10] Correccion post-auditoria — Meta Scraper jungla, Gaps UI y docs

### Que se hizo
- **Meta Scraper jungla:** el normalizer ahora filtra contaminacion cross-role
  en rol `jungle` usando `champion_base.json` + overrides curados, y registra
  el evento en `source_gaps`.
- **Datos imposibles:** `games_analyzed` mayor a 50M se conserva en el desglose
  con valor `0`, no pondera el agregado y queda auditado como gap.
- **Snapshot:** `latest_jungle_tier.json` fue regenerado desde raw locales
  existentes, sin scraping externo. El anterior quedo respaldado en
  `data/meta_scraper/normalized/backups/jungle/`.
- **Frontend Meta Scraper:** la vista `Gaps` ahora existe en la SPA y muestra
  razon, fuente, etapa y hora de deteccion.
- **Docs:** se alinearon README raiz, project map, docs index, API guide,
  getting-started, rule de agentes, handoff de Jungle Meta y copy operativo.

### Archivos creados
- `projects/active/home-hub/README.md`
- `tests/meta_scraper/test_jungle_snapshot_integrity.py`

### Archivos modificados
- `src/riot_lol_cli/meta_scraper/normalizer.py`
- `src/riot_lol_cli/meta_scraper/static/index.html`
- `src/riot_lol_cli/meta_scraper/static/app.js`
- `src/riot_lol_cli/meta_scraper/static/styles.css`
- `data/meta_scraper/normalized/latest_jungle_tier.json`
- `data/meta_scraper/normalized/history/*_merged.json`
- `data/meta_scraper/normalized/backups/jungle/*`
- `tests/meta_scraper/test_normalizer.py`
- `README.md`, `AGENTS.md`, `docs/README.md`, `docs/api-guide.md`,
  `docs/getting-started.md`, `docs/design-system.md`, `projects/README.md`,
  `.agent/rules/agent-workflow.md`, `projects/active/meta-scraper/README.md`,
  `projects/active/jungle-meta/CODEX_HANDOFF.md`, `scripts/bat/meta_scraper.bat`

---

## [2026-05-10] Pattern Library v2 — `patterns.css` drop-in + reference page

### Que se hizo
- ➕ `design-system/patterns.css`: 18 patrones drop-in HTML+CSS vanilla
  (hero, control-panel, tabs, tier-row, cat-card, stat-strip, data-table,
  modal, slots, toasts, banners, entity-card, score-factor, etc).
- 🔄 `design-system/tokens.css` → v2 canónica. Cambios visuales sutiles
  esperados:
  - `--radius-sm/md/lg/xl`: 8/12/16/20px → 6/8/12/16px (bordes más chicos)
  - `--motion-fast/default/slow`: 150/200/400ms → 120/180/320ms (animaciones más rápidas)
  - `--state-success-dim/error-dim/warning-dim`: cambiaron de hex sólido a rgba
    semitransparente. **Cambio drástico** en `components.css:494` donde
    `--state-error-dim` se usa como border-color del slot enemy filled
    (rojo sólido `#d13639` → rojo translúcido `rgba(255,70,85,0.18)`).
- ➕ Tokens nuevos del v2: `--tier-s/a/b/c`, `--font-anton`, `--font-hero`,
  `--tracking-hero`, `--space-20`, `--ease-out`, `--state-info-dim`.
- ➖ Tokens deprecados (no se usaban en runtime activo, safe):
  `--motion-spin`, `--motion-glow-pulse`, `--motion-border-flow`,
  `--motion-grid-flow`, `--container-3xl`, `--tracking-tighter`.
- ⚠️ Token `--gap` queda undefined → fallback a `initial`. Solo lo usaba
  `compat-spa.css:57`. Se documenta en bitácora; si se rompe spacing en
  Draft Advisor SPA, agregar mitigación en otra iteración.
- 📖 Doc page nueva: `claude-design-handoff_revolution/patrones_diseños_claude_design/Pattern Library.html`
  con TOC, demos, snippets y checklist (mirrors de tokens.css + patterns.css
  para abrirla standalone).
- 📝 Nuevo `design-system/README.md` con orden de carga canónico.
- 📝 `docs/design-system.md` extendido con sección Pattern Library v2 + tabla
  de recipes por surface.
- Ref: PR `feat/pattern-library-v2`.

### Archivos creados
- `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css`
- `src/riot_lol_cli/draft_advisor/static/design-system/README.md`
- `claude-design-handoff_revolution/patrones_diseños_claude_design/Pattern Library.html`
- `claude-design-handoff_revolution/patrones_diseños_claude_design/tokens.css` (mirror)
- `claude-design-handoff_revolution/patrones_diseños_claude_design/patterns.css` (mirror)

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css` (reemplazo total → v2)
- `docs/design-system.md` (sección Pattern Library v2 al final)
- `bitacora_de_cambios.md` (esta entrada)

### Verificación
- Smoke test visual de Draft Advisor (única surface que importa tokens.css).
- Surfaces Home/Meta/Jungle/Items no afectadas (no importan tokens.css).
- Doc page abre standalone sin errores de consola.

---

## [2026-05-10] Claude Design — prompt maestro para libreria de patrones

### Que se hizo
- Se publico `main` a `origin/main` con los 4 commits locales pendientes (`a63b2b8` -> `808d553`).
- Se agrego un prompt maestro para Claude Design orientado a crear una libreria propia de patrones visuales para `riot_lol_cli`.
- El prompt fija el alcance transversal: Home Hub, Draft Advisor, Meta Scraper, Jungle Meta, Items Browser, Meta Analyzer, Splash Gallery y exports HTML.
- Se documentaron restricciones de implementacion: HTML/CSS/JS vanilla, tokens `arc-*`/`forge-*`, estados accesibles, dark premium gaming y anti-patterns.

### Archivos creados
- `claude-design-handoff/pattern-library-prompt.md` — prompt, fuentes oficiales, adjuntos recomendados, criterios de aceptacion y handoff posterior a ingenieria.

### Archivos modificados
- `claude-design-handoff/README.md` — referencia al prompt maestro.
- `docs/design-system.md` — nota de uso de Claude Design sin reemplazar tokens canonicos.
- `docs/README.md` — indice actualizado con el nuevo prompt.

---

## [2026-05-09] Home Hub — empty states (skeleton + error + empty fallback)

### Que se hizo
- **Frontend:** la grilla de servicios deja de aparecer vacía durante la carga inicial.
  - 5 skeleton cards con `@keyframes shimmer` se renderizan inmediatamente al init (antes del primer poll).
  - Si el fetch falla en first load → estado "Error al cargar servicios" con botón "Reintentar".
  - Si la API devuelve `services: []` → estado "Sin servicios configurados".
- `fetchAndRender` también refresca el botón de cada card en cada poll respetando el estado de launch en curso.

### Archivos modificados
- `src/riot_lol_cli/home/static/app.js` — `buildSkeletonCard`, `renderGridSkeletons(5)` al init, `renderGridError`, `renderGridEmpty`, manejo en `fetchAndRender`.
- `src/riot_lol_cli/home/static/styles.css` — `@keyframes shimmer`, clases `.skel-*`, `.services-empty`, `.btn-retry`.

---

## [2026-05-09] Meta Scraper — accuracy fixes en adapters + min_pick_rate filter

### Que se hizo
- **lolalytics adapter:** `games_analyzed` ahora itera celdas individuales desde el índice 8 con regla numérica (100 ≤ N ≤ 50M). Antes usaba un regex greedy sobre `fullText` que concatenaba números no relacionados.
- **opgg adapter:** ahora extrae `games_analyzed` de las celdas (ignorando `%`) en vez de hardcodear 0.
- **ugg adapter:** `_JS_EXTRACT` recibe `targetRole` y filtra solo links cuyo href matchea `/build/{role}` (antes contaminaba cross-rol — picks de support aparecían en jungla).
- **normalizer:** nuevo parámetro `min_pick_rate=0.5` en `merge_platform_data()`; campeones bajo ese umbral se excluyen del dataset final.

### Archivos modificados
- `src/riot_lol_cli/meta_scraper/adapters/lolalytics.py`
- `src/riot_lol_cli/meta_scraper/adapters/opgg.py`
- `src/riot_lol_cli/meta_scraper/adapters/ugg.py`
- `src/riot_lol_cli/meta_scraper/normalizer.py`

---

## [2026-05-09] Home Hub — launch on-demand + documentación de scripts

### Que se hizo
- **Backend:** Nuevo endpoint `POST /api/v1/home/launch/{service_id}` — spawnea subproceso del servicio si no está corriendo.
  - Valida que no esté online (quick health ping).
  - Expone `health_path` en `/api/v1/home/status` para polling directo desde frontend.
- **Frontend:** "Abrir" en cards offline → lanza servicio → muestra "⏳ Iniciando…" → poll health cada 1s hasta 20s → abre browser automáticamente.
- **Documentación:** Secciones Home Hub + Levantar Todo en `docs/getting-started.md`.
- **Scripts:** Nuevo `scripts/bat/home.bat` + actualizado `levantar_todo.bat` para incluir Home Hub (`:8080`).
- **Tests:** 3 smoke tests (home routes, health_path en status, 404 on unknown service) + restaurado test items_browser completo.

### Archivos creados
- `scripts/bat/home.bat` — launcher independiente para Home Hub.

### Archivos modificados
- `src/riot_lol_cli/home/server.py` — imports os/subprocess/sys, `_LAUNCH_CMDS` dict, `_running_processes`, `POST /api/v1/home/launch/{id}`, expone `health_path`.
- `src/riot_lol_cli/home/static/app.js` — `buildOpenButton()`, `launchAndOpen()`, `refreshCardButton()`, event delegation `.btn-launch`.
- `src/riot_lol_cli/home/static/styles.css` — reset `button.btn-open`, estilo disabled y `--launching`.
- `docs/getting-started.md` — secciones Home Hub + Levantar Todo al inicio.
- `scripts/bat/levantar_todo.bat` — Home Hub `:8080` agregado, abre browser al inicio, actualizado display de frontends.
- `tests/test_server_factories.py` — 3 nuevos tests home, restaurado test items_browser.

---

## [2026-05-09] Rediseño frontend Home Hub (`:8080`)

### Que se hizo
- Reemplazo de `static/index.html`, `static/styles.css` y `static/app.js` del Home Hub con rediseño visual completo.
- Sin cambios en `server.py` — contrato 100% preservado con `/api/v1/home/status`.
- Self-contained CSS: desacoplado de `/design-system/*` para evitar drift entre subsistemas.
- Tipografía: Inter (UI) + IBM Plex Mono (stats/labels) reemplazando la display pesada anterior.
- Top bar compacto con version pill + status dot + refresh button (reemplaza hero decorativo).
- Stats strip operacional: servicios online con barra de progreso, offline, última actualización, uptime de sesión.
- Tweaks panel: 4 paletas de acento (gold/cyan/green/violet), densidad balanceado/compacto, layout grid/lista, partículas on/off.
- Atajos de teclado: R=refresh, G=grid, L=list, 1-5=abrir servicio, Esc=cerrar tweaks.
- Responsive mobile/tablet, `prefers-reduced-motion`, WCAG focus rings.

### Archivos modificados
- `src/riot_lol_cli/home/static/index.html` — reescrito.
- `src/riot_lol_cli/home/static/styles.css` — reescrito (self-contained).
- `src/riot_lol_cli/home/static/app.js` — reescrito (contrato preservado, funcionalidad extendida).
- `bitacora_de_cambios.md` — esta entrada.

### Archivos NO tocados
- `server.py`, `__init__.py` — sin cambios.
- `/design-system/*` — sin cambios (otros subsistemas siguen usándolo).

---

## [2026-05-09] Rediseño frontend Meta Scraper (`:8002`)

### Que se hizo
- Reemplazo de `static/index.html` y `static/styles.css` del meta_scraper con rediseño visual completo.
- Sin cambios en `app.js`, server, scoring ni endpoints — contrato 100% preservado (IDs, clases, onclick handlers).
- Self-contained CSS: desacoplado de `/design-system/*` para evitar drift entre subsistemas.
- Removida dependencia CDN de JetBrains Mono → system mono stack.
- Mejoras visuales: glassmorphism, progress bars 6px con gradientes, tier badges con glow, panel detalle con backdrop blur, role tabs con pill animado, quick stats cards con accents por tipo, responsive mobile/tablet, `prefers-reduced-motion`.

### Archivos modificados
- `src/riot_lol_cli/meta_scraper/static/index.html` — reemplazado.
- `src/riot_lol_cli/meta_scraper/static/styles.css` — reemplazado.
- `bitacora_de_cambios.md` — esta entrada.

### Archivos NO tocados
- `static/app.js`, `server.py`, adapters, normalizer, orchestrator, endpoints.
- `/design-system/*` (archivos siguen en el repo, solo no se cargan desde este HTML).

---

## [2026-05-09] Meta Scraper - Jungle Meta v1 multi-fuente

### Que se hizo
- Se extendio Meta Scraper para soportar rol `jungle` en el nucleo v1: OP.GG, LoLalytics y U.GG.
- Se agregaron endpoints `GET /api/v1/meta/jungle/tier`, `GET /api/v1/meta/jungle/champion/{champion_id}` y `POST /api/v1/meta/scrape/jungle`.
- El normalizador subio a schema `1.2` y ahora guarda `source_status`, `source_gaps` y metadata de agregacion.
- El meta total usa promedio ponderado por `games_analyzed` cuando existe; si no hay partidas, cae a promedio simple por fuente y lo marca como fallback.
- `latest_jungle_tier.json` queda como snapshot actual de jungla; antes de sobrescribirlo, el anterior se copia a `normalized/backups/jungle/`.
- El frontend de `:8002` suma tab Jungla, selector `Total`/fuentes/`Gaps`, fecha y hora de update, y panel visible de gaps.
- League of Graphs, Mobalytics, METAsrc, Asia, cuentas pro y pro-stage quedan registrados como backlog, no como fuentes activas en v1.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/` - rol jungla, endpoints, adapters, normalizer, backups y UI.
- `data/meta_scraper/normalized/latest_jungle_tier.json` - placeholder inicial sin datos inventados.
- `tests/meta_scraper/` y `tests/test_server_factories.py` - regresiones de rol jungla, agregacion y rutas.
- `AGENTS.md`, `docs/getting-started.md`, `projects/active/meta-scraper/README.md` - contrato actualizado.

### Verificacion
- `pytest tests/meta_scraper -q`
- `pytest tests/test_server_factories.py -q`
- `pytest tests/ -q`
- `ruff check src tests scripts`
- `ruff format --check src/riot_lol_cli/meta_scraper tests/meta_scraper tests/test_server_factories.py`
- `git diff --check`
- Nota: `ruff format --check src tests scripts` queda bloqueado por `src/riot_lol_cli/home/server.py`, archivo ajeno/untracked de Home Hub.

---

## [2026-05-09] Home Hub — Centro de Operaciones (puerto 8080)

### Que se hizo
- Se creo el modulo `src/riot_lol_cli/home/` como nuevo subsistema FastAPI en puerto 8080 (configurable via `LOLCLI_HOME_PORT`).
- El Home Hub es un portal unificado de acceso a los 5 servicios activos (Meta API, Draft Advisor, Meta Scraper, Jungle Meta, Items Browser) mas Junglas Pro como proyecto standalone.
- Health-check agregado en tiempo real via `/api/v1/home/status`: el backend consulta async (httpx) el `/health` de cada servicio con timeout de 2s y retorna estado online/offline.
- Frontend SPA con design system canonico (`tokens.css` + `components.css`): hero con titulo gradiente, grid de service cards con indicador de estado live, botones "Abrir" y "Docs", polling cada 30s con updates in-place.
- Se agrego `get_home_host()` / `get_home_port()` a `settings.py` siguiendo el patron existente.
- Se actualizo AGENTS.md con el nuevo subsistema (6 FastAPI), entrada en tabla de puertos, entry points y gotchas.

### Archivos creados
- `src/riot_lol_cli/home/__init__.py` — module marker.
- `src/riot_lol_cli/home/server.py` — FastAPI + health-check agregado + factory.
- `src/riot_lol_cli/home/static/index.html` — SPA shell con design system.
- `src/riot_lol_cli/home/static/styles.css` — estilos propios del Home.
- `src/riot_lol_cli/home/static/app.js` — fetch de status + rendering de cards.

### Archivos modificados
- `src/riot_lol_cli/settings.py` — `DEFAULT_HOME_HOST/PORT` + helpers.
- `AGENTS.md` — Home Hub en 5 secciones (subsistemas, puertos, entry points, APIs, gotchas).
- `bitacora_de_cambios.md` — este registro.

### Verificacion
- `python -m riot_lol_cli.home.server` levanta sin errores en :8080.
- `GET /health` retorna `{"status":"ok","service":"home","version":"1.6.4"}`.
- `GET /api/v1/home/status` retorna JSON con estado de cada servicio (3/5 online en prueba).
- SPA carga correctamente con design system canonico, animaciones y health-check en vivo.

---

## [2026-05-09] Jungle Meta — Xin Zhao build corregido contra captura

### Que se hizo
- Se continuo la correccion iniciada por Claude para Xin Zhao en `data/jungle_meta/patch_26.09.json`.
- Se reemplazaron los builds arquetipicos anteriores por la fuente visual confirmada: `Statikk Shiv` (`3087`), `Dusk and Dawn` (`2510`) y `Riftmaker` (`4633`).
- Se saco `XinZhao` de `items_meta.voltaic_sword_abusers` porque el build verificado ya no usa Voltaic.
- Se agrego `items_meta.statikk_dusk_riftmaker_abusers` con `XinZhao`.
- Se agregaron tests de regresion para el build exacto de Xin Zhao y su nueva categoria de item meta.
- Se actualizo el handoff de Jungle Meta para dejar asentado que Xin Zhao ya no esta pendiente.

### Archivos modificados clave
- `data/jungle_meta/patch_26.09.json` — build y metadata de items para Xin Zhao.
- `tests/jungle_meta/test_loader.py` — regresiones de builds y item abusers.
- `projects/active/jungle-meta/README.md` — schema vigente con `core_builds`.
- `projects/active/jungle-meta/CODEX_HANDOFF.md` — estado actualizado para proximos agentes.

### Verificacion
- `pytest tests/jungle_meta/ -q`
- `pytest tests/ -q`
- `ruff check src tests scripts`
- `ruff format --check src tests scripts`
- `git diff --check`

---

## [2026-05-09] Items Browser — ocultar variantes duplicadas por mapa/modo

### Que se hizo
- Se corrigio el catalogo visual de Items Browser para no mostrar duplicados de Data Dragon como `Riftmaker` (`4633` vs Arena `224633`) ni variantes internas de smite (`1101`-`1103` vs `1105`-`1107`).
- `loader.py` ahora calcula un item canonico por nombre y oculta variantes por defecto, priorizando items de Summoner's Rift (`map 11`), items multi-mapa y IDs base.
- La API conserva acceso al dato bruto con `include_variants=true` en `/api/v1/items/all`, `/groups` y `/search`.
- `health` expone `catalog_count` para distinguir catalogo visible de `current_count` bruto de Data Dragon.
- Se agregaron tests para asegurar que la busqueda y el grupo Jungla no vuelvan a mostrar variantes duplicadas por defecto.

### Archivos modificados clave
- `src/riot_lol_cli/items_browser/loader.py` — deduplicacion de catalogo y anotacion `catalog_variant`.
- `src/riot_lol_cli/items_browser/server.py` — query param `include_variants` y `catalog_count`.
- `tests/items_browser/test_loader.py` y `tests/test_server_factories.py` — regresion de Riftmaker y smite variants.
- `projects/active/items-browser/README.md`, `docs/getting-started.md`, `AGENTS.md` — documentacion del comportamiento.

### Verificacion
- `pytest tests/items_browser/test_loader.py tests/test_server_factories.py -q`
- `ruff check src tests scripts`
- `ruff format --check src tests scripts`
- `git diff --check`

---

## [2026-05-08] Prolijidad post-auditoria — estado FastAPI, puertos y guard Python 3.9

### Que se hizo
- Draft Advisor: los servicios (`ChampionDataService` + `ScoringEngine`) dejaron de depender de singletons globales de import y ahora se crean por `create_app()` en `app.state`. La API usa dependencias FastAPI con `Annotated`.
- Meta Scraper: `_orchestrator` y ultimo resultado de scraping pasaron a `app.state`; los endpoints de scraping usan un orquestador por app y mensajes compartidos para Playwright.
- Playwright: se centralizo el copy operativo en `meta_scraper/messages.py`; los adapters ya no sugieren `pip install playwright` como paso principal, sino `playwright install chromium`.
- FastAPI: logs de arranque de Meta API, Draft Advisor, Meta Scraper, Jungle Meta e Items Browser usan `host`/`port` configurables en lugar de `localhost` hardcodeado.
- Scripts: `levantar_todo.bat` ahora levanta los cinco servicios activos (`8000`-`8004`) respetando `LOLCLI_*_PORT`; scripts individuales ajustaron copy visible de puertos.
- Python 3.9: agregado guard `tests/test_python39_annotations.py` para detectar pipe-unions sin `from __future__ import annotations`.
- Tests: se ampliaron smoke tests de factories, aislamiento de estado runtime, mensaje Playwright sin `pip install playwright`, y una rama `blocked_user_excluded` del Draft Advisor.
- Ruff: se corrigieron excepciones `raise ... from e` en Jungle Meta e Items Browser y se aplico formato al codigo afectado.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/api.py` y `server.py` — servicios por app y dependencia tipada.
- `src/riot_lol_cli/meta_scraper/server.py` y `messages.py` — estado runtime por app y mensajes operativos compartidos.
- `src/riot_lol_cli/meta_api/app.py`, `jungle_meta/server.py`, `items_browser/server.py` — logs con host/port configurables.
- `scripts/bat/levantar_todo.bat` — launcher de cinco servidores.
- `tests/test_server_factories.py` y `tests/test_python39_annotations.py` — cobertura nueva de factories, estado y Python 3.9.

### Verificacion
- `pytest tests/test_server_factories.py tests/test_python39_annotations.py tests/meta_scraper/test_adapter_name_maps.py tests/draft_advisor/test_adc_priority_policy.py -q` -> 37 passed.
- `pytest tests/ -q` -> 169 passed.
- `ruff check src tests scripts` -> passed.
- `ruff format --check src tests scripts` -> passed.
- `git diff --check` -> passed.

---

## [2026-05-08] Items Browser — Catalogo de items LoL (EN+ES) + regla wrap-up

### Que se hizo

#### 1. Regla de cierre con lista de archivos
- `.agent/rules/documentation-and-commits.md`: agregado paso 7 al checklist post-accion: el agente debe cerrar cada respuesta final con dos secciones explicitas — **Archivos creados** y **Archivos modificados**. Si la lista es vacia, decirlo. Esto da al usuario un mapa rapido de blast radius sin leer el diff entero. La regla aplica a cualquier iteracion, no solo features grandes.

#### 2. Items Database (Data Dragon EN+ES)
- `scripts/update_items_database.py` nuevo: resuelve version actual de Data Dragon (`versions.json`), descarga `item.json` en `en_US` y `es_ES`, construye `data/items/database.json` mezclado con: `id`, `name_en`, `name_es`, `tags`, `stats`, `gold_total/base/sell`, `purchasable`, `depth`, `from`, `into`, `maps`, `image`, `deprecated`. Marca como deprecated los items presentes en `assets/items/*.png` o CSV legacy pero ausentes en la version vigente. Descarga PNG faltantes a `assets/items/`. Tiene fallback `verify=False` para certificate stores rotos en Windows (Data Dragon es CDN publico sin auth).
- `data/items/database.json` generado: 705 items (DDragon 16.9.1, 0 deprecated en este ciclo). Nombres canonicos confirmados: `6699` = "Voltaic Cyclosword" / "Espada ciclovoltaica", `3071` = "Black Cleaver" / "Cuchilla negra".

#### 3. Items Browser FastAPI + SPA (puerto 8004)
- Modulo nuevo `src/riot_lol_cli/items_browser/`:
  - `loader.py`: cache en memoria, `get_item`, `list_categories` (tags Riot), `list_groups` (buckets curados: starter/boots/components/legendary/consumables/trinkets/jungle_specific/deprecated), `search_items` (substring case-insensitive en EN o ES).
  - `server.py`: 7 endpoints, mount `/items` para PNGs locales, factory `create_app()` y `run()` con settings.
  - SPA vanilla en `static/`: hero con DDragon version, controles (busqueda + toggle EN/ES + checkbox mostrar deprecated), tabs por grupo con badges de count, grid responsivo con item cards (icon + nombre + gold + id), modal de detalle con stats humanizados, tags Riot, plaintext bilingue, banner para deprecated.
- `settings.py`: agregadas constantes y helpers `get_items_browser_host` / `get_items_browser_port` (`LOLCLI_ITEMS_BROWSER_*`, default 8004).
- `scripts/bat/items_browser.bat` nuevo: levanta el server, regenera la database si no existe.
- `projects/active/items-browser/README.md` nuevo: manifiesto del proyecto con schema, endpoints, configuracion.

#### 4. Documentacion sincronizada
- `AGENTS.md`: agregada Items Browser a Mapa de Subsistemas, tabla de servidores FastAPI, Entry Points, APIs locales, gotchas (de 4 a 5 FastAPI, puertos 8000-8004 configurables).
- `docs/getting-started.md`: nueva seccion 7 "Items Browser" con setup + manual + endpoints; tablas de scripts actualizadas.
- `.agent/rules/agent-workflow.md`: gotcha de FastAPI count actualizado, agregado items-browser a tabla de docs canonicas.

### Archivos clave

**Creados:**
- `scripts/update_items_database.py` — script de regeneracion de la DB.
- `data/items/database.json` — 705 items, EN+ES, version 16.9.1.
- `src/riot_lol_cli/items_browser/__init__.py` — module marker.
- `src/riot_lol_cli/items_browser/loader.py` — cache + groups + search.
- `src/riot_lol_cli/items_browser/server.py` — FastAPI + factory.
- `src/riot_lol_cli/items_browser/static/index.html` — SPA shell.
- `src/riot_lol_cli/items_browser/static/styles.css` — design tokens reusados.
- `src/riot_lol_cli/items_browser/static/app.js` — SPA logica.
- `scripts/bat/items_browser.bat` — launcher Windows.
- `projects/active/items-browser/README.md` — manifiesto.
- `tests/items_browser/__init__.py` + `tests/items_browser/test_loader.py` — 8 tests.

**Modificados:**
- `.agent/rules/documentation-and-commits.md` — paso 7 wrap-up.
- `.agent/rules/agent-workflow.md` — count FastAPI 4 -> 5.
- `AGENTS.md` — Items Browser en 5 secciones.
- `docs/getting-started.md` — seccion 7 + tablas.
- `src/riot_lol_cli/settings.py` — host/port helpers.
- `tests/test_server_factories.py` — 2 smoke tests nuevos.

### Verificacion
- `pytest -q` → 163 passed (153 anterior + 8 loader items_browser + 2 server factory items_browser).
- `curl http://localhost:8004/health` → `{"status":"ok","version":"16.9.1","total_count":705}`.
- `curl /api/v1/items/groups` → `{boots:29, components:464, legendary:157, consumables:30, trinkets:16, jungle_specific:9}`.
- `curl /api/v1/items/6699` → `{"name_en":"Voltaic Cyclosword","name_es":"Espada ciclovoltaica","gold_total":2900}`.
- Browser http://localhost:8004 → grid con 705 items, filtros por grupo, modal con detalle bilingue, busqueda en vivo.

### Pendiente / Notas
- Los items en builds del Jungle Meta (`data/jungle_meta/patch_26.09.json`) siguen siendo arquetipos canonicos (no slot-by-slot del video SkillCapped). Ahora con el Items Browser el usuario puede identificar IDs reales y corregir los slots.
- Cuando Riot publique nuevos items o renombre, re-correr `scripts/update_items_database.py` para sincronizar.

---

## [2026-05-08] Jungle Meta Dashboard v1.1 — Rediseño basado en SkillCapped

### Que se hizo
- Rediseño completo del SPA para alinearlo con la estética de SkillCapped Patch 26.09 (display itálica grande tipo Anton, tier list grid con filas S/A/B/C separadas, sidebar con OP/Low Elo/Bans, hero con jungla icon).
- **Nuevo schema de datos** en `data/jungle_meta/patch_26.09.json`:
  - `core_builds`: array de builds por champion (Xin Zhao tiene 2 variantes según video).
  - `core_rune`: objeto estructurado `{name, tree}`.
  - `categories`: agrupación curada `overpowered`, `low_elo_picks`, `bans`.
  - `items_meta.voltaic_sword_abusers`: campeones que abusan de Cicloespada Voltaica.
  - **Items por DDragon ID (int)** en lugar de strings — sirve `assets/items/<id>.png` localmente.
- Backend (`loader.py` + `server.py`):
  - Nuevas funciones: `get_categories`, `get_item_abusers`, `list_used_item_ids`.
  - Nuevos endpoints: `/api/v1/jungle/categories`, `/api/v1/jungle/items/abusers/{key}`, `/api/v1/jungle/items/used`.
  - Mount estático `/items` que sirve los 706 PNGs de `assets/items/`.
  - `health` y `run()` ahora usan `get_jungle_meta_host()` y `get_jungle_meta_port()` de `settings.py`.
- Frontend (rewrite completo):
  - `index.html` separado en estructura + `<template>` shells (overview + champion detail).
  - `styles.css` nuevo: tokens del design system, Anton itálica display, tier-rows separadas, splash bg en detail view.
  - `app.js` nuevo: hash router (`#overview`, `#champion/{id}`), fetch de tier-list + categorías en paralelo, render de cards expandidas con WR/PR, builds múltiples, fallback de error 404 en items.

### Decisiones de UX (validadas con el usuario)
- **Hash routing** para detail (no modal). Deeplink-friendly.
- **Cards expandidas** (icon + nombre + WR/PR) en lugar de solo iconos.
- **Tabs S/A/B/C mantenidos** como filtro adicional (default: ALL muestra todas las filas).

### Archivos clave
- `data/jungle_meta/patch_26.09.json` — schema nuevo.
- `src/riot_lol_cli/jungle_meta/loader.py` — 3 funciones nuevas.
- `src/riot_lol_cli/jungle_meta/server.py` — 3 endpoints nuevos + mount /items.
- `src/riot_lol_cli/jungle_meta/static/index.html` — rewrite con templates.
- `src/riot_lol_cli/jungle_meta/static/styles.css` — nuevo.
- `src/riot_lol_cli/jungle_meta/static/app.js` — nuevo.
- `tests/jungle_meta/test_loader.py` — 4 tests nuevos (categories, abusers, used items, multi-builds).
- `tests/test_server_factories.py` — asserts para 3 endpoints nuevos.
- `projects/active/jungle-meta/REDESIGN_PLAN.md` — plan de referencia.
- `projects/active/jungle-meta/screenshots/` — 7 capturas de SkillCapped como source-of-truth visual.

### Pendiente (correcciones del usuario)
- Slot-by-slot de items por champion vs video real de SkillCapped (la estructura permite cambiar `int` por `int`).
- Categorías `low_elo_picks` y `bans` curadas — el usuario validará vs criterio del video.

### Verificación
- `pytest -q` → 153 passed (era 148, +5 nuevos: multi-builds, categories, abusers, used IDs, endpoints smoke).
- `curl /items/6699.png` → 200 (Cicloespada Voltaica servida local).
- `curl /api/v1/jungle/categories` → estructura completa con champion dicts.
- Browser http://localhost:8003 → hero + tier rows + sidebar + champion detail navegable por hash.

---

## [2026-05-08] Jungle Metagame Dashboard — FastAPI + SPA (MVP patch 26.09)

### Que se hizo
- Se creó nuevo módulo `src/riot_lol_cli/jungle_meta/` con FastAPI + SPA para visualizar tier lists de jungla.
- Backend: 4 endpoints (`/health`, `/api/v1/jungle/tier-list`, `/api/v1/jungle/tier/{tier}`, `/api/v1/jungle/champion/{champion_id}`).
- Frontend: SPA vanilla HTML/CSS/JS con filtrado por tier (S/A/B/C), grid responsivo, integración DDragon para iconos.
- Datos: `data/jungle_meta/patch_26.09.json` con 16 campeones (S/A/B/C), estadísticas (WR/PR/BR), items core, runa, razón de fortaleza.
- Lanzador: `scripts/bat/jungle_meta.bat` para Windows + Linux equivalente.
- Configuración: `settings.py` extendido con helpers `get_jungle_meta_host()`, `get_jungle_meta_port()` (puerto 8003).
- Proyecto: Nuevo en `projects/active/jungle-meta/` con README completo.

### Archivos nuevos
- `src/riot_lol_cli/jungle_meta/__init__.py`, `server.py`, `loader.py`
- `src/riot_lol_cli/jungle_meta/static/index.html`
- `data/jungle_meta/patch_26.09.json`
- `scripts/bat/jungle_meta.bat`
- `projects/active/jungle-meta/README.md`

### Archivos modificados
- `src/riot_lol_cli/settings.py` — agregados helpers de host/port para puerto 8003

### Design
- Dark navy (`#010a13`) + ARC gold (`#c89b3c`) + tier colors (S=gold, A=cyan, B=gray, C=red)
- Responsive grid, DDragon CDN para assets
- No dependencies externas (vanilla JS)

### MVP scope
- Tier list completa patch 26.09 (16 champs)
- Manual JSON data source (can scrape in future)
- Responsive design, dark theme
- API + SPA functional

### Not in MVP
- Multi-patch navigation, scraper, historical trends, build variations

### Verificación
- Manual test: http://localhost:8003 ✅
- API endpoint tests (smoke tests pendientes)
- DDragon assets load OK

---

## [2026-05-08] Prolijidad Meta Scraper: copy, puerto configurable y docs cercanas

### Que se hizo
- Se elimino el log duplicado del arranque de Meta Scraper que seguia mostrando `localhost:8002/docs` hardcodeado junto al mensaje parametrizado.
- Se alinearon los mensajes operativos de Playwright en `server.py` y en los 3 adapters para reflejar el flujo vigente: dependencias Python ya instaladas y paso manual `playwright install chromium`.
- Se prolijo el copy cercano al puerto configurable del Meta Scraper en `AGENTS.md`, `docs/getting-started.md`, `projects/active/meta-scraper/README.md` y `scripts/bat/meta_scraper.bat`.
- Se mantuvo el alcance en limpieza y coherencia; no hubo cambios de logica funcional de scraping ni del Draft Advisor.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/server.py` - limpieza del log de arranque y copy operativo.
- `src/riot_lol_cli/meta_scraper/adapters/{opgg,lolalytics,ugg}.py` - mensaje unificado de prerequisito Playwright.
- `scripts/bat/meta_scraper.bat` - copy visible alineado con `LOLCLI_META_SCRAPER_PORT`.
- `AGENTS.md`, `docs/getting-started.md`, `projects/active/meta-scraper/README.md` - docs cercanas sincronizadas.

### Verificacion
- `pytest tests/test_server_factories.py -q`
- `pytest tests/meta_scraper/test_adapter_name_maps.py -q`
- `ruff check src tests scripts`
- `ruff format --check src tests scripts`
- `pytest tests/ -q`
- `git diff --check`

---

## [2026-05-07] Hardening post-auditoria: factories, fallbacks y cierre proporcional

### Que se hizo
- Se ampliaron los smoke tests de `create_app()` para Draft Advisor y Meta Scraper: ya no solo validan paths registrados, sino redirect/root, `health` y `openapi`.
- Se agregaron regresiones focalizadas del Draft Advisor para dos ramas que el refactor habia dejado sin test directo: politica `never_top_pick` y `fallback_meta_missing`.
- Se alineo el runtime del Meta Scraper con el resto de los servicios: ahora usa helpers de `settings.py` para host/port y el mensaje operativo de Playwright apunta al paso manual real (`playwright install chromium`).
- Se desduplicaron y aterrizaron las rules de cierre de tarea: la verificacion ahora queda explicitamente ligada al alcance real del cambio, sin forzar siempre la suite completa.

### Archivos modificados clave
- `tests/test_server_factories.py` - smoke tests HTTP reales para las factories FastAPI.
- `tests/draft_advisor/test_adc_priority_policy.py` - cobertura de `never_top_pick` y `fallback_meta_missing`.
- `src/riot_lol_cli/meta_scraper/server.py` - mensaje de adapters no disponibles y host/port configurables.
- `src/riot_lol_cli/settings.py` - helpers `get_meta_scraper_host()` y `get_meta_scraper_port()`.
- `.agent/rules/agent-workflow.md` - cierre proporcional al alcance.
- `.agent/rules/documentation-and-commits.md` - checklist canonico sin exigir suite completa por defecto.

### Verificacion
- `pytest tests/test_server_factories.py -q`
- `pytest tests/meta_scraper/test_adapter_name_maps.py -q`
- `pytest tests/draft_advisor/test_adc_priority_policy.py -q`
- `ruff check src tests scripts`
- `ruff format --check src tests scripts`

---

## [2026-05-07] Fix CI Python 3.9 — from __future__ import annotations

### Que se hizo
- CI de GitHub Actions fallaba con exit code 2 (error de coleccion de pytest, no test failure).
- Causa raiz: `meta_scraper` usaba sintaxis PEP 604 (`X | None`) sin `from __future__ import annotations`. Python 3.9 evalua las anotaciones en runtime y lanza `TypeError`. Local pasaba porque el entorno es Python 3.13.
- Fix: se agrego `from __future__ import annotations` (PEP 563) al inicio de 5 archivos del modulo `meta_scraper` para hacer las anotaciones lazy y compatibles con 3.9.
- Los 132 tests siguieron pasando tras el fix. Commit: `bfa31de`.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/server.py` — `from __future__ import annotations`
- `src/riot_lol_cli/meta_scraper/orchestrator.py` — idem
- `src/riot_lol_cli/meta_scraper/normalizer.py` — idem
- `src/riot_lol_cli/meta_scraper/adapters/base.py` — idem
- `src/riot_lol_cli/meta_scraper/adapters/ugg.py` — idem

### Verificacion
- `pytest -q`: 132/132 OK post-fix.
- `ast.parse(..., feature_version=(3,9))` corrido sobre `src/`, `tests/`, `scripts/`: 0 errores.
- CI de GitHub Actions verde tras push.

---

## [2026-05-07] Correccion post-auditoria independiente

### Que se hizo
- Se corrigio drift documental posterior a la auditoria `f0d0d82..67c895b`: Playwright ya esta en `requirements.txt`, y el paso manual vigente es `playwright install chromium`.
- Se reemplazaron referencias operativas a `_archive/` por `projects/legacy/` y se marco `data/supports_list.json` como dato historico eliminado/absorbido.
- Se cambiaron comandos runtime activos de `src.riot_lol_cli.api_server:app` a `riot_lol_cli.api_server:app`.
- Se reforzo `tests/meta_scraper/test_adapter_name_maps.py` con asserts por plataforma para `KSante` y allowlist explicita de duplicados de U.GG.
- Se refactorizo `ScoringEngine._get_adc_priority` en helpers de bloqueo, contexto meta, vetos, core y fallbacks sin cambiar eligibilities ni scoring.
- Draft Advisor y Meta Scraper ahora exponen `create_app()` y mantienen `app = create_app()` para compatibilidad con imports y entrypoints actuales.
- Se dejo el prompt documentacional para Claude en el cierre de la iteracion, sin crear un Markdown adicional.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/server.py`
- `src/riot_lol_cli/meta_scraper/server.py`
- `tests/meta_scraper/test_adapter_name_maps.py`
- `AGENTS.md`, `README.md`, `projects/README.md`, `docs/getting-started.md`
- `.agent/rules/security-and-testing.md`

---

## [2026-05-07] Auditoría completa, cleanup git y refactors seguros

### Que se hizo
- Auditoría documental: se confirmó que README.md, AGENTS.md, projects/README.md, docs/ y .agent/rules/ son la fuente viva sin huérfanos.
- Cleanup git monumental (392 cambios pendientes desde reorganizaciones previas) commiteado en 11 lotes lógicos:
  1. `chore(rules)`: 7 rules antiguas → 4 canónicas en `.agent/rules/`.
  2. `feat(structure)`: adopción de `projects/` con 7 activos + 5 legacy; `riot-lol-cli/` raíz movido a `projects/legacy/riot-lol-cli/` (rename detectado).
  3. `feat(meta-scraper)`: módulo nuevo en puerto 8002 con adapters OP.GG/LoLalytics/U.GG via Playwright + tests.
  4. `docs`: colapso de 35 archivos fragmentados (~9k líneas) en READMEs canónicos (`_analysis/`, `REORGANIZATION_*`, `docs/adc_tracker/`, `docs/changelog/`, `claude-design-handoff/*`).
  5. `chore(archive)`: drop de `_archive/` y `_quarantine/` (absorbidos en `projects/legacy/` + bitácora).
  6. `feat(draft-advisor,kb)`: integración NotebookLM + ADC priority policy + 7 perfiles AP-mage bot + tests draft.
  7. `feat(assets)`: refresh Data Dragon (~100 items, ~70 splash arts) + nuevo `scripts/update_ddragon_assets.py`.
  8. `chore(core)`: alineación src/ + scripts/ con docs consolidadas; drop de `*/AGENTS.md` per-módulo.
  9. `chore(config)`: AGENTS.md como mapa maestro; CLAUDE.md como shim; `logs/` ignorado; ruff y CI refrescados.
  10. `docs(handoff)`: snapshot del design system de Claude Design.
- Refactors seguros aplicados:
  - **Bug fix**: los 3 adapters de Meta Scraper mapeaban `K-Sante` → `Ksante`, pero `champion_base.json` usa `KSante` (canonical Riot). Fix en opgg.py, lolalytics.py, ugg.py.
  - **Test de consistencia**: `tests/meta_scraper/test_adapter_name_maps.py` verifica que los 3 adapters comparten targets canónicos y que cada target existe en `champion_base.json`. Atrapó el bug de KSante.
  - **Dependencias**: `playwright>=1.40.0` declarado en `requirements.txt` con nota de `playwright install chromium`.
  - **Código muerto**: drop de `data/junglers_list.json` y `data/supports_list.json` (no referenciados).
- Auditoría y actualización de CLAUDE.md + 4 rules `.agent/rules/`:
  - `CLAUDE.md` extendido con setup runtime y verificación mínima.
  - `agent-workflow.md`: removidas referencias a `_archive/`/`_quarantine/` (no existen); agregada mención al test de consistencia y a Playwright en requirements.
  - `engineering-standards.md`: actualizada lista de exclusiones de ruff.
  - `pyproject.toml`: ruff exclude limpio (sin `_archive`/`_quarantine`).
- Documentación nueva:
  - `projects/legacy/riot-lol-cli/README.md` extendido con contexto del proyecto **deshu** y referencia al frontend `outputs/claude-4-5/deshu-las-claude-4-5.html`.
  - `README.md` raíz expandido a catálogo completo con tabla de proyectos activos/legacy, capacidades por dominio, comandos clave y mapa de docs.

### Archivos modificados clave
- `README.md` - catálogo completo del repo.
- `CLAUDE.md` - shim extendido con setup runtime.
- `.agent/rules/agent-workflow.md` - alineado con realidad post-reorg.
- `.agent/rules/engineering-standards.md` - exclusiones ruff actualizadas.
- `pyproject.toml` - exclude sin `_archive`/`_quarantine`.
- `requirements.txt` - playwright>=1.40.0 declarado.
- `src/riot_lol_cli/meta_scraper/adapters/{opgg,lolalytics,ugg}.py` - fix KSante.
- `tests/meta_scraper/test_adapter_name_maps.py` - test de consistencia (nuevo).
- `projects/legacy/riot-lol-cli/README.md` - contexto deshu + frontend documentado.
- `data/{junglers_list,supports_list}.json` - eliminados (huérfanos).
- `.gitignore` - `logs/` ignorado.

### Verificación
- 132 tests pasan (`pytest -q`): 129 baseline + 3 nuevos en `test_adapter_name_maps.py`.
- 11 commits lógicos sobre `main`.

---

## [2026-05-05] Draft Advisor - veto Nilah/Soraka y meta ADC estricto

### Que se hizo
- Se endurecio la politica de primera recomendacion ADC: requiere maestria `S/A` y meta fuerte real (`tier S` o `climb_score >= 80`).
- Los ADC con meta `A` y `climb_score < 80` pasan a `fallback_meta_soft`; pueden verse como alternativa, pero no compiten como core contra picks realmente fuertes.
- Se agrego la regla KB `Nilah + Soraka vs Caitlyn + Nautilus` con `score_delta -35` y `top_pick_block`, porque la linea pierde prioridad, crash, rango seguro y queda expuesta a hook/all-in.
- Se agrego una regla general para ADCs de rango muy bajo con support sustain contra bully de rango + support engage/catcher.
- Se registro el aprendizaje `Xayah vs Malphite/TahmKench` como bonus KB de matchup: Xayah gana fit contra engage frontal predecible y frontlines melee por R + plumas, sin saltarse el gate de meta/maestria.
- Se agrego `fallback_draft_veto` para impedir top picks de hypercarries sin movilidad/frontline contra dive o burst pesado, aunque sean fuertes en meta global.
- Se ajusto el perfil de Nilah para reflejar menor prioridad de linea y peor respuesta al poke/rango alto.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/champion_data.py`
- `data/draft_advisor/kb/structured/matchup_rules.json`
- `data/draft_advisor/adc_profiles.json`
- `data/draft_advisor/kb/research/matchups/mu-nilah-soraka-vs-caitlyn-nautilus.md`
- `data/draft_advisor/kb/research/matchups/mu-xayah-vs-malphite-tahmkench.md`
- `tests/draft_advisor/test_adc_priority_policy.py`

---

## [2026-05-04] Draft Advisor - prioridad ADC, meta y lenguaje

### Que se hizo
- Se agregaron controles de politica personal ADC: `excluded_from_recommendations` y `never_top_pick`.
- Vladimir quedo excluido de recomendaciones ADC por preferencia personal del usuario.
- Ezreal puede aparecer como alternativa si corresponde, pero nunca como primera opcion.
- Se reajusto el puntaje final ADC a `30%` maestria personal, `30%` meta scraping y `40%` fit de draft para que la composicion y los matchups vuelvan a pesar fuerte dentro de los candidatos validos.
- Se cambio el badge superior de `Datos` a `Data Dragon` y se agrego hora al campo `Actualizado`, usando `last_verified_at` con timestamp ISO.
- Se retiro del header la leyenda `ADC meta pendiente/OK` para evitar ruido visual; el estado del meta ADC queda visible en los chips de cada recomendacion.
- Se agrego `data/draft_advisor/personal_adc_mastery.json` como fuente editable de la tier list personal ADC, con la captura `KB/tier list adc 04 05 2026.png` como evidencia visual y entradas dudosas en `needs_review`.
- El scoring ADC ahora aplica un gate personal+meta antes de ordenar: top pick requiere maestria `S/A` y scraping ADC `S/A`; meta `B` o inferior queda como fallback, y tier personal `B` solo entra si el scraping es `S`.
- El puntaje final ADC queda en `30%` maestria personal, `30%` meta scraping y `40%` fit de draft. La logica de draft/KB vuelve a pesar fuerte, sin permitir que picks fuera de maestria/meta dominen.
- El Draft Advisor detecta snapshot ADC faltante/stale (>72h), devuelve warning y reporta campeones del scraping sin perfil local como `meta_only_missing_profiles`.
- La API y el front exponen chips de auditoria por pick: `Maestría`, `Meta`, `Subida`, `Scraping` y `Alternativa`.
- Se actualizaron golden drafts para reflejar el nuevo contrato ADC y evitar expectativas antiguas que favorecian picks meta-bajos como Ezreal/Vayne/KogMaw.
- Se saneo lenguaje visible del Draft Advisor: `Bard` se muestra como `Bardo`, `Master Yi` como `Maestro Yi`, los perfiles activos y notas de KB del Drafter quedaron en español, y se mantiene una lista acotada de terminos gamer permitidos (`ADC`, `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline`).
- `jungler_archetypes.json` ahora usa IDs canonicos (`MasterYi`, `LeeSin`, `JarvanIV`, `RekSai`, `XinZhao`, `MonkeyKing`, `Belveth`) para evitar drift entre nombres visibles y relaciones internas.

### Archivos modificados clave
- `data/draft_advisor/personal_adc_mastery.json`
- `src/riot_lol_cli/draft_advisor/champion_data.py`
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/schemas.py`
- `src/riot_lol_cli/draft_advisor/api.py`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `tests/draft_advisor/test_adc_priority_policy.py`
- `data/draft_advisor/kb/evals/golden_drafts.json`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`
- `KB/README.md`
- `.agent/rules/security-and-testing.md`

---

## [2026-05-03] Draft Advisor - fecha visible de ultimo update

### Que se hizo
- El header del Draft Advisor ahora muestra `Parche`, `Datos` y `Actualizado`, usando `last_verified_at` de `/api/v1/draft/meta/version-info`.
- Se agrego formateo local `dd/mm/aaaa` para la fecha de ultimo update y se subio el cache bust del front a `app.js?v=12`.
- Se ajusto el badge para tolerar el texto mas largo sin desbordar en pantallas chicas.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `docs/draft_advisor/README.md`

---

## [2026-05-03] Draft Advisor - auditoria y guardrails de datos

### Que se hizo
- Se agrego `tests/draft_advisor/test_data_integrity.py` para validar carga de `ChampionDataService`, conteos actuales y referencias con IDs canonicos en perfiles ADC/Support/Priority.
- Se documento el contrato de IDs canonicos en `.agent/rules/security-and-testing.md`, `AGENTS.md`, `docs/draft_advisor/README.md` y `projects/active/draft-advisor/README.md`.
- Se sincronizo `data_manifest.json` a `live_patch_label=16.9` y `static_data_version=16.9.1`, cubierto por el test de integridad.
- Se ajusto el scoring ADC para que Yasuo bot quede tratado como pick de nicho: requiere setup de airborne y valor real contra poke/proyectiles; queda penalizado contra dive/burst sin ese contexto.
- Se reforzo el scoring anti-tank para priorizar tank-shredders con alto anti-tank y DPS a objetivos, evitando que mages AP genericos tapen casos de Vayne/KogMaw.
- Se sincronizaron tests/evals: roster Support actual de 34 perfiles, golden draft que acepta `Kaisa` como carry movil con engage aliado, y test anti-enchanter que acepta counters hard actuales (`Camille`/`Pantheon`).
- Se limpio lint/formato dentro de `src/riot_lol_cli/draft_advisor` y `tests/draft_advisor`.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/api.py`
- `tests/draft_advisor/test_data_integrity.py`
- `tests/draft_advisor/test_antimeta.py`
- `tests/draft_advisor/test_notebook_kb.py`
- `data/draft_advisor/data_manifest.json`
- `data/draft_advisor/kb/evals/golden_drafts.json`
- `.agent/rules/security-and-testing.md`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`

---

## [2026-05-03] Draft Advisor - fix carga de campeones

### Que se hizo
- Se corrigio un drift de IDs en `data/draft_advisor/adc_profiles.json`: `Seraphine.best_with` apuntaba a `Jarvan`, pero el ID canonico en `champion_base.json` es `JarvanIV`.
- El error rompia la validacion cruzada de `ChampionDataService` y hacia que `/api/v1/draft/health` y `/api/v1/draft/champions` devolvieran `500`, dejando vacio el selector del front.
- Se verifico nuevamente la API local: health queda `ok` y el endpoint de campeones devuelve `172` campeones.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json`

---

## [2026-05-03] Draft Advisor — 7 nuevos perfiles ADC de magos AP bot lane

### Que se hizo
- Se corrio el Meta Scraper y se analizó el snapshot ADC completo (58 campeones, 3 fuentes, patch 16.9).
- Se identificaron 7 picks S/A tier sin perfil en `adc_profiles.json` — el Drafter los ignoraba completamente porque el scoring solo itera sobre `_adc_profiles.keys()`.
- Se crearon perfiles curados para: **Vladimir** (CS 84, WR 55%), **Karthus** (CS 82, WR 54.6%), **Seraphine** (CS 82, WR 54.6%), **Swain** (CS 77, WR 53.8%), **Veigar** (CS 75, WR 53.5%), **Ziggs** (CS 73, WR 53%), **Yasuo** (CS 64, WR 52.7%).
- Yasuo recibió teoría estratégica completa desde la KB del proyecto: condiciones de pick (airborne support, comp de Attack), counter proyectiles con Windwall, gestión de oleada (crash wave / evitar slow push enemigo).
- Se agregó `off_roles: ["Bot"]` a Vladimir, Karthus y Swain en `champion_base.json` (los otros ya lo tenían).
- Tendencia meta identificada: el patch 16.9 favorece **magos AP en bot lane** — Vladimir, Karthus, Seraphine se suman a Brand como picks tier S con la nueva runa.
- Servidor reiniciado para cargar los 32 perfiles ADC activos.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json` — 7 perfiles nuevos; total: 25 → 32 perfiles
- `data/draft_advisor/champion_base.json` — off_roles Bot agregado a Vladimir, Karthus, Swain

---

## [2026-05-03] Draft Advisor default ADC

### Que se hizo
- Se dejo `ADC` seleccionado por defecto en el selector de rol objetivo del front del Draft Advisor.
- Se elimino la leyenda `ADC (Tirador)` y toda referencia visible a `Tirador` en el front activo.
- Se alineo el estado inicial JS (`targetRole: 'adc'`) con el valor seleccionado en HTML.
- Se actualizo la leyenda del resumen a `Amenaza Enemiga al ADC`.
- Se actualizo el cache bust del front a `app.js?v=11`.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`

---

## [2026-05-02] Actualizacion Data Dragon assets 16.9.1

### Que se hizo
- Se agrego `scripts/update_ddragon_assets.py` para sincronizar items, CSV de items y splash arts desde Data Dragon con rate limiting configurable.
- Se actualizo la version default de Data Dragon a `16.9.1`.
- Se regenero `assets/data_id_imagen/items_ddragon.csv` y se descargaron `705` iconos de items.
- Se descargaron `61` splash arts faltantes en total y se regenero `data/splash-manifest.json` con `172` campeones y `2079` imagenes, alineado al catalogo oficial de skins base.
- Se agrego `data/ddragon-splash-catalog.json` con parche Data Dragon, fecha de importacion, locale y nombres localizados de skins para el front.
- Se regenero `outputs/splash-viewer.html` con badge visible de parche/importacion.
- Se corrigio el updater para saltar variantes `parentSkin` por defecto sin excluir skins base que tienen chromas.
- Se agrego alias de CDN para `Fiddlesticks` -> `FiddleSticks`, resolviendo los 3 splash faltantes del parche.
- Se elimino el duplicado legacy `Shyvana_Ironscale_Shyvana.jpg`; el asset canonico actual es `Shyvana_Shyvana_Ironscale.jpg`.
- Se verificaron skins recientes como `Annie Pandemonium` y `Vayne Maleficio Demoníaco`.
- Se auditaron filtros y ordenamientos del front: busqueda ahora cubre campeones y skins en `es_MX`/`en_US` sin depender de acentos, familias filtra sobre nombres localizados e ingleses, el modal usa la misma lista filtrada que la grilla, el orden default usa `skinNum` y el shuffle deterministico ya no genera indices negativos.

### Archivos modificados clave
- `scripts/update_ddragon_assets.py` - nuevo actualizador canonico de assets Data Dragon.
- `src/riot_lol_cli/settings.py` - default Data Dragon `16.9.1`.
- `assets/items/`, `assets/data_id_imagen/items_ddragon.csv`, `assets/splash_arts/` - assets actualizados.
- `data/ddragon-splash-catalog.json`, `data/splash-manifest.json`, `outputs/splash-viewer.html` - derivados regenerados.

---

## [2026-05-02] Limpieza y unificacion de Markdown

### Que se hizo
- Se consolidaron las reglas de agentes en cuatro documentos canonicos dentro de `.agent/rules/`.
- `CLAUDE.md` quedo como shim corto y `AGENTS.md` sigue como entrypoint raiz para agentes.
- ADC Tracker se absorbio dentro de `docs/meta_analyzer/README.md` y se elimino su carpeta documental separada.
- Los reportes de seguridad y auditoria de datos se absorbieron en `.agent/rules/security-and-testing.md` y `docs/draft_advisor/README.md`.
- KB NotebookLM se redujo a un unico `KB/notebooklm/sintesis/README.md`; las notas sueltas de fuentes y jungla se integraron en `KB/README.md`.
- Junglas Pro consolido sus docs operativas en `projects/active/junglas-pro/research-notes.md`.
- El handoff visual para Claude Design quedo unificado en `claude-design-handoff/README.md`.
- Se elimino la copia paralela de docs historicas; ese material quedo absorbido en bitacora y luego en `projects/legacy/`.

### Archivos modificados clave
- `.agent/rules/*.md` - nueva taxonomia de reglas para agentes.
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/README.md`, `projects/README.md` - indices alineados a la estructura reducida.
- `docs/meta_analyzer/README.md`, `docs/draft_advisor/README.md` - absorcion de docs tecnicas redundantes.
- `KB/README.md`, `KB/notebooklm/sintesis/README.md` - KB consolidada sin notas sueltas redundantes.
- `projects/active/junglas-pro/research-notes.md` y `claude-design-handoff/README.md` - proyectos standalone con docs atomizadas.

---

## [2026-05-02] Scripts bat — levantamiento de frontends

### Que se hizo
- Se creo `scripts/bat/draft_advisor.bat`: launcher individual para el Draft Advisor (puerto 8001), siguiendo el mismo patron que `meta_scraper.bat` (verifica venv, setea PYTHONPATH, imprime URLs).
- Se creo `scripts/bat/levantar_todo.bat`: bat maestro idempotente que levanta los 3 servidores Python (Draft Advisor :8001, Meta Scraper :8002, Meta Analyzer :8000) en ventanas CMD minimizadas con titulo, y abre los 4 frontends en el navegador por defecto. Antes de arrancar cada servidor verifica si el puerto ya esta ocupado con `netstat` y lo omite si esta corriendo — permite correrlo varias veces sin duplicar procesos.
- Frontends cubiertos por el bat maestro:
  - `http://localhost:8001/draft` — Draft Advisor SPA
  - `http://localhost:8002` — Meta Scraper dashboard
  - `outputs/splash-viewer.html` — galeria de splash arts (HTML estatico)
  - `projects/active/junglas-pro/index.html` — Junglas Pro viewer (HTML estatico)

### Archivos nuevos / modificados
- `scripts/bat/draft_advisor.bat` — launcher standalone Draft Advisor; corre el proceso oculto y redirige stdout/stderr a `logs/draft_advisor.log` y `logs/draft_advisor.err`
- `scripts/bat/levantar_todo.bat` — bat maestro idempotente; lanza los 3 servidores como procesos ocultos (sin ventanas CMD) via PowerShell `Start-Process -WindowStyle Hidden -RedirectStandardOutput/Error`, luego abre los 4 frontends en el navegador
- `logs/` — directorio creado en tiempo de ejecucion para los logs de cada servidor

---

## [2026-05-02] Traduccion completa al español — Draft Advisor (scoring + perfiles ADC/Support)

### Que se hizo
- Se tradujeron al español rioplatense las 6 funciones generadoras de texto del modo ADC en `scoring.py`: `_generate_strengths()`, `_generate_risks()`, `_generate_play_pattern()`, `_generate_one_liner()`, `_compare_advantages()`, `_compare_disadvantages()`. El modo Support ya estaba en español.
- Se reescribieron todos los campos de texto usuario-visible de los 24 perfiles ADC en `adc_profiles.json`: `strengths`, `weaknesses`, `draft_notes`, `power_spikes`.
- Se tradujeron 20 de los 34 perfiles Support en `support_profiles.json` que estaban en inglés: Leona, Nautilus, Thresh, Pyke, Lulu, Janna, Soraka, Milio, Lux, Karma, Yuumi, Renata, Zyra, Brand (sup), Xerath, Vel'Koz, Swain, Senna, Bard, Sona. Los 14 restantes ya estaban en español.
- Todos los `patch` actualizados a "16.9" y `last_updated` a "2026-05-02".
- El servidor Draft Advisor requiere reinicio para aplicar los cambios (usa módulos en memoria).

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py` — 6 funciones ADC: strings de fortalezas, riesgos, patron de juego, one-liner, ventajas/desventajas comparativas
- `data/draft_advisor/adc_profiles.json` — 24 perfiles ADC completamente traducidos
- `data/draft_advisor/support_profiles.json` — 20 perfiles Support traducidos de inglés a español

---

## [2026-05-02] Brand ADC — perfil curado + meta integrado desde snapshot

### Que se hizo
- Se agrego el perfil ADC de Brand a `adc_profiles.json` (patch 16.9). Brand es un mago AP jugado en bot lane, actualmente tier S con 54%+ WR en las 3 fuentes. Perfil: anti_tank=10, synergy_engage_support=10, execution_difficulty=7, solo_queue_stability=5.
- Se agrego `"Bot"` al `off_roles` de Brand en `champion_base.json` para que aparezca en el filtro de rol del picker del Draft Advisor.
- Se disparo un scraping ADC fresco que confirmo Brand en el snapshot con WR=54.19%, climb_score=81.02, tier S (fuentes: OP.GG, LoLalytics, U.GG).
- El motor de scoring aplica automaticamente el meta bonus maximo (+12) a Brand en `solo_queue_reliability` via `_score_adc_climb_meta_bonus()`.
- Resultado verificado: Brand aparece como alternativa #1 en drafts con soporte engage (Leona/Nautilus) y enemigos tankudos.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json` - nuevo perfil Brand ADC, patch actualizado a 16.9
- `data/draft_advisor/champion_base.json` - off_roles Brand: agregado "Bot"

---

## [2026-05-01] Meta Scraper multi-fuente + integración Support en Draft Advisor

### Que se hizo
- Se agrego el adapter `ugg.py` para U.GG (tabla React `.rt-tr`/`.rt-td`, links `/lol/champions/{slug}/build/`).
- Se corrigio el adapter `lolalytics.py` para ADC: la extraccion de stats pasó a basarse en indices de celda fijos (WR=child[5], PR=child[6], BR=child[7]) en lugar de buscar `%` en el texto libre, que no funcionaba para el endpoint bot lane.
- El Meta Scraper ahora opera con 3 fuentes simultaneas (OP.GG, LoLalytics, U.GG) para ADC y Support.
- Se agrego la integracion de snapshot de Support al Draft Advisor: `champion_data.py` carga `latest_support_tier.json` de forma opcional; `scoring.py` aplica `_score_support_meta_bonus()` acotado a `[-10, +12]` en `_score_supp_solo_queue()`, paralelo a lo que ya existia para ADC.
- Se extendiò el dashboard del Meta Scraper (puerto 8002): tabs Soporte/ADC, columna Climb Score visible solo en ADC, boton Actualizar que dispara el endpoint correcto segun el tab activo.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/adapters/ugg.py` - nuevo adapter U.GG
- `src/riot_lol_cli/meta_scraper/adapters/lolalytics.py` - fix extraccion ADC por indice de celda
- `src/riot_lol_cli/meta_scraper/server.py` - registro de UggAdapter
- `src/riot_lol_cli/meta_scraper/static/index.html` y `app.js` - tabs rol, climb_score, scrape por rol
- `src/riot_lol_cli/draft_advisor/champion_data.py` - carga opcional de support meta snapshot
- `src/riot_lol_cli/draft_advisor/scoring.py` - `_score_support_meta_bonus()`

## [2026-05-01] Meta Scraper ADC para climb y ajuste del Draft Advisor

### Que se hizo
- Se extendio Meta Scraper para scrapear tier lists de ADC ademas de Support desde los adapters existentes de OP.GG y LoLalytics.
- Se agrego normalizacion por rol y `climb_score` basado en winrate, pickrate y banrate.
- Se agregaron endpoints `GET /api/v1/meta/adc/tier`, `GET /api/v1/meta/adc/champion/{champion_id}` y `POST /api/v1/meta/scrape/adc`.
- El Draft Advisor ahora carga opcionalmente `data/meta_scraper/normalized/latest_adc_tier.json` y usa sus stats como ajuste acotado de `solo_queue_reliability` para recomendaciones ADC.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/` - scraping/normalizacion ADC y endpoints nuevos.
- `src/riot_lol_cli/draft_advisor/champion_data.py` y `scoring.py` - consumo opcional del snapshot ADC.
- `tests/meta_scraper/test_normalizer.py` - cobertura de `climb_score` y merge ADC.
- `AGENTS.md`, `docs/draft_advisor/README.md`, `projects/active/*/README.md` - documentacion sincronizada.

## [2026-04-30] Reorganizacion hibrida por proyecto y absorcion de analysis

### Que se hizo
- Se promovio la investigacion de junglas desde legacy a `projects/active/junglas-pro/` como proyecto activo standalone.
- Se actualizo `projects/README.md` como indice principal por proyecto y se quitaron referencias a Junglas Pro desde legacy.
- Se absorbio la informacion vigente de los reportes de auditoria en `AGENTS.md`, `projects/README.md`, `docs/README.md`, reglas de agentes, KB y esta bitacora.
- Se agrego una nota en KB para definir que conocimiento de jungla puede entrar al Draft Advisor sin copiar la investigacion completa.
- Se elimino la carpeta de auditoria como fuente activa tras distribuir sus decisiones, inventario, testing, CI/linting y dead-code en documentos canonicos.

### Archivos modificados clave
- `projects/active/junglas-pro/README.md` - manifiesto del proyecto activo de junglas.
- `projects/README.md` - mapa operacional hibrido y resumen historico.
- `AGENTS.md`, `README.md`, `docs/README.md` - indices actualizados sin carpeta de auditoria separada.
- Reglas de testing/coding - absorcion de notas de CI, Ruff y dead code.
- KB - politica de absorcion estrategica desde Junglas Pro.

## [2026-04-30] Organizacion del repo por proyectos y limpieza documental

### Que se hizo
- Se agrego `projects/` como mapa operativo por proyectos activos y legacy.
- Se crearon manifiestos para CLI Match History, Splash Gallery, Meta Analyzer + Dashboard, Draft Advisor, Meta Scraper y assets/datos Riot.
- Se movieron proyectos no runtime a `projects/legacy/`: copia antigua `riot-lol-cli`, investigacion de junglas profesionales, scraper de items/Data Dragon, screenshots ADC y proyectos de notas de parche.
- Se agruparon scripts manuales sueltos en `projects/dev-scratch/` y se elimino el directorio `scratch/` vacio.
- Se alinearon `README.md`, `AGENTS.md`, `docs/README.md`, reglas de agentes y reportes de auditoria con la nueva estructura.
- Se reemplazo `scripts/bat/ROADMAP_DOCUMENTACION.sh` por un roadmap breve apuntando a docs canonicas actuales.
- Se fusionaron `REORGANIZATION_LOG.md` y `REORGANIZATION_REPORT.md` en un historial de reorganizacion luego absorbido por docs canonicas.

### Archivos modificados clave
- `projects/README.md` y `projects/active/*/README.md` - mapa por proyectos.
- `projects/legacy/` - proyectos historicos agrupados.
- `AGENTS.md` - mapa maestro actualizado con la organizacion por proyectos.
- Reglas de agentes - regla explicita de revisar `AGENTS.md`, `projects/README.md` y `docs/README.md`.
- `README.md`, `CLAUDE.md`, `docs/README.md` y reportes de auditoria previos - documentacion alineada.

---

## [2026-04-30] Actualizacion exhaustiva de AGENTS.md como mapa maestro

### Que se hizo
- Se reescribio `AGENTS.md` raiz como documento canonico para agentes: arquitectura, subsistemas, flujos runtime, datos, APIs, tests, docs vivas, gotchas y deuda conocida.
- Se documento el estado real del working tree, incluyendo `meta_api`, `meta_scraper`, `rendering.py`, `splash.py`, la copia legacy ahora ubicada en `projects/legacy/riot-lol-cli/` y el drift actual de datos.

### Archivos modificados clave
- `AGENTS.md` — pasa a ser el mapa maestro exhaustivo del repositorio para agentes IA.
- `bitacora_de_cambios.md` — registra esta iteracion documental segun el protocolo antidraft.

---

## [2026-04-30] Consolidacion de Markdown activos en docs/

### Que se hizo
- Se fusionaron los documentos redundantes de dashboard, Meta Analyzer y ADC Tracker en READMEs canonicos por subsistema.
- Se actualizo `docs/README.md` para apuntar a la nueva estructura documental activa.
- Los documentos originales completos se preservaron temporalmente en archivo historico para no perder detalle.

### Archivos modificados clave
- `docs/dashboard/README.md` — guia canonica del dashboard.
- `docs/meta_analyzer/README.md` — guia canonica del Meta Analyzer.
- ADC Tracker - guia canonica inicial, luego absorbida en Meta Analyzer.
- `docs/README.md` — indice actualizado de documentacion activa.

---

## [2026-04-28 — sesión 2] Meta Scraper — Subsistema de extracción de datos de meta de soporte

### Motivación

Los `support_profiles.json` están basados en curación manual experta, pero los datos quedan desactualizados con cada parche. Este subsistema automatiza la recolección de winrates, pickrates, banrates y tier lists desde plataformas de estadísticas externas (LoLalytics, OP.GG).

### Nuevo subsistema: `meta_scraper` (puerto 8002)

**Arquitectura de 3 capas:**
1. **Capa 1 (XHR):** intercepción de APIs internas JSON — la más limpia y rápida
2. **Capa 2 (HTML parsing):** parsing de HTML server-side con BeautifulSoup
3. **Capa 3 (Playwright):** browser headless con stealth para sitios con anti-bot agresivo

**Archivos nuevos:**
- `src/riot_lol_cli/meta_scraper/__init__.py` — módulo raíz
- `src/riot_lol_cli/meta_scraper/server.py` — FastAPI en :8002 (7 endpoints + frontend)
- `src/riot_lol_cli/meta_scraper/orchestrator.py` — orquestador con retry y rate-limiting
- `src/riot_lol_cli/meta_scraper/normalizer.py` — merge multi-plataforma + tier calculation
- `src/riot_lol_cli/meta_scraper/adapters/base.py` — BaseAdapter con User-Agent rotation + humanized delays
- `src/riot_lol_cli/meta_scraper/adapters/lolalytics.py` — Playwright para LoLalytics (SPA, necesita JS)
- `src/riot_lol_cli/meta_scraper/adapters/opgg.py` — Playwright para OP.GG (403 a HTTP directo)
- `src/riot_lol_cli/meta_scraper/static/index.html` — dashboard midnight navy con tier list
- `src/riot_lol_cli/meta_scraper/static/styles.css` — score bars, tier badges, glassmorphism
- `src/riot_lol_cli/meta_scraper/static/app.js` — renderizado + filtros + scraping trigger

**Datos:**
- `data/meta_scraper/` — JSON timestamped organizado por plataforma (raw/) y normalizado (normalized/)
- `data/meta_scraper/manifest.json` — índice de snapshots

**Decisiones de diseño:**
- JSON con timestamp como "BD momentánea" (no SQL) — decisión del usuario
- Design system reutilizado del Draft Advisor (tokens.css, compat-spa.css)
- Ambas plataformas requieren Playwright porque no ofrecen API pública y bloquean httpx directo

### Tests
- **11 tests nuevos** en `tests/meta_scraper/test_normalizer.py` (tier calc, name normalization, merge), 11/11 passing

### Documentación
- `AGENTS.md` actualizado con nuevo subsistema, puerto 8002, entry point
- `docs/getting-started.md` actualizado con sección Meta Scraper

---

## [2026-04-28] Definición de SSoT para Scraping de Datos

### Qué se hizo
- **Migración y Extensión:** Se restauró el archivo en cuarentena y se integró a la base de conocimiento.
- Se amplió la lista original (U.GG, OP.GG, LoLalytics, Blitz.gg, Mobalytics, Probuilds.net, METAsrc) incorporando 4 nuevas fuentes de alto nivel.
- **Nuevas fuentes agregadas:** Onetricks.gg (datos OTP), LeagueOfGraphs (macro estadísticas), Gol.gg (Pro Play), y DeepLoL.gg (análisis de impacto temprano).
- Se definió este documento como *Single Source of Truth* (SSoT) para guiar la construcción de los futuros adaptadores de scraping.

### Archivos clave
- **[NUEVO]** Nota SSoT para extracción de datos en KB, luego absorbida en `KB/README.md`.
- **[ELIMINADO]** Archivo legacy de referencias de paginas tras su migración.

---

## [2026-04-27 — sesión 3b] D6-D9: item_path, Crash & Move, jungler classification, queue hints

### D6: item_path en support_profiles
- **[NUEVO]** `ItemPath` model en `schemas.py` (evolution, core_items, situational_items, boots, first_back)
- Inyectado `item_path` a los **27 soportes** basado en la economía asimétrica (KB síntesis 06)
- 5 evoluciones mapped: Bloodsong (AD), Solstice Sleigh (engage tank), Celestial Opposition (warden), Zaz'Zak's (mage), Dream Maker (enchanter)

### D7: Crash & Move en play_pattern_template
- **4 roamers** (Pyke, Bard, Thresh, Rakan): templates enriquecidos con Crash & Move + 3 Chequeos
- **4 anchored** (Soraka, Yuumi, Milio, Sona): templates con B-Prox alta + "Crash & Move NO aplica"
- Fuente: KB/notebooklm/sintesis/07 y 08

### D8: Jungler archetype classification
- **[NUEVO]** `jungler_archetypes.json` con 4 arquetipos: engage, farm_scaling, early_gank, control
- **[NUEVO]** `classify_jungler_archetype()` + `get_jungler_scoring_modifier()` en champion_data.py
- **Wiring**: `_score_supp_ally_synergy()` ahora usa clasificación explícita (JSON) con fallback a heurística por tags
- Scoring modifiers: engage_jg → boost enchanter/poke, farm_jg → boost engage/catcher

### D9: queue_style_hints
- **[NUEVO]** `queue_style_hints.json` con 4 colas: ranked_solo, ranked_flex, clash, normal
- **Weight adjustments**: se aplican en `_compute_weights()` (ej: clash → ally_synergy +5%, blind_pick -5%)
- **Archetype boosts**: flat bonus en raw scores (ej: clash engage +4pts, normal enchanter +2pts)
- Fuente: KB/notebooklm/sintesis/09 (meta regional LCK/LPL)

### Tests
- 51 → **66 tests** (+15 nuevos: 4 D6 + 3 D7 + 5 D8 + 3 D9), 0 regresiones

---


## [2026-04-27 — sesión 3] Auditoría profunda KB → Código (12 drift issues)

### Fuentes auditadas
- 8 archivos markdown KB, 2 PDFs (via 9 síntesis NotebookLM), 1 infografía, 1 guía de estudio

### Drift Issues Resueltos

| # | Issue | Fix |
|---|-------|-----|
| D1 | Tabla sinergias 10×15 no alimentaba el motor | **[NUEVO]** `synergy_matrix.json` + `get_synergy_score()` + integrado en scoring |
| D2 | Sona mencionada en SUPPORT_THEORY pero sin perfil | **[NUEVO]** perfil Sona en `support_profiles.json` (27 totales) |
| D3 | `engage.loses_to` no incluía warden | **FIX** `strategic_triangle.json` v1.2 — bidireccionalidad completa |
| D4 | `arquetipos-de-soporte.md` no mencionaba Warden | **FIX** reescritura completa con §5 Warden + tabla 5 arquetipos |
| D5 | 50 matchups lane individuales no codificados | **FIX** `matchup_rules.json` poblado con matchups + scoring numérico |
| D10 | `enchanter_pure.beats: []` (debería beat engage) | **FIX** ahora `beats: ["engage"]` per SUPPORT_THEORY §4 |
| D11 | `filosofia-de-pickeo.md` decía 5 factores (eran 6) | **FIX** actualizada tabla a 6 factores con pesos v1.1 |

### Archivos nuevos
- `data/draft_advisor/kb/structured/synergy_matrix.json` — 26 soportes × 15+ ADCs cuantitativo

### Archivos modificados
- `strategic_triangle.json` v1.1→v1.2: +Bard a catcher, +Senna a enchanter_pure, bidireccionalidad
- `matchup_rules.json` v1.0→v1.2: +50 matchups lane individuales, bullies/scalers
- `support_profiles.json`: +Sona (27 total)
- `champion_data.py`: +loaders synergy_matrix + matchup_rules, +4 accessors
- `scoring.py`: synergy_matrix integrada en `_score_supp_ally_synergy()`, lane matchups en `_score_supp_enemy_matchup()`
- `KB/arquetipos-de-soporte.md`: +§5 Warden, subdivisions enchanter
- `KB/filosofia-de-pickeo.md`: tabla 5→6 factores

### Tests
- 36 → **49 tests** (+13 nuevos, 0 regresión)

---

## [2026-04-27 — sesión 2b] Phase 3: 26 soportes + endpoint triángulo + ajuste de pesos

### Cambios

**`data/draft_advisor/support_profiles.json`** (Phase 1 → Phase 3):
- 9 perfiles nuevos: Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard
- Total: **26 soportes** (Engage 4, Enchanter 8, Poke/Mage 6, Warden 2, Catcher 6)
- Cada perfil incluye: 21 stats numéricas, sinergias ADC, counter-matchups, play_pattern_template en español

**`data/draft_advisor/scoring_weights.json`** (v1.0 → v1.1):
- `ally_synergy`: 0.25 → 0.30 (alineado con KB/filosofia que prioriza sinergia ADC al 30-35%)
- `blind_pick_safety`: 0.10 → 0.05 (compensación; la safety importa menos con información)
- Justificación: la sinergia con el ADC es el factor #1 del soporte (KB doc)

**`src/riot_lol_cli/draft_advisor/api.py`** — 2 endpoints nuevos:
- `GET /api/v1/draft/strategic-triangle/{champion_id}` — inspección del triángulo estratégico
- `GET /api/v1/draft/champions/supports` — roster completo de soportes con fine-grained archetype

### Tests

- **36/36 tests passing** (sin regresión)

---

## [2026-04-27 — sesión 2] Auditoría de drift + expansión triángulo estratégico + comp predominance consumido

### Motivación

Auditoría completa del Draft Advisor post-integración de NotebookLM. Se detectaron 6 issues de drift entre KB, datos estructurados y código. Esta sesión los corrige e implementa funcionalidad nueva.

### Hallazgos de Drift (6 issues)

| # | Drift | Severidad | Estado |
|---|-------|-----------|--------|
| 1 | `comp_predominance.json` cargado en `champion_data.py` pero **nunca consumido** en scoring | Alta | ✅ Corregido |
| 2 | `support_archetypes.json` tiene `engage_hybrid` (Pyke) no mapeado en strategic_triangle | Media | ✅ Pyke ya estaba en `catcher` fine-grained |
| 3 | `matchup_rules.json` vacío (235 bytes, `rules: []`) | Alta | ✅ Poblado con reglas archetype-vs-comp |
| 4 | KB/SUPPORT_THEORY.md define Warden (Braum, Taric, TahmKench) sin entrada en strategic_triangle | Alta | ✅ Añadido archetype `warden` |
| 5 | Tests fallan por `ModuleNotFoundError` (falta PYTHONPATH en pyproject.toml) | Alta | ✅ Añadido `pythonpath = ["src"]` |
| 6 | KB/filosofia pesos (35% ally, 20% enemy, 20% gap, 10% jungle, 15% blind) difieren de scoring_weights.json (25/20/10/20/10/15) | Baja | ℹ️ Documentado como diferencia de diseño |

### Cambios de Código

**`data/draft_advisor/kb/structured/strategic_triangle.json`** (v1.0 → v1.1):
- Nuevo archetype `warden`: `["Braum", "Taric", "TahmKench"]`
- Warden beats: engage, catcher. Loses_to: poke.
- Rakan añadido a `catcher` (faltaba).
- Catcher ahora `loses_to: ["engage", "warden"]` (antes solo engage).

**`data/draft_advisor/kb/structured/matchup_rules.json`** (vacío → poblado):
- `archetype_vs_enemy_comp` con 5 reglas (vs_dive, vs_poke, vs_pick, vs_scaling, vs_tank).
- Warden incluido en `best_archetypes` para dive y pick comps.
- `lane_bullies` y `lane_scalers` clasificados.

**`src/riot_lol_cli/draft_advisor/scoring.py`**:
- `_apply_comp_predominance_bonus()` — nuevo método que consume comp_predominance.json.
- `_teamfight_shape_to_comp_type()` — mapea TeamfightShape a comp type keys.
- `_score_supp_comp_gap_fill()` — ahora llama a `_apply_comp_predominance_bonus()` y reconoce `WARDEN` en frontline check.

**`src/riot_lol_cli/draft_advisor/champion_data.py`**:
- `get_comp_predominance()` — nuevo accessor público para comp_predominance data.

**`pyproject.toml`**:
- `pythonpath = ["src"]` en `[tool.pytest.ini_options]` — fix de PYTHONPATH para tests.

### Tests

- 9 tests nuevos en `test_notebook_kb.py` (warden classification, triangle interactions, comp predominance).
- **36/36 tests passing** (incluido regression suite).

---

## [2026-04-27] KB extendida con material NotebookLM + nuevas reglas de scoring

### Motivación

Dario sumó 4 fuentes pesadas a `KB/notebooklm/` (2 PDFs, 1 infografía, 1 guía de estudio en texto plano) extraídos de NotebookLM. Las fuentes contienen conceptos avanzados que el motor del Draft Advisor no estaba aplicando: el triángulo estratégico fino (Engage > Poke > Sustain con eje invertido Disengage > Engage), sinergias 2v2 con winrate medido, predominancia entre las 5 composiciones canónicas, y vocabulario nuevo (J Prox, B Prox, Crash & Move, Regla de los 3 Chequeos).

### Cambios

**KB humano (markdown):**
- 10 docs nuevos en `KB/notebooklm/sintesis/` (INDEX + 9 ejes temáticos): paradigma del arquitecto, jerarquía de pick order, las 5 composiciones, triángulo Engage/Poke/Sustain, sinergias medidas, economía asimétrica, regla de los 3 chequeos, Crash & Move, meta regional LCK vs LPL.
- `KB/README.md` extendido con sección "Material extendido NotebookLM".

**Datos estructurados (3 JSON nuevos consumidos por el motor):**
- `data/draft_advisor/kb/structured/measured_synergies.json` — 4 sinergias 2v2 con WR medido (Samira+Naut 53.7%, Lucian+Nami 54.0%, Ashe+Sera 54.7%, Jinx+Thresh 54.3%) + 10 heurísticas pro-scene. Confidence dual: `measured` vs `heuristic` con bonus diferenciado.
- `data/draft_advisor/kb/structured/strategic_triangle.json` — Triángulo fine-grained: subdivide enchanter en `enchanter_disengage` (Janna, Lulu, Milio, Renata, Karma) vs `enchanter_pure` (Soraka, Yuumi, Nami). Aplica el eje invertido Disengage > Engage (Wardens invalidan iniciadores).
- `data/draft_advisor/kb/structured/comp_predominance.json` — Ciclo piedra-papel-tijera entre las 5 comps (Attack > Siege > Protect > Catch > Attack > Siege; Split asimétrica).

**Lógica del motor (scoring.py):**
- `_score_measured_synergy(adc_id, supp_id)` — busca pareja en JSON, devuelve bonus interpolado por WR (cada 1pp sobre 50% = +3 score, hasta 15pts).
- `_apply_strategic_triangle(my_archetype, enemy_supp_archetype)` — devuelve +10 si counterea, -8 si es counter-pickeable.
- Integración en `_recommend_support()` como bonificadores aditivos al `enemy_matchup` y `ally_synergy`.

### Archivos modificados clave
- `KB/README.md` — sección "Material extendido NotebookLM"
- `src/riot_lol_cli/draft_advisor/scoring.py` — 2 funciones nuevas + integración en pipeline de scoring
- `src/riot_lol_cli/draft_advisor/champion_data.py` — loaders de los 3 JSON nuevos
- `docs/draft_advisor/README.md` — sección "Reglas de scoring (sinergias medidas + triángulo)"

---

## [2026-04-26] UI Redesign — Draft Advisor SPA (dark navy, WCAG AA, i18n parcial)

### Motivación

La UI tenía fondos grises demasiado claros, barras de score de 6px ilegibles, tarjetas de alternativas con layout roto (texto desbordando columnas de 2-col), y términos de UI en inglés (MEDIUM, LOW, HIGH) mezclados con la interfaz en español.

### Cambios

- **`compat-spa.css`**: paleta midnight navy (`--bg-primary: #04080f`, `--bg-card: #091520`), bordes más visibles, texto secundario más contrastado para WCAG AA.
- **`styles.css`**: barras de score `6px → 10px`, labels `130px → 182px`, valores en Outfit Bold. Alt cards rediseñadas con `.alt-info` + `.alt-score-number` + `.alt-compare` vertical. Nuevas clases `.comp-badge`. Reduced-motion explícito.
- **`app.js`**: `threatLevelEs()` y `confidenceEs()` traducen nivel de amenaza y confianza a español. `scoreBarGradient()` colorea barras dinámicamente. `renderAlternatives()` con nuevo HTML. `renderDraftSummary()` con `.comp-badge` en lugar de estilos inline.
- **Accesibilidad**: `aria-label` en `.modal-close` y `.remove-btn`. Desktop-first documentado en `CLAUDE.md`.

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/design-system/compat-spa.css`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `CLAUDE.md`

---

## [2026-04-26] Design System Unificado + Support Advisor MVP

### Support Advisor (target_role: ADC | SUPPORT)

Se extendió el Draft Advisor para recomendar **Soportes** además de ADCs, sin clonar el módulo. Cambios:

- **`schemas.py`**: `AdvisorMode` enum, `SupportProfile` model, `SupportArchetype` enum, `target_role` en `DraftState`.
- **`champion_data.py`**: carga de `support_profiles.json`, helpers `get_support_ids()`, `get_support_profile()`.
- **`scoring.py`**: refactor `recommend()` enruta por `target_role`. Nuevo `_recommend_support()` con 6 factores de scoring (ally_synergy 35%, enemy_matchup 20%, comp_gap_fill 20%, scaling_fit 15%, solo_queue 10%).
- **`api.py`**: endpoint `GET /api/v1/draft/champions/supports`.
- **Data**: `data/draft_advisor/support_profiles.json` (10 soportes core), `data/draft_advisor/kb/structured/support_archetypes.json`; el antiguo `data/supports_list.json` fue absorbido y eliminado en la limpieza 2026-05-07.
- **KB/**: 6 documentos de base de conocimiento estratégico (filosofía, arquetipos, sinergias, matchups, game plans, amenazas).
- **Frontend**: `state.targetRole`, select de Rol Objetivo, payload incluye `target_role`.

**Soportes fase 1:** Leona, Nautilus, Thresh, Lulu, Janna, Soraka, Milio, Lux, Pyke, Karma.
**Fase 2 pendiente:** 14 soportes adicionales (Blitzcrank, Rakan, Rell, Alistar, Nami, Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard).

### Design System — Migración completa de tokens CSS

Se unificó la paleta de tokens de las 4 surfaces (Draft Advisor SPA, Match History, Splash Viewer, Dashboard) bajo un sistema canónico.

**Archivos nuevos en `static/design-system/`:**
- `tokens.css` — 169 líneas, tokens canónicos `--arc-*`, `--forge-*`, `--state-*`
- `components.css` — 506 líneas, clases `.btn`, `.card`, `.pill`, `.score-bar`
- `compat-spa.css` — aliases legacy para el SPA (tokens con valores distintos al canónico)
- `compat-dashboard.css` — aliases legacy para el Dashboard (referencia)

**Migración por surface:**
- Splash Viewer: `--hextech-* → --arc-*`, `--piltover-* → --forge-*`, 16 familias
- Match History: ídem + `--victory/--defeat → --state-success/--state-error`, 18 familias
- SPA (styles.css + app.js): 7 familias migradas, NO MIGRAR tokens quedan via compat-spa
- Dashboard (f-string Python): `--accent/--secondary/--dark/--danger` renombrados

**Componentes adoptados en el SPA:**
- `.btn .btn-primary` en "Recomendar Pick"
- `.btn .btn-ghost` en role-filters del modal y modal-close
- `.pill .pill-gold` en patch-badge

**Pool de Campeones comentado** en `index.html` como upgrade futuro (backend ya implementado).

**Documentación generada:**
- `docs/design-system.md` — referencia completa del sistema de tokens y componentes
- `docs/draft_advisor/README.md` — actualizado con Support Advisor, endpoints, flujo
- `docs/getting-started.md` — sección Draft Advisor actualizada con flujo de uso real

---

## [2026-04-24] Modernización Arquitectónica y Estabilización

Hemos completado exitosamente las tareas de estabilización y modernización descritas en el plan post-refactorización. El repositorio ha pasado de ser un conjunto de scripts con algunas inconsistencias a un paquete moderno y escalable.

### 1. Limpieza de Linting (Ruff)
Se corrigieron todos los errores residuales reportados por `ruff`:
- Importaciones rotas de tipado (`DraftState`, `RecommendationOutput`) resueltas usando `TYPE_CHECKING` guards para evitar dependencias circulares.
- Variables muertas eliminadas en los scripts de descarga de splash arts.
- Solucionado el manejo de excepciones genéricas (`bare except`) en el validador de frescura de datos.

Además, se **amplió la configuración de Ruff** en `pyproject.toml` agregando reglas más estrictas (`I` para ordenamiento automático de imports y `UP` para modernización de sintaxis antigua como `typing.Dict`). Todo el código fue auto-formateado bajo este nuevo estándar.

### 2. API Client Modernizado (`httpx`)
El cliente original `api.py` fue ampliado con una versión asíncrona robusta.
- Se agregó la clase `AsyncRiotClient` que usa `httpx.AsyncClient`.
- Implementa **backoff exponencial real asíncrono** usando `asyncio.sleep()` en lugar de bloquear el thread cuando Riot responde con `429 Rate Limit`.
- El cliente original síncrono fue conservado por compatibilidad estricta con la CLI, pero su manejo de rate-limits fue pulido bajo el mismo estándar.
- Se agregaron tests asíncronos con mocks completos usando `pytest-asyncio`.

### 3. Schemas Estrictos (Pydantic V2)
El corazón de la recolección de datos era frágil por usar diccionarios anidados. 
- Se crearon modelos Pydantic V2 en `src/riot_lol_cli/schemas/riot_api.py` para parsear fuertemente el payload de `Match-V5`.
- Incluyen `extra="allow"` como blindaje: si Riot Games añade campos nuevos el día de mañana a las partidas, el parser no se romperá en producción.
- El `MetaDataCollector` (tanto en su versión file como db) ahora instancia estos objetos y usa factorías para destilar los stats de forma tipada, logrando evitar `KeyErrors` accidentales si un stat no viene.

### 4. Transición a Logging Estándar
Todos los módulos que corren como servidores o jobs de fondo (`api_server.py`, `server.py` del Draft, `data_collector_db.py`, `tier_generator.py`) pasaron de usar `print()` a utilizar `logging` estándar de Python.
- Los logs ahora tienen niveles reales (`INFO`, `WARNING`, `ERROR`).
- Módulos CLI interactivos (como los comandos `click`) mantienen su output limpio.

### 5. Testing y Cobertura (`pytest-cov`)
- Se incluyó `pytest-cov` a las herramientas de desarrollo.
- Se escribieron pruebas para los nuevos modelos de Pydantic y el cliente asíncrono.
- La ejecución de `pytest` indica que **todos los tests pasan** y la **cobertura del código en `src/` subió a >50%**.
- Hemos integrado este reporte a la nueva base de GitHub Actions (`ci.yml`) que ahora fallará si la cobertura baja de 30%.

---

## [2026-05-24] Esports Research C.1 - tests de BaseEsportsAdapter

Se agrego cobertura dedicada para `BaseEsportsAdapter`, enfocada en los paths de mayor riesgo del audit V0:

- headers HTTP identificables (`User-Agent` + `From`);
- parsing de `Retry-After`;
- retry de 429 con y sin header;
- 403/401 como `PermissionError` sin retry;
- retries de `httpx.RequestError`;
- retries de `httpx.HTTPStatusError`;
- agotamiento de 429 tras 3 intentos.

La implementacion usa un cliente HTTP fake local y monkeypatch de `time.sleep`, sin sumar dependencias nuevas ni hacer requests reales.
