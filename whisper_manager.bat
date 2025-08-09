@echo off
title Whisper Hotkey Service Manager
color 0A

:menu
cls
echo.
echo ========================================
echo     WHISPER HOTKEY SERVICE MANAGER
echo ========================================
echo.
echo Current Status: 
call :check_service_status
echo.
echo ----------------------------------------
echo   1. Install Service (with tray icon)
echo   2. Remove Service  
echo   3. Check Service Status
echo   4. View Logs
echo   5. Restart Service
echo   6. Install Dependencies
echo   7. Exit
echo ----------------------------------------
echo.
set /p choice="Select option (1-7): "

if "%choice%"=="1" goto install_service
if "%choice%"=="2" goto remove_service  
if "%choice%"=="3" goto status_service
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto restart_service
if "%choice%"=="6" goto install_deps
if "%choice%"=="7" goto exit
echo Invalid choice. Please try again.
ping -n 3 127.0.0.1 >nul
goto menu

:install_service
cls
echo.
echo ========================================
echo           INSTALLING SERVICE
echo ========================================
echo.

REM Check if already running
tasklist | findstr /i "pythonw.exe" >nul 2>&1
if %errorlevel%==0 (
    echo WARNING: Whisper service already running!
    echo Stopping existing instances...
    taskkill /f /im pythonw.exe >nul 2>&1
    ping -n 2 127.0.0.1 >nul
)

echo Checking Python virtual environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and accessible
        pause
        goto menu
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/updating required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    goto menu
)

echo.
echo Setting up Windows service registration...
echo Adding to Windows startup...

set startup_vbs=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs
copy /Y "%CD%\start_hidden.vbs" "%startup_vbs%" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Added to Windows startup
) else (
    echo [ERROR] Failed to add to startup - check permissions
)

REM Startup configuration complete

echo.
echo Starting Whisper service with tray icon...
start "" "%CD%\start_hidden.vbs"

echo.
echo SUCCESS: Service installed and started!
echo - Service will start automatically with Windows
echo - Look for the microphone icon in your system tray
echo - Press F9 to record voice and convert to text
echo.
pause
goto menu

:remove_service
cls
echo.
echo ========================================
echo           REMOVING SERVICE
echo ========================================
echo.

echo Stopping any running Whisper processes...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq Whisper*" >nul 2>&1

echo Removing from Windows startup...
set startup_vbs=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs
if exist "%startup_vbs%" (
    del /F "%startup_vbs%"
    echo [OK] Removed from startup folder
) else (
    echo [--] Not found in startup folder
)

echo Cleaning registry entries (if any)...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WhisperHotkey" /f >nul 2>&1

echo.
echo SUCCESS: Service removed!
echo - Whisper service stopped
echo - Removed from Windows startup  
echo - Registry entries cleaned
echo.
pause
goto menu

:status_service
cls
echo.
echo ========================================
echo           SERVICE STATUS
echo ========================================
echo.
call :check_service_status
echo.
echo Process Information:
tasklist | findstr /i "python" | findstr /v "findstr"
echo.
echo Startup Status:
set startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set shortcut_path=%startup_folder%\Whisper Hotkey.lnk
if exist "%shortcut_path%" (
    echo [OK] Startup shortcut exists
) else (
    echo [--] No startup shortcut found
)

reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WhisperHotkey" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Registry startup entry found
) else (
    echo [--] No registry startup entry
)

echo.
echo Log File Status:
if exist "whisper.log" (
    echo [OK] Log file exists: whisper.log
    for %%A in (whisper.log) do echo     Size: %%~zA bytes
    echo     Last 3 entries:
    powershell -Command "Get-Content 'whisper.log' | Select-Object -Last 3"
) else (
    echo [--] No log file found
)
echo.
pause
goto menu

:view_logs
cls
echo.
echo ========================================
echo             VIEW LOGS
echo ========================================
echo.
if exist "whisper.log" (
    echo Opening whisper.log in notepad...
    notepad whisper.log
) else (
    echo No log file found (whisper.log)
    echo The log file will be created when the service runs.
)
echo.
pause
goto menu

:restart_service
cls  
echo.
echo ========================================
echo           RESTARTING SERVICE
echo ========================================
echo.

echo Stopping ALL existing Whisper processes...
REM Kill all pythonw.exe processes (tray versions)
taskkill /f /im pythonw.exe >nul 2>&1
REM Also try to kill specific python processes
wmic process where "name='python.exe' and commandline like '%%whisper%%'" delete >nul 2>&1
REM Wait a moment
ping -n 3 127.0.0.1 >nul

echo Starting Whisper service...
start "" "%CD%\start_hidden.vbs"

echo.
echo SUCCESS: Service restarted!
echo Check your system tray for the microphone icon.
echo.
pause
goto menu

:install_deps
cls
echo.
echo ========================================
echo        INSTALLING DEPENDENCIES
echo ========================================
echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        goto menu
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Additional tray dependencies...
pip install pystray pillow

echo.
echo SUCCESS: All dependencies installed!
echo.
pause
goto menu

:check_service_status
REM Check for pythonw.exe process (tray version)
tasklist | findstr /i "pythonw.exe" >nul 2>&1
if %errorlevel%==0 (
    echo [RUNNING] Whisper service is active ^(tray mode^)
    goto :eof
)

REM Check for python.exe process running whisper
wmic process where "name='python.exe'" get commandline 2>nul | findstr /i "whisper" >nul 2>&1
if %errorlevel%==0 (
    echo [RUNNING] Whisper service is active ^(console mode^)
    goto :eof
)

REM Check if status file exists (created by tray app)
if exist "%TEMP%\whisper_running.lock" (
    echo [RUNNING] Whisper service is active
    goto :eof
)

echo [STOPPED] Whisper service is not running
goto :eof

:exit
cls
echo.
echo Thank you for using Whisper Hotkey Service Manager!
echo.
ping -n 3 127.0.0.1 >nul
exit /b 0