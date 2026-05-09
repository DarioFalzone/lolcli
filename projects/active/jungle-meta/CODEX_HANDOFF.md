# Codex Handoff — Jungle Meta + Items Browser (Sesión 2026-05-08)

> Prompt auto-contenido para Codex u otro agente que entre frio al repo. Asume cero contexto previo.

---

## Repositorio

`riot_lol_cli` — proyecto Python único con multiples subsistemas para League of Legends. Stack: FastAPI + Uvicorn (servidores), vanilla HTML/CSS/JS (SPAs), pytest, ruff. Python 3.9+. Entornos virtuales en `.venv/`.

Mapa maestro vivo: `AGENTS.md`. Reglas operativas: `.agent/rules/`. Bitácora: `bitacora_de_cambios.md`. Lectura inicial obligatoria de `CLAUDE.md`.

Servidores FastAPI activos (todos con `create_app()` factory + `run()` entry):

| Subsistema | Puerto | Path |
|------------|--------|------|
| Meta API / Meta Analyzer | 8000 | `src/riot_lol_cli/meta_api/` |
| Draft Advisor | 8001 | `src/riot_lol_cli/draft_advisor/` |
| Meta Scraper | 8002 | `src/riot_lol_cli/meta_scraper/` |
| Jungle Meta | 8003 | `src/riot_lol_cli/jungle_meta/` |
| Items Browser | 8004 | `src/riot_lol_cli/items_browser/` |

Hosts/puertos configurables vía env `LOLCLI_<MODULE>_HOST` / `LOLCLI_<MODULE>_PORT` con helpers en `src/riot_lol_cli/settings.py`.

---

## Que se entregó en esta sesión

### 1. Regla de cierre con lista de archivos (paso 7)

Archivo: `.agent/rules/documentation-and-commits.md`. Toda respuesta final del agente cierra con dos secciones explicitas: **Archivos creados** y **Archivos modificados** (paths relativos). Si vacio, decirlo. La regla aplica a cualquier iteración significativa.

### 2. Jungle Meta v1.1 (rediseño previo)

Modulo `src/riot_lol_cli/jungle_meta/` ya tenia un MVP. En esta sesion se reescribio con:

- **Nuevo schema** en `data/jungle_meta/patch_26.09.json`:
  - `core_builds: [{label, items: [int, ...]}]` con builds multiples por champion (Xin Zhao tiene 2: Standard + Crit Variant). Items son IDs numericos de Data Dragon.
  - `core_rune: {name, tree}` estructurado.
  - `categories: {overpowered, low_elo_picks, bans}`.
  - `items_meta: {voltaic_sword_abusers}`.
- **3 endpoints nuevos**: `/categories`, `/items/abusers/{key}`, `/items/used`.
- **Mount `/items`** sirve `assets/items/<id>.png` localmente.
- **SPA reescrita** (`static/index.html`, `styles.css`, `app.js`): hash router (`#overview` / `#champion/{id}`), cards expandidas con WR/PR, filter tabs ALL/S/A/B/C, splash bg en detail view, builds multiples renderizadas con flechas entre items.
- **Source of truth visual**: `projects/active/jungle-meta/screenshots/` — 7 capturas de SkillCapped Patch 26.09. La carátula define la estética (Anton italic display + jungla icon).

**Estado 2026-05-09:** Xin Zhao ya fue corregido contra la captura/manual review. Sus builds usan `Statikk Shiv` (`3087`), `Dusk and Dawn` (`2510`) y `Riftmaker` (`4633`). Tambien se quito de `voltaic_sword_abusers` porque ya no usa Voltaic en el build verificado.

**Pendiente conocido:** los champions sin screenshot dedicada siguen usando arquetipos canonicos. La estructura permite que cada correccion futura sea cambiar un `int` por otro dentro de `core_builds`.

### 3. Items Browser (puerto 8004)

Modulo nuevo para identificar exactamente qué items aparecen en cada screenshot.

- **Database** en `data/items/database.json`: 705 items (DDragon 16.9.1) con `id`, `name_en`, `name_es`, `tags`, `stats`, `gold_total/base/sell`, `purchasable`, `depth`, `from`, `into`, `maps`, `image`, `deprecated`. Generada por `scripts/update_items_database.py` que pide `versions.json`, descarga `item.json` en `en_US` y `es_ES`, mezcla, y descarga PNG faltantes a `assets/items/`.
- **Modulo** `src/riot_lol_cli/items_browser/`:
  - `loader.py`: cache en memoria, `get_item`, `list_categories` (Riot tags), `list_groups` (buckets curados: starter/boots/components/legendary/consumables/trinkets/jungle_specific/deprecated), `search_items` substring EN/ES.
  - `server.py`: 7 endpoints (`/health`, `/api/v1/items/all?include_deprecated=`, `/{id}`, `/groups`, `/categories`, `/search?q=&lang=`, root SPA), mount `/items` y `/static`.
  - SPA: hero con version badge, busqueda + toggle EN/ES, tabs por grupo con count badges, grid responsive, modal con stats humanizados + tags + plaintext bilingue.
- **Launcher**: `scripts/bat/items_browser.bat` (auto-regenera DB si no existe).
- **README**: `projects/active/items-browser/README.md`.

### 4. Tests

`pytest -q` → 163 passed (was 153 antes de items_browser). 8 tests nuevos en `tests/items_browser/test_loader.py` + 2 smoke tests en `tests/test_server_factories.py`.

### 5. Documentación sincronizada

- `AGENTS.md`: subsistemas (5 ahora), tabla server, entry points, APIs locales, gotchas (4→5 FastAPI, puertos 8000-8004 configurables).
- `docs/getting-started.md`: nueva sección 7 "Items Browser" + sección 8 renumerada.
- `.agent/rules/agent-workflow.md`: gotcha y tabla de docs canónicas.
- `bitacora_de_cambios.md`: entrada completa con "Archivos creados/modificados".

---

## Próximo paso (lo que tu sesión deberia ejecutar)

**Tarea**: corregir slot-by-slot los items restantes de `core_builds` en `data/jungle_meta/patch_26.09.json` para que matcheen las screenshots reales.

**Workflow sugerido**:

1. Levantar Items Browser:
   ```powershell
   scripts\bat\items_browser.bat   # http://localhost:8004
   ```
2. Por cada champion con screenshot disponible pendiente:
   - Abrir `projects/active/jungle-meta/screenshots/core build <champ>.png`.
   - Identificar visualmente los 4 items del core build.
   - En el browser, buscar por nombre/grupo para encontrar el ID.
   - Reemplazar el `int` correspondiente en `data/jungle_meta/patch_26.09.json`.
3. Para los champions sin screenshot, **dejar arquetipos canónicos** (no inventar).
4. Validar:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests/jungle_meta/ -q
   ```
5. Commit con scope `feat(jungle-meta): align core_builds slot-by-slot with SkillCapped screenshots`.

**Restricciones**:

- No tocar `assets/items/` ni `data/items/database.json` salvo pedido explicito.
- No alterar el schema de `patch_26.09.json` (solo cambiar valores `int` dentro de `items` arrays).
- Mantener compatibilidad: tests `test_xin_zhao_core_builds_match_skillcapped_screenshot`, `test_xin_zhao_has_two_builds` y `test_get_item_abusers_voltaic_sword` deben seguir pasando.
- Si un item de la screenshot resulta deprecated (no esta en DDragon vigente), hacerlo notar en commit body.

**Verificación end-to-end**:

1. `pytest -q` → 163+ passed.
2. `curl http://localhost:8003/api/v1/jungle/champion/XinZhao` → builds `[3087,2510,4633]` y `[2510,4633,3087]`.
3. Browser `http://localhost:8003/#champion/XinZhao` → 2 builds con iconos cargando desde `/items/{id}.png`.

---

## Convenciones del repo

- **Imports**: `from __future__ import annotations` siempre que se usen type hints modernos (Python 3.9 floor para CI).
- **Logging**: `logging` en libs/servers, `click.echo()` solo en CLI.
- **Pydantic V2** para payloads complejos; nunca dict access frágil.
- **Conventional Commits** (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, etc.) con scope (`jungle-meta`, `items-browser`, `meta-scraper`, `draft`, `cli`, `docs`).
- **Tests focalizados como piso**, suite completa solo cuando alcance lo justifica.
- **Bitácora obligatoria** en cada iteración significativa.
- **Cierre de respuesta** con `### Archivos creados` + `### Archivos modificados` (regla nueva paso 7).

## Documentación canónica

- `AGENTS.md` — mapa maestro
- `.agent/rules/agent-workflow.md` — flujo operativo
- `.agent/rules/engineering-standards.md` — estilo + Python 3.9 compat
- `.agent/rules/documentation-and-commits.md` — protocolo doc + Conventional Commits
- `.agent/rules/security-and-testing.md` — secretos, Riot API, tests
- `docs/getting-started.md` — setup por subsistema
- `bitacora_de_cambios.md` — historico
