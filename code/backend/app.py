import json
import os
import threading
import time
from queue import Empty, Queue
from typing import Any, Dict, Optional

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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")
ARDUINO_BAUD = int(os.getenv("ARDUINO_BAUD", "115200"))
STEP_DELAY_SECONDS = float(os.getenv("STEP_DELAY_SECONDS", "1.0"))

SPICES = ["paprika", "cumin", "pepper", "salt", "oregano", "flakes"]

RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "assistant_message": {"type": "string"},
        "recipe": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "servings": {"type": "integer", "minimum": 1},
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "spice": {"type": "string", "enum": SPICES},
                            "description": {"type": "string"}
                        },
                        "required": ["spice", "description"],
                        "additionalProperties": False,
                    },
                },
                "notes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["title", "summary", "servings", "steps", "notes"],
            "additionalProperties": False,
        },
    },
    "required": ["assistant_message", "recipe"],
    "additionalProperties": False,
}

ser = None
serial_lock = threading.Lock()
job_queue: Queue = Queue()
cancel_event = threading.Event()
worker_started = False
worker_lock = threading.Lock()

current_recipe: Optional[Dict[str, Any]] = None
active_job: Dict[str, Any] = {
    "state": "idle",
    "kind": None,
    "label": None,
    "current_spice": None,
}

def enrich_steps(recipe):
    default_descriptions = {
        "cumin": "Builds a warm, earthy base",
        "paprika": "Adds smoky depth and color",
        "salt": "Balances and enhances flavors",
        "pepper": "Adds gentle heat and complexity",
        "oregano": "Brings a fresh, herby note",
        "flakes": "Adds a kick of heat",
    }

    for step in recipe.get("steps", []):
        if "description" not in step:
            step["description"] = default_descriptions.get(step["spice"], "Enhances flavor")

    return recipe

def connect_serial() -> None:
    global ser

    if serial is None:
        print("pyserial not installed; running in mock mode.")
        ser = None
        return

    try:
        ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        time.sleep(2)
        print(f"✅ Connected to Arduino on {ARDUINO_PORT} at {ARDUINO_BAUD}")
    except Exception as e:
        ser = None
        print(f"⚠️ Running without Arduino (mock mode): {e}")


def send_command(spice: str) -> str:
    if spice not in SPICES:
        raise ValueError(f"Invalid spice: {spice}")

    message = f"SPICE {spice}\n"

    if ser is None:
        print("🧪 MOCK SEND:", message.strip())
        return "MOCK OK"

    with serial_lock:
        ser.write(message.encode("utf-8"))
        ser.flush()
        response = ser.readline().decode("utf-8", errors="ignore").strip()

    return response or "OK"


def drain_queue() -> None:
    try:
        while True:
            job_queue.get_nowait()
            job_queue.task_done()
    except Empty:
        pass


def start_worker() -> None:
    global worker_started

    with worker_lock:
        if worker_started:
            return

        thread = threading.Thread(target=worker_loop, daemon=True)
        thread.start()
        worker_started = True


def worker_loop() -> None:
    global active_job

    while True:
        job = job_queue.get()
        try:
            cancel_event.clear()

            if job["kind"] == "spice":
                spice = job["spice"]
                active_job.update(
                    {
                        "state": "running",
                        "kind": "spice",
                        "label": spice,
                        "current_spice": spice,
                    }
                )
                send_command(spice)
                time.sleep(STEP_DELAY_SECONDS)
                active_job["state"] = "done"

            elif job["kind"] == "recipe":
                recipe = job["recipe"]
                active_job.update(
                    {
                        "state": "running",
                        "kind": "recipe",
                        "label": recipe.get("title", "Recipe"),
                        "current_spice": None,
                    }
                )

                for step in recipe.get("steps", []):
                    if cancel_event.is_set():
                        active_job["state"] = "canceled"
                        break

                    spice = step["spice"]
                    active_job["current_spice"] = spice
                    send_command(spice)
                    time.sleep(STEP_DELAY_SECONDS)

                if active_job["state"] != "canceled":
                    active_job["state"] = "done"

            else:
                active_job["state"] = "error"

        except Exception as e:
            active_job["state"] = "error"
            active_job["label"] = str(e)
        finally:
            active_job["kind"] = None
            active_job["current_spice"] = None
            job_queue.task_done()
            cancel_event.clear()


def enqueue_job(job: Dict[str, Any]) -> None:
    cancel_event.clear()
    job_queue.put(job)


def fallback_recipe(user_text: str, previous_recipe: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    lower = user_text.lower()

    if "taco" in lower:
        return {
            "assistant_message": "Let’s build a smoky, street-style taco seasoning with a warm cumin base and paprika for depth.",
            "recipe": {
                "title": "Taco seasoning plan",
                "summary": "Smoky, savory, and easy to adjust.",
                "servings": 4,
                "steps": [
                    {"spice": "cumin", "description": "Builds a warm, earthy base"},
                    {"spice": "paprika", "description": "Adds smoky depth and color"},
                    {"spice": "salt", "description": "Balances and enhances the flavors"},
                ],
                "notes": [
                    "Great with ground beef or grilled vegetables",
                    "Add lime juice after cooking for brightness",
                    "Adjust paprika for more or less heat",
                ],
            },
        }

    if "pasta" in lower:
        return {
            "assistant_message": "Let’s finish your pasta with a light, herby seasoning that enhances the sauce without overpowering it.",
            "recipe": {
                "title": "Pasta finish plan",
                "summary": "Herby and balanced.",
                "servings": 4,
                "steps": [
                    {"spice": "oregano", "description": "Adds a fresh, herby aroma"},
                    {"spice": "pepper", "description": "Brings subtle heat and complexity"},
                    {"spice": "salt", "description": "Enhances and balances the sauce"},
                ],
                "notes": [
                    "Works best with tomato-based sauces",
                    "Go light on salt if your sauce is already seasoned",
                ],
            },
        }

    base = previous_recipe or {
        "title": "Balanced seasoning plan",
        "summary": "A flexible savory blend.",
        "servings": 4,
        "steps": [
            {"spice": "salt", "description": "Establishes the base seasoning"},
            {"spice": "pepper", "description": "Adds gentle heat and depth"},
        ],
        "notes": ["Adjust freely if the user wants a different direction."],
    }

    return {
        "assistant_message": "I updated the recipe card with a flexible seasoning plan.",
        "recipe": base,
    }


def generate_recipe(user_text: str, previous_recipe: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    system_prompt = """
    You are Shroom, an AI cooking assistant for a smart spice carousel.

    Your job is to turn the user's request into a recipe plan that feels specific, vivid, and culinary—not generic.

    Core goals for assistant_message:
    - Sound like a chef guiding a cook
    - Make the food feel concrete and appetizing
    - Use the dish, ingredients, and cooking context to shape the tone
    - Avoid repetitive phrasing across requests
    - Avoid generic template language

    Hard rules:
    - Do NOT say "I drafted"
    - Do NOT say "I updated"
    - Do NOT say "recipe card"
    - Do NOT say "flexible seasoning plan"
    - Do NOT say "balanced seasoning plan"
    - Do NOT reuse the same opener style every time
    - Do NOT sound like a chatbot or support agent

    Writing requirements for assistant_message:
    - 1 to 2 sentences only
    - 18 to 35 words total
    - Include at least one sensory detail
    - Include at least one specific flavor or spice reference when appropriate
    - Make the phrasing feel tailored to the exact dish
    - Each response should feel distinct from the last one
    - Do not start multiple responses with the same sentence structure.

    Style guidance:
    - Choose a culinary angle that fits the request: smoky, bright, earthy, rich, fresh, savory, bold, clean, cozy, or sharp
    - Let the angle come from the food itself, not from a fixed phrase
    - If the user is revising a prior recipe, improve the tone and specificity rather than resetting to something generic
    - The message should feel like an invitation to cook, not a status update

    Recipe rules:
    - Use only these spices: paprika, cumin, pepper, salt, oregano, flakes
    - Keep steps to 3–5
    - Each step must include:
    - spice
    - description of the flavor role

    Notes rules:
    - Notes must be practical cooking tips for the user
    - Notes should help the cook adjust the flavor, pairing, or finishing touch
    - Do NOT include system instructions like "dispense in order"

    Return ONLY valid JSON matching the schema.
    """

    user_payload = {
        "request": user_text,
        "previous_recipe": previous_recipe,
        "instructions": {
            "assistant_message": "Write a distinct, dish-specific, chef-like opening with a clear flavor angle.",
            "avoid_repetition": True
        }
    }

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "recipe_card",
                "strict": True,
                "schema": RECIPE_SCHEMA,
            }
        },
    )

    return json.loads(response.output_text)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(
        {
            "active_job": active_job,
            "current_recipe": current_recipe,
            "queue_size": job_queue.qsize(),
        }
    )


@app.route("/api/recipe", methods=["POST"])
def recipe():
    global current_recipe

    payload = request.get_json(force=True) or {}
    user_text = str(payload.get("text", "")).strip()
    previous_recipe = payload.get("current_recipe")

    print("RECIPE REQUEST:", user_text)
    print("PREVIOUS RECIPE:", previous_recipe)

    if not user_text:
        return jsonify({"error": "Missing text"}), 400

    try:
        data = generate_recipe(user_text, previous_recipe)
        print("RECIPE RESPONSE:", data)
    except Exception as e:
        print("RECIPE ERROR:", repr(e))
        data = fallback_recipe(user_text, previous_recipe)

    recipe_obj = data.get("recipe")
    recipe_obj = enrich_steps(recipe_obj)
    data["recipe"] = recipe_obj

    current_recipe = recipe_obj
    return jsonify(data)


@app.route("/api/recipe/dispense", methods=["POST"])
def dispense_recipe():
    global current_recipe

    payload = request.get_json(force=True) or {}
    recipe_obj = payload.get("recipe") or current_recipe

    if not recipe_obj:
        return jsonify({"error": "Missing recipe"}), 400

    steps = recipe_obj.get("steps") or []
    if not steps:
        return jsonify({"error": "Recipe has no steps"}), 400

    for step in steps:
        spice = str(step.get("spice", "")).strip().lower()
        if spice not in SPICES:
            return jsonify({"error": f"Invalid spice in recipe: {spice}"}), 400

    current_recipe = recipe_obj
    enqueue_job({"kind": "recipe", "recipe": recipe_obj})

    return jsonify(
        {
            "status": "queued",
            "steps": len(steps),
            "recipe": recipe_obj,
        }
    )


@app.route("/api/recipe/cancel", methods=["POST"])
def cancel_recipe():
    cancel_event.set()
    drain_queue()
    active_job["state"] = "canceled"
    return jsonify({"status": "canceled"})


@app.route("/api/dispense", methods=["POST"])
def dispense():
    payload = request.get_json(force=True) or {}
    spice = str(payload.get("spice", "")).strip().lower()

    if spice not in SPICES:
        return jsonify({"error": "Invalid spice"}), 400

    enqueue_job({"kind": "spice", "spice": spice})

    return jsonify(
        {
            "spice": spice,
            "status": "queued",
        }
    )


if __name__ == "__main__":
    connect_serial()
    start_worker()
    app.run(host="0.0.0.0", port=5000, debug=True)