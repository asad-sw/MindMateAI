import csv
import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

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
# Backend Logic
# --------------------------------------------------------------------------

def get_ai_recommendation_mock(symptoms):
    """
    MOCK FUNCTION: Simulates a call to a powerful AI model like watsonx.ai.
    """
    symptoms_lower = symptoms.lower()
    
    anxiety_keywords = ['anxious', 'stress', 'worried', 'overwhelmed', 'panic']
    depression_keywords = ['sad', 'depressed', 'down', 'empty', 'hopeless', 'no motivation']
    sleep_keywords = ['sleep', 'tired', 'exhausted', 'insomnia', 'can\'t sleep']
    
    is_anxiety = any(keyword in symptoms_lower for keyword in anxiety_keywords)
    is_depression = any(keyword in symptoms_lower for keyword in depression_keywords)
    is_sleep = any(keyword in symptoms_lower for keyword in sleep_keywords)

    recommendation = ""
    severity = "Low"  # Default severity

    if is_anxiety and is_depression:
        recommendation = "It sounds like you're dealing with a mix of anxiety and low mood, which is very challenging. These feelings often go hand-in-hand. Focusing on small, manageable steps can be helpful. For example, a short walk each day can impact both. It's highly recommended to discuss these overlapping symptoms with a therapist who can provide targeted strategies."
        severity = "High"
    elif is_anxiety:
        recommendation = random.choice([
            "Feeling anxious and overwhelmed is incredibly tough. It might be helpful to try a grounding technique, like the 5-4-3-2-1 method, to bring yourself back to the present moment. Speaking with a mental health professional could help you find long-term coping strategies.",
            "It sounds like stress is having a significant impact right now. Prioritizing a moment of calm, even just for a few minutes of deep breathing, can make a difference. A therapist can help you unpack these feelings and build resilience."
        ])
        severity = "Medium"
    elif is_depression:
        recommendation = random.choice([
            "It takes a lot of strength to talk about feeling sad and hopeless. Please know that you're not alone in this. Sometimes, the first step is the hardest. Reaching out to a trusted friend or family member, or a professional, can provide a crucial support line.",
            "Feeling down and unmotivated can be draining. It might be helpful to focus on one small, achievable task today, no matter how minor it seems. Building momentum starts with a single step. We strongly encourage you to connect with a professional who can support you."
        ])
        severity = "Medium"
    elif is_sleep:
        recommendation = "Disrupted sleep can affect every part of your life. Creating a 'wind-down' routine before bed, like reading a book or listening to calm music instead of looking at screens, can signal to your brain that it's time to rest. If this persists, a doctor or sleep specialist can help rule out underlying issues."
        severity = "Low"
    else:
        recommendation = "Thank you for sharing that. It's clear you're going through a difficult time, and it takes courage to articulate it. Based on what you've described, the most helpful step would be to speak with a mental health professional. They are trained to listen and can provide you with personalized guidance and support for what you're experiencing."
        severity = "Not Determined"

    return {"recommendation": recommendation, "severity": severity}

def log_submission(name, age, symptoms, recommendation, severity):
    """
    Appends a new submission to the local CSV log file, now including severity.
    """
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(LOG_HEADER)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, name, age, symptoms, recommendation, severity])
    except IOError as e:
        print(f"Error writing to log file: {e}")

# --------------------------------------------------------------------------
# API Routes
# --------------------------------------------------------------------------

@app.route('/')
def index():
    return "✅ MindMate AI backend is running."

@app.route('/analyze', methods=['POST'])
def analyze_symptoms():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    symptoms = data.get('symptoms')

    if not all([name, age, symptoms]):
        return jsonify({"error": "Missing data: 'name', 'age', and 'symptoms' are required."}), 400

    try:
        age_int = int(age)
        
        ai_response = get_ai_recommendation_mock(symptoms)
        recommendation_text = ai_response["recommendation"]
        severity_level = ai_response["severity"]

        full_recommendation = f"Thank you, {name}. {recommendation_text}"
        
        log_submission(name, age_int, symptoms, full_recommendation, severity_level)

        # --- CHANGE: The API response now includes the severity level ---
        response = {
            "status": "success",
            "message": full_recommendation,
            "severity": severity_level 
        }
        return jsonify(response), 200
    except ValueError:
        return jsonify({"error": "Invalid age format. Age must be an integer."}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# --------------------------------------------------------------------------
# Main Execution Block
# --------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
