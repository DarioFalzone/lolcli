# Bitácora de Cambios

Este documento registra los cambios significativos, refactorizaciones y evoluciones arquitectónicas del proyecto `riot_lol_cli`.

**Los agentes de IA deben actualizar este archivo luego de cada iteración significativa para mantener un registro histórico de los cambios realizados.**

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
