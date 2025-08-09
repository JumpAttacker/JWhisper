# JWhisper Configuration Guide

This guide explains how to configure JWhisper for optimal performance and to suit your specific needs.

## 📁 Configuration File Location

The main configuration is located in `src/jwhisper.py`. Look for the settings section at the top of the file:

```python
# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         
CHANNELS = 1                
DTYPE = "float32"           
PUSH_TO_TALK_KEY = keyboard.Key.f9  

WHISPER_MODEL_NAME = "small"   
WHISPER_DEVICE = "cpu"         
WHISPER_COMPUTE_TYPE = "int8"  

LANGUAGE = None                
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        
```

## ⚙️ Configuration Options

### Audio Settings

#### SAMPLE_RATE
- **Default**: `16000`
- **Description**: Audio sample rate in Hz
- **Recommendations**: 
  - `16000` - Standard for speech recognition (recommended)
  - `44100` - CD quality (may use more resources)

#### CHANNELS
- **Default**: `1`
- **Description**: Number of audio channels
- **Options**: 
  - `1` - Mono (recommended for speech)
  - `2` - Stereo (not recommended)

#### DTYPE
- **Default**: `"float32"`
- **Description**: Audio data type
- **Options**: 
  - `"float32"` - Recommended for better accuracy
  - `"int16"` - Lower memory usage

### Hotkey Configuration

#### PUSH_TO_TALK_KEY
- **Default**: `keyboard.Key.f9`
- **Description**: Key to press and hold for recording
- **Examples**:
  ```python
  # Function keys
  PUSH_TO_TALK_KEY = keyboard.Key.f9      # F9 (default)
  PUSH_TO_TALK_KEY = keyboard.Key.f8      # F8
  PUSH_TO_TALK_KEY = keyboard.Key.f10     # F10
  
  # Control combinations (requires code modification)
  # PUSH_TO_TALK_KEY = keyboard.Key.ctrl   # Ctrl key
  
  # Character keys
  PUSH_TO_TALK_KEY = keyboard.KeyCode.from_char('`')  # Backtick key
  ```

### Whisper Model Settings

#### WHISPER_MODEL_NAME
- **Default**: `"small"`
- **Description**: Size of the Whisper model to use
- **Options** (in order of accuracy vs speed):
  - `"tiny"` - Fastest, least accurate (~39 MB)
  - `"base"` - Good balance (~74 MB)
  - `"small"` - Recommended default (~244 MB)
  - `"medium"` - Higher accuracy (~769 MB)
  - `"large-v3"` - Best accuracy (~1550 MB)

#### WHISPER_DEVICE
- **Default**: `"cpu"`
- **Description**: Processing device
- **Options**:
  - `"cpu"` - Use CPU (compatible with all systems)
  - `"cuda"` - Use NVIDIA GPU (requires CUDA setup)

#### WHISPER_COMPUTE_TYPE
- **Default**: `"int8"`
- **Description**: Computation precision
- **Options** (CPU):
  - `"int8"` - Fastest, good accuracy
  - `"int8_float16"` - Balanced
  - `"float32"` - Highest accuracy, slowest
- **Options** (GPU):
  - `"float16"` - Recommended for GPU
  - `"int8_float16"` - Memory efficient

### Language Settings

#### LANGUAGE
- **Default**: `None`
- **Description**: Target language for transcription
- **Options**:
  - `None` - Auto-detect language (recommended)
  - `"en"` - English
  - `"ru"` - Russian
  - `"es"` - Spanish
  - `"fr"` - French
  - `"de"` - German
  - `"it"` - Italian
  - `"pt"` - Portuguese
  - `"zh"` - Chinese
  - And many more...

### Audio Processing Settings

#### MIN_SPEECH_SEC
- **Default**: `0.5`
- **Description**: Minimum recording duration in seconds
- **Recommendations**:
  - `0.3` - For quick commands
  - `0.5` - Balanced (default)
  - `1.0` - For longer phrases

#### AUDIO_THRESHOLD
- **Default**: `0.001`
- **Description**: Minimum audio level to consider as speech
- **Tuning**:
  - **Too high** - May miss quiet speech
  - **Too low** - May pick up background noise
  - **Quiet environment**: Try `0.0005`
  - **Noisy environment**: Try `0.005`

## 🔧 Advanced Configuration

### Custom Hotkey Combinations

For more complex hotkey combinations, you may need to modify the keyboard handling code. Here's an example for Ctrl+Shift+F9:

```python
# In the keyboard listener section, replace the simple key check with:
def on_key_press(key):
    global recording_flag, ctrl_pressed, shift_pressed
    
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = True
    elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
        shift_pressed = True
    elif key == keyboard.Key.f9 and ctrl_pressed and shift_pressed:
        if not recording_flag:
            start_recording()
```

### Performance Tuning

#### For Low-End Systems
```python
WHISPER_MODEL_NAME = "tiny"
WHISPER_COMPUTE_TYPE = "int8"
SAMPLE_RATE = 16000
```

#### For High-End Systems
```python
WHISPER_MODEL_NAME = "large-v3"
WHISPER_COMPUTE_TYPE = "float32"
SAMPLE_RATE = 16000
```

#### For GPU Systems (NVIDIA with CUDA)
```python
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
WHISPER_MODEL_NAME = "medium"  # or "large-v3"
```

### Logging Configuration

The logging system can be configured by modifying the `setup_logging()` function:

```python
def setup_logging():
    # Change log file size and backup count
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB instead of 5MB
        backupCount=5           # Keep 5 backups instead of 3
    )
    
    # Change log level
    logger.setLevel(logging.DEBUG)  # More verbose logging
```

## 🔄 Applying Configuration Changes

1. **Stop the service** using `scripts\manager.bat` (option 2)
2. **Edit** `src/jwhisper.py` with your changes
3. **Restart the service** using `scripts\manager.bat` (option 5)

## 🧪 Testing Configuration

After making changes:

1. **Test basic functionality** - Press F9 and speak
2. **Check transcription accuracy** - Try different phrases
3. **Monitor performance** - Check CPU/memory usage
4. **Review logs** - Look for any errors in the log file

## 💡 Configuration Tips

### For Different Use Cases

#### **Gaming**
- Use a less common hotkey to avoid conflicts
- Consider `keyboard.Key.scroll_lock` or `keyboard.Key.pause`

#### **Programming**
- Set language to `"en"` for consistency
- Use `"small"` or `"medium"` model for technical terms

#### **Multilingual Use**
- Keep `LANGUAGE = None` for auto-detection
- Use `"medium"` or `"large-v3"` for better language detection

#### **Presentations**
- Lower `AUDIO_THRESHOLD` for better pickup
- Use `"medium"` model for accuracy

### Troubleshooting Configuration Issues

#### Model Not Loading
- Check available disk space
- Verify internet connection for first-time model download
- Try a smaller model first

#### Poor Transcription Quality
- Increase model size
- Check microphone quality
- Adjust `AUDIO_THRESHOLD`
- Set specific language instead of auto-detect

#### High CPU Usage
- Use smaller model (`"tiny"` or `"base"`)
- Use `"int8"` compute type
- Check for other resource-intensive applications

## 📞 Support

If you need help with configuration:

1. **Check logs** in `src/jwhisper.log`
2. **Try default settings** first
3. **Report issues** on GitHub with your configuration details