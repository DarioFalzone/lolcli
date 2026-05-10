@echo off
chcp 65001 >nul
REM ============================================================================
REM Home Hub — Centro de Operaciones
REM Health checks, service launcher, panel central
REM ============================================================================

cd /d "%~dp0\..\.."

set ROOT=%CD%
set PY=%ROOT%\.venv\Scripts\python.exe
set PYPATH=%ROOT%\src
set HOME_PORT=%LOLCLI_HOME_PORT%
if "%HOME_PORT%"=="" set HOME_PORT=8080

if not exist "%PY%" (
    echo ERROR: No se encontro .venv\Scripts\python.exe
    echo    Crea el entorno: python -m venv .venv
    echo    Instala deps:    .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Levantando Home Hub en puerto %HOME_PORT%...
echo.

set PYTHONPATH=%PYPATH%
%PY% -m riot_lol_cli.home.server

pause
