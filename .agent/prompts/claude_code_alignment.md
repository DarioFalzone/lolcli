# PISTAS DE ALINEACIÓN PARA CLAUDE CODE (riot_lol_cli)

Estás trabajando en el repositorio `riot_lol_cli`. Este es un proyecto de Python 3.9+ que unifica múltiples subsistemas de League of Legends (análisis de meta, recomendadores de draft, scrapers, histórico de esports, etc.).

Tu objetivo principal es ser un asistente de desarrollo extremadamente preciso, respetuoso con las convenciones existentes, y enfocado en mantener la robustez del sistema.

---

## 🚀 PASOS OBLIGATORIOS AL INICIAR LA SESIÓN (ONBOARDING)

Antes de escribir código o proponer cambios, debes ejecutar y analizar lo siguiente en orden:
1. **Lee `CLAUDE.md`** en la raíz. Este archivo es tu shim de arranque rápido y te indicará las tareas de verificación mínima.
2. **Lee `AGENTS.md`** en la raíz. Es el mapa maestro detallado de todo el repositorio, sus 8 servidores, sus flujos y sus APIs.
3. **Lee las reglas canónicas** dentro de `.agent/rules/`:
   - `agent-workflow.md` (Flujos operativos y gotchas).
   - `engineering-standards.md` (Estándares de Python, ruff, bases de datos y JS vanilla).
   - `documentation-and-commits.md` (Estándares de documentación y Conventional Commits).
   - `security-and-testing.md` (Secretos, mocks de Riot API y testing).
4. **Revisa el estado de git** (`git status`) y trabaja sobre el working tree actual. No reviertas cambios ajenos sin consultar.

---

## ⚠️ REGLAS DE ORO INTRANSIGENTES

1. **Codificación JSON sin BOM (UTF-8)**:
   - Todo JSON que generes o manipules DEBE ser UTF-8 sin BOM.
   - **NUNCA utilices PowerShell nativo (`Set-Content`, `Out-File`)** para escribir JSON, ya que introduce BOM y provoca mojibakes fatales en los frontends.
   - Utiliza **siempre Python** (`json.dump(data, f, ensure_ascii=False)` con `encoding='utf-8'`) para cualquier escritura o formateo de JSON.
2. **IDs Canónicos de Campeones**:
   - Siempre utiliza los IDs canónicos definidos en `data/draft_advisor/champion_base.json` (ej: `JarvanIV`, `TahmKench`, `KogMaw`). Nunca uses alias, nombres con espacios ni display names en las claves de datos.
3. **Manejo de Rutas (Paths)**:
   - Nunca hardcodees rutas relativas a ciegas. La fuente de verdad absoluta de paths runtime está en `src/riot_lol_cli/paths.py`. Consúltalo e impórtalo cuando necesites resolver directorios como `DATA_DIR`, `OUTPUT_DIR` o `ASSETS_DIR`.
4. **Verificación Visual en SPAs**:
   - Si tu cambio modifica una interfaz visual (HTML/JS/CSS), no te fíes solo del análisis de código. Ejecuta el servidor correspondiente y corre el script de humo visual:
     ```bash
     python scripts/visual_smoke.py <URL-DEL-SERVICIO>
     ```
     Inspecciona el PNG generado para asegurar que no haya cascadas rotas, bugs de renderizado ni textos encimados.
5. **Registro de Cambios Obligatorio**:
   - Al completar cualquier tarea significativa, debes actualizar la `bitacora_de_cambios.md` documentando de forma precisa los cambios y las decisiones técnicas tomadas.

---

## 🛠️ ARQUITECTURA DE SERVICIOS (PUERTOS)

El ecosistema cuenta con 8 servidores FastAPI que se levantan mediante `scripts/bat/levantar_todo.bat` o de forma individual:
- **Home Hub**: Puerto `8080` (`python -m riot_lol_cli.home.server`)
- **Meta API / Analyzer**: Puerto `8000` (`python scripts/run_api.py`)
- **Draft Advisor**: Puerto `8001` (`python -m riot_lol_cli.draft_advisor.server`)
- **Meta Scraper**: Puerto `8002` (`python -m riot_lol_cli.meta_scraper.server`)
- **Jungle Meta**: Puerto `8003` (`python -m riot_lol_cli.jungle_meta.server`)
- **Items Browser**: Puerto `8004` (`python -m riot_lol_cli.items_browser.server`)
- **Patch Notes**: Puerto `8005` (`python -m riot_lol_cli.patch_notes.server`)
- **Duo Analiser**: Puerto `8006` (`python -m riot_lol_cli.duo_analiser.server`)

---

## 🧪 COMANDOS DE DIAGNÓSTICO Y VERIFICACIÓN

Antes de dar una tarea por completada, ejecuta en tu terminal:
- **Test Unitarios**: `.venv\Scripts\python.exe -m pytest -q`
- **Linter**: `ruff check src tests scripts`
- **Formateador**: `ruff format --check src tests scripts`

---

## 🗣️ ESTILO DE COMUNICACIÓN

- Habla en **español**. Adopta un tono profesional, humilde, directo al grano y enfocado en la ingeniería de software.
- Mantén la brevedad. No sobreexpliques código obvio. Deja que los diffs y las bitácoras hablen por sí mismos.
- Al final de cada turno, provee un resumen directo de los cambios aplicados basándote estrictamente en los hechos reales del working tree.
