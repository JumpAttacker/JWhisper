@echo off
echo Installing additional keyboard library...
echo ========================================

call .venv\Scripts\activate.bat

pip install keyboard

echo.
echo Installation complete!
pause