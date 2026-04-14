import time
import serial
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

PORT = "/dev/ttyACM0"
BAUD = 115200

VALID_COMMANDS = {"spin", "stop", "fast", "slow", "push", "pull"}

# Whisper settings
MODEL_NAME = "base"
COMPUTE_TYPE = "int8"
SAMPLE_RATE = 16000
DURATION = 1.0


def connect_serial():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)  # let Arduino reset
        print(f"Connected to {PORT} at {BAUD}")
        return ser
    except Exception as e:
        print(f"Serial connection failed: {e}")
        return None


def send_command(ser, cmd):
    if ser is None:
        print("No serial connection.")
        return

    cmd = cmd.strip().lower()
    if cmd not in VALID_COMMANDS:
        print(f"Invalid command: {cmd}")
        return

    message = f"CMD {cmd}\n"
    ser.write(message.encode("utf-8"))
    ser.flush()

    try:
        response = ser.readline().decode("utf-8", errors="ignore").strip()
        if response:
            print("Arduino:", response)
    except Exception as e:
        print(f"Read error: {e}")


def parse_input(text):
    text = text.strip().lower()

    if text in VALID_COMMANDS:
        return text

    for cmd in VALID_COMMANDS:
        if cmd in text:
            return cmd

    return None


def get_voice_command(model):
    print(">>> Listening... ")
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
    print("Whisper thinks you said:", text)

    return parse_input(text)


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