# Prompt de contexto para Anti Gravity

Usa este prompt cuando abras el repo `riot_lol_cli` con Anti Gravity o con
otro agente que llegue sin contexto previo.

````markdown
Sos un agente tecnico senior entrando por primera vez al repositorio
`riot_lol_cli`.

Tu objetivo no es leer todo el repo de golpe. Tu objetivo es construir contexto
experto de forma incremental, respetar las fuentes de verdad actuales y evitar
romper flujos locales que ya existen.

## 1. Lectura obligatoria inicial

Lee estos documentos en este orden:

1. `README.md`
   - Vista rapida: que es el repo, proyectos activos, puertos, comandos y
     estructura general.
2. `AGENTS.md`
   - Mapa maestro para agentes. Es la referencia principal de subsistemas,
     entrypoints, APIs locales, datos, fuentes externas, reglas y gotchas.
3. `CLAUDE.md`
   - Shim corto de onboarding. Aunque mencione Claude, aplica como lista de
     arranque para cualquier agente.
4. `.agent/rules/agent-workflow.md`
   - Flujo operativo antes de editar, contrato Home Hub, cierre de tarea y
     verificacion proporcional.
5. `.agent/rules/engineering-standards.md`
   - Reglas de Python, FastAPI, frontend vanilla, encoding UTF-8 sin BOM,
     design system y verificacion visual.
6. `.agent/rules/security-and-testing.md`
   - Secretos, Riot API, scraping, DB local y criterio de tests.
7. `.agent/rules/documentation-and-commits.md`
   - Que docs actualizar, formato de bitacora y protocolo de cierre.
8. `projects/README.md`
   - Mapa por proyecto logico. Importante: `projects/active/*` son
     manifiestos navegables, no copias del codigo runtime.
9. `docs/README.md`
   - Indice de documentacion activa y advertencia sobre docs historicas.

Despues de esa lectura, ejecuta:

```powershell
git status --short
```

El working tree puede estar sucio. No reviertas cambios ajenos. Trabaja sobre
el estado actual, no solo sobre `HEAD`.

## 2. Modelo mental del repo

`riot_lol_cli` es un unico paquete Python con multiples subsistemas. No es un
monorepo. El runtime activo vive principalmente en:

- `src/riot_lol_cli/`
- `data/`
- `assets/`
- `templates/`
- `scripts/`
- `tests/`

`projects/active/` contiene manifiestos por proyecto. No asumas que el codigo
real vive ahi salvo proyectos standalone como `projects/active/junglas-pro/`.

`projects/legacy/` es historico. No lo uses como fuente operacional ni lo
edites salvo pedido explicito.

## 3. Puertos y servicios principales

Usa estos puertos como mapa local:

- Home Hub: `8080`, `python -m riot_lol_cli.home.server`
- Meta API / Meta Analyzer: `8000`, `python scripts/run_api.py`
- Draft Advisor: `8001`, `python -m riot_lol_cli.draft_advisor.server`
- Meta Scraper: `8002`, `python -m riot_lol_cli.meta_scraper.server`
- Jungle Meta: `8003`, `python -m riot_lol_cli.jungle_meta.server`
- Items Browser: `8004`, `python -m riot_lol_cli.items_browser.server`
- Patch Notes: `8005`, `python -m riot_lol_cli.patch_notes.server`

El Home Hub en `http://localhost:8080/` es la entrada/salida central. Toda UI
integrada debe tener un link visible de vuelta al Home Hub.

## 4. Que leer segun el area que vas a tocar

### Home Hub

- `projects/active/home-hub/README.md`
- `src/riot_lol_cli/home/`
- `tests/test_server_factories.py`
- `.agent/rules/agent-workflow.md`, seccion contrato Home Hub

### Meta Analyzer / Dashboard / Jungle Research

- `projects/active/meta-analyzer-dashboard/README.md`
- `docs/meta_analyzer/README.md`
- `docs/dashboard/README.md`
- `docs/meta_analyzer/jungle-research-roadmap.md` si el cambio toca Jungla 360
- `src/riot_lol_cli/meta_api/`
- `src/riot_lol_cli/meta_analyzer/`
- `src/riot_lol_cli/jungle_research/`
- `tests/jungle_research/`

Puntos de cuidado:

- `api_server.py` es wrapper; la app real vive en
  `src/riot_lol_cli/meta_api/app.py`.
- `dashboard_enhanced.py` tiene HTML/CSS/JS embebido y puede ser fragil.
- La DB `data/meta_analyzer.db` es runtime local, no fuente de verdad.
- Jungle Research usa JSON storage bajo
  `data/meta_analyzer/jungle_research/`; no inventes datos si falta una capa:
  los endpoints deben devolver `200` con `gaps` visibles.

### Draft Advisor

- `projects/active/draft-advisor/README.md`
- `docs/draft_advisor/README.md`
- `KB/README.md`
- `src/riot_lol_cli/draft_advisor/`
- `data/draft_advisor/`
- `tests/draft_advisor/`

Puntos de cuidado:

- IDs internos siempre canon Data Dragon: `JarvanIV`, `KogMaw`,
  `TahmKench`, `LeeSin`, etc.
- La UI visible y razones deben estar en espanol rioplatense.
- `KB/` no es documentacion generica del repo: solo conocimiento estrategico
  reutilizable por el motor.
- Antes de diagnosticar bugs del front, valida
  `/api/v1/draft/health` y `/api/v1/draft/champions`.

### Meta Scraper

- `projects/active/meta-scraper/README.md`
- `src/riot_lol_cli/meta_scraper/`
- `data/meta_scraper/`
- `tests/meta_scraper/`

Puntos de cuidado:

- No corras scraping real con Playwright salvo pedido explicito.
- OP.GG, LoLalytics y U.GG tienen name maps; si agregas un campeon o alias,
  revisa los tres.
- Snapshots en `data/meta_scraper/` son generados.

### Patch Notes

- `projects/active/patch-notes/README.md`
- `projects/active/patch-notes/DESIGN.md`
- `projects/active/patch-notes/V3_ROADMAP.md` si el cambio toca roadmap
- `src/riot_lol_cli/patch_notes/`
- `data/patch_notes/`
- `tests/patch_notes/`

Puntos de cuidado:

- La fuente canonica de contenido es Riot LoL oficial `es-es`.
- No rehostees contenido completo innecesariamente; prioriza resumen,
  estructura, busqueda, diffs y links canonicos.
- El design contract de Patch Notes es referencia para propuestas visuales.

### Esports Research

- `docs/esports_research/README.md`
- `docs/esports_research/source-activation-guide.md`
- `docs/esports_research/roadmap.md`
- `src/riot_lol_cli/esports_research/`
- `src/riot_lol_cli/meta_api/routes/esports.py`
- `src/riot_lol_cli/meta_api/static/esports/`
- `tests/esports_research/`

Puntos de cuidado:

- Si falta una fuente o capa, responder `200` con `gaps`, no 500.
- No asistencia en vivo, no bypass de captcha/login, no rehost de VODs.

### Items Browser

- `projects/active/items-browser/README.md`
- `src/riot_lol_cli/items_browser/`
- `data/items/database.json`
- `scripts/update_items_database.py`
- `tests/items_browser/`

Puntos de cuidado:

- `data/items/database.json` se regenera desde Data Dragon.
- El catalogo visual oculta variantes duplicadas por defecto; la API puede
  exponerlas con `include_variants=true`.

### Jungle Meta

- `projects/active/jungle-meta/README.md`
- `src/riot_lol_cli/jungle_meta/`
- `data/jungle_meta/`
- `tests/jungle_meta/`

Puntos de cuidado:

- Es una tier list curada por parche, usada por Draft Advisor como fuente
  primaria de jungla v1.
- No confundas Jungle Meta (`:8003`) con Jungle Research/Jungla 360 dentro de
  Meta API (`:8000`).

### Splash Gallery y assets

- `projects/active/splash-gallery/README.md`
- `projects/active/assets-and-data/README.md`
- `docs/splash-viewer.md`
- `src/riot_lol_cli/splash.py`
- `templates/splash-viewer.html`
- `scripts/update_ddragon_assets.py`

Puntos de cuidado:

- `outputs/splash-viewer.html` es generado. Preferi regenerar desde template y
  manifest antes que editar output a mano.
- Assets y datos de Riot/Data Dragon cambian con cada parche.

### CLI Match History

- `projects/active/cli-match-history/README.md`
- `main.py`
- `src/riot_lol_cli/cli.py`
- `src/riot_lol_cli/api.py`
- `src/riot_lol_cli/rendering.py`
- `templates/claude-4-5.html`
- `tests/test_cli.py`, `tests/test_api.py`, `tests/test_async_api.py`

Puntos de cuidado:

- No hagas requests reales a Riot en tests.
- La API key vive en `.env`, nunca en git.

### Junglas Pro

- `projects/active/junglas-pro/README.md`
- `projects/active/junglas-pro/research-notes.md`
- `projects/active/junglas-pro/index.html`

Puntos de cuidado:

- Es standalone, no parte del paquete Python.
- La investigacion completa queda ahi. Solo copiar a `KB/` si es conocimiento
  estrategico reutilizable por Draft Advisor.

## 5. Reglas duras antes de editar

- No reviertas cambios ajenos.
- No muevas `src/`, `data/`, `assets/`, `templates/` ni `scripts/` sin plan
  explicito de imports, paths, docs y tests.
- No commitees `.env` ni claves `RGAPI-*`.
- No corras scraping real ni requests reales a Riot salvo pedido explicito.
- Todo texto/JSON debe ser UTF-8 sin BOM. Evita `Set-Content -Encoding UTF8`
  y `Out-File -Encoding UTF8` en PowerShell.
- Para paths runtime usa `src/riot_lol_cli/paths.py`.
- Para FastAPI, preferi `create_app()` y `app = create_app()`.
- Frontend: HTML/CSS/JS vanilla. Sin React, sin bundler, sin TypeScript.
- Design system canonico:
  `src/riot_lol_cli/draft_advisor/static/design-system/`.

## 6. Verificacion proporcional

Elegir tests segun alcance:

- Codigo general:
  ```powershell
  .venv\Scripts\python.exe -m pytest -q
  .venv\Scripts\python.exe -m ruff check src tests scripts
  ```
- Draft Advisor:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/draft_advisor -q
  ```
- Meta Scraper:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/meta_scraper -q
  ```
- Jungle Research:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/jungle_research -q
  ```
- Patch Notes:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/patch_notes -q
  ```
- Encoding:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/test_no_mojibake.py tests/test_encoding_global.py -q
  ```
- Frontend visible:
  ```powershell
  python scripts/visual_smoke.py http://localhost:<port>/<path>
  ```
  Luego mirar el PNG resultante: texto sin mojibake, layout sin overlays,
  estados no colgados en "Cargando...", tipografia y hero correctos.

## 7. Documentacion y cierre

Si el cambio es significativo, actualiza docs en la misma iteracion:

- Arquitectura, puerto, path critico: `AGENTS.md`
- Ownership/proyecto: `projects/README.md`
- Indice docs: `docs/README.md`
- Setup/comandos: `docs/getting-started.md`
- Subsistema especifico: `docs/<area>/README.md` o
  `projects/active/<area>/README.md`
- Siempre que aplique: `bitacora_de_cambios.md`

Al cerrar, informa:

- Que cambiaste.
- Que verificaste.
- Archivos creados.
- Archivos modificados.

## 8. Heuristica de experto

Cuando una doc y el codigo discrepan, verifica contra codigo y tests antes de
implementar. `AGENTS.md` y los manifests de `projects/active/` son el mapa; el
codigo y los tests son la confirmacion final.
````

## Auditoria documental rapida

Estado observado al crear este prompt:

- `AGENTS.md` es el mejor mapa maestro para agentes.
- `projects/README.md` es la fuente para ownership logico y diferencia entre
  runtime real y manifiestos.
- `docs/README.md` es el indice activo y advierte no crear Markdown suelto fuera
  del mapa canonico salvo decision explicita.
- `.agent/rules/` contiene las reglas operativas reales: workflow, engineering,
  docs/commits y seguridad/testing.
- `README.md` es util como primera vista, pero algunos conteos resumidos pueden
  quedar viejos frente a branches activos; confirmar contra codigo/tests.
- `docs/design-system.md` describe tokens canonicos, pero puede tener estado de
  migracion parcialmente historico; confirmar contra `patterns.css`, `tokens.css`
  y la surface concreta.
- `docs/meta_analyzer/README.md` incluye Jungle Research/Jungla 360 y Esports
  Research, pero los detalles vivos deben verificarse contra `src/riot_lol_cli/`
  y `tests/`.
- Hay working tree activo; cualquier agente debe empezar con `git status --short`
  y evitar revertir cambios ajenos.
