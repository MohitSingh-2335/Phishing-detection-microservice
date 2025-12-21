import pandas as pd
import numpy as np
import os

DATA_PATH = os.path.join("data", "data.csv")
df = pd.read_csv(DATA_PATH)

# Encode labels
df["label"] = df["label"].map({"good": 0, "bad": 1})

# Apply feature extraction
X = np.array(df["url"].apply(extract_features).tolist())
y = df["label"].values

print("Feature matrix shape:", X.shape)
