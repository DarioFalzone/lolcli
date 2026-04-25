@echo off
chcp 65001 >nul

:: Navegar al root del repo
cd /d "%~dp0\..\.."

echo ================================================
echo   🎨 Regenerador de Splash Arts Viewer
echo ================================================
echo.

echo 📊 Paso 1: Construyendo manifest...
python src/riot_lol_cli/cli.py build-splash-manifest
if errorlevel 1 (
    echo.
    echo ❌ Error al construir manifest
    pause
    exit /b 1
)

echo.
echo 🖼️ Paso 2: Generando HTML...
python src/riot_lol_cli/cli.py generate-splash-viewer
if errorlevel 1 (
    echo.
    echo ❌ Error al generar HTML
    pause
    exit /b 1
)

echo.
echo ================================================
echo   ✅ Visor regenerado exitosamente
echo ================================================
echo.
echo 💡 Abriendo en navegador...
start outputs\splash-viewer.html

timeout /t 3 >nul
