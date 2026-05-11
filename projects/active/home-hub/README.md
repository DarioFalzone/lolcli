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
- El launcher del Hub reserva la nueva pestaña desde el click y la navega
  cuando el servicio llega a `online`; no espera al final para recien intentar
  `window.open()`.

## Checklist de integracion

Cada proyecto o servicio nuevo que aparezca en el Home Hub debe cumplir este
contrato minimo:

- Card registrada en `SERVICES` con `health_path` y `ui_path` correctos.
- Health check valido desde el Hub.
- Link visible de vuelta al `Home Hub` dentro de la UI del proyecto.
- Favicon explicito para evitar `404` ruidosos en consola (`/static/favicon.svg`,
  `favicon.svg` local o equivalente).
- Si el frontend se abre despues de un launch on-demand, evitar popups tardios:
  reservar la ventana en el click y navegarla cuando el servicio quede `online`.

## Deuda conocida

- El Hub debe actualizarse cada vez que se agregue un nuevo servicio o proyecto
  operativo.
- El copy visible de cada card debe mantenerse alineado con el alcance real del
  subsistema.
