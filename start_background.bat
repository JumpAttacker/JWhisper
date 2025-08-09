@echo off
echo Starting Whisper in Background
echo ========================================
echo.
echo The app will run hidden in background
echo F9 = Record and insert text
echo Ctrl+Alt+Q = Exit the application
echo.
echo Starting...

call .venv\Scripts\activate.bat

start /min pythonw whisper_background.py

echo.
echo Whisper is now running in background!
echo You can close this window.
echo.
timeout /t 5