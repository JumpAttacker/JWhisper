import queue
import threading
import time
from typing import List

import numpy as np
import sounddevice as sd
from pynput import keyboard
from faster_whisper import WhisperModel
import pyautogui
import pyperclip

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         # Microphone sample rate
CHANNELS = 1                # Mono
DTYPE = "float32"           # Changed to float32 for better compatibility
PUSH_TO_TALK_KEY = keyboard.Key.f9  # Hold F9 while speaking

# Model: small is fast and good quality; can use "medium" or "large-v3"
WHISPER_MODEL_NAME = "small"   # "tiny" | "base" | "small" | "medium" | "large-v3"
WHISPER_DEVICE = "cpu"         # "cpu" or "cuda" (if NVIDIA GPU available)
WHISPER_COMPUTE_TYPE = "int8"  # "int8"/"int8_float16" (CPU) | "float16"/"int8_float16" (GPU)

LANGUAGE = None                # None for auto-detect, or specific like "en", "ru", "es", etc.
MIN_SPEECH_SEC = 0.5           # Increased minimum recording duration
PASTE_WITH_CLIPBOARD = True    # True: paste via clipboard (Ctrl+V), False: type character by character
AUDIO_THRESHOLD = 0.01         # Minimum audio level to consider as speech

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  # Store audio chunks while key is held

# Initialize model at startup (first run will download weights to cache)
print("Loading Whisper model... (first run may take some time)")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Model loaded: {WHISPER_MODEL_NAME}")

# List available audio devices
print("\nAvailable audio devices:")
print(sd.query_devices())
print("\nUsing default input device:", sd.query_devices(kind='input')['name'])
print("=" * 60)

# -------------------- AUDIO STREAM --------------------
def audio_callback(indata, frames, time_info, status):
    global recording_flag, buffers
    if status:
        # Driver overflow/warnings
        print("Audio status:", status)
    if recording_flag:
        # Copy the current fragment
        with buffer_lock:
            buffers.append(indata.copy())

# -------------------- RECORDING LOGIC --------------------
def start_recording():
    global recording_flag, buffers
    with buffer_lock:
        buffers = []
    recording_flag = True
    print("▶ Recording started (holding F9)...")

def stop_recording_and_transcribe():
    global recording_flag, buffers
    recording_flag = False
    print("■ Recording stopped, transcribing...")

    # Concatenate all chunks
    with buffer_lock:
        if not buffers:
            print("Empty recording - skipping.")
            return
        audio_chunk = np.concatenate(buffers, axis=0)
        buffers = []

    # Flatten if multi-channel
    if len(audio_chunk.shape) > 1:
        audio_chunk = audio_chunk.flatten()
    
    # Check duration
    duration_sec = len(audio_chunk) / SAMPLE_RATE
    if duration_sec < MIN_SPEECH_SEC:
        print(f"Too short ({duration_sec:.2f}s) - skipping.")
        return

    # Check audio level
    audio_level = np.abs(audio_chunk).mean()
    print(f"Audio level: {audio_level:.4f}, Duration: {duration_sec:.2f}s")
    
    if audio_level < AUDIO_THRESHOLD:
        print("Audio level too low - no speech detected.")
        return

    # Audio is already float32 from sounddevice
    audio_float = audio_chunk

    # Transcribe
    try:
        if LANGUAGE is None:
            # Auto-detect language
            segments, info = model.transcribe(
                audio_float,
                language=None,          # Auto-detect language
                vad_filter=True,        # Simple VAD to remove silence
                beam_size=5,
                best_of=5,
                without_timestamps=False,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            detected_lang = info.language
            print(f"Detected language: {detected_lang}")
        else:
            # Force specific language
            segments, info = model.transcribe(
                audio_float,
                language=LANGUAGE,      # Force specific language
                vad_filter=True,        # Simple VAD to remove silence
                beam_size=5,
                best_of=5,
                without_timestamps=False,
                temperature=0.0
            )
    except Exception as e:
        print(f"Transcription error: {e}")
        return

    # Combine segments into one string
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    final_text = " ".join(t for t in text_parts if t).strip()

    if not final_text:
        print("No text recognized.")
        return

    print(f"📄 Text: {final_text}")

    # Insert into active window
    try:
        if PASTE_WITH_CLIPBOARD:
            pyperclip.copy(final_text)
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "v")
        else:
            # Character-by-character typing (slower, but doesn't use clipboard)
            pyautogui.typewrite(final_text)
        print("✓ Text inserted")
    except Exception as e:
        print("Text insertion error:", e)

# -------------------- KEY HANDLING --------------------
pressed_keys = set()

def on_press(key):
    # Start recording when F9 is pressed, if not already recording
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()

def on_release(key):
    # Stop when F9 is released
    if key == PUSH_TO_TALK_KEY:
        if PUSH_TO_TALK_KEY in pressed_keys:
            pressed_keys.remove(PUSH_TO_TALK_KEY)
        if recording_flag:
            stop_recording_and_transcribe()
    
    # Exit on ESC key
    if key == keyboard.Key.esc:
        print("\nESC pressed - exiting...")
        return False

# -------------------- MAIN --------------------
def main():
    print("Ready! Hold F9, speak → release F9, and text will be inserted into active window.")
    print("Focus cursor must be in the target application (notepad, browser, etc.).")
    print("Press ESC to exit the program.")
    print("=" * 60)
    
    # Start audio stream
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if microphone is connected and working")
        print("2. Run 'python -m sounddevice' to test audio devices")
        print("3. Make sure no other application is using the microphone exclusively")

if __name__ == "__main__":
    main()