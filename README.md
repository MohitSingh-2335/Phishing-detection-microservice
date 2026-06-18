<div align="center">

# 🛡️ Phishing Detection Microservice

### Real-Time URL Phishing Detection API — XGBoost · HMAC-SHA256 · Redirect Tracing

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-337AB7?style=flat-square)](https://xgboost.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

> XGBoost classifier trained on **700,000+ URLs** · 12-feature URL analysis · HMAC-SHA256 authentication · Replay attack prevention · Redirect tracing for shortened links

</div>

---

## 🔍 The Problem

Every phishing attack starts with a link. A user clicks a URL that looks legitimate — `secure-paypal-login.xyz` instead of `paypal.com` — and their credentials are stolen.

Simple checks like "does it have HTTPS?" aren't enough. Attackers buy HTTPS certificates too.

This microservice analyzes **12 structural and statistical properties** of a URL — things that are very hard to fake — and returns a real-time risk verdict in milliseconds.

---

## ⚡ How It Works

```
User sends URL → Redirect Tracing → Feature Extraction (12 features) → XGBoost Model
                                                                              │
                                                                              ▼
                                                               SAFE / MODERATE / CRITICAL
                                                               + Security Report
                                                               + Feature debug data
```

**Redirect Tracing:** If a shortened URL is submitted (e.g. `bit.ly/xyz`), the API follows the redirect chain and analyzes the **final destination** — not the shortened link. Attackers can't hide behind URL shorteners.

---

## 🧠 Feature Engineering — 12 URL Properties

| # | Feature | Why It Matters |
|---|---------|---------------|
| 1 | **URL Length** | Phishing URLs tend to be long to hide the real domain |
| 2 | **Dot Count** | Excess dots indicate subdomain abuse (e.g. `paypal.secure.evil.com`) |
| 3 | **HTTPS Status** | HTTP = unencrypted; however HTTPS alone ≠ safe |
| 4 | **IP Address in Domain** | Legitimate sites use domain names, not raw IPs |
| 5 | **Digit Count** | High digit density in domain is a phishing signal |
| 6 | **`@` Symbol Count** | `@` in a URL redirects to the real (malicious) destination |
| 7 | **Dash Count** | Dashes fake legitimate brands (e.g. `pay-pal-secure.com`) |
| 8 | **Subdomain Depth** | Deep subdomain nesting is a common obfuscation tactic |
| 9 | **Directory Depth** | Long path depth indicates redirect chains |
| 10 | **Shannon Entropy** | High entropy = random-looking domain = likely auto-generated malicious URL |
| 11 | **URL Shortener Detection** | Flags `bit.ly`, `tinyurl.com`, `goo.gl` etc. for automatic tracing |
| 12 | **Suspicious Keywords** | Detects: `login`, `secure`, `verify`, `bank`, `wallet`, `crypto`, `confirm` |

---

## 🔐 Security Layers

This is an internal microservice — not a public API. It's designed to be called by a trusted backend only.

| Layer | Implementation |
|-------|---------------|
| **Authentication** | HMAC-SHA256 signature on every request (`X-INTERNAL-SECRET` header) |
| **Replay Attack Prevention** | Timestamp validation — requests older than 60 seconds are rejected |
| **Input Validation** | URL sanitized and normalized before feature extraction |
| **Secure Compare** | `hmac.compare_digest()` used — prevents timing attacks |

---

## 📡 API

### `POST /predict`

**Headers required:**
```
X-INTERNAL-SECRET: <HMAC-SHA256 signature>
X-TIMESTAMP: <Unix timestamp>
Content-Type: application/json
```

**Request body:**
```json
{
  "url": "http://secure-paypal-login.xyz/account/verify"
}
```

**Response:**
```json
{
  "url_analyzed": "http://secure-paypal-login.xyz/account/verify",
  "is_phishing": true,
  "phishing_probability": 0.9731,
  "security_report": {
    "risk_level": "CRITICAL",
    "action_taken": "Blocked",
    "https_status": "Not Secure (HTTP)",
    "advice": [
      "🛑 DO NOT CLICK. This site matches known phishing patterns.",
      "🔓 Warning: Connection is not encrypted."
    ]
  },
  "features_debug": {
    "url_length": 51,
    "dot_count": 3,
    "is_https": 0,
    "entropy": 3.84,
    "suspicious_words": 1
  }
}
```

**Risk levels:**
- `CRITICAL` — High confidence phishing (probability > 0.5)
- `MODERATE` — Suspicious (probability 0.4–0.5)
- `SAFE` — Likely legitimate (probability < 0.4)

---

## 🤖 Model

- **Algorithm:** XGBoost Classifier (chosen after comparing Random Forest vs. XGBoost vs. SVM)
- **Training data:** 700,000+ labelled URLs (safe + phishing)
- **Hypertuning:** `RandomizedSearchCV` on XGBoost parameters
- **Serialized model:** `model.pkl` (3.7 MB) + `model_metadata.pkl` (accuracy, params, version)

> **Why XGBoost?** It outperformed both Random Forest and SVM in the comparison (`compare_models.py`) on precision, recall, and F1 score on this dataset.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| API | Flask · Python 3.11+ |
| ML Model | XGBoost · scikit-learn · Pandas · NumPy |
| Feature Engineering | urllib · re · math · collections |
| Security | hmac · hashlib · time |
| Serialization | joblib |
| Deployment | Render (Procfile) |

---

## 🚀 Run Locally

```bash
git clone https://github.com/MohitSingh-2335/Phishing-detection-microservice.git
cd Phishing-detection-microservice

pip install -r requirements.txt

# Train the model first (generates model.pkl)
python train_model.py

# Start the API
python app.py
# → Running on http://localhost:5001
```

**Test it:**
```bash
# Generate HMAC signature for timestamp
python -c "import hmac, hashlib, time; ts=str(time.time()); print(ts, hmac.new(b'default_dev_secret_DO_NOT_USE_IN_PROD', ts.encode(), hashlib.sha256).hexdigest())"

# Send a test request
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-SECRET: <signature>" \
  -H "X-TIMESTAMP: <timestamp>" \
  -d '{"url": "http://secure-paypal-login.xyz/verify"}'
```

---

## 📂 Project Structure

```
Phishing-detection-microservice/
├── app.py                  # Flask API — HMAC auth, redirect tracing, risk reports
├── feature_extractor.py    # 12-feature URL parser (Shannon entropy, IP check, etc.)
├── train_model.py          # Production training script
├── hypertuning.py          # RandomizedSearchCV hyperparameter search
├── compare_models.py       # RF vs XGBoost vs SVM model tournament
├── data_preprocessing.py   # Dataset cleaning pipeline
├── data_merger.py          # Merging safe + phishing URL datasets
├── data_inspect.py         # EDA script
├── model.pkl               # Trained XGBoost model (3.7 MB)
├── model_metadata.pkl      # Model accuracy, parameters, version info
├── Procfile                # Render deployment config
└── requirements.txt
```

---

## 📄 License

MIT License
