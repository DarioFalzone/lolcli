# Home Hub

Portal local de operaciones para abrir, lanzar y monitorear los servicios
activos de `riot_lol_cli`.

## Rutas runtime

- Backend FastAPI: `src/riot_lol_cli/home/server.py`
- Frontend SPA: `src/riot_lol_cli/home/static/`
- Launcher Windows: `scripts/bat/home.bat`
- Launcher completo: `scripts/bat/levantar_todo.bat`
- Tests: `tests/test_server_factories.py`

## Comandos

```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.home.server
```

URL principal: `http://localhost:8080`.

El puerto default `8080` se puede cambiar con `LOLCLI_HOME_PORT`.

## Contrato

- `GET /` sirve la SPA.
- `GET /health` valida el Home Hub.
- `GET /api/v1/home/status` agrega health checks de Meta API, Draft Advisor,
  Meta Scraper, Jungle Meta e Items Browser.
- `POST /api/v1/home/launch/{service_id}` lanza servicios offline usando
  comandos registrados, no comandos arbitrarios del usuario.

## Deuda conocida

- El Hub debe actualizarse cada vez que se agregue un nuevo servicio o proyecto
  operativo.
- El copy visible de cada card debe mantenerse alineado con el alcance real del
  subsistema.
