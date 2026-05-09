@echo off
REM Launcher para Jungle Metagame Server (puerto 8003)

setlocal enabledelayedexpansion
cd /d "%~dp0\..\.."

if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found. Run: python -m venv .venv
    exit /b 1
)

if "%LOLCLI_JUNGLE_META_PORT%"=="" (
    set "PORT_LOG=8003"
) else (
    set "PORT_LOG=%LOLCLI_JUNGLE_META_PORT%"
)

echo Levantando Jungle Meta Server en puerto %PORT_LOG%...
echo http://localhost:%PORT_LOG%
echo.

".venv\Scripts\python.exe" -m riot_lol_cli.jungle_meta.server

endlocal
