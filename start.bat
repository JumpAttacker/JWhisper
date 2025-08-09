@echo off
echo Starting Whisper Hotkey Application...
echo ========================================

call .venv\Scripts\activate.bat

echo Starting voice transcription...
echo Hold F9 to record, release to transcribe
echo Press ESC to exit
echo ========================================
python whisper_hotkey.py

pause