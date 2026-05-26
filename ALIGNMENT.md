# Claude Code Alignment Prompt

Actúa como un asistente senior de development para el repositorio `riot_lol_cli` (League of Legends Meta Analysis + Jungle Research).

## 🚀 ONBOARDING OBLIGATORIO (Cada sesión)

1. **Lee en orden** (3 min):
   - `CLAUDE.md` (shim de arranque)
   - `AGENTS.md` (mapa maestro técnico)
   - `projects/README.md` (ubicación del proyecto lógico)
   - `.agent/rules/*.md` (4 reglas canónicas)

2. **Estado actual**:
   - Rama: `git branch` (verificar al iniciar)
   - Working tree: `git status` (no reverter cambios ajenos)
   - Memoria personal: `~/.claude/projects/e--Desarrollos-LOLCLI/memory/MEMORY.md`

3. **Verificación mínima**:
   ```powershell
   .venv\Scripts\python.exe -m pytest -q
   ruff check src tests scripts
   ```

## ⚠️ REGLAS INTRANSIGENTES

### 1. ❌ UTF-8 Sin BOM (Los mojibakes rompen frontends)
- Todo JSON: `json.dump(..., ensure_ascii=False)` + `encoding='utf-8'` en Python
- ❌ NUNCA: `Set-Content`, `Out-File` en PowerShell nativo
- ✅ SIEMPRE: Python scripts o Bash con `Write` tool

### 2. 🆔 IDs Canónicos de Campeones
- Fuente: `data/draft_advisor/champion_base.json`
- Ejemplos: `JarvanIV`, `TahmKench`, `KogMaw` (no `Jarvan IV`, `Tahm Kench`, espacios)

### 3. 📍 Paths Runtime
- Importar desde `src/riot_lol_cli/paths.py`: `DATA_DIR`, `OUTPUT_DIR`, `ASSETS_DIR`
- ❌ NO hardcodes como `"./data/"` o `os.getcwd()`

### 4. 👁️ Verificación Visual (SPAs/Frontend)
- Alterar HTML/CSS/JS → **obligatorio** smoke test:
  ```powershell
  python scripts/visual_smoke.py http://localhost:8000/dashboard-enhanced
  ```
- Inspeccionar PNG antes de dar tarea por concluida

### 5. 📝 Bitácora + Roadmap
- Cambios significativos → entrada en `bitacora_de_cambios.md`
- Decisiones arquitectónicas → actualizar roadmaps en `docs/`
- No dejar TODOs huérfanos

## 🏗️ ARQUITECTURA (8 servicios FastAPI)

| Servicio | Puerto | Módulo | Responsabilidad |
|----------|--------|--------|-----------------|
| Home Hub | 8080 | `home.server` | Landing + links a APIs |
| Meta API | 8000 | `meta_api.app` | Core: tier lists, matchups, items, raw-data |
| Draft Advisor | 8001 | `draft_advisor.server` | Asesor de picks/bans |
| Meta Scraper | 8002 | `meta_scraper.server` | Orchestrador de adapters |
| Jungle Research | 8003 | `jungle_research.orchestrator` | Knowledge base de jungla (soloQ + pro) |
| Items Browser | 8004 | `items_browser.server` | Browse builds de items |
| Patch Notes | 8005 | `patch_notes.scheduler` | Timeline de cambios |
| Duo Analiser | 8006 | `duo_analiser.server` | Análisis de duos/sinergias |

**Launcher único**: `scripts/bat/levantar_todo.bat`

## 📋 PLAN ACTUAL (PR-A → PR-B → PR-C → PR-D)

Leer el plan en: `~/.claude/plans/cuddly-sprouting-newell.md`

**Estado a 2026-05-25**:
- ✅ PR-A: Audit esports_research (read-only, feedback doc)
- ✅ PR-B: V3.7 METAsrc real (adapter + tests + fixture)
- ✅ PR-C: Integración esports→jungle (pro_stage_bridge + STEP_PRO_STAGE)
- 🔄 **PR-D EN PROGRESO**: Tier 3 deuda UI
  - ✅ Extracción HTML/CSS/JS a archivos estáticos
  - 📋 Separar jungle-research.js del dashboard.js
  - 📋 Mini-router hash (#tab/subtab)
  - 📋 Drill-down expandible en tabla Consenso
  - 📋 Split docs: status + decisions + roadmap
  - 📋 Smoke visual post-refactor

## 🎯 CONVENCIONES DE CÓDIGO

### Python
- Imports: type hints, `from __future__ import annotations`
- Docstrings: 1 línea max (solo si el WHY es no-obvio)
- Logging: `logging.getLogger(__name__)`
- Tests: pytest, fixtures en `tests/conftest.py`
- Ruff: `line-length = 100`, `target-version = "py39"`

### JavaScript (vanilla, no frameworks)
- Vanilla JS (axios sí, React no)
- Event listeners: `addEventListener`, no `onclick` inline si es posible
- Variables globales: mínimas (`API_BASE`, `allChampions`)
- Formateo: 4-space tabs, IIFE para scope
- Comments: solo si WHY es no-obvio

### HTML/CSS
- Charset: `<meta charset="UTF-8">`
- CSS variables: `var(--arc-gold)`, `var(--primary)`
- Responsive: `@media (max-width: 768px)`
- Accesibilidad: `aria-expanded`, `role` cuando sea necesario

## 🧪 TESTING

```powershell
# Tests generales (esperar ~2 min)
.venv\Scripts\python.exe -m pytest -q

# Tests rápidos (subset)
.venv\Scripts\python.exe -m pytest tests/jungle_research -q

# Coverage
.venv\Scripts\python.exe -m pytest --cov=src --cov-report=html
```

**Reglas**:
- No mockear BD en tests de integración (usar `pytest-postgresql` si es necesario)
- Fixtures reales en `tests/**/fixtures/`
- `test_no_mojibake.py` → siempre debe pasar (valida encoding de docs)

## 💾 MEMORIA PERSISTENTE

Después de cada PR, actualizar:
- `~/.claude/projects/.../memory/MEMORY.md` (índice)
- Archivos en `memory/` con tipo (`project_*.md`, `feedback_*.md`, `reference_*.md`)

**Leer al iniciar** si existe: `MEMORY.md` te da contexto cross-session.

## 📞 CONTACTO CON USUARIO

- Español siempre (profesional, conciso)
- Resumen **fáctico** al cerrar turno (qué se editó, qué tests pasaron)
- ❌ NO explicar código evidente
- ✅ SÍ señalar decisiones no triviales o cambios arquitectónicos

## 🚨 GOTCHAS HISTÓRICOS

1. **Mojibakes en JSON**: Usar `Write` tool o Python, nunca PowerShell
2. **Cambios ajenos en working tree**: Verificar con `git status`, NO revertir
3. **Tests sin fixture real**: Smoke visual puede romper sin el HTML actual
4. **Rutas hardcodeadas**: Usar `paths.py`, no `./data/` directo
5. **Commits sin bitácora**: Siempre actualizar `bitacora_de_cambios.md`
6. **Imports circulares**: Validar con `ruff check` antes de push
7. **Hash router sin race condition**: Pequeño delay en DOMContentLoaded si cargas async

---

**Última actualización**: 2026-05-25 (PR-D en progreso)
