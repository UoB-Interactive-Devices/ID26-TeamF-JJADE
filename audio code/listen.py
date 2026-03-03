import speech_recognition as sr
# pip install pyserial
import serial
import time

# Initialize the recognizer
r = sr.Recognizer()

def send_command(cmd):
    ser.write((cmd).encode())
    time.sleep(1)

# source changes across devices
# linux is /dev/ttyACM0
ser = serial.Serial("/dev/ttyACM0", 115200)


# Use the microphone as source
with sr.Microphone() as source:
    print(">>> Listening (Google)...")
    # This helps filter out background hiss
    r.adjust_for_ambient_noise(source, duration=0.5)
    audio = r.listen(source)

try:
    # recognize_google uses the free web API
    text = r.recognize_google(audio)
    print(f"Google thinks you said: {text}")

    command = text.strip()
    send_command(command)
    
except sr.UnknownValueError:
    print("Google could not understand the audio.")
except sr.RequestError as e:
    print(f"Could not request results from Google; {e}")