@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: Navegar al root del repo
cd /d "%~dp0\..\.."

REM ==============================================
REM   League of Legends - Splash Arts Downloader
REM ==============================================

echo.
echo ==============================================
echo   League of Legends - Splash Arts Downloader
echo ==============================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install Python 3 and try again.
    pause
    exit /b 1
)

REM Ensure requests is installed
echo Checking 'requests' module...
python -c "import requests" 1>nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing 'requests'...
    pip install requests
)

echo.
echo 1) Download ALL champions (may take a while)
echo 2) Download ONE champion
echo 3) Exit
echo.
set /p option=Select an option (1-3): 

if "%option%"=="1" (
    echo.
    echo Downloading ALL splash arts...
    python scripts\download_splash_arts.py
    goto :end
)

if "%option%"=="2" (
    echo.
    set /p champion=Enter champion name (e.g., Ahri or "Twisted Fate"): 
    echo Downloading splash arts for: !champion!
    python scripts\download_splash_arts.py "!champion!"
    goto :end
)

echo Invalid option.

:end
echo.
echo Output folder: assets\splash_arts\
echo Each champion has its own subfolder.
echo.
pause
