# Phishing Detection Microservice

Real-time URL phishing detection API powered by an XGBoost classifier with HMAC-SHA256 authentication and redirect tracing.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-337AB7?style=flat-square)](https://xgboost.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

Phishing attacks deceive users with lookalike URLs to steal credentials, and standard HTTPS indicators cannot be trusted because malicious domains also use SSL certificates. This microservice extracts 12 lexical, structural, and statistical URL features to detect phishing links without downloading entire webpages. Evaluated on a 20% holdout split from 707,517 labeled URLs, the trained XGBoost classifier delivers 91.05% accuracy and 91.37% precision.

**Live Demo:** https://url-tester.netlify.app/

## Results

| Metric | Value | Dataset & Size | How Measured | Source File |
|---|---|---|---|---|
| Accuracy | 91.05% | 707,517 URLs (141,504 test samples) | Stratified 80/20 train/test split | `model_metadata.pkl`, `train_model.py` |
| Precision | 91.37% | 707,517 URLs (141,504 test samples) | Stratified 80/20 train/test split | `model_metadata.pkl`, `train_model.py` |

## How It Works

1. **Client Request:** The client sends a `POST /predict` request with a URL, HMAC-SHA256 signature (`X-INTERNAL-SECRET`), and Unix timestamp (`X-TIMESTAMP`).
2. **Security Verification:** The API rejects requests older than 60 seconds to prevent replay attacks, then verifies the signature with `hmac.compare_digest` to prevent timing attacks.
3. **Redirect Resolution:** If the URL is shortened (e.g., `bit.ly`), `requests.head` follows HTTP redirects to inspect the final landing URL without downloading page bodies.
4. **Feature Extraction:** `feature_extractor.py` converts the URL into a 12-dimensional vector (length, dot count, HTTP scheme, digits, special characters `@`, `-`, `//`, subdomain depth, directory depth, Shannon entropy, shortener flag, and sensitive keywords).
5. **Inference & Report:** The pre-trained XGBoost model predicts phishing probability, returning a structured verdict (`CRITICAL` if phishing, `MODERATE` if probability > 0.4, or `SAFE`) with actionable security advice and feature debug data.

## Features

- **12-Feature URL Analysis:** Computes structural, statistical, and lexical indicators including Shannon entropy, directory depth, and subdomain count.
- **Redirect Chain Tracing:** Automatically unfurls shortened links via HTTP HEAD requests to analyze final destinations rather than vanity domains.
- **HMAC-SHA256 Authentication:** Protects the internal endpoint using header-based signature verification and constant-time digest comparison.
- **Replay Attack Defense:** Enforces a 60-second timestamp freshness window to block repeated intercepted payloads.
- **Granular Security Reports:** Outputs classified risk tiers (`CRITICAL`, `MODERATE`, `SAFE`), enforcement actions (`Blocked`, `Warning`, `Allowed`), and feature breakdowns.

## Tech Stack

Python, Flask, XGBoost, scikit-learn, Pandas, NumPy, Joblib, Requests

## Run Locally

```bash
# Clone the repository
git clone https://github.com/MohitSingh-2335/Phishing-detection-microservice.git
cd Phishing-detection-microservice

# Install dependencies
pip install -r requirements.txt

# Start the Flask API server (runs on port 5001 by default)
python app.py
```

Test the prediction endpoint:
```bash
# Generate timestamp and HMAC signature
python -c "import hmac, hashlib, time; ts=str(time.time()); print('Timestamp:', ts); print('Signature:', hmac.new(b'default_dev_secret_DO_NOT_USE_IN_PROD', ts.encode(), hashlib.sha256).hexdigest())"

# Send test request
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-SECRET: <signature>" \
  -H "X-TIMESTAMP: <timestamp>" \
  -d '{"url": "http://secure-paypal-login.xyz/verify"}'
```

## Project Structure

All modules reside at repository root (flat layout):
- `app.py`: Flask API with HMAC-SHA256 authentication, redirect tracing, and prediction endpoints
- `feature_extractor.py`: 12-feature URL parser (Shannon entropy, subdomain count, sensitive keywords)
- `train_model.py`: Production XGBoost training script with stratified train-test split
- `hypertuning.py`: Hyperparameter tuning for Random Forest and XGBoost via `RandomizedSearchCV`
- `compare_models.py`: Model tournament script comparing Logistic Regression, Random Forest, XGBoost, and SVM
- `data_merger.py`: Merges and deduplicates multi-source URL datasets into a single master file
- `data_preprocessing.py`: Shuffles, sanitizes, and prepares final training datasets
- `model.pkl`: Serialized production XGBoost model (3.72 MB)
- `model_metadata.pkl`: Serialized model training timestamp, parameters, and evaluation metrics

## Limitations

- **Lexical Heuristics Only:** Detection operates solely on URL strings; it does not inspect webpage DOM, HTML content, or SSL certificate chains.
- **Static Pattern Matching:** Shortener detection matches 7 predefined services, and keyword scanning matches 11 predefined terms.
- **Redirect Network Dependency:** Redirect tracing relies on `requests.head` with a 3-second timeout; network failures fall back to analyzing the unexpanded URL.
- **Clock Synchronization:** Replay protection rejects requests older than 60 seconds, requiring client and server clocks to stay in sync.

## License

MIT License

---

Mohit Singh | GitHub: https://github.com/MohitSingh-2335 | LinkedIn: https://www.linkedin.com/in/mohit-singh-172548253/ | Portfolio: https://mohitsingh-2335.github.io/
