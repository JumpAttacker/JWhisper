@echo off
echo Installing system tray dependencies...
echo ========================================

call .venv\Scripts\activate.bat

pip install pystray
pip install pillow
pip install pywin32
pip install keyboard

echo.
echo Installation complete!
pause