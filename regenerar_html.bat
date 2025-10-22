@echo off
setlocal enabledelayedexpansion

echo ===================================
echo  Regenerando HTML con plantilla claude-4-5
echo ===================================

echo.
echo [1/2] Verificando entorno...

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no está instalado o no está en el PATH.
    echo Por favor, instala Python 3.x y asegúrate de que esté en el PATH.
    pause
    exit /b 1
)

echo [2/2] Generando HTML (versión se incrementa automáticamente)...
python -m src.riot_lol_cli.cli generate --read-json data/cache/matches.json --html-template claude-4-5 --output outputs/claude-4-5/deshu-las-claude-4-5.html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo  ¡HTML regenerado exitosamente!
    echo  Archivos en la carpeta: outputs\claude-4-5
    echo ===================================
) else (
    echo.
    echo ===================================
    echo  ERROR: No se pudo generar el HTML
    echo ===================================
)

echo.
pause
