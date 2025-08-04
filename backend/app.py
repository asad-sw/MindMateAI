import re
import csv
import os
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# --------------------------------------------------------------------------
# --- IBM WATSONX.AI CREDENTIALS ---
# --------------------------------------------------------------------------
API_KEY = "Cn5Ft1EIYG9dN8uCYGy67Vn-htSwcvLRJCBLCLI15YEI"
PROJECT_ID = "78032f12-5c28-4fa3-ba9b-175b08e06966"
# --------------------------------------------------------------------------

# --- Watsonx.ai API Configuration ---
TOKEN_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
API_ENDPOINT = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-29"
MODEL_ID = "ibm/granite-3-8b-instruct"

# --- Global variable to hold the access token ---
iam_access_token = None

# --- Simple in-memory store for rate limiting ---
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
LOG_HEADER = ['timestamp', 'name', 'age', 'symptoms', 'recommendation', 'severity']

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

def get_watsonx_recommendation(symptoms):
    token = get_iam_token()
    if not token:
        return {"error": "Failed to authenticate with IBM Cloud."}

    # --- NEW: Final, High-Performance Prompt ---
    prompt = f"""
**Persona:** You are MindMate, an AI assistant with a warm, caring, and supportive tone. You are designed for mental health triage. Your primary goal is to make the user feel heard and validated, and to offer a gentle, non-medical suggestion.

**Strict Instructions:**
1.  **NEVER** say you are "unable to provide help" or "not a medical professional." The user knows this.
2.  **DO NOT** diagnose.
3.  Your recommendation **MUST** be a supportive statement and a general well-being suggestion (e.g., journaling, talking to a friend, practicing mindfulness, going for a walk).
4.  You **MUST** return only a single, valid JSON object. Do not include any other text or explanations.

**Task:** Analyze the user's symptoms and return a JSON object with two keys: "recommendation" and "severity".
- "recommendation": A 2-3 sentence supportive message.
- "severity": "Low", "Medium", or "High".

**Example of a good response:**
User Symptoms: "I feel sad all the time and have no energy."
JSON:
{{
  "recommendation": "It sounds incredibly difficult to be carrying such a heavy feeling. Focusing on one small, gentle activity each day, like a short walk, can sometimes help. It's brave of you to share this, and speaking with a therapist could provide you with dedicated support.",
  "severity": "High"
}}

**User Input to Analyze:**
User Symptoms: "{symptoms}"
JSON:
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
            "max_new_tokens": 300,
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
            print(f"No valid JSON found in response: {generated_text}")
            return {"error": "Received a malformed response from the AI."}

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        print(f"Response content: {response.content}")
        return {"error": "The AI service is currently unavailable."}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Failed to parse response. Raw text: '{generated_text}'. Error: {e}")
        return {"error": "Received an invalid response from the AI."}

# --------------------------------------------------------------------------
# Logging and API Routes
# --------------------------------------------------------------------------

def log_submission(name, age, symptoms, recommendation, severity):
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(LOG_FILE) == 0:
                writer.writerow(LOG_HEADER)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, name, age, symptoms, recommendation, severity])
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

    if not all([name, age, symptoms]):
        return jsonify({"error": "Missing fields: name, age, and symptoms are required."}), 400

    if len(symptoms) > MAX_SYMPTOMS_LENGTH:
        return jsonify({"error": f"Symptoms input is too long. Max characters: {MAX_SYMPTOMS_LENGTH}"}), 413

    try:
        age_int = int(age)
        ai_response = get_watsonx_recommendation(symptoms)

        if "error" in ai_response:
            return jsonify({"error": ai_response["error"]}), 500

        recommendation_text = ai_response.get("recommendation", "No recommendation provided.")
        severity_level = ai_response.get("severity", "Not Determined")
        
        full_recommendation = f"Thank you, {name}. {recommendation_text}"
        
        log_submission(name, age_int, symptoms, full_recommendation, severity_level)

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

# --------------------------------------------------------------------------
# Main Execution Block
# --------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
