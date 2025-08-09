@echo off
title Add Whisper to Autostart
color 0A
echo ========================================
echo    ADD WHISPER TO WINDOWS AUTOSTART
echo ========================================
echo.

echo This will add Whisper to Windows startup.
echo The app will start automatically when Windows starts.
echo.

set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="y" goto cancel

echo.
echo Adding to startup folder...

REM Copy the VBS launcher to startup
copy "%~dp0start_minimized.vbs" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs" >nul

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo         SUCCESSFULLY INSTALLED!
    echo ========================================
    echo.
    echo Whisper will start automatically with Windows.
    echo.
    echo HOW TO USE:
    echo   - F9 (hold) = Record speech
    echo   - F9 (release) = Insert text
    echo   - Ctrl+Shift+Q = Exit app
    echo.
    echo TO REMOVE FROM STARTUP:
    echo   Run REMOVE_FROM_AUTOSTART.bat
    echo.
) else (
    echo.
    echo ERROR: Could not add to startup!
    echo Try running as Administrator.
    echo.
)

goto end

:cancel
echo.
echo Cancelled.
echo.

:end
pause