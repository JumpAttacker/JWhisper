# JWhisper Troubleshooting Guide

This guide helps you diagnose and fix common issues with JWhisper.

## 🚨 Quick Diagnosis

Before diving into specific issues, try these quick checks:

1. **Check if JWhisper is running**: Look for the microphone icon in your system tray
2. **Test your microphone**: Ensure it works in other applications
3. **Check logs**: Open `src/jwhisper.log` for error messages
4. **Restart the service**: Use `scripts\manager.bat` → option 5

## 🔧 Installation Issues

### Python Not Found

**Problem**: Error message "Python is not installed or not in PATH"

**Solutions**:
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **During installation**, check "Add Python to PATH"
3. **Restart command prompt** after installation
4. **Verify installation**: `python --version`

### Virtual Environment Creation Failed

**Problem**: Error creating virtual environment

**Solutions**:
1. **Run as Administrator**: Right-click command prompt → "Run as administrator"
2. **Update Python**: Ensure you have Python 3.8 or later
3. **Clear existing .venv**: Delete `.venv` folder and try again
4. **Check disk space**: Ensure sufficient disk space available

### Dependency Installation Failed

**Problem**: pip install failures

**Solutions**:
1. **Update pip**: `python -m pip install --upgrade pip`
2. **Clear pip cache**: `pip cache purge`
3. **Use different index**: `pip install -r requirements.txt -i https://pypi.python.org/simple/`
4. **Install individually**: Install packages one by one to identify issues

## 🎤 Audio Issues

### Microphone Not Detected

**Problem**: No audio input detected

**Solutions**:
1. **Check Windows settings**:
   - Settings → Privacy → Microphone
   - Allow apps to access microphone
   - Allow desktop apps to access microphone

2. **Test microphone**:
   - Windows Voice Recorder app
   - Check microphone levels in Sound settings

3. **Update audio drivers**:
   - Device Manager → Audio inputs and outputs
   - Update driver software

4. **Set default microphone**:
   - Right-click volume icon → Sounds
   - Recording tab → Set as default

### Poor Audio Quality / No Transcription

**Problem**: Audio recorded but not transcribed correctly

**Solutions**:
1. **Adjust audio threshold**:
   ```python
   # In src/jwhisper.py
   AUDIO_THRESHOLD = 0.0005  # Lower for quiet environments
   # or
   AUDIO_THRESHOLD = 0.005   # Higher for noisy environments
   ```

2. **Check microphone position**:
   - Speak directly into microphone
   - Maintain consistent distance (6-12 inches)
   - Reduce background noise

3. **Increase model size**:
   ```python
   # In src/jwhisper.py
   WHISPER_MODEL_NAME = "medium"  # or "large-v3"
   ```

4. **Set specific language**:
   ```python
   # In src/jwhisper.py
   LANGUAGE = "en"  # Replace with your language code
   ```

### Recording Too Short

**Problem**: "Recording too short" error messages

**Solutions**:
1. **Reduce minimum duration**:
   ```python
   # In src/jwhisper.py
   MIN_SPEECH_SEC = 0.3  # Reduce from default 0.5
   ```

2. **Hold F9 longer**: Ensure you hold the key while speaking
3. **Speak immediately**: Start speaking right after pressing F9

## 🖥️ System Integration Issues

### Service Won't Start

**Problem**: JWhisper service fails to start

**Solutions**:
1. **Check for existing instances**:
   - Task Manager → End all python/pythonw processes
   - Use manager.bat → option 5 (Restart Service)

2. **Run from command line**:
   ```bash
   cd "C:\path\to\JWhisper"
   .venv\Scripts\activate.bat
   python src\jwhisper.py
   ```
   Check error messages displayed

3. **Check permissions**:
   - Run manager.bat as Administrator
   - Ensure antivirus isn't blocking

4. **Verify file paths**:
   - Ensure all files are in correct locations
   - Check start_hidden.vbs points to correct paths

### System Tray Icon Missing

**Problem**: No microphone icon in system tray

**Solutions**:
1. **Check hidden icons**: Click ^ arrow in system tray
2. **Restart Windows Explorer**:
   - Task Manager → Windows processes → Windows Explorer
   - Right-click → Restart

3. **Check if service is running**:
   - Use manager.bat → option 3 (Check Status)
   - Task Manager → Look for pythonw.exe process

4. **Reinstall service**:
   - manager.bat → option 2 (Remove Service)
   - manager.bat → option 1 (Install Service)

### Text Not Pasting

**Problem**: Transcribed text doesn't appear

**Solutions**:
1. **Check target application focus**:
   - Click where you want text to appear
   - Ensure the application accepts text input

2. **Try different paste method**:
   ```python
   # In src/jwhisper.py, modify paste settings
   PASTE_WITH_CLIPBOARD = True   # Use Ctrl+V
   # or
   PASTE_WITH_CLIPBOARD = False  # Type character by character
   ```

3. **Check for conflicting software**:
   - Disable other clipboard managers temporarily
   - Check for keyboard hook conflicts

4. **Test with simple applications**:
   - Try with Notepad first
   - Verify basic functionality works

## 🔑 Hotkey Issues

### F9 Key Not Working

**Problem**: Pressing F9 doesn't start recording

**Solutions**:
1. **Check for key conflicts**:
   - Close other applications that might use F9
   - Check gaming software (Discord, Steam, etc.)

2. **Test in safe mode**: Boot Windows in safe mode to test
3. **Change hotkey**:
   ```python
   # In src/jwhisper.py
   PUSH_TO_TALK_KEY = keyboard.Key.f8  # or other key
   ```

4. **Check keyboard hardware**:
   - Test F9 in other applications
   - Try external keyboard if using laptop

### Hotkey Conflicts

**Problem**: F9 triggers other applications

**Solutions**:
1. **Identify conflicting software**: Check running applications
2. **Change JWhisper hotkey**: Use less common key like F12 or scroll lock
3. **Configure other software**: Disable F9 in conflicting applications

## 🧠 Model Issues

### Model Download Failed

**Problem**: Unable to download Whisper model

**Solutions**:
1. **Check internet connection**: Ensure stable internet access
2. **Clear model cache**: Delete `models/` folder if it exists
3. **Try smaller model**: Start with "tiny" or "base" model
4. **Manual download**: Download model files manually if needed

### Out of Memory Errors

**Problem**: System runs out of memory during transcription

**Solutions**:
1. **Use smaller model**:
   ```python
   WHISPER_MODEL_NAME = "tiny"  # or "base"
   ```

2. **Reduce audio quality**:
   ```python
   SAMPLE_RATE = 16000  # Don't go higher
   ```

3. **Close other applications**: Free up system memory
4. **Add more RAM**: Consider hardware upgrade for large models

## 🔄 Startup Issues

### Auto-startup Not Working

**Problem**: JWhisper doesn't start with Windows

**Solutions**:
1. **Reinstall startup**:
   - manager.bat → option 2 (Remove Service)
   - manager.bat → option 1 (Install Service)

2. **Check startup folder**: Look in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`
3. **Verify VBS file**: Ensure `start_hidden.vbs` exists and has correct paths
4. **Run as Administrator**: Try running manager.bat as Administrator

### Multiple Instances Running

**Problem**: Several JWhisper instances running simultaneously

**Solutions**:
1. **Stop all instances**:
   - Task Manager → End all python/pythonw processes
   - Or use manager.bat → option 5 (Restart Service)

2. **Clear lock file**: Delete `%TEMP%\jwhisper_running.lock`
3. **Check startup entries**: Remove duplicates from startup

## 📊 Performance Issues

### High CPU Usage

**Problem**: JWhisper uses too much CPU

**Solutions**:
1. **Use smaller model**: Switch to "tiny" or "base"
2. **Lower audio quality**: Reduce sample rate
3. **Check background processes**: Ensure no other heavy applications running
4. **Update drivers**: Update audio and system drivers

### Slow Transcription

**Problem**: Long delay between recording and text output

**Solutions**:
1. **Use GPU acceleration** (if available):
   ```python
   WHISPER_DEVICE = "cuda"  # Requires NVIDIA GPU + CUDA
   ```

2. **Optimize model settings**:
   ```python
   WHISPER_COMPUTE_TYPE = "int8"  # Fastest
   ```

3. **Shorter recordings**: Keep recordings under 30 seconds
4. **Close other applications**: Free up system resources

## 🔍 Diagnostic Tools

### Log Analysis

**Location**: `src/jwhisper.log`

**Common Error Messages**:
- `"Failed to load model"` → Model/memory issue
- `"Recording too short"` → Audio threshold issue
- `"No audio detected"` → Microphone issue
- `"Permission denied"` → Admin rights needed

### System Information Gathering

For support, gather this information:

```bash
# System info
python --version
pip list | findstr -i "whisper torch numpy"

# Audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# JWhisper status
# Run manager.bat → option 3
```

## 🆘 Getting Additional Help

### Before Seeking Help

1. **Check logs**: Review `src/jwhisper.log`
2. **Try default settings**: Reset configuration to defaults
3. **Test with minimal setup**: Basic installation on clean system

### Where to Get Help

1. **GitHub Issues**: Report bugs with system information
2. **Discussions**: Ask questions in GitHub Discussions
3. **Documentation**: Review configuration guide

### Information to Include

When reporting issues, include:
- **OS Version**: Windows 10/11 version
- **Python Version**: `python --version`
- **JWhisper Version**: Git commit or release version
- **Error Messages**: Copy from log file
- **Steps to Reproduce**: Detailed reproduction steps
- **System Specs**: CPU, RAM, microphone type

## 🔄 Reset to Defaults

If all else fails, try a complete reset:

1. **Stop service**: manager.bat → option 2
2. **Delete virtual environment**: Remove `.venv` folder
3. **Reset configuration**: Restore default settings in `src/jwhisper.py`
4. **Reinstall**: Run `scripts\install.bat`
5. **Reconfigure**: Use manager.bat → option 1

This should resolve most configuration-related issues.