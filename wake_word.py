import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
import argparse
import sys
from scipy.signal import resample
import subprocess # Import the subprocess module

# One-time download of all pre-trained models (or only select models)
openwakeword.utils.download_models()

# Parse input arguments
parser=argparse.ArgumentParser()
parser.add_argument(
    "--chunk_size",
    help="How much audio (in number of samples) to predict on at once",
    type=int,
    default=1280,
    required=False
)
parser.add_argument(
    "--model_path",
    help="The path of a specific model to load",
    type=str,
    default="",
    required=False
)
parser.add_argument(
    "--inference_framework",
    help="The inference framework to use (either 'onnx' or 'tflite'",
    type=str,
    default='tflite',
    required=False
)
args=parser.parse_args()

# Get microphone stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
TARGET_RATE = 16000
CHUNK = 4096
INPUT_DEVICE_ID = 1


audio = pyaudio.PyAudio()

mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=INPUT_DEVICE_ID)

# Load pre-trained openwakeword models

if args.model_path != "":
    owwModel = Model(wakeword_models=[args.model_path], inference_framework=args.inference_framework)
else:
    owwModel = Model(inference_framework=args.inference_framework)

n_models = len(owwModel.models.keys())

# Run capture loop continuosly, checking for wakewords
if __name__ == "__main__":
    print("Listening for wakewords...")

    while True:
        # Get audio
        audio_buffer = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        num_samples_resampled = int(len(audio_buffer) * (TARGET_RATE/RATE))
        audio_resampled = resample(audio_buffer, num_samples_resampled).astype(np.int16)
        # Feed to openWakeWord model
        prediction = owwModel.predict(audio_resampled)
        wakeword_detected = False # Flag to track if any wakeword is detected
        for mdl in owwModel.prediction_buffer.keys():
            # Add scores in formatted table
            scores = list(owwModel.prediction_buffer[mdl])
            if scores[-1] > 0.5: # Assuming 0.5 is your detection threshold
                print("Wakeword Detected!")
                wakeword_detected = True # Set flag to True
                break # Exit loop once a wakeword is detected

        if wakeword_detected:
            print("Starting agent.py...")
            mic_stream.stop_stream()
            mic_stream.close()
            # Run agent.py as a subprocess
            agent_process = subprocess.Popen([sys.executable, "agent.py", "console"])
            agent_process.wait() # Wait for agent.py to finish

            print("Agent terminated. Resuming wake word listening...")
            # Reinitialize the microphone stream
            mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=INPUT_DEVICE_ID)
            owwModel.reset()
            wakeword_detected = False