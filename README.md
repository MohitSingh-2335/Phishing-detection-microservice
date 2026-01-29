# 🛡️ Phishing Detection Microservice (The URL Tester)

A high-performance, AI-powered API designed to detect phishing URLs in real-time. This microservice uses a **Supercharged XGBoost Classifier** trained on over 700,000 URLs to distinguish between safe websites and malicious phishing attempts with high precision.

## 🚀 Key Features

- **Supercharged AI Model:** Powered by an XGBoost classifier, hyper-tuned for maximum precision using `RandomizedSearchCV`.
- **Advanced Feature Extraction:** Analyzes 12 distinct URL characteristics, including Shannon Entropy (randomness), IP address masking, subdomain depth, and suspicious keywords.
- **Real-Time Security Report:** Returns not just a prediction (Safe/Unsafe), but a detailed security report including HTTPS status, redirect tracing, and actionable advice.
- **Secure API:** Protected by **HMAC-SHA256 authentication** and Timestamp Replay Attack prevention.
- **Redirect Tracing:** Automatically unfurls shortened links (e.g., `bit.ly`) to analyze the final destination.

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Machine Learning:** XGBoost, Scikit-Learn, Pandas, NumPy
- **API Framework:** Flask
- **Security:** HMAC, Hashlib
- **Utilities:** Joblib, Requests, Urllib

## 📂 Project Structure

```bash
Phishing-Detection-Microservice/
├── data/
│   └── processed_dataset.csv    # The cleaned dataset (Safe + Phishing URLs)
├── app.py                       # The Flask API Server (The Receptionist)
├── train_model.py               # Final production training script (The Builder)
├── feature_extractor.py         # The Brain (Extracts 12 features from URLs)
├── hypertuning.py               # Script to find the best model parameters
├── compare_models.py            # Tournament script (RF vs XGB vs SVM)
├── model.pkl                    # The saved XGBoost model (Generated after training)
├── model_metadata.pkl           # Metadata (Accuracy, params, version info)
└── requirements.txt             # List of dependencies
```
