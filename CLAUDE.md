# Claude Code Shim

Claude Code debe usar este archivo solo como puntero de arranque.

## Lectura inicial

1. Leer `README.md` en la raiz para una vista rapida del repo (proyectos, puertos, comandos).
2. Leer `AGENTS.md` como mapa maestro detallado.
3. Leer `projects/README.md` para ubicar el proyecto logico afectado.
4. Leer las 4 reglas canonicas en `.agent/rules/`:
   - `agent-workflow.md` — flujo operativo, subsistemas, gotchas.
   - `engineering-standards.md` — Python, ruff, patrones, frontend.
   - `documentation-and-commits.md` — protocolo doc + Conventional Commits.
   - `security-and-testing.md` — secretos, Riot API, DB, pytest, draft data.
5. Para cualquier iteracion significativa actualizar `bitacora_de_cambios.md`.

## Setup runtime

- Python 3.9+, virtualenv en `.venv/`.
- `pip install -r requirements.txt` y `pip install -r requirements-dev.txt`.
- Para scraping real (Meta Scraper): `playwright install chromium`.
- 6 servidores FastAPI: Home `:8080`, Meta API `:8000`, Draft `:8001`, Meta Scraper `:8002`, Jungle `:8003`, Items `:8004`. Launcher unico: `scripts/bat/levantar_todo.bat`.

## Verificacion minima

```powershell
.venv\Scripts\python.exe -m pytest -q
ruff check src tests scripts
```

Si el cambio toca una surface visual: ademas correr `python scripts/visual_smoke.py <URL>` y abrir el PNG resultante. Auditar el codigo no atrapa cascadas rotas ni mojibake renderizado.

No crear ni mantener reglas largas especificas de Claude en este archivo. Las reglas operativas viven en `.agent/rules/` y `AGENTS.md` sigue siendo el entrypoint comun para agentes.
