@echo off
title Whisper Hotkey - Setup Autostart
color 0A
echo ========================================
echo     WHISPER HOTKEY - AUTOSTART SETUP
echo ========================================
echo.

echo Choose installation type:
echo.
echo [1] Simple Background (no tray icon)
echo [2] System Tray Version (with menu)
echo [3] Remove from autostart
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto simple
if "%choice%"=="2" goto tray
if "%choice%"=="3" goto remove
if "%choice%"=="4" goto end

:simple
echo.
echo Installing Simple Background version...
echo ========================================

REM Create startup script
echo @echo off > "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo cd /d "C:\whisper_hotkey" >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo call .venv\Scripts\activate.bat >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo start /min pythonw whisper_background.py >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo exit >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"

echo.
echo Successfully installed!
echo Whisper will start automatically with Windows.
echo.
echo Controls:
echo   F9 = Hold to record, release to insert text
echo   Ctrl+Alt+Q = Exit application
echo.
goto end

:tray
echo.
echo Installing System Tray version...
echo ========================================

REM First install dependencies
call .venv\Scripts\activate.bat
pip install pystray pillow pywin32 > nul 2>&1

REM Create startup script
echo @echo off > "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo cd /d "C:\whisper_hotkey" >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo call .venv\Scripts\activate.bat >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo start /min python whisper_tray.py >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"
echo exit >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat"

echo.
echo Successfully installed!
echo Whisper will start with system tray icon.
echo.
echo Controls:
echo   F9 = Hold to record, release to insert text
echo   Right-click tray icon = Menu options
echo.
goto end

:remove
echo.
echo Removing from autostart...
echo ========================================

del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.bat" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs" 2>nul

REM Also remove from registry if exists
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WhisperHotkey" /f 2>nul

echo.
echo Successfully removed from autostart!
echo.
goto end

:end
echo Press any key to exit...
pause > nul