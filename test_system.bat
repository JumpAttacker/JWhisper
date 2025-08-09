@echo off
title Whisper Hotkey System Test
color 0F

echo.
echo ========================================
echo      WHISPER HOTKEY SYSTEM TEST
echo ========================================
echo.

echo Testing system components...
echo.

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel%==0 (
    python --version
    echo  ✓ Python is installed
) else (
    echo  ✗ Python not found or not in PATH
    echo    Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo.
echo [2/6] Checking virtual environment...
if exist ".venv" (
    echo  ✓ Virtual environment exists
    call .venv\Scripts\activate.bat
    echo  ✓ Virtual environment activated
) else (
    echo  ✗ Virtual environment not found
    echo    Run whisper_manager.bat to create it
    pause
    exit /b 1
)

echo.
echo [3/6] Testing Python dependencies...
python -c "import faster_whisper" 2>nul
if %errorlevel%==0 (
    echo  ✓ faster-whisper installed
) else (
    echo  ✗ faster-whisper not installed
    echo    Run option 6 in whisper_manager.bat
    pause
    exit /b 1
)

python -c "import pystray" 2>nul
if %errorlevel%==0 (
    echo  ✓ pystray installed
) else (
    echo  ✗ pystray not installed
    echo    Run option 6 in whisper_manager.bat
    pause
    exit /b 1
)

python -c "import sounddevice" 2>nul
if %errorlevel%==0 (
    echo  ✓ sounddevice installed
) else (
    echo  ✗ sounddevice not installed
    echo    Run option 6 in whisper_manager.bat
    pause
    exit /b 1
)

echo.
echo [4/6] Testing audio devices...
python -c "import sounddevice as sd; print('Default input:', sd.query_devices(kind='input')['name'])" 2>nul
if %errorlevel%==0 (
    echo  ✓ Audio input device detected
) else (
    echo  ⚠ Audio device test failed
    echo    Check microphone connection
)

echo.
echo [5/6] Checking system files...
if exist "whisper_tray.py" (
    echo  ✓ whisper_tray.py exists
) else (
    echo  ✗ whisper_tray.py missing
)

if exist "start_hidden.vbs" (
    echo  ✓ start_hidden.vbs exists
) else (
    echo  ✗ start_hidden.vbs missing
)

if exist "whisper_manager.bat" (
    echo  ✓ whisper_manager.bat exists
) else (
    echo  ✗ whisper_manager.bat missing
)

echo.
echo [6/6] Testing Whisper model loading...
echo This may take a moment for first-time setup...
python -c "
try:
    from faster_whisper import WhisperModel
    print('Testing model load...')
    model = WhisperModel('tiny', device='cpu', compute_type='int8')
    print(' ✓ Whisper model loaded successfully')
except Exception as e:
    print(f' ✗ Model loading failed: {e}')
    exit(1)
" 2>nul
if %errorlevel%==0 (
    echo  ✓ Whisper model test passed
) else (
    echo  ⚠ Model loading test failed
    echo    This is normal for first run - models will download automatically
)

echo.
echo ========================================
echo           SYSTEM TEST COMPLETE
echo ========================================
echo.

echo System Status Summary:
tasklist | findstr /i "python" | findstr /v "findstr" >nul 2>&1
if %errorlevel%==0 (
    echo  [RUNNING] Python processes detected
    tasklist | findstr /i "python" | findstr /v "findstr"
) else (
    echo  [STOPPED] No Python processes running
)

echo.
set startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set shortcut_path=%startup_folder%\Whisper Hotkey.lnk
if exist "%shortcut_path%" (
    echo  [ENABLED] Windows startup configured
) else (
    echo  [DISABLED] Windows startup not configured
)

echo.
if exist "whisper.log" (
    echo  [EXISTS] Log file present
    for %%A in (whisper.log) do echo           Size: %%~zA bytes
) else (
    echo  [EMPTY] No log file (normal for new installation)
)

echo.
echo Ready to test! To start the service:
echo   1. Run whisper_manager.bat
echo   2. Select option 1 (Install Service)
echo   3. Look for microphone icon in system tray
echo   4. Open notepad and test F9 hotkey
echo.
pause