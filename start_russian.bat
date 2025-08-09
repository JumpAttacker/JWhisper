@echo off
echo Starting Whisper Russian version...
echo ========================================

call .venv\Scripts\activate.bat

echo Starting Russian speech recognition...
echo Hold F9 to record
echo Release F9 to insert text
echo Press ESC to exit
echo ========================================
python whisper_hotkey_ru.py

pause