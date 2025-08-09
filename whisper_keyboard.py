import threading
import time
from typing import List

import numpy as np
import sounddevice as sd
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Controller, Key
import keyboard  # Alternative keyboard library
from faster_whisper import WhisperModel
import pyperclip

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         
CHANNELS = 1                
DTYPE = "float32"           
PUSH_TO_TALK_KEY = pynput_keyboard.Key.f9  

WHISPER_MODEL_NAME = "small"   
WHISPER_DEVICE = "cpu"         
WHISPER_COMPUTE_TYPE = "int8"  

LANGUAGE = "ru"                
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        
INSERT_METHOD = "keyboard"  # "keyboard", "pynput", or "clipboard"

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  
keyboard_controller = Controller()

print("Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")
print("=" * 60)

# -------------------- TEXT INSERTION FUNCTIONS --------------------
def insert_text_keyboard_lib(text):
    """Insert text using keyboard library"""
    try:
        # Small delay to ensure focus
        time.sleep(0.1)
        # Type the text
        keyboard.write(text, delay=0.001)
        return True
    except Exception as e:
        print(f"keyboard lib failed: {e}")
        return False

def insert_text_pynput(text):
    """Insert text using pynput Controller"""
    try:
        # Small delay to ensure focus
        time.sleep(0.1)
        # Type the text
        keyboard_controller.type(text)
        return True
    except Exception as e:
        print(f"pynput failed: {e}")
        return False

def insert_text_clipboard(text):
    """Insert text via clipboard"""
    try:
        # Copy to clipboard
        pyperclip.copy(text)
        time.sleep(0.1)
        
        # Press Ctrl+V using pynput
        keyboard_controller.press(Key.ctrl)
        keyboard_controller.press('v')
        keyboard_controller.release('v')
        keyboard_controller.release(Key.ctrl)
        return True
    except Exception as e:
        print(f"clipboard paste failed: {e}")
        return False

def insert_text_auto(text):
    """Try multiple methods to insert text"""
    
    # Method selection based on INSERT_METHOD
    if INSERT_METHOD == "keyboard":
        if insert_text_keyboard_lib(text):
            print("✓ Text inserted (keyboard lib)")
            return
    elif INSERT_METHOD == "pynput":
        if insert_text_pynput(text):
            print("✓ Text inserted (pynput)")
            return
    elif INSERT_METHOD == "clipboard":
        if insert_text_clipboard(text):
            print("✓ Text inserted (clipboard)")
            return
    
    # Try all methods if preferred one fails
    methods = [
        ("keyboard lib", insert_text_keyboard_lib),
        ("pynput", insert_text_pynput),
        ("clipboard", insert_text_clipboard)
    ]
    
    for name, method in methods:
        if method(text):
            print(f"✓ Text inserted ({name})")
            return
    
    # Final fallback
    pyperclip.copy(text)
    print("✓ Text copied to clipboard. Press Ctrl+V to paste.")

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
    global INSERT_METHOD
    
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()
    
    # F10 to switch methods
    if key == pynput_keyboard.Key.f10:
        methods = ["keyboard", "pynput", "clipboard"]
        current_idx = methods.index(INSERT_METHOD)
        INSERT_METHOD = methods[(current_idx + 1) % len(methods)]
        print(f"\n➤ Switched to: {INSERT_METHOD} method")

def on_release(key):
    if key == PUSH_TO_TALK_KEY:
        if PUSH_TO_TALK_KEY in pressed_keys:
            pressed_keys.remove(PUSH_TO_TALK_KEY)
        if recording_flag:
            stop_recording_and_transcribe()
    
    if key == pynput_keyboard.Key.esc:
        print("\nExiting...")
        return False

# -------------------- MAIN --------------------
def main():
    print("WHISPER VOICE TO TEXT (MULTI-METHOD)")
    print("=" * 40)
    print("F9 (hold) = Record")
    print("F9 (release) = Auto-insert text")
    print("F10 = Switch insertion method")
    print("ESC = Exit")
    print("=" * 40)
    print(f"Current method: {INSERT_METHOD}")
    print("\nReady! Text will be inserted automatically.")
    
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()