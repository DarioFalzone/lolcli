# Bitácora de Cambios

Este documento registra los cambios significativos, refactorizaciones y evoluciones arquitectónicas del proyecto `riot_lol_cli`.

**Los agentes de IA deben actualizar este archivo luego de cada iteración significativa para mantener un registro histórico de los cambios realizados.**

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
- **Data**: `data/draft_advisor/support_profiles.json` (10 soportes core), `data/supports_list.json`, `data/draft_advisor/kb/structured/support_archetypes.json`.
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
