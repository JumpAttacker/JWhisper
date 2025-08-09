@echo off
echo Adding Whisper to Windows Startup
echo ========================================

REM Create VBS script for silent startup
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\whisper_startup.vbs"
echo WshShell.Run """%~dp0start_server_hidden.bat""", 0 >> "%TEMP%\whisper_startup.vbs"
echo Set WshShell = Nothing >> "%TEMP%\whisper_startup.vbs"

REM Copy to startup folder
copy "%TEMP%\whisper_startup.vbs" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs"

REM Create the hidden starter batch
echo @echo off > "%~dp0start_server_hidden.bat"
echo cd /d "%~dp0" >> "%~dp0start_server_hidden.bat"
echo call .venv\Scripts\activate.bat >> "%~dp0start_server_hidden.bat"
echo start /min python whisper_tray.py >> "%~dp0start_server_hidden.bat"
echo exit >> "%~dp0start_server_hidden.bat"

echo.
echo Successfully added to startup!
echo Whisper will start automatically when Windows starts.
echo.
echo To remove from startup, delete:
echo %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs
echo.
pause