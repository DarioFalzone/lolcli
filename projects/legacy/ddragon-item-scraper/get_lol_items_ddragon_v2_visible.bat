@echo off
setlocal
set "DIR=%~dp0"
set "PS1=%DIR%get_lol_items_ddragon_v2.ps1"

if not exist "%PS1%" (
  echo [ERROR] No encuentro "%PS1%". Guardalo en esta misma carpeta.
  pause
  exit /b 1
)

REM Ejecuta mostrando la TUI en esta misma ventana (sin redireccionar a log)
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Lang es_AR -Out "%DIR%items_ddragon.csv"

echo.
echo [FIN] Si queres revisar los logs completos, miralos en la carpeta "logs".
pause
endlocal
