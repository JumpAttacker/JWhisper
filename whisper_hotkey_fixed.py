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
import win32clipboard
import win32con

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# -------------------- SETTINGS --------------------
SAMPLE_RATE = 16000         # Microphone sample rate
CHANNELS = 1                # Mono
DTYPE = "float32"           # Changed to float32 for better compatibility
PUSH_TO_TALK_KEY = keyboard.Key.f9  # Hold F9 while speaking

# Model: small is fast and good quality; can use "medium" or "large-v3"
WHISPER_MODEL_NAME = "small"   # "tiny" | "base" | "small" | "medium" | "large-v3"
WHISPER_DEVICE = "cpu"         # "cpu" or "cuda" (if NVIDIA GPU available)
WHISPER_COMPUTE_TYPE = "int8"  # "int8"/"int8_float16" (CPU) | "float16"/"int8_float16" (GPU)

LANGUAGE = "ru"                # Force Russian language
MIN_SPEECH_SEC = 0.5           # Increased minimum recording duration
INSERT_METHOD = "type"         # "clipboard", "type", or "manual"
AUDIO_THRESHOLD = 0.001        # Lowered threshold for better detection

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
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"  {i}: {device['name']} - {device['max_input_channels']} channels")

default_device = sd.query_devices(kind='input')
print(f"\nUsing device: {default_device['name']}")
print("=" * 60)

# -------------------- CLIPBOARD FUNCTIONS --------------------
def set_clipboard_text(text):
    """Set text to Windows clipboard"""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"Clipboard error: {e}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return False

def insert_text(text, method="type"):
    """Insert text using specified method"""
    if method == "manual":
        # Just copy to clipboard, user will paste manually
        if set_clipboard_text(text):
            print("✓ Text copied to clipboard. Press Ctrl+V to paste.")
        else:
            # Fallback to pyperclip
            pyperclip.copy(text)
            print("✓ Text copied to clipboard. Press Ctrl+V to paste.")
    
    elif method == "clipboard":
        # Copy to clipboard and paste
        if set_clipboard_text(text):
            time.sleep(0.1)
            # Try to paste with pyautogui
            try:
                pyautogui.hotkey('ctrl', 'v')
                print("✓ Text pasted")
            except Exception as e:
                print(f"Could not paste automatically: {e}")
                print("✓ Text is in clipboard. Press Ctrl+V to paste manually.")
        else:
            # Fallback
            pyperclip.copy(text)
            print("✓ Text copied to clipboard. Press Ctrl+V to paste.")
    
    else:  # method == "type"
        # Type character by character
        try:
            # Small delay before typing
            time.sleep(0.1)
            pyautogui.write(text, interval=0.01)
            print("✓ Text typed")
        except Exception as e:
            print(f"Could not type text: {e}")
            # Fallback to clipboard
            pyperclip.copy(text)
            print("✓ Text copied to clipboard. Press Ctrl+V to paste.")

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
    max_level = np.abs(audio_chunk).max()
    print(f"Audio level: avg={audio_level:.4f}, max={max_level:.4f}, Duration: {duration_sec:.2f}s")
    
    if audio_level < AUDIO_THRESHOLD:
        print("Audio level too low - no speech detected.")
        print("Try speaking louder or increase microphone volume in Windows.")
        return

    # Normalize audio if levels are low but above threshold
    if max_level < 0.1:
        print("Normalizing quiet audio...")
        audio_chunk = audio_chunk / max_level * 0.5

    # Audio is already float32 from sounddevice
    audio_float = audio_chunk

    # Transcribe
    try:
        print(f"Transcribing Russian speech...")
        segments, info = model.transcribe(
            audio_float,
            language="ru",              # Force Russian
            vad_filter=True,            # Simple VAD to remove silence
            beam_size=5,
            best_of=5,
            without_timestamps=False,
            temperature=0.0,
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            initial_prompt="Это русская речь."  # Hint for better Russian recognition
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
        print("Try:")
        print("1. Speak clearer and louder")
        print("2. Check microphone settings in Windows")
        print("3. Run test_audio.py to check microphone")
        return

    print(f"📄 Text: {final_text}")

    # Insert text using selected method
    insert_text(final_text, INSERT_METHOD)

# -------------------- KEY HANDLING --------------------
pressed_keys = set()

def on_press(key):
    # Start recording when F9 is pressed, if not already recording
    if key == PUSH_TO_TALK_KEY and PUSH_TO_TALK_KEY not in pressed_keys:
        pressed_keys.add(PUSH_TO_TALK_KEY)
        if not recording_flag:
            start_recording()
    
    # Change insertion method with F10
    if key == keyboard.Key.f10:
        global INSERT_METHOD
        methods = ["type", "clipboard", "manual"]
        current_idx = methods.index(INSERT_METHOD)
        INSERT_METHOD = methods[(current_idx + 1) % len(methods)]
        print(f"\n➤ Insertion method changed to: {INSERT_METHOD}")
        if INSERT_METHOD == "manual":
            print("  Text will be copied to clipboard only")
        elif INSERT_METHOD == "clipboard":
            print("  Text will be pasted using Ctrl+V")
        else:
            print("  Text will be typed character by character")

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
    print("Ready! Hold F9, speak → release F9")
    print("Cursor must be in target application (notepad, browser, etc.)")
    print("")
    print("Controls:")
    print("  F9  - Hold to record, release to transcribe")
    print("  F10 - Change insertion method (type/clipboard/manual)")
    print("  ESC - Exit program")
    print("")
    print(f"Current insertion method: {INSERT_METHOD}")
    print("=" * 60)
    print("CONFIGURED FOR RUSSIAN LANGUAGE")
    print("=" * 60)
    
    # Start audio stream
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check microphone connection")
        print("2. Run 'python test_audio.py' to test audio devices")
        print("3. Make sure no other app is using microphone exclusively")
        print("4. Check microphone settings in Windows")

if __name__ == "__main__":
    main()