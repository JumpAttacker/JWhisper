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

LANGUAGE = "ru"                # Force Russian language
MIN_SPEECH_SEC = 0.5           # Increased minimum recording duration
PASTE_WITH_CLIPBOARD = True    # True: paste via clipboard (Ctrl+V), False: type character by character
AUDIO_THRESHOLD = 0.001        # Lowered threshold for better detection

# -------------------- GLOBAL STATE --------------------
recording_flag = False
buffer_lock = threading.Lock()
buffers: List[np.ndarray] = []  # Store audio chunks while key is held

# Initialize model at startup (first run will download weights to cache)
print("Загрузка модели Whisper... (первый запуск может занять время)")
model = WhisperModel(WHISPER_MODEL_NAME, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print(f"Модель загружена: {WHISPER_MODEL_NAME}")

# List available audio devices
print("\nДоступные аудио устройства:")
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"  {i}: {device['name']} - {device['max_input_channels']} каналов")

default_device = sd.query_devices(kind='input')
print(f"\nИспользуется устройство: {default_device['name']}")
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
    print("▶ Запись началась (удерживайте F9)...")

def stop_recording_and_transcribe():
    global recording_flag, buffers
    recording_flag = False
    print("■ Запись остановлена, распознаю...")

    # Concatenate all chunks
    with buffer_lock:
        if not buffers:
            print("Пустая запись - пропускаю.")
            return
        audio_chunk = np.concatenate(buffers, axis=0)
        buffers = []

    # Flatten if multi-channel
    if len(audio_chunk.shape) > 1:
        audio_chunk = audio_chunk.flatten()
    
    # Check duration
    duration_sec = len(audio_chunk) / SAMPLE_RATE
    if duration_sec < MIN_SPEECH_SEC:
        print(f"Слишком коротко ({duration_sec:.2f}с) - пропускаю.")
        return

    # Check audio level
    audio_level = np.abs(audio_chunk).mean()
    max_level = np.abs(audio_chunk).max()
    print(f"Уровень аудио: средний={audio_level:.4f}, макс={max_level:.4f}, Длительность: {duration_sec:.2f}с")
    
    if audio_level < AUDIO_THRESHOLD:
        print("Уровень аудио слишком низкий - речь не обнаружена.")
        print("Попробуйте говорить громче или увеличить громкость микрофона в Windows.")
        return

    # Normalize audio if levels are low but above threshold
    if max_level < 0.1:
        print("Нормализация тихого аудио...")
        audio_chunk = audio_chunk / max_level * 0.5

    # Audio is already float32 from sounddevice
    audio_float = audio_chunk

    # Transcribe
    try:
        print(f"Распознавание на русском языке...")
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
        print(f"Ошибка распознавания: {e}")
        return

    # Combine segments into one string
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    final_text = " ".join(t for t in text_parts if t).strip()

    if not final_text:
        print("Текст не распознан.")
        print("Попробуйте:")
        print("1. Говорить четче и громче")
        print("2. Проверить настройки микрофона в Windows")
        print("3. Запустить test_audio.py для проверки микрофона")
        return

    print(f"📄 Текст: {final_text}")

    # Insert into active window
    try:
        if PASTE_WITH_CLIPBOARD:
            pyperclip.copy(final_text)
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "v")
        else:
            # Character-by-character typing (slower, but doesn't use clipboard)
            pyautogui.typewrite(final_text)
        print("✓ Текст вставлен")
    except Exception as e:
        print("Ошибка вставки текста:", e)

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
        print("\nESC нажат - выход...")
        return False

# -------------------- MAIN --------------------
def main():
    print("Готово! Удерживайте F9, говорите → отпустите F9, и текст вставится в активное окно.")
    print("Курсор должен быть в нужном приложении (блокнот, браузер и т.п.).")
    print("Нажмите ESC для выхода из программы.")
    print("=" * 60)
    print("НАСТРОЕНО ДЛЯ РУССКОГО ЯЗЫКА")
    print("=" * 60)
    
    # Start audio stream
    try:
        with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE):
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
    except Exception as e:
        print(f"Ошибка: {e}")
        print("\nРешение проблем:")
        print("1. Проверьте подключение микрофона")
        print("2. Запустите 'python test_audio.py' для проверки аудио устройств")
        print("3. Убедитесь, что другие приложения не используют микрофон")
        print("4. Проверьте настройки микрофона в Windows")

if __name__ == "__main__":
    main()