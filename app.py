from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
from feature_extractor import extract_features
import hmac
import hashlib
import time

app = Flask(__name__)

# --- CONFIGURATION ---
INTERNAL_SECRET_KEY = os.environ.get("MOHIT_SHARED_SECRET")

# --- LOAD MODEL ---
model_path = 'model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Model loaded successfully.")
else:
    print("WARNING: model.pkl not found! Run train_model.py first.")
    model = None

@app.route('/')
def home():
    return "Phishing Detection Microservice is Active."

@app.route('/predict', methods=['POST'])
def predict():
    # 1. SECURITY CHECK
    received_signature = request.headers.get('X-INTERNAL-SECRET')
    timestamp = request.headers.get('X-TIMESTAMP')

    if not timestamp or not received_signature:
        return jsonify({"error" : "Missing Security Headers"}), 401
    
    expected_signature = hmac.new(
        INTERNAL_SECRET_KEY.encode(),
        timestamp.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return jsonify({"error" : "Unauthorized Access"}), 401

    # if auth_header != INTERNAL_SECRET_KEY:
    #    return jsonify({"error": "Unauthorized Access"}), 401

    # 2. INPUT VALIDATION
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    url = data['url']

    # 3. FEATURE EXTRACTION
    features = extract_features(url)
    features_array = np.array(features).reshape(1, -1)

    # 4. PREDICTION
    prediction = model.predict(features_array)[0]
    phishing_index = list(model.classes_).index(1)
    probability = model.predict_proba(features_array)[0][phishing_index]

    result = "Unsafe" if prediction == 1 else "Safe"

    return jsonify({
        "url": url,
        "result": result,
        "phishing_probability": round(float(probability), 4),
        "features_used": features
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
