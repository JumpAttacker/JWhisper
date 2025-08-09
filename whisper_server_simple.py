import threading
import time
from typing import List
import sys
import os

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
is_running = True

print("=" * 60)
print("WHISPER SERVER - SIMPLE VERSION")
print("=" * 60)
print("Loading model...")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")
print("=" * 60)
print("Server is running!")
print("F9 (hold) = Record")
print("F9 (release) = Insert text")
print("Ctrl+Shift+Q = Exit server")
print("=" * 60)
print("\nYou can minimize this window.")
print("The app will continue working in background.\n")

# -------------------- TEXT INSERTION --------------------
def insert_text(text):
    """Insert text with the most reliable method"""
    
    # Copy new text to clipboard
    pyperclip.copy(text)
    time.sleep(0.05)
    
    # Try pyautogui hotkey
    try:
        pyautogui.hotkey('ctrl', 'v')
        print(f"✓ Inserted: {text[:50]}...")
        return
    except:
        pass
    
    # Try pynput Controller
    try:
        kb.press(Key.ctrl)
        kb.press('v')
        time.sleep(0.01)
        kb.release('v')
        kb.release(Key.ctrl)
        print(f"✓ Inserted: {text[:50]}...")
        return
    except:
        pass
    
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
    print("▶ Recording...")

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

    # Insert text
    insert_text(final_text)

# -------------------- KEY HANDLING --------------------
pressed_keys = set()

def on_press(key):
    global is_running
    
    # Record on F9
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()
    
    # Track Ctrl and Shift
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pressed_keys.add('ctrl')
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        pressed_keys.add('shift')
    
    # Exit on Ctrl+Shift+Q
    if 'ctrl' in pressed_keys and 'shift' in pressed_keys:
        if hasattr(key, 'char') and key.char == 'q':
            print("\nExiting server...")
            is_running = False
            return False

def on_release(key):
    # Stop recording on F9 release
    if key == PUSH_TO_TALK_KEY:
        if PUSH_TO_TALK_KEY in pressed_keys:
            pressed_keys.remove(PUSH_TO_TALK_KEY)
        if recording_flag:
            stop_recording_and_transcribe()
    
    # Track Ctrl and Shift release
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pressed_keys.discard('ctrl')
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        pressed_keys.discard('shift')

# -------------------- MAIN --------------------
def main():
    global is_running
    
    try:
        # Start audio stream
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            # Start keyboard listener
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
                
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()