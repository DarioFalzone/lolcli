@echo off
setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0"

set "PS1=fetch_lol_patchnotes_v33b.ps1"
set "OUT=lol_patch_notes.json"
set "N=%~1"
if "%N%"=="" set "N=6"

if not exist "%PS1%" (
  echo [ERROR] Falta "%PS1%" en esta carpeta.
  pause
  exit /b 1
)

echo === Fetch LOL Patch Notes V3.3b (N=%N%) ===
echo Carpeta: %CD%
echo --------------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -File ".\%PS1%" -LatestN %N% -Out "%OUT%"
set RC=%ERRORLEVEL%
echo --------------------------------------
echo Codigo de salida: %RC%
echo Si hay errores, revisa .\logs\fetch_patchnotes_v33b_*.log
echo Presiona una tecla para salir...
pause >nul

popd
endlocal

