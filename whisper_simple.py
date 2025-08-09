import threading
import time
from typing import List

import numpy as np
import sounddevice as sd
from pynput import keyboard
from faster_whisper import WhisperModel
import pyperclip
import winsound

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         # Microphone sample rate
CHANNELS = 1                # Mono
DTYPE = "float32"           
PUSH_TO_TALK_KEY = keyboard.Key.f9  # Hold F9 while speaking

# Model settings
WHISPER_MODEL_NAME = "small"   
WHISPER_DEVICE = "cpu"         
WHISPER_COMPUTE_TYPE = "int8"  

LANGUAGE = "ru"                # Russian language
MIN_SPEECH_SEC = 0.5           
AUDIO_THRESHOLD = 0.001        

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  

# Initialize model
print("Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")
print("=" * 60)

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
    print("\n▶ Recording... (hold F9)")
    # Beep to indicate recording started
    try:
        winsound.Beep(1000, 100)  # 1000Hz for 100ms
    except:
        pass

def stop_recording_and_transcribe():
    global recording_flag, buffers
    recording_flag = False
    
    # Beep to indicate recording stopped
    try:
        winsound.Beep(500, 100)  # 500Hz for 100ms
    except:
        pass
    
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
        print("No speech detected (too quiet)")
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

    # Copy to clipboard
    pyperclip.copy(final_text)
    
    # Success beep
    try:
        winsound.Beep(1500, 200)  # 1500Hz for 200ms
    except:
        pass
    
    print(f"✓ COPIED: {final_text}")
    print("  → Press Ctrl+V to paste")

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
    print("╔════════════════════════════════════════╗")
    print("║     WHISPER VOICE TO TEXT (RUSSIAN)    ║")
    print("╠════════════════════════════════════════╣")
    print("║  F9 (hold)  = Record                   ║")
    print("║  F9 (release) = Copy text to clipboard ║")
    print("║  Ctrl+V = Paste text                   ║")
    print("║  ESC = Exit                            ║")
    print("╚════════════════════════════════════════╝")
    print("\nReady! Text will be copied to clipboard.")
    print("You need to paste it manually with Ctrl+V")
    print("-" * 40)
    
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()