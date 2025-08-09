@echo off
title Remove Whisper from Autostart
color 0C
echo ========================================
echo   REMOVE WHISPER FROM WINDOWS AUTOSTART
echo ========================================
echo.

del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat" 2>nul

if %errorlevel% == 0 (
    echo Successfully removed from autostart!
) else (
    echo Whisper was not in autostart.
)

echo.
pause