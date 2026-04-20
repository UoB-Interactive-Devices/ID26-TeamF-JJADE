import json
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

try:
    import serial
except ImportError:
    serial = None

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")
ARDUINO_BAUD = int(os.getenv("ARDUINO_BAUD", "115200"))

SPICES = ["paprika", "cumin", "pepper", "salt", "oregano", "flakes"]

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "assistant_message": {"type": "string"},
        "cards": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "spices": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 3,
                        "items": {"type": "string", "enum": SPICES},
                    },
                },
                "required": ["title", "summary", "spices"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["assistant_message", "cards"],
    "additionalProperties": False,
}

ser = None


def connect_serial() -> Optional[Any]:
    global ser

    if serial is None:
        print("pyserial not installed; running in mock mode.")
        return None

    try:
        connection = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        time.sleep(2)
        print(f"✅ Connected to Arduino on {ARDUINO_PORT} at {ARDUINO_BAUD}")
        ser = connection
        return connection
    except Exception as e:
        print(f"⚠️ Running without Arduino (mock mode): {e}")
        ser = None
        return None


def send_command(spice: str) -> str:
    if spice not in SPICES:
        raise ValueError(f"Invalid spice: {spice}")

    message = f"SPICE {spice}\n"

    if ser is None:
        print("🧪 MOCK SEND:", message.strip())
        return "MOCK OK"

    ser.write(message.encode("utf-8"))
    ser.flush()

    try:
        response = ser.readline().decode("utf-8", errors="ignore").strip()
        return response or "OK"
    except Exception:
        return "OK"


def fallback_suggestion(user_text: str) -> Dict[str, Any]:
    lower = user_text.lower()

    if "taco" in lower:
        return {
            "assistant_message": "For tacos, I recommend a smoky, savory blend.",
            "cards": [
                {
                    "title": "Taco build",
                    "summary": "Warm, savory, and a little smoky.",
                    "spices": ["cumin", "paprika", "salt"],
                }
            ],
        }

    if "pasta" in lower:
        return {
            "assistant_message": "For pasta, try an herb-forward profile.",
            "cards": [
                {
                    "title": "Pasta boost",
                    "summary": "Herby, balanced, and bright.",
                    "spices": ["oregano", "pepper", "salt"],
                }
            ],
        }

    return {
        "assistant_message": "Here is a flexible seasoning suggestion for this dish.",
        "cards": [
            {
                "title": "Balanced blend",
                "summary": "A versatile seasoning profile for most savory dishes.",
                "spices": ["salt", "pepper"],
            }
        ],
    }


def get_ai_suggestion(user_text: str) -> Dict[str, Any]:
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are Shroom, an AI seasoning assistant for a smart spice carousel. "
                    "Interpret the user's cooking request and return a short helpful recommendation. "
                    "Only use these spices: paprika, cumin, pepper, salt, oregano, flakes. "
                    "Return only valid JSON that matches the schema."
                ),
            },
            {"role": "user", "content": user_text},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "shroom_suggestion",
                "strict": True,
                "schema": JSON_SCHEMA,
            }
        },
    )

    return json.loads(response.output_text)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/suggest", methods=["POST"])
def suggest():
    payload = request.get_json(force=True) or {}
    user_text = str(payload.get("text", "")).strip()

    if not user_text:
        return jsonify({"error": "Missing text"}), 400

    try:
        data = get_ai_suggestion(user_text)
    except Exception:
        data = fallback_suggestion(user_text)

    return jsonify(data)


@app.route("/api/dispense", methods=["POST"])
def dispense():
    payload = request.get_json(force=True) or {}
    spice = str(payload.get("spice", "")).strip().lower()

    if spice not in SPICES:
        return jsonify({"error": "Invalid spice"}), 400

    arduino_response = send_command(spice)

    return jsonify(
        {
            "spice": spice,
            "arduino_response": arduino_response,
            "status": "sent",
        }
    )


if __name__ == "__main__":
    connect_serial()
    app.run(host="0.0.0.0", port=5000, debug=True)