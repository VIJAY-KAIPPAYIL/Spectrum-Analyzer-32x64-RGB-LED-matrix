import numpy as np
import sounddevice as sd
import serial
import time

# Serial connection to ESP32
SERIAL_PORT = "COM3"  # Replace with your ESP32 serial port
BAUD_RATE = 115200

# Audio settings
SAMPLE_RATE = 8000  # Sampling frequency
FFT_SIZE = 256  # Number of FFT bins
NUM_BANDS = 32  # Number of frequency bands to map

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for ESP32 to initialize
    print(f"Connected to ESP32 on {SERIAL_PORT}")
except Exception as e:
    print(f"Error connecting to ESP32: {e}")
    exit()

# Function to map FFT data to RGB matrix bands
def process_audio_data(data):
    fft_data = np.fft.rfft(data)  # Perform FFT
    magnitude = np.abs(fft_data)  # Get magnitude
    magnitude = magnitude[:FFT_SIZE // 2]  # Only use positive frequencies
    
    # Group FFT bins into bands
    band_data = []
    band_size = len(magnitude) // NUM_BANDS
    for i in range(NUM_BANDS):
        band = np.mean(magnitude[i * band_size:(i + 1) * band_size])
        band_data.append(min(int(band), 255))  # Clamp to max value of 255
    
    return band_data

# Audio callback function
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_data = indata[:, 0]  # Use the first channel
    band_data = process_audio_data(audio_data)
    
    # Send data to ESP32
    try:
        ser.write(bytes(band_data))  # Send band data
    except Exception as e:
        print(f"Error sending data to ESP32: {e}")

# Start audio stream
try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=FFT_SIZE):
        print("Streaming audio... Press Ctrl+C to stop.")
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("Audio stream stopped.")
except Exception as e:
    print(f"Error starting audio stream: {e}")
finally:
    ser.close()
    print("Serial connection closed.")
