@echo off
echo Installing Python packages...
echo ========================================

call .venv\Scripts\activate.bat

pip install --upgrade pip
pip install faster-whisper
pip install sounddevice
pip install numpy
pip install pynput
pip install pyautogui
pip install pyperclip

echo.
echo Installation complete!
echo ========================================
pause