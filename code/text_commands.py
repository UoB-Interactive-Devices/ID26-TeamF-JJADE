# same as whisper listen but uses typed commmand line instead
# pip install pyserial NOT just serial
import serial
import time

# in order:
# makes big servo spin
# makes big servo stop
# makes big servo (very) fast
# makes big servo slow/standard
# makes small servo go to 180
# makes big servo go to 0
commands = ["spin", "stop", "fast", "slow", "push", "pull"]

# source changes across devices
# linux is /dev/ttyACM0
# windows is COM- whatever number shows in the IDE
ser = serial.Serial("/dev/ttyACM0")

def send_command(cmd):
    ser.write(cmd.encode())
    time.sleep(1)

while True:
    # record audio
    text = input("Enter command: ")

    text = text.strip()

    for command in commands:
        if command in text.lower():
            send_command(f"{command}\n")
