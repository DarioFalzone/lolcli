@echo off
REM ============================================================================
REM LOLCLI Meta Analyzer - Script de Levantamiento Rápido (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

REM Navegar al root del repo
cd /d "%~dp0\..\.."

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   LOLCLI Meta Analyzer - Levantamiento Rápido            ║
echo ║   [BD + API + Frontend]                                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Paso 1: Instalar dependencias
echo [1/4] Instalando dependencias...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

REM Paso 2: Setup BD + datos demo
echo.
echo [2/4] Inicializando BD y generando datos demo...
python scripts\setup_meta_analyzer.py --demo
if errorlevel 1 (
    echo ❌ Error en setup
    pause
    exit /b 1
)
echo ✅ BD lista

REM Paso 3: Información
echo.
echo [3/4] Información del sistema:
echo.
echo   📊 Base de datos: data\meta_analyzer.db
echo   🎨 Frontend: outputs\meta-analyzer-dashboard.html
echo   🚀 API Backend: http://localhost:8000
echo   📚 Docs: http://localhost:8000/docs
echo.

REM Paso 4: Levantar API (opcional)
echo [4/4] ¿Deseas levantar el API Backend?
echo.
choice /C YN /M "Presiona Y para Si, N para No: "
if errorlevel 2 goto skip_api
if errorlevel 1 goto start_api

:start_api
echo.
echo ✅ Levantando API en puerto 8000...
echo.
echo 📝 Cuando veas "Uvicorn running on http://0.0.0.0:8000", presiona:
echo    1. Win+R y escribe: start outputs\meta-analyzer-dashboard.html
echo    2. O abre en navegador: http://localhost:8000/docs
echo.
python -m uvicorn src.riot_lol_cli.api_server:app --reload --port 8000
goto end

:skip_api
echo.
echo ⚠️  API no levantado. Para levantarlo manualmente:
echo    python -m uvicorn src.riot_lol_cli.api_server:app --reload
echo.
echo 📱 Para ver el frontend sin API (datos estáticos):
echo    start outputs\meta-analyzer-dashboard.html
echo.

:end
echo.
echo ✨ ¡Listo!
pause
