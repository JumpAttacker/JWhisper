@echo off
echo Starting Fixed Whisper Russian version...
echo ========================================

call .venv\Scripts\activate.bat

pip install pywin32 2>nul

echo Starting Russian speech recognition...
echo.
echo CONTROLS:
echo   F9  - Hold to record, release to insert text
echo   F10 - Switch insertion method
echo   ESC - Exit
echo ========================================
python whisper_hotkey_fixed.py

pause