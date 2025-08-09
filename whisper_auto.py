import threading
import time
from typing import List
import ctypes
from ctypes import wintypes

import numpy as np
import sounddevice as sd
from pynput import keyboard
from faster_whisper import WhisperModel
import pyperclip

# Windows API for sending input
SendInput = ctypes.windll.user32.SendInput

# Constants for Windows API
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_CONTROL = 0x11
VK_V = 0x56

# C struct definitions
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         
CHANNELS = 1                
DTYPE = "float32"           
PUSH_TO_TALK_KEY = keyboard.Key.f9  

WHISPER_MODEL_NAME = "small"   
WHISPER_DEVICE = "cpu"         
WHISPER_COMPUTE_TYPE = "int8"  

LANGUAGE = "ru"                
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  

print("Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")
print("=" * 60)

# -------------------- TEXT INSERTION FUNCTIONS --------------------
def press_key(hexKeyCode):
    """Press a single key"""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    """Release a single key"""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0x48, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def type_unicode_char(char):
    """Type a single Unicode character"""
    inputs = []
    
    # Key down
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, ord(char), KEYEVENTF_UNICODE, 0, ctypes.pointer(extra))
    inputs.append(Input(ctypes.c_ulong(1), ii_))
    
    # Key up
    ii2_ = Input_I()
    ii2_.ki = KeyBdInput(0, ord(char), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    inputs.append(Input(ctypes.c_ulong(1), ii2_))
    
    # Send both events
    nInputs = len(inputs)
    LPINPUT = Input * nInputs
    pInputs = LPINPUT(*inputs)
    SendInput(nInputs, pInputs, ctypes.sizeof(Input))

def type_text(text):
    """Type text character by character using Windows API"""
    for char in text:
        type_unicode_char(char)
        time.sleep(0.001)  # Small delay between characters

def paste_via_ctrl_v():
    """Simulate Ctrl+V using Windows API"""
    # Press Ctrl
    press_key(VK_CONTROL)
    time.sleep(0.05)
    
    # Press V
    press_key(VK_V)
    time.sleep(0.05)
    
    # Release V
    release_key(VK_V)
    time.sleep(0.05)
    
    # Release Ctrl
    release_key(VK_CONTROL)

def insert_text_auto(text):
    """Insert text automatically using the most reliable method"""
    # Method 1: Try direct typing with Windows API
    try:
        type_text(text)
        print("✓ Text inserted (direct typing)")
        return True
    except Exception as e:
        print(f"Direct typing failed: {e}")
    
    # Method 2: Try clipboard + Ctrl+V with Windows API
    try:
        pyperclip.copy(text)
        time.sleep(0.1)
        paste_via_ctrl_v()
        print("✓ Text inserted (clipboard paste)")
        return True
    except Exception as e:
        print(f"Clipboard paste failed: {e}")
    
    # Method 3: Fallback - just copy to clipboard
    try:
        pyperclip.copy(text)
        print("✓ Text copied to clipboard. Press Ctrl+V to paste.")
        return False
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")
        return False

# -------------------- AUDIO STREAM --------------------
def audio_callback(indata, frames, time_info, status):
    global recording_flag, buffers
    if recording_flag:
        with buffer_lock:
            buffers.append(indata.copy())

# -------------------- RECORDING LOGIC --------------------
def start_recording():
    global recording_flag, buffers
    with buffer_lock:
        buffers = []
    recording_flag = True
    print("\n▶ Recording...")

def stop_recording_and_transcribe():
    global recording_flag, buffers
    recording_flag = False
    print("■ Processing...")

    # Concatenate all chunks
    with buffer_lock:
        if not buffers:
            print("Empty recording")
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
        return

    # Check audio level
    audio_level = np.abs(audio_chunk).mean()
    max_level = np.abs(audio_chunk).max()
    
    if audio_level < AUDIO_THRESHOLD:
        print("No speech detected")
        return

    # Normalize if quiet
    if max_level < 0.1:
        audio_chunk = audio_chunk / max_level * 0.5

    # Transcribe
    try:
        segments, info = model.transcribe(
            audio_chunk,
            language="ru",              
            vad_filter=True,            
            beam_size=5,
            best_of=5,
            temperature=0.0,
            initial_prompt="Это русская речь."
        )
    except Exception as e:
        print(f"Error: {e}")
        return

    # Combine segments
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    final_text = " ".join(t for t in text_parts if t).strip()

    if not final_text:
        print("No text recognized")
        return

    print(f"📄 Text: {final_text}")
    
    # Insert text automatically
    insert_text_auto(final_text)

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
    
    if key == keyboard.Key.esc:
        print("\nExiting...")
        return False

# -------------------- MAIN --------------------
def main():
    print("WHISPER VOICE TO TEXT (AUTO-INSERT)")
    print("=" * 40)
    print("F9 (hold) = Record")
    print("F9 (release) = Auto-insert text")
    print("ESC = Exit")
    print("=" * 40)
    print("\nReady! Text will be inserted automatically.")
    
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()