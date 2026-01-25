import pandas as pd
import os

# --- CONFIGURATION ---
# Change this to match your actual file name
FILE_NAME = 'data/URL Classification.csv' 

def inspect_dataset():
    if not os.path.exists(FILE_NAME):
        print(f"ERROR: Could not find '{FILE_NAME}'. Make sure the file is in this folder.")
        return

    print(f"Loading {FILE_NAME}...")
    try:
        # Read the file
        df = pd.read_csv(FILE_NAME)
        
        print("\n" + "="*40)
        print(f"COLUMNS FOUND: {list(df.columns)}")
        print("="*40)

        # Automatically look for columns that look like 'Labels'
        # (Columns with very few unique values are usually labels)
        for col in df.columns:
            unique_count = df[col].nunique()
            
            # If a column has fewer than 20 unique types, it's likely a category/label
            if unique_count < 20: 
                print(f"\nAnalyzing Column: '{col}'")
                print("-" * 30)
                print(f"Unique Values: {df[col].unique()}")
                print(f"Counts:\n{df[col].value_counts()}")
                print("-" * 30)
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    inspect_dataset()