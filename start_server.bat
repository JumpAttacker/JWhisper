@echo off
echo Starting Whisper Server (System Tray)
echo ========================================

call .venv\Scripts\activate.bat

python whisper_tray.py

pause