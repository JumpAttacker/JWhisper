@echo off
echo ========================================
echo         TESTING WHISPER SERVER
echo ========================================
echo.

echo Checking Python virtual environment...
if exist .venv\Scripts\python.exe (
    echo [OK] Virtual environment found
) else (
    echo [ERROR] Virtual environment not found!
    echo Run install.bat first
    pause
    exit /b 1
)

echo.
echo Checking required modules...
call .venv\Scripts\activate.bat

python -c "import faster_whisper" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] faster_whisper not installed!
    echo Installing...
    pip install faster-whisper
)

python -c "import sounddevice" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] sounddevice not installed!
    echo Installing...
    pip install sounddevice
)

python -c "import pynput" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pynput not installed!
    echo Installing...
    pip install pynput
)

python -c "import pyautogui" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pyautogui not installed!
    echo Installing...
    pip install pyautogui
)

python -c "import pyperclip" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pyperclip not installed!
    echo Installing...
    pip install pyperclip
)

echo.
echo All modules OK!
echo.
echo Starting server for testing...
echo ========================================
echo.

python whisper_server_simple.py