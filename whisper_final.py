import threading
import time
from typing import List

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller, Key
from faster_whisper import WhisperModel
import pyperclip
import pyautogui

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

LANGUAGE = "ru"                
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  
kb = Controller()

print("Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")
print("=" * 60)

# -------------------- TEXT INSERTION --------------------
def insert_text(text):
    """Insert text with the most reliable method for your system"""
    
    # Save current clipboard
    old_clipboard = None
    try:
        old_clipboard = pyperclip.paste()
    except:
        pass
    
    # Copy new text to clipboard
    pyperclip.copy(text)
    time.sleep(0.05)
    
    # Method 1: Try pyautogui hotkey (most reliable on Windows)
    try:
        pyautogui.hotkey('ctrl', 'v')
        print("✓ Text inserted")
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
        print("✓ Text inserted")
        return
    except:
        pass
    
    # Method 3: Type directly with pyautogui
    try:
        time.sleep(0.1)
        pyautogui.write(text)
        print("✓ Text typed")
        return
    except:
        pass
    
    # If all fails, text is still in clipboard
    print("✓ Text in clipboard. Press Ctrl+V to paste.")

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
    
    if key == keyboard.Key.esc:
        print("\nExiting...")
        return False

# -------------------- MAIN --------------------
def main():
    print("WHISPER VOICE TO TEXT")
    print("=" * 40)
    print("F9 (hold) = Record")
    print("F9 (release) = Auto-insert text")
    print("ESC = Exit")
    print("=" * 40)
    print("\nReady!")
    
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()