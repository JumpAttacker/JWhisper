@echo off
title Whisper Hotkey - Quick Setup
color 0B

echo.
echo ██╗    ██╗██╗  ██╗██╗███████╗██████╗ ███████╗██████╗ 
echo ██║    ██║██║  ██║██║██╔════╝██╔══██╗██╔════╝██╔══██╗
echo ██║ █╗ ██║███████║██║███████╗██████╔╝█████╗  ██████╔╝
echo ██║███╗██║██╔══██║██║╚════██║██╔═══╝ ██╔══╝  ██╔══██╗
echo ╚███╔███╔╝██║  ██║██║███████║██║     ███████╗██║  ██║
echo  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo              HOTKEY VOICE-TO-TEXT SERVICE
echo              Quick Setup & Installation Guide
echo.
echo ========================================================
echo.

echo Welcome to Whisper Hotkey Service!
echo This tool converts your speech to text using AI.
echo.
echo How it works:
echo  1. Hold F9 key while speaking
echo  2. Release F9 key  
echo  3. Text appears automatically in your active app
echo.
echo ========================================================
echo.

set /p continue="Ready to begin setup? (Y/N): "
if /i not "%continue%"=="Y" (
    echo Setup cancelled. Run this file again when ready.
    pause
    exit /b 0
)

echo.
echo [STEP 1] Running system compatibility test...
echo.
call test_system.bat
if %errorlevel% neq 0 (
    echo.
    echo ⚠ System test failed. Please resolve the issues above before continuing.
    pause
    exit /b 1
)

echo.
echo [STEP 2] Installing service and dependencies...
echo.
call whisper_manager.bat

echo.
echo ========================================================
echo                    SETUP COMPLETE!
echo ========================================================
echo.
echo Your Whisper Hotkey service is now ready to use!
echo.
echo Quick Start Guide:
echo  • Look for the microphone icon in your system tray
echo  • Open any text editor (like Notepad)
echo  • Hold F9, speak clearly, then release F9
echo  • Your speech will appear as text automatically
echo.
echo Management Options:
echo  • Right-click tray icon for quick options
echo  • Run whisper_manager.bat for full control
echo  • View logs to monitor performance
echo.
echo Tips for best results:
echo  • Speak clearly and at normal pace
echo  • Use in quiet environments
echo  • Keep sentences reasonably short
echo  • Ensure microphone is working properly
echo.
echo Need help? Check SYSTEM_GUIDE.md for complete documentation.
echo.
echo Enjoy your new voice-to-text service!
echo.
pause