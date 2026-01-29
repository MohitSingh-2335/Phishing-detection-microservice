import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from feature_extractor import extract_features
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report

def train_model():
    print("1. Loading dataset...")

    # Loading real dataset
    DATA_PATH = os.path.join("data", "processed_dataset.csv")
    if not os.path.exists(DATA_PATH):
        print("Processed_dataset.csv not found.")
        return
    df = pd.read_csv(DATA_PATH)
    df['label'] = df['label'].astype(int)

    df.dropna(inplace=True)

    print(f"2. Extracting features from {len(df)}...")
    X = np.array(df["url"].apply(extract_features).tolist())
    y = df["label"].values

    print(f"Feature Matrix Shape: {X.shape}")

    print("3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("4. Training XGBoost model...")
    clf = XGBClassifier(
        subsample=1.0,
        scale_pos_weight=1,
        min_child_weight=5,
        max_depth=10,
        learning_rate=0.2,
        gamma=0,
        colsample_bytree=1.0,
        n_estimators=300,       
        eval_metric='logloss',
        use_label_encoder=False,
        n_jobs=-1                
    )
    clf.fit(X_train, y_train)

    print("5. Evaluating model...")
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    
    print("\n" + "="*40)
    print(f"FINAL RESULTS (Full Dataset)")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print("="*40)

    print("6. Saving model...")
    model_filename = "model.pkl"
    joblib.dump(clf, model_filename)
    print("SUCCESS: model.pkl saved")

    metadata = {
        "algorithm": "XGBoost",
        "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accuracy": acc,
        "precision": prec,
        "params": clf.get_params()
    }
    joblib.dump(metadata, "model_metadata.pkl")
    print("Metadata saved to model_metadata.pkl")

if __name__ == "__main__":
    train_model()
