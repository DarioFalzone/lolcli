@echo off
chcp 65001 >nul
REM ============================================================================
REM Rift Duel - Fixture del torneo 1v1
REM Regenera fixture.html desde fixture.json y lo sirve en localhost, con los
REM splash de assets/splash_arts como retratos (serve_fixture.py mapea /assets/).
REM Puerto: LOLCLI_RIFT_DUEL_PORT (default 8007). Cortar con Ctrl+C.
REM ============================================================================

cd /d "%~dp0\..\.."

set ROOT=%CD%
set PY=%ROOT%\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set RIFT_PORT=%LOLCLI_RIFT_DUEL_PORT%
if "%RIFT_PORT%"=="" set RIFT_PORT=8007
set RIFT_DIR=%ROOT%\claude-design-handoff\rift-duel
set RIFT_URL=http://localhost:%RIFT_PORT%/

REM Chequeo independiente del idioma de Windows (netstat dice LISTENING o ESCUCHANDO)
powershell -NoProfile -Command "if (Get-NetTCPConnection -State Listen -LocalPort %RIFT_PORT% -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if not errorlevel 1 (
    echo Ya hay un servidor en el puerto %RIFT_PORT%. Abriendo %RIFT_URL%
    start "" "%RIFT_URL%"
    exit /b 0
)

echo.
echo Regenerando fixture.html desde fixture.json...
"%PY%" "%RIFT_DIR%\build_fixture.py"
if errorlevel 1 (
    echo.
    echo AVISO: fixture.json tiene errores ^(ver arriba^). Se sirve la ultima version valida.
)

echo.
echo Rift Duel en %RIFT_URL%
echo Cortar con Ctrl+C.
echo.
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process '%RIFT_URL%'"
"%PY%" "%RIFT_DIR%\serve_fixture.py" --port %RIFT_PORT%

pause
