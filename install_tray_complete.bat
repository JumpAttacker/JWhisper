@echo off
title Installing Whisper Tray Dependencies

echo ========================================
echo    WHISPER TRAY DEPENDENCIES INSTALLER
echo ========================================
echo.

echo Checking Python virtual environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and accessible
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing core dependencies...
pip install --upgrade pip
pip install faster-whisper sounddevice numpy pynput pyautogui pyperclip pywin32

echo.
echo Installing tray-specific dependencies...
pip install pystray pillow

echo.
echo Verifying installations...
python -c "import pystray; import PIL; import faster_whisper; print('All dependencies installed successfully!')"

if errorlevel 1 (
    echo.
    echo ERROR: Some dependencies failed to install
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo    INSTALLATION COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo You can now run the Whisper service with:
echo   whisper_manager.bat
echo.
pause