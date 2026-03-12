from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import serial
import time

# source changes across devices
# linux is /dev/ttyACM0
# windows is COM- whatever number shows in the IDE
ser = serial.Serial("/dev/ttyACM0")

def send_command(cmd):
    ser.write(cmd.encode())
    time.sleep(1)

# load whisper model
model = WhisperModel("base", compute_type="int8")

# recording parameters
sample_rate = 16000
duration = 1

while True:
    # record audio
    print(">>> Listening... ")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()

    audio = np.squeeze(audio)

    # transcirbe
    segments, _ = model.transcribe(audio)

    text = ""
    for segment in segments:
        text += segment.text

    text = text.strip()

    print("Whisper thinks you said:", text)

    if "spin" in text.lower():
        send_command("spin\n")

    if "stop" in text.lower():
        send_command("stop\n")

    if "fast" in text.lower():
        send_command("fast\n")
    
    if "slow" in text.lower():
        send_command("slow\n")