@echo off
title JWhisper Installation
color 0A

echo.
echo ========================================
echo        JWHISPER INSTALLATION
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

echo Python found. Proceeding with installation...
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo     INSTALLATION COMPLETED!
echo ========================================
echo.
echo JWhisper has been installed successfully.
echo.
echo Next steps:
echo 1. Run 'scripts\manager.bat' to configure and start the service
echo 2. Or run 'scripts\start_hidden.vbs' to start immediately
echo.
echo Press F9 while JWhisper is running to record voice and convert to text.
echo.
pause