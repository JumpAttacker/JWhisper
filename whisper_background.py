import threading
import time
import sys
import os
from typing import List
import ctypes

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller, Key
from faster_whisper import WhisperModel
import pyperclip
import pyautogui

# Hide console window
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
SW_HIDE = 0
hWnd = kernel32.GetConsoleWindow()
if hWnd:
    user32.ShowWindow(hWnd, SW_HIDE)

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

# Load model
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)

# -------------------- TEXT INSERTION --------------------
def insert_text(text):
    """Insert text with the most reliable method"""
    
    # Copy new text to clipboard
    pyperclip.copy(text)
    time.sleep(0.05)
    
    # Try pyautogui hotkey
    try:
        pyautogui.hotkey('ctrl', 'v')
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
        return
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
    global recording_flag, buffers
    with buffer_lock:
        buffers = []
    recording_flag = True

def stop_recording_and_transcribe():
    global recording_flag, buffers
    recording_flag = False

    # Concatenate all chunks
    with buffer_lock:
        if not buffers:
            return
        audio_chunk = np.concatenate(buffers, axis=0)
        buffers = []

    # Flatten if multi-channel
    if len(audio_chunk.shape) > 1:
        audio_chunk = audio_chunk.flatten()
    
    # Check duration
    duration_sec = len(audio_chunk) / SAMPLE_RATE
    if duration_sec < MIN_SPEECH_SEC:
        return

    # Check audio level
    audio_level = np.abs(audio_chunk).mean()
    max_level = np.abs(audio_chunk).max()
    
    if audio_level < AUDIO_THRESHOLD:
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
    except:
        return

    # Combine segments
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    final_text = " ".join(t for t in text_parts if t).strip()

    if final_text:
        # Insert text
        insert_text(final_text)

# -------------------- KEY HANDLING --------------------
pressed_keys = set()

def on_press(key):
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()
    
    # Exit on Ctrl+Alt+Q
    if keyboard.Key.ctrl_l in pressed_keys and keyboard.Key.alt_l in pressed_keys and hasattr(key, 'char') and key.char == 'q':
        os._exit(0)
    
    # Track Ctrl and Alt
    if key == keyboard.Key.ctrl_l:
        pressed_keys.add(keyboard.Key.ctrl_l)
    if key == keyboard.Key.alt_l:
        pressed_keys.add(keyboard.Key.alt_l)

def on_release(key):
    if key == PUSH_TO_TALK_KEY:
        if PUSH_TO_TALK_KEY in pressed_keys:
            pressed_keys.remove(PUSH_TO_TALK_KEY)
        if recording_flag:
            stop_recording_and_transcribe()
    
    # Track Ctrl and Alt release
    if key == keyboard.Key.ctrl_l and keyboard.Key.ctrl_l in pressed_keys:
        pressed_keys.remove(keyboard.Key.ctrl_l)
    if key == keyboard.Key.alt_l and keyboard.Key.alt_l in pressed_keys:
        pressed_keys.remove(keyboard.Key.alt_l)

# -------------------- MAIN --------------------
def main():
    # Start audio stream
    with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
        # Start keyboard listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

if __name__ == "__main__":
    main()