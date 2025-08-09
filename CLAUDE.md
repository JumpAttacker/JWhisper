# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Windows voice-to-text application using OpenAI's Whisper model with push-to-talk functionality. The application runs as a system tray service with F9 hotkey for recording and automatic text insertion at cursor position.

## Key Architecture Components

### Main Application Variants
- **whisper_tray.py**: Primary version with system tray integration, logging, and full feature set
- **whisper_simple.py**: Simplified version without tray, used for testing
- **whisper_hotkey.py**: Original console version with basic functionality
- **whisper_server_simple.py**: Server variant for potential web interface

### Core Dependencies
- **faster-whisper**: Optimized Whisper implementation for transcription
- **pynput**: Keyboard hotkey monitoring (F9 push-to-talk)
- **sounddevice**: Audio capture from microphone
- **pystray**: System tray icon and menu functionality
- **pyautogui/pyperclip**: Text insertion via clipboard or typing

## Development Commands

### Running the Application
```bash
# Main tray version (hidden, no console)
wscript start_hidden.vbs

# With manager interface
start "" whisper_manager.bat

# Direct Python execution (shows console)
.venv\Scripts\python whisper_tray.py
```

### Dependency Management
```bash
# Create virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Additional tray dependencies if needed
pip install psutil pystray pillow
```

### Testing Audio
```bash
# Test microphone availability
python -m sounddevice

# Test audio recording
.venv\Scripts\python test_audio.py
```

## Important Configuration

### Key Settings in Python Files
Located at the top of whisper_tray.py and other variants:
- **PUSH_TO_TALK_KEY**: Default is keyboard.Key.f9
- **WHISPER_MODEL_NAME**: "tiny", "base", "small", "medium", "large-v3"
- **WHISPER_DEVICE**: "cpu" or "cuda" for GPU
- **LANGUAGE**: None for auto-detect or specific like "ru", "en"
- **MIN_SPEECH_SEC**: Minimum recording duration (0.5 seconds)
- **AUDIO_THRESHOLD**: Minimum audio level to consider as speech

### Service Management
**whisper_manager.bat** provides menu-driven interface for:
1. Install/Remove service with autostart
2. Check service status (uses pythonw.exe process and %TEMP%\whisper_running.lock file)
3. View logs (whisper.log with rotation at 5MB)
4. Restart service (kills ALL pythonw.exe processes to prevent duplicates)

### Autostart Configuration
- VBS file copied to: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WhisperHotkey.vbs`
- Uses start_hidden.vbs to launch without console window
- Status file created at: `%TEMP%\whisper_running.lock` containing PID

## Critical Implementation Details

### Audio Recording Flow
1. F9 pressed → `on_press()` sets `recording_flag = True`
2. Audio callback continuously appends to `buffers` list while flag is true
3. F9 released → `on_release()` triggers `stop_recording_and_transcribe()`
4. Audio chunks concatenated, checked for minimum duration and level
5. Transcription via faster_whisper model
6. Text insertion via clipboard (Ctrl+V) with fallback to typing

### Tray Menu Structure
- Show Status → MessageBox via ctypes.windll.user32.MessageBoxW (runs in thread)
- View Logs → Opens whisper.log in notepad
- Restart Service → Calls on_restart() function
- Toggle Autostart → Manages startup folder VBS file
- Exit → Cleanup and os._exit(0)

### Process Management
- Uses pythonw.exe for no-console execution
- Single instance enforcement via PID check in status file
- Prevents duplicates by checking existing pythonw.exe processes on startup
- Manager uses `taskkill /F /IM pythonw.exe` for complete cleanup

### Sound Notifications
- Quiet beep after successful transcription: `winsound.Beep(800, 150)`
- All other notifications suppressed when `quiet=True` parameter used
- Logging continues even when notifications are suppressed

## Common Issues and Solutions

### Status Window Freezing
Fixed by using ctypes MessageBoxW API in separate thread instead of tkinter

### Multiple Instances in Tray
Manager now kills ALL pythonw.exe processes before starting new instance

### Manager Status Not Updating
Check for pythonw.exe process presence and %TEMP%\whisper_running.lock file

### No Console Output
Application runs via pythonw.exe - check whisper.log for debug information

## File Structure Notes
- **start_hidden.vbs**: Launches whisper_tray.py without console
- **whisper_manager.bat**: Central management interface
- **whisper.log**: Rotating log file (5MB max, 3 backups)
- Virtual environment in `.venv\` directory