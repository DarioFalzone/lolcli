@echo off
chcp 65001 >nul
REM ============================================================================
REM LOLCLI — Levantar Todo
REM Levanta Home + Meta API + Draft + Meta Scraper + Jungle + Items + Patch Notes en background.
REM Idempotente: omite servidores que ya esten corriendo.
REM Logs: logs\*.log y logs\*.err
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0\..\.."

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   LOLCLI — Levantar Todo                                 ║
echo ║   Home Hub + Meta API + Draft + Scraper + Jungle + Items ║
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
set HOME_PORT=%LOLCLI_HOME_PORT%
if "%HOME_PORT%"=="" set HOME_PORT=8080
set META_API_PORT=%LOLCLI_META_API_PORT%
if "%META_API_PORT%"=="" set META_API_PORT=8000
set DRAFT_ADVISOR_PORT=%LOLCLI_DRAFT_ADVISOR_PORT%
if "%DRAFT_ADVISOR_PORT%"=="" set DRAFT_ADVISOR_PORT=8001
set META_SCRAPER_PORT=%LOLCLI_META_SCRAPER_PORT%
if "%META_SCRAPER_PORT%"=="" set META_SCRAPER_PORT=8002
set JUNGLE_META_PORT=%LOLCLI_JUNGLE_META_PORT%
if "%JUNGLE_META_PORT%"=="" set JUNGLE_META_PORT=8003
set ITEMS_BROWSER_PORT=%LOLCLI_ITEMS_BROWSER_PORT%
if "%ITEMS_BROWSER_PORT%"=="" set ITEMS_BROWSER_PORT=8004
set PATCH_NOTES_PORT=%LOLCLI_PATCH_NOTES_PORT%
if "%PATCH_NOTES_PORT%"=="" set PATCH_NOTES_PORT=8005

if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

REM ─── Home Hub :8080 ───────────────────────────────────────────────────────
netstat -ano | findstr ":%HOME_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Home Hub       :%HOME_PORT%  ya esta corriendo
) else (
    echo [START] Home Hub       :%HOME_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.home.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\home.log' -RedirectStandardError '%ROOT%\logs\home.err' -WindowStyle Hidden"
)

REM ─── Draft Advisor :8001 ──────────────────────────────────────────────────
netstat -ano | findstr ":%DRAFT_ADVISOR_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Draft Advisor  :%DRAFT_ADVISOR_PORT%  ya esta corriendo
) else (
    echo [START] Draft Advisor  :%DRAFT_ADVISOR_PORT%  ...
    set PYTHONPATH=%PYPATH%
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.draft_advisor.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\draft_advisor.log' -RedirectStandardError '%ROOT%\logs\draft_advisor.err' -WindowStyle Hidden"
)

REM ─── Meta Scraper :8002 ───────────────────────────────────────────────────
netstat -ano | findstr ":%META_SCRAPER_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Meta Scraper   :%META_SCRAPER_PORT%  ya esta corriendo
) else (
    echo [START] Meta Scraper   :%META_SCRAPER_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.meta_scraper.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\meta_scraper.log' -RedirectStandardError '%ROOT%\logs\meta_scraper.err' -WindowStyle Hidden"
)

REM ─── Meta Analyzer API :8000 ──────────────────────────────────────────────
netstat -ano | findstr ":%META_API_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Meta Analyzer  :%META_API_PORT%  ya esta corriendo
) else (
    echo [START] Meta Analyzer  :%META_API_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','uvicorn','riot_lol_cli.api_server:app','--reload','--port','%META_API_PORT%' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\meta_analyzer.log' -RedirectStandardError '%ROOT%\logs\meta_analyzer.err' -WindowStyle Hidden"
)

REM ─── Jungle Meta :8003 ───────────────────────────────────────────────────
netstat -ano | findstr ":%JUNGLE_META_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Jungle Meta    :%JUNGLE_META_PORT%  ya esta corriendo
) else (
    echo [START] Jungle Meta    :%JUNGLE_META_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.jungle_meta.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\jungle_meta.log' -RedirectStandardError '%ROOT%\logs\jungle_meta.err' -WindowStyle Hidden"
)

REM ─── Items Browser :8004 ─────────────────────────────────────────────────
netstat -ano | findstr ":%ITEMS_BROWSER_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Items Browser  :%ITEMS_BROWSER_PORT%  ya esta corriendo
) else (
    echo [START] Items Browser  :%ITEMS_BROWSER_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.items_browser.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\items_browser.log' -RedirectStandardError '%ROOT%\logs\items_browser.err' -WindowStyle Hidden"
)

REM ─── Patch Notes :8005 ───────────────────────────────────────────────────
netstat -ano | findstr ":%PATCH_NOTES_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP]  Patch Notes    :%PATCH_NOTES_PORT%  ya esta corriendo
) else (
    echo [START] Patch Notes    :%PATCH_NOTES_PORT%  ...
    start /b "" powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.patch_notes.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\patch_notes.log' -RedirectStandardError '%ROOT%\logs\patch_notes.err' -WindowStyle Hidden"
)

echo.
echo [INFO] Esperando que los servidores arranquen...
timeout /t 6 /nobreak >nul

REM ─── Abrir frontends en el navegador ──────────────────────────────────────
echo [BROWSER] Abriendo frontends...

start "" "http://localhost:%HOME_PORT%"
timeout /t 1 /nobreak >nul
start "" "http://localhost:%DRAFT_ADVISOR_PORT%/draft"
timeout /t 1 /nobreak >nul
start "" "http://localhost:%META_SCRAPER_PORT%"
timeout /t 1 /nobreak >nul
start "" "http://localhost:%JUNGLE_META_PORT%"
timeout /t 1 /nobreak >nul
start "" "http://localhost:%ITEMS_BROWSER_PORT%"
timeout /t 1 /nobreak >nul
start "" "http://localhost:%PATCH_NOTES_PORT%"
timeout /t 1 /nobreak >nul
start "" "%ROOT%\outputs\splash-viewer.html"
timeout /t 1 /nobreak >nul
start "" "%ROOT%\projects\active\junglas-pro\index.html"

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   Frontends disponibles                                   ║
echo ╠═══════════════════════════════════════════════════════════╣
echo ║   Home Hub        →  http://localhost:%HOME_PORT%                ║
echo ║   Draft Advisor   →  http://localhost:%DRAFT_ADVISOR_PORT%/draft           ║
echo ║   Meta Scraper    →  http://localhost:%META_SCRAPER_PORT%                 ║
echo ║   Meta Analyzer   →  http://localhost:%META_API_PORT%/docs            ║
echo ║   Jungle Meta     →  http://localhost:%JUNGLE_META_PORT%                 ║
echo ║   Items Browser   →  http://localhost:%ITEMS_BROWSER_PORT%                 ║
echo ║   Patch Notes    →  http://localhost:%PATCH_NOTES_PORT%                 ║
echo ║   Splash Gallery  →  outputs\splash-viewer.html            ║
echo ║   Junglas Pro     →  projects\active\junglas-pro\          ║
echo ╠═══════════════════════════════════════════════════════════╣
echo ║   Sin ventanas CMD. Logs en logs\*.log y logs\*.err        ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
pause
