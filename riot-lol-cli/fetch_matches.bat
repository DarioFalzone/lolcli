@echo off
setlocal enabledelayedexpansion

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

:: Verificar si existe la API KEY
if "%RIOT_API_KEY%"=="" (
    echo ERROR: La variable de entorno RIOT_API_KEY no está configurada.
    echo.
    echo Para configurarla:
    echo   setx RIOT_API_KEY "tu-api-key-aqui"
    echo.
    pause
    exit /b 1
)

echo Ejecutando script de obtención de datos...
python fetch_matches_full.py

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
