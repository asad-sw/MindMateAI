from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "✅ MindMate AI backend is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    name = data.get('name', '').strip()
    age = data.get('age', '').strip()
    symptoms = data.get('symptoms', '').strip()

    if not name or not age or not symptoms:
        return jsonify({"status": "error", "message": "Please fill in all fields."}), 400

    keywords = ['anxious', 'anxiety', 'tired', 'hopeless', 'stressed']
    if any(word in symptoms.lower() for word in keywords):
        recommendation = f"{name}, it may be helpful to speak with a mental health professional soon."
    else:
        recommendation = f"{name}, your response seems okay, but always prioritize mental wellness."

    return jsonify({"status": "success", "message": recommendation})

if __name__ == '__main__':
    app.run(debug=True)
