@echo off
echo Starting Whisper Server (Simple)
echo ========================================

call .venv\Scripts\activate.bat

echo.
echo Server is starting...
echo You can minimize this window after start.
echo.

python whisper_server_simple.py