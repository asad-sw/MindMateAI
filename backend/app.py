
import os
import re
import csv
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
API_ENDPOINT = os.getenv("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-29"
TOKEN_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
MODEL_ID = "ibm/granite-3-8b-instruct"

# Debug prints for environment variables (after assignment)
print("[DEBUG] API_KEY:", API_KEY)
print("[DEBUG] PROJECT_ID:", PROJECT_ID)
print("[DEBUG] API_ENDPOINT:", API_ENDPOINT)

# Debug prints for environment variables (after assignment)
print("[DEBUG] API_KEY:", API_KEY)
print("[DEBUG] PROJECT_ID:", PROJECT_ID)
print("[DEBUG] API_ENDPOINT:", API_ENDPOINT)

import re
import csv
import os
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# --- IBM WATSONX.AI CREDENTIALS (Loaded from .env) ---
# --------------------------------------------------------------------------
API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
API_ENDPOINT = os.getenv("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-29"
TOKEN_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
MODEL_ID = "ibm/granite-3-8b-instruct"

# Debug prints for environment variables
print("[DEBUG] API_KEY:", API_KEY)
print("[DEBUG] PROJECT_ID:", PROJECT_ID)
print("[DEBUG] API_ENDPOINT:", API_ENDPOINT)

# --- Globals ---
iam_access_token = None
request_timestamps = {}
RATE_LIMIT_SECONDS = 5
MAX_SYMPTOMS_LENGTH = 2000

# --------------------------------------------------------------------------
# Flask Application Initialization
# --------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# --- Configuration for CSV Logging ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'triage_log.csv')
LOG_HEADER = ['timestamp', 'name', 'age', 'language', 'symptoms', 'recommendation', 'severity']

# --------------------------------------------------------------------------
# --- IBM WATSONX.AI AUTHENTICATION & API CALL ---
# --------------------------------------------------------------------------

def get_iam_token():
    global iam_access_token
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
    try:
        response = requests.post(TOKEN_ENDPOINT, headers=headers, data=data)
        response.raise_for_status()
        iam_access_token = response.json()["access_token"]
        return iam_access_token
    except requests.exceptions.RequestException as e:
        print(f"Error getting IAM token: {e}")
        return None

def get_watsonx_recommendation(symptoms, language="English"):
    """
    Calls watsonx.ai with the final, high-performance prompt.
    """
    token = get_iam_token()
    if not token:
        return {"error": "Failed to authenticate with IBM Cloud."}

    # --- AGENTIC AI PROMPT WITH MULTI-SEVERITY EXAMPLES ---
    prompt = f"""
You are a mental health triage assistant. For each set of symptoms, respond with:
- An empathetic, actionable recommendation in {language}.
- A severity assessment: Low, Medium, or High.

Examples:
Symptoms: "I'm a bit stressed at work."
Response: {{"recommendation": "It's normal to feel stressed sometimes. Try some relaxation techniques like deep breathing or a short walk. If stress continues, consider talking to someone you trust.", "severity": "Low"}}

Symptoms: "I can't sleep and feel anxious every day."
Response: {{"recommendation": "It sounds like you're struggling. Consider reaching out to a counselor or mental health professional. Try to maintain a regular sleep schedule and practice relaxation techniques.", "severity": "Medium"}}

Symptoms: "I want to end my life."
Response: {{"recommendation": "I'm really sorry you're feeling this way. Please talk to a mental health professional or someone you trust immediately. You are not alone, and help is available.", "severity": "High"}}

Now, analyze the following symptoms and respond in the same format, in {language}:
Symptoms: "{symptoms}"
"""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "model_id": MODEL_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 350,
            "min_new_tokens": 50
        },
        "project_id": PROJECT_ID
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        generated_text = response.json()['results'][0]['generated_text']

        match = re.search(r'\{[\s\S]*?\}', generated_text)
        if match:
            ai_response = json.loads(match.group())
            return ai_response
        else:
            return {"error": "Received a malformed response from the AI."}

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return {"error": "The AI service is currently unavailable."}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Failed to parse response. Raw text: '{generated_text}'. Error: {e}")
        return {"error": "Received an invalid response from the AI."}

# --------------------------------------------------------------------------
# Logging and API Routes
# --------------------------------------------------------------------------

def log_submission(name, age, language, symptoms, recommendation, severity):
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(LOG_FILE) == 0:
                writer.writerow(LOG_HEADER)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, name, age, language, symptoms, recommendation, severity])
    except IOError as e:
        print(f"Error writing to log file: {e}")

@app.route('/')
def index():
    return "✅ MindMate AI backend is now LIVE with watsonx.ai!"

@app.route('/analyze', methods=['POST'])
def analyze_symptoms():
    user_ip = request.remote_addr
    current_time = time.time()

    if user_ip in request_timestamps:
        if current_time - request_timestamps[user_ip] < RATE_LIMIT_SECONDS:
            return jsonify({"error": "Please wait before submitting again."}), 429

    request_timestamps[user_ip] = current_time

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    symptoms = data.get('symptoms')
    language = data.get('language', 'English')

    if not all([name, age, symptoms]):
        return jsonify({"error": "Missing fields."}), 400

    if len(symptoms) > MAX_SYMPTOMS_LENGTH:
        return jsonify({"error": f"Symptoms input too long."}), 413

    try:
        age_int = int(age)
        print(f"Processing request in language: {language}") # Debug log
        print(f"Symptoms: {symptoms[:50]}...") # Debug log
        
        ai_response = get_watsonx_recommendation(symptoms, language)
        print(f"AI Response: {ai_response}") # Debug log

        if "error" in ai_response:
            return jsonify({"error": ai_response["error"]}), 500

        recommendation_text = ai_response.get("recommendation", "No recommendation provided.")
        severity_level = ai_response.get("severity", "Not Determined")
        
        # Multilingual greetings
        greetings = {
            "English": f"Thank you, {name}.",
            "Spanish": f"Gracias, {name}.",
            "French": f"Merci, {name}.",
            "German": f"Danke, {name}.",
            "Portuguese": f"Obrigado, {name}.",
            "Italian": f"Grazie, {name}.",
            "Chinese": f"谢谢你，{name}。",
            "Japanese": f"ありがとう、{name}さん。",
            "Arabic": f"شكراً لك، {name}.",
            "Hindi": f"धन्यवाद, {name}।"
        }
        
        greeting = greetings.get(language, f"Thank you, {name}.")
        full_recommendation = f"{greeting} {recommendation_text}"
        
        log_submission(name, age_int, language, symptoms, full_recommendation, severity_level)

        response = {
            "status": "success",
            "message": full_recommendation,
            "severity": severity_level
        }
        return jsonify(response), 200

    except ValueError:
        return jsonify({"error": "Age must be a valid number."}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        return jsonify([])

    logs = []
    try:
        with open(LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return jsonify([])
            
            for row in reader:
                logs.append(row)
        
        return jsonify(list(reversed(logs)))
    except Exception as e:
        print(f"Error reading or processing log file: {e}")
        return jsonify({"error": "Could not process log file."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
