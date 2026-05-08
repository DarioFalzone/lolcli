@echo off
REM Launcher para Jungle Metagame Server (puerto 8003)

setlocal enabledelayedexpansion
cd /d "%~dp0\..\.."

if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found. Run: python -m venv .venv
    exit /b 1
)

echo Levantando Jungle Meta Server en puerto 8003...
echo http://localhost:8003
echo.

".venv\Scripts\python.exe" -m riot_lol_cli.jungle_meta.server

endlocal
