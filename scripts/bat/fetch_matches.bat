@echo off
setlocal enabledelayedexpansion

:: Navegar al root del repo
cd /d "%~dp0\..\.."

echo ===================================
echo  Obteniendo datos completos de partidas
echo ===================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no está instalado o no está en el PATH.
    pause
    exit /b 1
)

:: Cargar RIOT_API_KEY desde .env si existe
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if /I "%%A"=="RIOT_API_KEY" set "RIOT_API_KEY=%%B"
    )
)

:: Verificar si existe la API KEY (ya sea por .env o variable de entorno)
if "%RIOT_API_KEY%"=="" (
    echo ERROR: No se encontro RIOT_API_KEY.
    echo.
    echo Opciones:
    echo   - Crear archivo .env con: RIOT_API_KEY=tu-api-key
    echo   - o ejecutar: setx RIOT_API_KEY "tu-api-key"
    echo.
    pause
    exit /b 1
)

echo Ejecutando script de obtención de datos...
python scripts\fetch_matches_full.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo  ¡Datos obtenidos exitosamente!
    echo ===================================
) else (
    echo.
    echo ===================================
    echo  ERROR: No se pudieron obtener los datos
    echo ===================================
)

echo.
pause
