import sounddevice as sd
import numpy as np
import time

print("Audio Device Test")
print("=" * 60)

# List all audio devices
devices = sd.query_devices()
print("\nAll available audio devices:")
for i, device in enumerate(devices):
    print(f"{i}: {device['name']} - Channels: {device['max_input_channels']} (input), {device['max_output_channels']} (output)")

# Get default input device
default_input = sd.query_devices(kind='input')
print(f"\nDefault input device: {default_input['name']}")
print(f"Sample rate: {default_input['default_samplerate']}")
print(f"Channels: {default_input['max_input_channels']}")

print("\n" + "=" * 60)
print("Recording 3 seconds of audio to test microphone...")
print("Please speak now!")

# Record audio
duration = 3  # seconds
sample_rate = 16000
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()

# Analyze the recording
audio_level = np.abs(recording).mean()
max_level = np.abs(recording).max()

print(f"\nRecording complete!")
print(f"Audio level (average): {audio_level:.6f}")
print(f"Audio level (max): {max_level:.6f}")
print(f"Recording shape: {recording.shape}")

if audio_level < 0.001:
    print("\n⚠️ WARNING: Very low audio level detected!")
    print("Possible issues:")
    print("1. Microphone is muted")
    print("2. Wrong microphone selected")
    print("3. Microphone permissions not granted")
    print("4. Microphone volume too low")
elif audio_level < 0.01:
    print("\n⚠️ Audio level is quite low. Consider increasing microphone volume.")
else:
    print("\n✓ Audio level looks good!")

# Save a sample for debugging
print("\nSaving audio sample to 'test_recording.txt' for analysis...")
with open('test_recording.txt', 'w') as f:
    f.write(f"Audio stats:\n")
    f.write(f"Mean: {audio_level}\n")
    f.write(f"Max: {max_level}\n")
    f.write(f"Min: {recording.min()}\n")
    f.write(f"Sample values (first 100):\n")
    f.write(str(recording[:100].flatten()))

print("\nTest complete! Check the audio levels above.")
print("If levels are too low, adjust your microphone settings in Windows.")