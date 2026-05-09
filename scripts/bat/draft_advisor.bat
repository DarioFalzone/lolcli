@echo off
chcp 65001 >nul
REM ============================================================================
REM LOLCLI Draft Advisor - Script de Levantamiento (Windows)
REM Puerto 8001 — recomendador de picks con scoring multifactor
REM Log: logs\draft_advisor.log / logs\draft_advisor.err
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0\..\.."

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   LOLCLI Draft Advisor                                   ║
echo ║   Recomendador de picks                                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No se encontro .venv\Scripts\python.exe
    echo    Crea el entorno: python -m venv .venv
    echo    Instala deps: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

set ROOT=%CD%
set PY=%ROOT%\.venv\Scripts\python.exe
set PYPATH=%ROOT%\src
set "DRAFT_ADVISOR_PORT=%LOLCLI_DRAFT_ADVISOR_PORT%"
if "%DRAFT_ADVISOR_PORT%"=="" set "DRAFT_ADVISOR_PORT=8001"

netstat -ano | findstr ":%DRAFT_ADVISOR_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [SKIP] Draft Advisor ya esta corriendo en :%DRAFT_ADVISOR_PORT%
    echo.
    start "" "http://localhost:%DRAFT_ADVISOR_PORT%/draft"
    goto end
)

if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

echo [START] Levantando Draft Advisor en http://localhost:%DRAFT_ADVISOR_PORT% ...
powershell -WindowStyle Hidden -Command "$env:PYTHONPATH='%PYPATH%'; Start-Process -FilePath '%PY%' -ArgumentList '-m','riot_lol_cli.draft_advisor.server' -WorkingDirectory '%ROOT%' -RedirectStandardOutput '%ROOT%\logs\draft_advisor.log' -RedirectStandardError '%ROOT%\logs\draft_advisor.err' -WindowStyle Hidden"

echo [INFO] Esperando arranque...
timeout /t 5 /nobreak >nul

echo.
echo   App     : http://localhost:%DRAFT_ADVISOR_PORT%/draft
echo   Logs    : logs\draft_advisor.log
echo   Errores : logs\draft_advisor.err
echo.

start "" "http://localhost:%DRAFT_ADVISOR_PORT%/draft"

:end
echo.
pause
