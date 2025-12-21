import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from feature_extractor import extract_features
from sklearn.metrics import classification_report

def train_model():
    print("1. Loading dataset...")

    # Load your real dataset
    import os
    DATA_PATH = os.path.join("data", "data.csv")
    df = pd.read_csv(DATA_PATH)  # make sure path is correct

    # Encode labels
    df["label"] = df["label"].map({
        "good": 0,   # Safe
        "bad": 1     # Phishing / Unsafe
    })

    df.dropna(inplace=True)

    print("2. Extracting features...")
    X = np.array(df["url"].apply(extract_features).tolist())
    y = df["label"].values

    print("3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("4. Training Random Forest model...")
    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
    clf.fit(X_train, y_train)

    print("5. Evaluating model...")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    print("6. Saving model...")
    joblib.dump(clf, "model.pkl")

    print("✅ SUCCESS: model.pkl saved")

if __name__ == "__main__":
    train_model()
