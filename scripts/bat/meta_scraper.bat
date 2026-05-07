@echo off
REM ============================================================================
REM LOLCLI Meta Scraper - Script de Levantamiento (Windows)
REM Puerto 8002 — dashboard tier list Support / ADC
REM ============================================================================

setlocal enabledelayedexpansion

REM Navegar al root del repo (dos niveles arriba de scripts\bat\)
cd /d "%~dp0\..\.."

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   LOLCLI Meta Scraper                                    ║
echo ║   Tier list Support / ADC — Puerto 8002                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Verificar que el venv existe
if not exist ".venv\Scripts\python.exe" (
    echo ❌ No se encontro .venv\Scripts\python.exe
    echo    Crea el entorno con: python -m venv .venv
    echo    Luego instala: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [INFO] Levantando Meta Scraper en http://localhost:8002 ...
echo [INFO] Presiona Ctrl+C para detener el servidor.
echo.
echo   Dashboard : http://localhost:8002
echo   API Docs  : http://localhost:8002/docs
echo   Health    : http://localhost:8002/health
echo.

set PYTHONPATH=%CD%\src
.venv\Scripts\python.exe -m riot_lol_cli.meta_scraper.server

echo.
echo Servidor detenido.
pause
