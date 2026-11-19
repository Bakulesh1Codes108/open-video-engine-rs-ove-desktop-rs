@echo off
setlocal enabledelayedexpansion
title Open Video Engine (OVE) - Studio Launcher

echo ======================================================================
echo   OPEN VIDEO ENGINE (OVE) - 1-CLICK WINDOWS STUDIO LAUNCHER
echo ======================================================================

set "REPO_DIR=%~dp0"
cd /d "%REPO_DIR%"

:: Check if virtual environment exists
if not exist "%REPO_DIR%.venv\Scripts\python.exe" (
    echo [!] Virtual environment not found.
    echo [*] Running automated 1-Click setup first...
    call "%REPO_DIR%setup.bat"
    if errorlevel 1 (
        echo [-] Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

:: Check if node_modules exists
if not exist "%REPO_DIR%node_modules" (
    echo [*] Installing Remotion React dependencies (npm install)...
    call npm install
)

echo [*] Activating Python environment...
call "%REPO_DIR%.venv\Scripts\activate.bat"

echo.
echo ======================================================================
echo   Launching OVE Studio Pro UI on http://127.0.0.1:8080/
echo   Themes: DaVinci Resolve, CapCut, VN Editor, Premiere, Filmora
echo   Press Ctrl+C in this terminal window to stop the studio.
echo ======================================================================
echo.

:: Open default browser in 2 seconds
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8080/"

:: Launch studio server
"%REPO_DIR%.venv\Scripts\python.exe" "%REPO_DIR%scripts\studio.py" ove 8080

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo [-] Studio encountered an issue or port was closed.
    echo [*] Would you like to run the AI Setup Doctor to diagnose & repair?
    echo ======================================================================
    "%REPO_DIR%.venv\Scripts\python.exe" "%REPO_DIR%scripts\setup_doctor.py" --fix
    pause
)
