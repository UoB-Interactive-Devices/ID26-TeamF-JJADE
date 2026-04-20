from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import json
import serial
import time

app = Flask(__name__)
client = OpenAI()

SPICES = ["paprika", "cumin", "pepper", "salt", "oregano", "flakes"]

PORT = "/dev/ttyACM0"
BAUD = 115200

# Open serial once when the server starts
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ Connected to Arduino")
except:
    ser = None
    print("⚠️ Running without Arduino (mock mode)")

def send_command(spice):
    if spice not in SPICES:
        raise ValueError(f"Invalid spice: {spice}")
    
    message = f"SPICE {spice}\n"

    if ser is None:
        print("🧪 MOCK SEND:", message.strip())
        return "MOCK OK"

    ser.write(message.encode("utf-8"))
    ser.flush()

    response = ser.readline().decode("utf-8", errors="ignore").strip()
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    user_text = request.json["text"]

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": (
                    "You control a spice carousel.\n"
                    "Return ONLY JSON: { \"spice\": \"...\" }\n"
                    "Allowed spices: paprika, cumin, pepper, salt, oregano, flakes."
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

    data = json.loads(response.output_text)
    spice = data["spice"]

    arduino_response = send_command(spice)

    return jsonify({
        "spice": spice,
        "arduino_response": arduino_response
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)