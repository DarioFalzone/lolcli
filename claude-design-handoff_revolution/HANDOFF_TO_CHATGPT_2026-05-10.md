# Context handoff — riot_lol_cli (al 2026-05-10)

> Pegá este archivo entero como primer mensaje a ChatGPT para que tome el estado actual del repo sin tener que leer todos los commits.

---

## Quién soy y qué es el repo

Soy Darío. El repo es **`riot_lol_cli`** (https://github.com/DarioFalzone/lolcli), un set de herramientas locales para analizar el meta de League of Legends y asistir el draft. Stack: Python 3.9+, FastAPI + SPAs vanilla HTML/CSS/JS, sin React, sin build step. Todo corre en local, en Windows con PowerShell.

## Arquitectura: 6 servicios FastAPI

| Servicio | Puerto | Path |
|---|---|---|
| Home Hub (centro de operaciones) | 8080 | `src/riot_lol_cli/home/` |
| Meta Analyzer API | 8000 | `src/riot_lol_cli/meta_api/` |
| Draft Advisor (recomendador ADC/Sup) | 8001 | `src/riot_lol_cli/draft_advisor/` |
| Meta Scraper (OP.GG + LoLalytics + U.GG) | 8002 | `src/riot_lol_cli/meta_scraper/` |
| Jungle Meta (tier list jungla) | 8003 | `src/riot_lol_cli/jungle_meta/` |
| Items Browser (DDragon EN+ES) | 8004 | `src/riot_lol_cli/items_browser/` |

Cada uno tiene `create_app()` factory + `app.state` para servicios runtime (refactor post-auditoría). Todos respetan `LOLCLI_*_PORT` env vars.

**Launcher único:** `scripts\bat\levantar_todo.bat` levanta los 6 en background sin ventanas (logs en `logs/`).

## Convenciones críticas (del repo)

- **Commits:** Conventional Commits (`feat`, `fix`, `docs`, `refactor`, `chore`, `test`). Scopes: `home`, `draft`, `meta`, `meta-scraper`, `jungle-meta`, `items-browser`, `design-system`.
- **Documentación:** se actualiza en la **misma iteración** que el código. `bitacora_de_cambios.md` registra todo cambio significativo. Ver `.agent/rules/documentation-and-commits.md`.
- **Cierre obligatorio de cada respuesta:** lista bullet de "Archivos creados" y "Archivos modificados".
- **Python 3.9 floor:** `from __future__ import annotations` requerido si se usa pipe-union (`X | Y`). Test guard en `tests/test_python39_annotations.py`.
- **Idioma:** español rioplatense + jerga gamer EN ("blind pick", "scaling", "peel" no se traducen).
- **No hay React, no hay bundler.** SPAs son HTML+CSS+JS plain. Si hace falta una utilidad, vainilla.

## Estado actual (post-última sesión, 2026-05-10)

### Lo más reciente que se mergeó

**PR #1 — Pattern Library v2** (commit `92421cd` → merge `6fcc9c2`):
- Nuevo `patterns.css` (~28 KB) con 18 clases drop-in (hero, control-panel, tabs, tier-row, cat-card, stat-strip, data-table, modal, slots, toasts, banners, etc.).
- `tokens.css` reemplazado por v2 canónica. **Cambios visuales sutiles intencionales:**
  - `--radius-sm/md/lg/xl`: 8/12/16/20 → 6/8/12/16 (bordes más chicos)
  - `--motion-fast/default/slow`: 150/200/400ms → 120/180/320ms (animaciones más rápidas)
  - `--state-success-dim/error-dim/warning-dim`: hex sólido → rgba semitransparente
- Tokens **agregados** v2: `--tier-s/a/b/c`, `--font-anton`, `--font-hero`, `--ease-out`, `--state-info-dim`, `--space-20`, `--tracking-hero`.
- Tokens **deprecados** sin uso runtime: `--gap`, `--motion-spin`, `--motion-glow-pulse`, `--motion-border-flow`, `--motion-grid-flow`, `--container-3xl`, `--tracking-tighter`.
- Doc page navegable: `claude-design-handoff_revolution/patrones_diseños_claude_design/Pattern Library.html`.
- Nuevo `src/riot_lol_cli/draft_advisor/static/design-system/README.md` con orden de carga canónico.

**Importante:** la única surface que actualmente importa `tokens.css` es Draft Advisor SPA. Las demás (Home, Meta Scraper, Jungle, Items) tienen su propio CSS aislado y NO se ven afectadas por v2. La migración de esas surfaces a `patterns.css` está en el roadmap (Fases 1-4 del PR_BODY).

### Lo que se hizo en la sesión que cerré (commits 2026-05-09 → 2026-05-10)

| Commit | Resumen |
|---|---|
| `a63b2b8` | fix(meta-scraper): mejor extracción de `games_analyzed` en lolalytics+opgg, U.GG ahora filtra por rol (corrige cross-rol contamination), normalizer agrega `min_pick_rate=0.5` |
| `c078ac1` | feat(home): nuevo `POST /api/v1/home/launch/{id}` que spawnea servicios subprocess. Botón "Abrir" en cards offline lanza el servicio, hace polling al `/health` cada 1s hasta 20s, y abre el browser cuando responde |
| `97f5050` | docs(home): nuevo `scripts/bat/home.bat`, sección Home Hub + Levantar Todo en `docs/getting-started.md`, actualizado `levantar_todo.bat` |
| `808d553` | feat(home): empty states — 5 skeleton cards con shimmer durante carga inicial, error/empty fallbacks con retry |
| `92421cd` + `6fcc9c2` | feat(design-system): Pattern Library v2 (descripto arriba) |

## Roadmap conocido (próximos pasos)

Del PR_BODY del Pattern Library v2:

1. **Fase 1**: migrar Items Browser y Jungle Meta a importar `tokens.css` compartido en lugar de redefinir `:root` con paleta local.
2. **Fase 2**: migrar Home Hub y Meta Scraper a clases de `patterns.css` (`.hero`, `.control-panel`, `.tabs`, `.tier-row`).
3. **Fase 3**: Draft Advisor SPA — alinear nombres de clase con `patterns.css` donde aplique.
4. **Fase 4**: deprecar `compat-spa.css` y `compat-dashboard.css`.

Otros temas activos:
- Meta Scraper requiere `playwright install chromium` (no se corre scraping salvo pedido explícito).
- Jungle Meta tiene 17 campeones en `data/jungle_meta/patch_26.09.json`. Algunos tienen `core_builds` basado en archetype (sin verificación visual contra screenshots de SkillCapped). Ver bitácora 2026-05-09 Xin Zhao para el patrón de corrección.

## Archivos clave para que ChatGPT lea (en este orden)

1. `README.md` (raíz) — vista rápida del repo.
2. `AGENTS.md` — mapa maestro detallado.
3. `bitacora_de_cambios.md` — historial cronológico de cambios (las últimas 10-15 entradas alcanzan).
4. `.agent/rules/agent-workflow.md` — reglas operativas, gotchas por subsistema.
5. `.agent/rules/documentation-and-commits.md` — protocolo doc + commits.
6. `.agent/rules/engineering-standards.md` — Python, ruff, patrones.
7. `docs/design-system.md` — design system, ahora con sección Pattern Library v2.
8. `src/riot_lol_cli/draft_advisor/static/design-system/README.md` — orden de carga canónico CSS.
9. `claude-design-handoff_revolution/patrones_diseños_claude_design/Pattern Library.html` — doc page navegable visual (abrila en browser).
10. `docs/getting-started.md` — setup + comandos para levantar cada servicio.

## Cómo me gusta colaborar

- Respuestas concisas, sin preámbulos.
- Si hay algo ambiguo → preguntar antes de inventar.
- Si vas a cambiar código de UI → probarlo en el browser real, no asumir que compila = funciona.
- Cierre con lista de archivos creados/modificados, siempre.
- Commits firmados con `Co-Authored-By: <model> <noreply@anthropic.com>`.
- **No hacer push automático ni mergear PRs.** Crear branch + commit + push + abrir PR. Yo reviso y mergeo.

## Stack de testing

- `pytest` con `pytest-asyncio` (modo strict).
- Tests viven en `tests/`, organizados por subsistema.
- Smoke tests de cada `create_app()` en `tests/test_server_factories.py`.
- Linter: `ruff check src tests scripts` (ver `pyproject.toml`).
- CI corre `pytest -q` + `ruff check`.

## Cosa importante: state de uncommitted

Justo ahora el working tree está limpio en `main` (sincronizado con `origin/main` en commit `6fcc9c2`). El único untracked es `claude-design-handoff_revolution/pattern-library-v2/` que es el bundle source del Cloud Claude (input, no output — no entra al repo).

---

**¿Qué hacés ahora?** Tomate este contexto como base. Si tengo algo nuevo que pedirte, te lo planteo. Si necesitás clarificación de algo de acá, preguntame antes de empezar.
