@echo off
title Weather App - Unit Test & Rubric Dashboard Runner
echo ======================================================================
echo    ALLIANCE UNIVERSITY - Alliance School of Advanced Computing
echo    Visual Test Suite & Rubric Verification Dashboard (15 Tests)
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Launching Visual Test Runner...
"%PYTHON_EXE%" run_tests_gui.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error. Press any key to exit.
    pause
)
