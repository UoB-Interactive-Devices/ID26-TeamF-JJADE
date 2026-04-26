import time
import serial
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from openai import OpenAI
import json
import os

PORT = "/dev/ttyACM0"
BAUD = 115200

# import API key
with open(os.path.expanduser("~/.openai/IDkey.txt")) as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()

client = OpenAI()

SPICES = ["none", "cumin", "pepper", "salt", "oregano", "flakes"]

SPICE_MAP = {
    "cumin": 30,
    "pepper": 60,
    "salt": 90,
    "oregano": 120,
    "flakes": 150
}

VALID_COMMANDS = set(SPICE_MAP.keys())

# Whisper settings
MODEL_NAME = "base"
COMPUTE_TYPE = "int8"
SAMPLE_RATE = 16000
DURATION = 1.0

def interpret_with_ai(user_text):
    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": (
                    "You control a spice carousel.\n"
                    "Select ONE spice based on the user's request.\n"
                    "If the user request is unrelated to spices, return nothing."
                    "Allowed spices: NONE, cumin, pepper, salt, oregano, flakes.\n"
                    "Return ONLY valid JSON.\n"
                )
            },
            {"role": "user", "content": user_text}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "spice_command",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "spice": {
                            "type": "string",
                            "enum": SPICES
                        }
                    },
                    "required": ["spice"],
                    "additionalProperties": False
                }
            }
        }
    )

    try:
        data = json.loads(response.output_text)
        return data
    except:
        print("Failed to parse AI output:", response.output_text)
        return None

def connect_serial():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)  # let Arduino reset
        print(f"Connected to {PORT} at {BAUD}")
        return ser
    except Exception as e:
        print(f"Serial connection failed: {e}")
        return None


def send_command(ser, spice):
    if ser is None:
        return

    if spice not in SPICE_MAP:
        print("Invalid spice")
        return

    message = f"SPICE {spice}\n"
    ser.write(message.encode("utf-8"))
    ser.flush()
    print("Command received", message)

    try:
        response = ser.readline().decode().strip()
        if response:
            print("Arduino:", response)
    except:
        pass

# For testing
'''
def send_command(ser, spice):
    message = f"SPICE {spice}\n"

    if ser is None:
        print("🧪 MOCK SEND:", message.strip())
        return

    ser.write(message.encode())
'''

def parse_input(text):
    text = text.strip().lower()

    if text in SPICE_MAP:
        return text

    for spice in SPICE_MAP:
        if spice in text:
            return spice

    return None


def get_voice_command(model):
    print(">>> Listening...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    audio = np.squeeze(audio)

    segments, _ = model.transcribe(audio)

    text = ""
    for segment in segments:
        text += segment.text

    text = text.strip()
    print("Heard:", text)
    if not text:
        return None

    ai_data = interpret_with_ai(text)

    if ai_data and "spice" in ai_data:
        spice = ai_data["spice"]

        if spice in SPICES:
            print(f"AI selected: {spice}")
            return spice

    print("No valid spice found")
    return None


def typed_mode(ser):
    print("Type commands like: spin, stop, fast, slow, push, pull")
    print("Type quit to exit.")

    while True:
        text = input("Enter command: ").strip()
        if text.lower() == "quit":
            break

        cmd = parse_input(text)
        if cmd:
            send_command(ser, cmd)
        else:
            print("No valid command found.")


def voice_mode(ser):
    model = WhisperModel(MODEL_NAME, compute_type=COMPUTE_TYPE)
    print("Voice mode started. Say: spin, stop, fast, slow, push, pull")
    print("Press Ctrl+C to exit.")

    while True:
        cmd = get_voice_command(model)
        if cmd:
            send_command(ser, cmd)
        else:
            print("No valid command found.")


def main():
    ser = connect_serial()
    if ser is None:
        return

    mode = input("Choose mode (type/voice): ").strip().lower()

    try:
        if mode == "voice":
            voice_mode(ser)
        else:
            typed_mode(ser)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ser.close()


if __name__ == "__main__":
    main()