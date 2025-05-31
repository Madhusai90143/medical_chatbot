from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import json
import pandas as pd
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
class ChromeFilter(logging.Filter):
    def filter(self, record):
        return "/.well-known/appspecific" not in record.getMessage()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
app.logger.addFilter(ChromeFilter())

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def handle_chrome_devtools():
    return '', 204

# Improved QA pipeline initialization
try:
    qa_pipeline = pipeline(
        "question-answering", 
        model="deepset/roberta-base-squad2",
        device=0 if torch.cuda.is_available() else -1
    )
    app.logger.info("QA pipeline initialized successfully")
except Exception as e:
    app.logger.error(f"QA pipeline failed: {e}")
    qa_pipeline = None

# Enhanced MedQuAD loading with validation
def load_medquad():
    try:
        with open("medquad_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        app.logger.info(f"Loaded {len(data)} MedQuAD entries")
        return pd.DataFrame(data)
    except Exception as e:
        app.logger.error(f"MedQuAD loading failed: {e}")
        return pd.DataFrame()

medquad_df = load_medquad()

# Enhanced symptom detection
SYMPTOM_ADVICE = {
    'fever': {
        'advice': (
            "For fever: Monitor temperature regularly, stay hydrated with water and electrolytes. "
            "If temperature exceeds 39°C (102°F) or persists beyond 3 days, seek medical attention."
        ),
        'keywords': ['fever', 'temperature', 'febrile', 'hot', 'chills']
    },
    'cough': {
        'advice': (
            "For cough: Stay hydrated, avoid irritants like smoke. "
            "Consult a doctor if coughing blood or lasting over 3 weeks."
        ),
        'keywords': ['cough', 'coughing', 'hacking', 'phlegm']
    }
}

def detect_symptoms(text):
    text_lower = text.lower()
    detected = []
    words = set(text_lower.split())
    for symptom, data in SYMPTOM_ADVICE.items():
        if any(keyword in words for keyword in data['keywords']):
            detected.append(data['advice'])
            break  # Return first match only
    return detected

# Improved medical QA with context caching
MEDQUAD_CONTEXTS = []
if not medquad_df.empty:
    MEDQUAD_CONTEXTS = [
        f"{row['question']} {row['answer']}"[:512]
        for _, row in medquad_df.iterrows()
    ]

def get_medical_answer(question):
    if not qa_pipeline or not MEDQUAD_CONTEXTS:
        return ""
    
    try:
        results = qa_pipeline(
            question=question,
            context=MEDQUAD_CONTEXTS,
            top_k=3,
            max_answer_len=200
        )
        best = max(results, key=lambda x: x['score'])
        return best['answer'] if best['score'] >= 0.1 else ""
    except Exception as e:
        app.logger.error(f"QA failed: {e}")
        return ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def handle_question():
    user_input = request.form.get("question", "").strip()
    app.logger.info(f"Received question: {user_input}")
    
    if not user_input:
        return jsonify({"answer": "Please enter a medical question."})
    
    symptom_advice = detect_symptoms(user_input)
    medical_info = get_medical_answer(user_input)
    
    response = []
    if symptom_advice:
        response.append(f"<div class='symptom-alert'>{symptom_advice[0]}</div>")
    if medical_info:
        response.append(f"<div class='medical-info'>{medical_info}</div>")
    
    if not response:
        return jsonify({"answer": "Please consult a healthcare professional for personalized advice."})
    
    return jsonify({"answer": "".join(response)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)