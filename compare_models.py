import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Import your custom feature extractor
from feature_extractor import extract_features

def run_tournament():
    print("🏆 STARTING MODEL TOURNAMENT...")
    
    # 1. Load Data
    DATA_PATH = os.path.join("data", "processed_dataset.csv")
    if not os.path.exists(DATA_PATH):
        print("❌ Error: Processed dataset not found.")
        return

    df = pd.read_csv(DATA_PATH)
    df['label'] = df['label'].astype(int)
    
    # 2. Extract Features
    print(f"   Extracting features from {len(df)} URLs...")
    X = np.array(df["url"].apply(extract_features).tolist())
    y = df["label"].values
    
    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 4. Define the Contenders
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=100, n_jobs=-1),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', n_jobs=-1),
        "SVM": SVC()
    }
    
    results = []

    # 5. Fight!
    for name, model in models.items():
        print(f"\nTraining {name}...")
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred)
            
            results.append({
                "Model": name,
                "Accuracy": acc,
                "Precision": prec
            })
            print(f"   ✅ Accuracy: {acc:.4f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # 6. Show Leaderboard
    results_df = pd.DataFrame(results).sort_values(by="Accuracy", ascending=False)
    print("\n" + "="*40)
    print("🎖️ TOURNAMENT LEADERBOARD 🎖️")
    print("="*40)
    print(results_df)

if __name__ == "__main__":
    run_tournament()