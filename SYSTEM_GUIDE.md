# Whisper Hotkey Service - Complete Management System

## Overview

This is a complete Windows management system for the Whisper voice-to-text hotkey service. It provides a professional interface for installing, managing, and monitoring the service with a system tray integration.

## Features

### 🎯 Core Functionality
- **F9 Hotkey**: Hold F9 to record voice, release to insert transcribed text
- **System Tray**: Runs silently in background with tray icon
- **Auto-start**: Optional Windows startup integration
- **Logging**: Comprehensive activity logging with rotation
- **Service Management**: Easy install/remove/restart functionality

### 🔧 Management Tools
- **whisper_manager.bat**: Complete service management menu
- **System Tray Menu**: Right-click for quick actions
- **Log Viewer**: Integrated log file viewing
- **Service Restart**: Restart service without full reinstall

### 📝 Logging System
- **whisper.log**: Main log file with timestamps
- **Log Rotation**: Automatic rotation at 5MB (keeps 3 backups)
- **Detailed Tracking**: Records transcriptions, errors, performance metrics

## File Structure

```
C:\whisper_hotkey\
├── whisper_manager.bat          # Main management interface
├── whisper_tray.py              # Enhanced tray application
├── whisper_hotkey.py            # Core hotkey functionality
├── start_hidden.vbs             # Hidden launcher
├── requirements.txt             # Python dependencies
├── install_tray_complete.bat    # Dependency installer
├── create_icon.py               # Icon generator
├── whisper.log                  # Activity log (generated)
└── .venv\                       # Python virtual environment
```

## Installation

### Method 1: Using Management Interface (Recommended)
1. Run `whisper_manager.bat` as Administrator
2. Select option `1` (Install Service)
3. Wait for installation to complete
4. The service will start automatically with tray icon

### Method 2: Manual Installation
1. Open Command Prompt as Administrator
2. Navigate to the whisper_hotkey directory
3. Run: `install_tray_complete.bat`
4. Run: `start_hidden.vbs`

## Usage

### Starting the Service
- **Automatic**: Service starts with Windows (if installed)
- **Manual**: Double-click `start_hidden.vbs` or use manager
- **Manager**: Run `whisper_manager.bat` → Option 1

### Using Voice-to-Text
1. Look for microphone icon in system tray
2. Focus cursor in target application (notepad, browser, etc.)
3. Hold F9 and speak clearly
4. Release F9 - text will be automatically inserted

### Managing the Service

#### System Tray Menu (Right-click tray icon):
- **Show Status**: Display current service status
- **View Logs**: Open log file in notepad
- **Restart Service**: Restart the service
- **Autostart**: Toggle Windows startup
- **Exit**: Stop service and exit

#### Management Interface (`whisper_manager.bat`):
- **Install Service**: Full installation with dependencies
- **Remove Service**: Complete uninstall
- **Check Status**: View service and process status
- **View Logs**: Open log file
- **Restart Service**: Quick restart
- **Install Dependencies**: Reinstall Python packages

## Configuration

### Voice Settings (in whisper_tray.py):
```python
WHISPER_MODEL_NAME = "small"       # Model size: tiny/base/small/medium/large-v3
WHISPER_DEVICE = "cpu"             # Processing: cpu/cuda
LANGUAGE = "ru"                    # Language: ru/en/auto-detect
MIN_SPEECH_SEC = 0.5               # Minimum recording duration
AUDIO_THRESHOLD = 0.001            # Audio sensitivity
```

### Hotkey Settings:
```python
PUSH_TO_TALK_KEY = keyboard.Key.f9 # Change hotkey (f8, f10, etc.)
```

## Troubleshooting

### Service Won't Start
1. Check if Python is installed and accessible
2. Verify virtual environment: `cd C:\whisper_hotkey && .venv\Scripts\activate`
3. Install dependencies: Run option 6 in manager
4. Check logs: `whisper.log` for error messages

### Audio Issues
1. Test microphone in Windows Settings
2. Check available audio devices: `python -m sounddevice`
3. Verify no other apps are using microphone exclusively
4. Run `test_microphone.bat` if available

### Text Not Inserting
1. Make sure target application has focus
2. Verify clipboard functionality
3. Check Windows permissions for automation
4. Try different target applications (notepad, browser)

### Tray Icon Missing
1. Check Windows hidden icon settings
2. Restart Windows Explorer: Ctrl+Shift+Esc → Explorer.exe → Restart
3. Verify pystray installation: `pip show pystray`

## Log Analysis

### Log Format
```
2025-01-09 10:30:45 | INFO | TRANSCRIPTION SUCCESS | Duration: 2.30s | Language: ru (0.998) | Processing: 1.50s | Text: Привет, как дела?
```

### Log Levels
- **INFO**: Normal operations, transcriptions
- **WARNING**: Non-critical issues (empty recordings, etc.)
- **ERROR**: Transcription failures, audio issues
- **CRITICAL**: System failures, model loading errors

### Log Rotation
- Main log: `whisper.log`
- Rotated logs: `whisper.log.1`, `whisper.log.2`, `whisper.log.3`
- Rotation trigger: 5MB file size

## Advanced Configuration

### Model Performance
- **tiny**: Fastest, least accurate
- **base**: Good balance for older hardware
- **small**: Recommended for most users
- **medium**: Better accuracy, slower
- **large-v3**: Best accuracy, requires powerful hardware

### GPU Acceleration (NVIDIA only)
1. Install CUDA toolkit
2. Set `WHISPER_DEVICE = "cuda"`
3. Set `WHISPER_COMPUTE_TYPE = "float16"`

### Multi-language Support
- Set `LANGUAGE = None` for auto-detection
- Set specific language: `LANGUAGE = "en"` (English), `"es"` (Spanish), etc.

## Uninstallation

### Complete Removal
1. Run `whisper_manager.bat`
2. Select option `2` (Remove Service)
3. Delete the entire `C:\whisper_hotkey` directory
4. Check Windows startup folder and registry (cleaned automatically)

## Support

### Log Files
Always check `whisper.log` first for error messages and system behavior.

### System Requirements
- Windows 10/11
- Python 3.8+
- 4GB RAM minimum (8GB+ recommended for larger models)
- Microphone access
- 2GB free disk space

### Performance Tips
1. Close unnecessary applications when using voice recognition
2. Use a quality microphone for better accuracy  
3. Speak clearly and avoid background noise
4. Use smaller models on older hardware