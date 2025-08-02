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
        return jsonify({"message": "All fields are required.", "status": "error"}), 400

    keywords = ['sad', 'tired', 'hopeless', 'anxious', 'anxiety', 'stressed']
    if any(word in symptoms.lower() for word in keywords):
        message = f"{name}, it may be helpful to speak with a mental health professional soon."
    else:
        message = f"{name}, your response seems okay. Still, prioritizing your well-being is important."

    return jsonify({"message": message, "status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
