@echo off
chcp 65001 >nul
REM ============================================================================
REM Rift Duel - Fixture del torneo 1v1
REM Regenera fixture.html y lo sirve en http://localhost:8007/ con los splash de
REM assets/splash_arts (serve_fixture.py). Dejar esta ventana abierta.
REM Puerto: LOLCLI_RIFT_DUEL_PORT (default 8007). Cortar con Ctrl+C.
REM ============================================================================

cd /d "%~dp0\..\.."

set "ROOT=%CD%"
set "RIFT_DIR=%ROOT%\claude-design-handoff\rift-duel"
set "RIFT_PORT=%LOLCLI_RIFT_DUEL_PORT%"
if "%RIFT_PORT%"=="" set "RIFT_PORT=8007"

REM Python, en orden: .venv de esta carpeta; .venv del clon principal (en un git
REM worktree el .venv no viaja); lanzador py de python.org; python del PATH.
REM Cada candidato se prueba de verdad: el alias de la Microsoft Store no cuenta.
set "PY="
set "PYARGS="
if exist "%ROOT%\.venv\Scripts\python.exe" set "PY=%ROOT%\.venv\Scripts\python.exe"
if defined PY "%PY%" -c "import sys" >nul 2>&1 || set "PY="
if not defined PY for /f "delims=" %%G in ('git -C "%ROOT%" rev-parse --path-format=absolute --git-common-dir 2^>nul') do for %%P in ("%%G\..") do if exist "%%~fP\.venv\Scripts\python.exe" set "PY=%%~fP\.venv\Scripts\python.exe"
if defined PY "%PY%" -c "import sys" >nul 2>&1 || set "PY="
if not defined PY py -3 -c "import sys" >nul 2>&1 && set "PY=py" && set "PYARGS=-3"
if not defined PY python -c "import sys" >nul 2>&1 && set "PY=python"
if not defined PY (
    echo ERROR: No encontre Python 3.
    echo    Opcion 1: crear el entorno en esta carpeta: python -m venv .venv
    echo    Opcion 2: instalar Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python: %PY% %PYARGS%
echo.

"%PY%" %PYARGS% "%RIFT_DIR%\serve_fixture.py" --build --open --port %RIFT_PORT%

pause
