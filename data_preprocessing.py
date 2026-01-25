import pandas as pd
import numpy as np
import os

# --- CONFIGURATION ---
INPUT_FILE = 'data/master_dataset.csv'
OUTPUT_FILE = 'data/processed_dataset.csv'

def preprocess_data():
    print("Loading master dataset...")
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run the merger script first.")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Original shape: {df.shape}")

    # 1. Shuffle the Data
    # We use sample(frac=1) to shuffle 100% of the rows randomly.
    # This prevents the model from learning "all safe URLs are at the top".
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 2. Final Null Check
    # Ensure no empty strings in URL column
    df = df.dropna(subset=['url'])
    df = df[df['url'].str.strip() != ""]

    # 3. Ensure Labels are Integers (0 or 1)
    # Since the merger script already handled 'good'/'bad', we just ensure type safety.
    df['label'] = df['label'].astype(int)

    # 4. Save to a new file
    df.to_csv(OUTPUT_FILE, index=False)
    
    print("="*30)
    print("PREPROCESSING COMPLETE")
    print(f"Final shape: {df.shape}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("="*30)
    
    # 5. Sanity Check
    print("First 5 rows:")
    print(df.head())

if __name__ == "__main__":
    preprocess_data()