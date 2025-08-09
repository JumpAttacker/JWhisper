import threading
import time
import sys
import os
from typing import List
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import subprocess

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller, Key
from faster_whisper import WhisperModel
import pyperclip
import pyautogui
import winsound

# System tray imports
import pystray
from PIL import Image, ImageDraw
import winreg
import win32api
import win32con
import win32gui_struct
import win32gui

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         
CHANNELS = 1                
DTYPE = "float32"           
PUSH_TO_TALK_KEY = keyboard.Key.f9  

WHISPER_MODEL_NAME = "small"   
WHISPER_DEVICE = "cpu"         
WHISPER_COMPUTE_TYPE = "int8"  

LANGUAGE = None  # Auto-detect language                
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        

# -------------------- LOGGING SETUP --------------------
def setup_logging():
    """Setup rotating log file for JWhisper activities"""
    log_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create rotating file handler (max 5MB, keep 3 backups)
    log_file = os.path.join(os.path.dirname(__file__), 'jwhisper.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(log_formatter)
    
    # Setup logger
    logger = logging.getLogger('JWhisperHotkey')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

# Create status file to indicate service is running
status_file = os.path.join(os.environ.get('TEMP', ''), 'jwhisper_running.lock')

# Check if already running
if os.path.exists(status_file):
    try:
        with open(status_file, 'r') as f:
            old_pid = int(f.read())
        # Check if old process still running
        import psutil
        if old_pid in [p.pid for p in psutil.process_iter() if p.name() == 'pythonw.exe']:
            logger.error("Another instance is already running!")
            print("ERROR: JWhisper is already running in system tray!")
            sys.exit(1)
    except:
        pass  # File exists but can't read/check - continue

try:
    with open(status_file, 'w') as f:
        f.write(str(os.getpid()))
    logger.info(f"Created status file: {status_file}")
except Exception as e:
    logger.error(f"Failed to create status file: {e}")

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  
kb = Controller()
tray_icon = None
audio_stream = None
keyboard_listener = None
model = None
is_running = True
recording_start_time = None
start_time = time.time()  # Track when application started

# -------------------- TRAY ICON --------------------
def create_icon_image():
    """Create an icon for the system tray"""
    # Create a simple microphone icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple microphone shape
    # Microphone body
    draw.ellipse([20, 10, 44, 40], fill='black')
    # Microphone stand
    draw.rectangle([30, 40, 34, 50], fill='black')
    # Microphone base
    draw.rectangle([20, 50, 44, 54], fill='black')
    
    return image

def on_quit(icon, item):
    """Quit the application from tray"""
    global is_running, audio_stream, keyboard_listener
    print("\nExiting from tray...")
    logger.info("Application shutdown initiated from tray")
    is_running = False
    
    # Remove status file
    try:
        if os.path.exists(status_file):
            os.remove(status_file)
            logger.info(f"Removed status file: {status_file}")
    except Exception as e:
        logger.error(f"Failed to remove status file: {e}")
    
    # Clean shutdown
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
    if keyboard_listener:
        keyboard_listener.stop()
    
    # Stop the tray icon
    icon.stop()
    
    # Exit the application
    os._exit(0)

def on_show_status(icon, item):
    """Show status in a message box"""
    def show_status_window():
        import ctypes
        
        # Get process info
        pid = os.getpid()
        uptime = time.time() - start_time if 'start_time' in globals() else 0
        uptime_str = f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
        
        # Check log file
        log_file = os.path.join(os.path.dirname(__file__), 'jwhisper.log')
        log_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
        log_size_str = f"{log_size/1024:.1f} KB" if log_size < 1024*1024 else f"{log_size/(1024*1024):.1f} MB"
        
        status_text = f"""JWhisper Voice-to-Text Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Service: RUNNING
📍 Process ID: {pid}
⏱️ Uptime: {uptime_str}
📝 Log size: {log_size_str}

Hotkeys:
• F9 (hold) = Start recording
• F9 (release) = Insert text
• ESC = Exit application

Model: {WHISPER_MODEL_NAME}
Language: {LANGUAGE if LANGUAGE else 'Auto-detect'}"""
        
        # Use Windows MessageBox API directly
        ctypes.windll.user32.MessageBoxW(
            0, 
            status_text, 
            "JWhisper Status", 
            0x40 | 0x0  # MB_ICONINFORMATION | MB_OK
        )
    
    # Run in separate thread to avoid blocking
    status_thread = threading.Thread(target=show_status_window, daemon=True)
    status_thread.start()
    
    logger.info("Status displayed to user")

def on_view_logs(icon, item):
    """Open log file in notepad"""
    log_file = os.path.join(os.path.dirname(__file__), 'jwhisper.log')
    try:
        if os.path.exists(log_file):
            subprocess.run(['notepad.exe', log_file], check=False)
            logger.info("Log file opened in notepad")
        else:
            show_notification("JWhisper Hotkey", "No log file found yet. Start using the application to generate logs.", quiet=True)
    except Exception as e:
        logger.error(f"Error opening log file: {e}")
        show_notification("Error", f"Could not open log file: {e}", quiet=True)

def on_restart_service(icon, item):
    """Restart the whisper service"""
    logger.info("Service restart requested from tray")
    show_notification("JWhisper Hotkey", "Restarting service...", quiet=True)
    
    # Get current script path
    script_path = os.path.abspath(__file__)
    vbs_path = os.path.join(os.path.dirname(__file__), 'start_hidden.vbs')
    
    try:
        # Start new instance
        subprocess.Popen([vbs_path], shell=True)
        time.sleep(1)
        
        # Exit current instance
        logger.info("Restarting application")
        on_quit(icon, item)
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        show_notification("Error", f"Could not restart service: {e}", quiet=True)

def toggle_autostart(icon, item):
    """Toggle autostart in Windows registry"""
    app_name = "JWhisperHotkey"
    app_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    
    try:
        # Open registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Check if already in autostart
        try:
            winreg.QueryValueEx(key, app_name)
            # Remove from autostart
            winreg.DeleteValue(key, app_name)
            print("✓ Removed from autostart")
            show_notification("JWhisper Hotkey", "Removed from autostart", quiet=True)
        except FileNotFoundError:
            # Add to autostart
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            print("✓ Added to autostart")
            show_notification("JWhisper Hotkey", "Added to autostart", quiet=True)
        
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error toggling autostart: {e}")

def is_in_autostart():
    """Check if app is in autostart"""
    app_name = "JWhisperHotkey"
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        return True
    except:
        return False

def show_notification(title, message, timeout=3000, quiet=False):
    """Show Windows notification - can be suppressed for quiet operation"""
    if quiet:
        # Only log, don't show notification for quiet operation
        logger.info(f"Notification (quiet): {title} - {message}")
        return
        
    try:
        # Try to show system tray notification first
        if tray_icon:
            tray_icon.notify(message, title)
        else:
            # Fallback to message box
            win32api.MessageBox(0, message, title, win32con.MB_OK | win32con.MB_ICONINFORMATION)
        logger.info(f"Notification shown: {title} - {message}")
    except Exception as e:
        logger.warning(f"Could not show notification: {e}")
        print(f"Notification: {title} - {message}")

def setup_tray():
    """Setup system tray icon"""
    global tray_icon
    
    # Create menu
    menu = pystray.Menu(
        pystray.MenuItem("Show Status", on_show_status),
        pystray.MenuItem("View Logs", on_view_logs),
        pystray.MenuItem("Restart Service", on_restart_service),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Autostart", toggle_autostart, checked=lambda item: is_in_autostart()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_quit)
    )
    
    # Create icon
    image = create_icon_image()
    tray_icon = pystray.Icon("JWhisperHotkey", image, "JWhisper Voice-to-Text\nF9 to record\nRight-click for options", menu)
    
    # Run icon in separate thread
    threading.Thread(target=tray_icon.run, daemon=True).start()

# -------------------- MODEL LOADING --------------------
def load_model():
    """Load JWhisper model"""
    global model
    print("Loading JWhisper model...")
    logger.info(f"Loading JWhisper model: {WHISPER_MODEL_NAME} on {WHISPER_DEVICE}")
    
    try:
        model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
        print(f"Model loaded: {WHISPER_MODEL_NAME}")
        logger.info(f"Model successfully loaded: {WHISPER_MODEL_NAME}")
        # Quiet startup - no notification sound, just log
        show_notification("JWhisper Hotkey", "Model loaded successfully. Press F9 to record.", quiet=True)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        show_notification("Error", f"Failed to load JWhisper model: {e}", quiet=True)
        raise

# -------------------- TEXT INSERTION --------------------
def insert_text(text):
    """Insert text with automatic clipboard pasting - prioritized method"""
    
    # Save current clipboard
    old_clipboard = None
    try:
        old_clipboard = pyperclip.paste()
    except:
        pass
    
    # Copy new text to clipboard
    pyperclip.copy(text)
    time.sleep(0.1)  # Slightly longer delay for reliability
    
    # Method 1: Try pyautogui hotkey (most reliable on Windows) - PRIORITIZED
    try:
        pyautogui.hotkey('ctrl', 'v')
        print("✓ Text pasted from clipboard")
        
        # Quiet completion beep - very brief and low volume
        try:
            winsound.Beep(800, 150)  # 800Hz for 150ms - quiet success sound
        except:
            pass
        return
    except:
        pass
    
    # Method 2: Try pynput Controller
    try:
        kb.press(Key.ctrl)
        kb.press('v')
        time.sleep(0.01)
        kb.release('v')
        kb.release(Key.ctrl)
        print("✓ Text pasted from clipboard")
        
        # Quiet completion beep
        try:
            winsound.Beep(800, 150)  # 800Hz for 150ms
        except:
            pass
        return
    except:
        pass
    
    # Method 3: Type directly with pyautogui (fallback only)
    try:
        time.sleep(0.1)
        pyautogui.write(text)
        print("✓ Text typed character by character")
        
        # Quiet completion beep
        try:
            winsound.Beep(800, 150)  # 800Hz for 150ms
        except:
            pass
        return
    except:
        pass
    
    # If all fails, text is still in clipboard
    print("✓ Text ready in clipboard. Press Ctrl+V to paste.")
    
    # Quiet completion beep even if auto-paste failed
    try:
        winsound.Beep(600, 100)  # Lower tone for partial success
    except:
        pass

# -------------------- AUDIO STREAM --------------------
def audio_callback(indata, frames, time_info, status):
    global recording_flag, buffers
    if recording_flag:
        with buffer_lock:
            buffers.append(indata.copy())

# -------------------- RECORDING LOGIC --------------------
def start_recording():
    global recording_flag, buffers, recording_start_time
    with buffer_lock:
        buffers = []
    recording_flag = True
    recording_start_time = time.time()
    print("\n▶ Recording...")
    logger.info("Recording started")

def stop_recording_and_transcribe():
    global recording_flag, buffers, model, recording_start_time
    recording_flag = False
    print("■ Processing...")
    
    processing_start = time.time()
    recording_duration = processing_start - recording_start_time if recording_start_time else 0

    # Concatenate all chunks
    with buffer_lock:
        if not buffers:
            print("Empty recording")
            logger.warning("Empty recording - no audio data captured")
            return
        audio_chunk = np.concatenate(buffers, axis=0)
        buffers = []

    # Flatten if multi-channel
    if len(audio_chunk.shape) > 1:
        audio_chunk = audio_chunk.flatten()
    
    # Check duration
    duration_sec = len(audio_chunk) / SAMPLE_RATE
    if duration_sec < MIN_SPEECH_SEC:
        print(f"Too short ({duration_sec:.1f}s)")
        logger.info(f"Recording too short: {duration_sec:.2f}s (min: {MIN_SPEECH_SEC}s)")
        return

    # Check audio level
    audio_level = np.abs(audio_chunk).mean()
    max_level = np.abs(audio_chunk).max()
    
    if audio_level < AUDIO_THRESHOLD:
        print("No speech detected")
        logger.info(f"No speech detected - audio level too low: {audio_level:.4f} (threshold: {AUDIO_THRESHOLD})")
        return

    # Normalize if quiet
    if max_level < 0.1:
        audio_chunk = audio_chunk / max_level * 0.5

    # Transcribe
    try:
        logger.info(f"Starting transcription - Duration: {duration_sec:.2f}s, Audio level: {audio_level:.4f}")
        
        segments, info = model.transcribe(
            audio_chunk,
            language="ru",              
            vad_filter=True,            
            beam_size=5,
            best_of=5,
            temperature=0.0,
            initial_prompt="Это русская речь."
        )
        
        detected_language = getattr(info, 'language', 'unknown')
        language_probability = getattr(info, 'language_probability', 0)
        
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Transcription error: {e}")
        return

    # Combine segments
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    final_text = " ".join(t for t in text_parts if t).strip()

    processing_time = time.time() - processing_start
    
    if not final_text:
        print("No text recognized")
        logger.info(f"No text recognized after {processing_time:.2f}s processing")
        return

    print(f"📄 Text: {final_text}")
    
    # Log successful transcription
    logger.info(
        f"TRANSCRIPTION SUCCESS | "
        f"Duration: {duration_sec:.2f}s | "
        f"Language: {detected_language} ({language_probability:.3f}) | "
        f"Processing: {processing_time:.2f}s | "
        f"Text: {final_text[:100]}{'...' if len(final_text) > 100 else ''}"
    )
    
    # Insert text
    insert_text(final_text)

# -------------------- KEY HANDLING --------------------
pressed_keys = set()

def on_press(key):
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()

def on_release(key):
    if key == PUSH_TO_TALK_KEY:
        if PUSH_TO_TALK_KEY in pressed_keys:
            pressed_keys.remove(PUSH_TO_TALK_KEY)
        if recording_flag:
            stop_recording_and_transcribe()

# -------------------- MAIN --------------------
def main():
    global audio_stream, keyboard_listener, is_running
    
    print("=" * 60)
    print("WHISPER VOICE-TO-TEXT SERVER")
    print("=" * 60)
    print("Running in system tray...")
    print("F9 (hold) = Record")
    print("F9 (release) = Auto-insert text")
    print("Right-click tray icon for options")
    print("=" * 60)
    
    # Log startup
    logger.info("="*50)
    logger.info("WHISPER HOTKEY SERVICE STARTING")
    logger.info(f"Model: {WHISPER_MODEL_NAME}, Device: {WHISPER_DEVICE}, Language: {LANGUAGE}")
    logger.info(f"Hotkey: {PUSH_TO_TALK_KEY}, Min duration: {MIN_SPEECH_SEC}s")
    logger.info("="*50)
    
    # Load model
    try:
        load_model()
    except Exception as e:
        logger.critical(f"Failed to initialize model: {e}")
        show_notification("Critical Error", "Failed to load JWhisper model. Check logs for details.", quiet=True)
        return
    
    # Setup system tray
    setup_tray()
    
    # Start audio stream
    try:
        # List available audio devices for logging
        devices = sd.query_devices()
        default_input = sd.query_devices(kind='input')
        logger.info(f"Using audio device: {default_input['name']}")
        
        audio_stream = sd.InputStream(
            callback=audio_callback, 
            channels=CHANNELS, 
            samplerate=SAMPLE_RATE, 
            dtype=DTYPE
        )
        audio_stream.start()
        
        # Start keyboard listener
        keyboard_listener = keyboard.Listener(
            on_press=on_press, 
            on_release=on_release
        )
        keyboard_listener.start()
        
        print("\n✓ Server started successfully!")
        print("Minimize this window - app will run quietly in system tray")
        print("Note: Only a quiet beep will sound after successful transcription")
        logger.info("Service started successfully - all components initialized")
        
        # Keep running
        while is_running:
            time.sleep(1)
            
    except Exception as e:
        error_msg = f"Failed to start audio/keyboard services: {e}"
        print(f"Error: {error_msg}")
        logger.critical(error_msg)
        show_notification("Startup Error", error_msg, quiet=True)
    finally:
        logger.info("Service shutting down")
        if audio_stream:
            audio_stream.stop()
            audio_stream.close()
        if keyboard_listener:
            keyboard_listener.stop()
        logger.info("Service stopped")

if __name__ == "__main__":
    # Hide console window (optional)
    # win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_MINIMIZE)
    
    main()