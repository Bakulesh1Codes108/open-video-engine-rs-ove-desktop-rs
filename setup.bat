@echo off
setlocal enabledelayedexpansion
title Open Video Engine (OVE) - Setup & Hardware Assistant
cd /d "%~dp0"

echo ======================================================================
echo   OPEN VIDEO ENGINE (OVE) - AUTOMATED SETUP & HARDWARE ASSISTANT
echo   Inspected & Verified under NVIDIA Security & Model Guidelines
echo ======================================================================
echo.
echo  Welcome to Open Video Engine (OVE)!
echo  This installer will guide you through setting up your local studio:
echo.
echo    [1] USER PERMISSIONS & CONSENT:
echo        Configure Node.js, Python 3.10+, FFmpeg, and Remotion React.
echo.
echo    [2] MULTI-DRIVE STORAGE SPACE GUIDANCE:
echo        Scan all storage drives (C:, D:, E:) and protect your OS drive
echo        from filling up by routing 4K/1080p video renders to your
echo        largest drive (e.g. D:\OVE_Video_Renders).
echo.
echo    [3] AI SETUP ASSISTANT & PROBLEM SOLVER:
echo        Autonomous diagnostic doctor that detects and self-heals
echo        missing dependencies, PATH issues, and GPU CUDA settings.
echo.
echo ======================================================================
echo.

:: Request user permission & consent
set /p USER_CONSENT="[?] Do you authorize Open Video Engine to configure your environment? [Y/n]: "
if /i "%USER_CONSENT%"=="n" (
    echo.
    echo [-] Setup cancelled by user. No system changes were made.
    echo [*] You can re-run setup.bat anytime when you are ready.
    pause
    exit /b 0
)

echo.
echo [+] Permission granted! Starting automated setup...
echo [*] Launching PowerShell configuration assistant with execution bypass...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo [-] Setup encountered an issue.
    echo [*] Launching AI Setup Assistant Doctor to diagnose and heal...
    echo ======================================================================
    if exist "%~dp0.venv\Scripts\python.exe" (
        "%~dp0.venv\Scripts\python.exe" "%~dp0scripts\setup_doctor.py" --fix
    ) else (
        python "%~dp0scripts\setup_doctor.py" --fix 2>nul
    )
    echo.
    echo [*] If issues persist, check setup_doctor.bat or visit https://github.com/Bakulesh1Codes108/Complete-Local-Video-Studio-Engine-
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [+] Setup finished successfully!
echo [*] You can now start the studio anytime by double-clicking 'Run_Studio.bat'!
echo ======================================================================
echo.
pause
