@echo off
echo Removing Whisper from Windows Startup
echo ========================================

del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs" 2>nul

if %errorlevel% == 0 (
    echo Successfully removed from startup!
) else (
    echo Whisper was not in startup.
)

echo.
pause