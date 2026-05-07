@echo off
chcp 65001 >nul
REM ============================================================================
REM LOLCLI — Levantar Todo
REM Levanta los 3 servidores en background (sin ventanas) + abre el navegador.
REM Idempotente: omite servidores que ya esten corriendo.
REM Logs: logs\draft_advisor.log / meta_scraper.log / meta_analyzer.log
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0\..\.."

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   LOLCLI — Levantar Todo                                 ║
echo ║   Draft Advisor + Meta Scraper + Meta Analyzer           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No se encontro .venv\Scripts\python.exe
    echo    Crea el entorno: python -m venv .venv
    echo    Instala deps:    .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

set ROOT=%CD%
set PY=%ROOT%\.venv\Scripts\python.exe
set PYPATH=%ROOT%\src

if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

REM ─── Draft Advisor :8001 ──────────────────────────────────────────────────
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Draft Advisor  :8001  ya esta corriendo
) else (
    echo [START] Draft Advisor  :8001  ...
    set PYTHONPATH=%PYPATH%
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.draft_advisor.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\draft_advisor.log' -RedirectStandardError '%ROOT%\logs\draft_advisor.err' -WindowStyle Hidden"
)

REM ─── Meta Scraper :8002 ───────────────────────────────────────────────────
netstat -ano | findstr ":8002" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Meta Scraper   :8002  ya esta corriendo
) else (
    echo [START] Meta Scraper   :8002  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.meta_scraper.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\meta_scraper.log' -RedirectStandardError '%ROOT%\logs\meta_scraper.err' -WindowStyle Hidden"
)

REM ─── Meta Analyzer API :8000 ──────────────────────────────────────────────
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Meta Analyzer  :8000  ya esta corriendo
) else (
    echo [START] Meta Analyzer  :8000  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','uvicorn','src.riot_lol_cli.api_server:app','--reload','--port','8000' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\meta_analyzer.log' -RedirectStandardError '%ROOT%\logs\meta_analyzer.err' -WindowStyle Hidden"
)

echo.
echo [INFO] Esperando que los servidores arranquen...
timeout /t 6 /nobreak >nul

REM ─── Abrir frontends en el navegador ──────────────────────────────────────
echo [BROWSER] Abriendo frontends...

start "" "http://localhost:8001/draft"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8002"
timeout /t 1 /nobreak >nul
start "" "%ROOT%\outputs\splash-viewer.html"
timeout /t 1 /nobreak >nul
start "" "%ROOT%\projects\active\junglas-pro\index.html"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   Frontends disponibles                                  ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║   Draft Advisor   →  http://localhost:8001/draft         ║
echo ║   Meta Scraper    →  http://localhost:8002               ║
echo ║   Meta Analyzer   →  http://localhost:8000/docs          ║
echo ║   Splash Gallery  →  outputs\splash-viewer.html          ║
echo ║   Junglas Pro     →  projects\active\junglas-pro\        ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║   Sin ventanas CMD. Logs en logs\*.log y logs\*.err      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
