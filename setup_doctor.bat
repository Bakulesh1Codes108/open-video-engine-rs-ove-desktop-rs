@echo off
setlocal
title Open Video Engine (OVE) - AI Setup Assistant & Problem Solver
cd /d "%~dp0"

echo ======================================================================
echo   OVE AI SETUP ASSISTANT & SYSTEM DIAGNOSTIC DOCTOR
echo ======================================================================
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0scripts\setup_doctor.py" --fix
) else (
    python "%~dp0scripts\setup_doctor.py" --fix
)

echo.
echo ======================================================================
echo Diagnosis complete. Press any key to exit.
echo ======================================================================
pause
