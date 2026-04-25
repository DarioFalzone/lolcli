@echo off
setlocal EnableExtensions
pushd "%~dp0"

set "PS1=fetch_lol_patchnotes_v33a.ps1"
set "OUT=lol_patch_notes.json"
for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd-HHmmss')"') do set "TS=%%I"
set "LAUNCHER_LOG=logs\launcher_patchnotes_v33a_%TS%.log"
if not exist "logs" mkdir "logs"

set "N=%~1"
if "%N%"=="" set "N=6"

echo Iniciando... > "%LAUNCHER_LOG%"
if not exist "%PS1%" (
  echo [ERROR] Falta "%PS1%". >> "%LAUNCHER_LOG%"
  echo [ERROR] Falta "%PS1%".
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File ".\%PS1%" -LatestN %N% -Out "%OUT%" 1>> "%LAUNCHER_LOG%" 2>&1
set RC=%ERRORLEVEL%
echo PowerShell salio con codigo %RC% >> "%LAUNCHER_LOG%"
if not "%RC%"=="0" (
  echo [ERROR] Fallo. Ver "%LAUNCHER_LOG%"
  exit /b %RC%
)
echo OK. JSON: "%OUT%"
echo Log del lanzador: "%LAUNCHER_LOG%"
endlocal
