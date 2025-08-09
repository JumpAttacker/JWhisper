@echo off
echo Test Microphone
echo ========================================

call .venv\Scripts\activate.bat

echo Starting microphone test...
echo Speak into microphone for 3 seconds
echo ========================================
python test_audio.py

pause