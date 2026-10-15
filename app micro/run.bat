@echo off
title Weather Forecast Dashboard - Alliance University
echo ======================================================================
echo    ALLIANCE UNIVERSITY - Alliance School of Advanced Computing
echo    Micro-Project: Weather Forecast Dashboard using REST API and Tkinter
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found in system PATH. Attempting local user installation...
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting Weather Forecast Dashboard...
"%PYTHON_EXE%" main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error. Press any key to exit.
    pause
)
