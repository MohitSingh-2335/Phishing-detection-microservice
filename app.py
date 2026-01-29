from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
import hmac
import hashlib
import time
import requests
from feature_extractor import extract_features

app = Flask(__name__)

# --- CONFIGURATION ---
# 1. FAIL-SAFE: Prevents crash if key is missing (Defaults to a dev key)
INTERNAL_SECRET_KEY = os.environ.get("MOHIT_SHARED_SECRET", "default_dev_secret_DO_NOT_USE_IN_PROD")

# --- LOAD MODEL ---
model_path = 'model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("✅ Model loaded successfully.")
else:
    print("⚠️ WARNING: model.pkl not found! Run train_model.py first.")
    model = None

# --- HELPER: Follow Shortened Links (e.g., bit.ly) ---
def check_redirects(url):
    try:
        # 'HEAD' request follows redirects without downloading the whole page (Fast)
        response = requests.head(url, allow_redirects=True, timeout=3)
        return response.url
    except:
        return url  # If it fails, just use the original

# --- HELPER: Generate User Report ---
def generate_security_report(url, is_phishing, prob):
    report = {
        "risk_level": "Unknown",
        "action_taken": "None",
        "https_status": "Secure (HTTPS)" if url.startswith("https") else "Not Secure (HTTP)",
        "advice": []
    }

    if is_phishing:
        report["risk_level"] = "CRITICAL"
        report["action_taken"] = "Blocked"
        report["advice"].append("🛑 DO NOT CLICK. This site matches known phishing patterns.")
    elif prob > 0.4:
        report["risk_level"] = "MODERATE"
        report["action_taken"] = "Warning"
        report["advice"].append("⚠️ Proceed with caution. High suspicion score.")
    else:
        report["risk_level"] = "SAFE"
        report["action_taken"] = "Allowed"
        report["advice"].append("✅ Site appears safe.")

    if not url.startswith("https"):
        report["advice"].append("🔓 Warning: Connection is not encrypted.")
        
    return report

@app.route('/')
def home():
    return "Phishing Detection Microservice is Active (Supercharged)."

@app.route('/predict', methods=['POST'])
def predict():
    # 1. SECURITY CHECK (HMAC + Timestamp)
    received_signature = request.headers.get('X-INTERNAL-SECRET')
    timestamp_str = request.headers.get('X-TIMESTAMP')

    if not timestamp_str or not received_signature:
        return jsonify({"error": "Missing Security Headers"}), 401

    # REPLAY ATTACK PREVENTION
    try:
        request_time = float(timestamp_str)
        # Reject requests older than 60 seconds
        if abs(time.time() - request_time) > 60:
            return jsonify({"error": "Request Expired (Replay Attack)"}), 401
    except ValueError:
        return jsonify({"error": "Invalid Timestamp"}), 400
    
    expected_signature = hmac.new(
        INTERNAL_SECRET_KEY.encode(),
        timestamp_str.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return jsonify({"error": "Unauthorized Access"}), 401

    # 2. INPUT PROCESSING
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    raw_url = data['url'].strip()
    
    # 3. ADVANCED ANALYSIS
    # First, trace where the link actually goes
    final_url = check_redirects(raw_url)
    
    # Extract the 12 features
    features = extract_features(final_url)
    features_array = np.array(features).reshape(1, -1)

    # 4. PREDICTION
    prediction = model.predict(features_array)[0]
    phishing_index = list(model.classes_).index(1)
    probability = model.predict_proba(features_array)[0][phishing_index]
    is_phishing = bool(prediction == 1)

    # 5. GENERATE RESPONSE
    security_report = generate_security_report(final_url, is_phishing, probability)

    return jsonify({
        "url_analyzed": final_url,
        "is_phishing": is_phishing,
        "phishing_probability": round(float(probability), 4),
        "security_report": security_report,
        # Map the list of 12 numbers to readable names for the frontend
        "features_debug": {
            "url_length": features[0],
            "dot_count": features[1],
            "is_https": features[2],
            "digit_count": features[3],
            "special_chars": features[4] + features[5], # @ and -
            "subdomains": features[7],
            "entropy": features[9],
            "suspicious_words": features[11]
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)