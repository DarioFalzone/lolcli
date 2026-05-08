@echo off
REM Launcher para Items Browser Server (puerto 8004 default)

setlocal enabledelayedexpansion
cd /d "%~dp0\..\.."

if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found. Run: python -m venv .venv
    exit /b 1
)

if not exist "data\items\database.json" (
    echo Items database no encontrada. Generandola...
    ".venv\Scripts\python.exe" scripts\update_items_database.py
    if errorlevel 1 (
        echo Fallo la generacion. Abortando.
        exit /b 1
    )
)

if "%LOLCLI_ITEMS_BROWSER_PORT%"=="" (
    set "PORT_LOG=8004"
) else (
    set "PORT_LOG=%LOLCLI_ITEMS_BROWSER_PORT%"
)

echo Levantando Items Browser en puerto %PORT_LOG%...
echo http://localhost:%PORT_LOG%
echo.

".venv\Scripts\python.exe" -m riot_lol_cli.items_browser.server

endlocal
