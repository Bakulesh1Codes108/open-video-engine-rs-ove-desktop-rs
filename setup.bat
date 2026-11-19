@echo off
setlocal
title Open Video Engine (OVE) - Windows Automated Setup
cd /d "%~dp0"

echo ======================================================================
echo   OPEN VIDEO ENGINE (OVE) - AUTOMATED WINDOWS SETUP INSTALLER
echo   (Configures Python, Node.js, FFmpeg, Remotion, and AI Engines)
echo ======================================================================
echo.

:: Launch PowerShell installer with execution policy bypass
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if errorlevel 1 (
    echo.
    echo [-] Setup encountered an issue. See above output for details.
    pause
    exit /b 1
)

echo.
echo [+] Setup finished successfully!
echo [*] You can now start the studio anytime by double-clicking 'Run_Studio.bat'!
echo.
pause
