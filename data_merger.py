import pandas as pd
import glob
import os

# --- CONFIGURATION ---
CSV_FILES = [
    'data/data.csv', 
    'data/malicious_phish.csv', 
    'data/phishing_site_urls.csv',
    'data/URL Classification.csv'
]
OUTPUT_FILE = 'data/master_dataset.csv'

def normalize_label(value):
    """
    Robustly converts labels to binary:
    1 (Unsafe): 'bad', 'phishing', 'malicious', 'malware', 'spam', 'defacement', 1
    0 (Safe): 'good', 'benign', 'safe', 0
    """
    # Convert to string, lower case, and strip whitespace
    s = str(value).lower().strip()
    
    # List of unsafe keywords
    unsafe_keywords = ['bad', 'phishing', 'malicious', 'malware', 'defacement', 'spam', '1', '1.0']
    
    # Check if the value matches any keyword
    if s in unsafe_keywords:
        return 1
    return 0

def merge_datasets():
    all_data = []

    # Create data directory if it doesn't exist to avoid errors
    if not os.path.exists('data'):
        os.makedirs('data')

    for file in CSV_FILES:
        if not os.path.exists(file):
            print(f"⚠️  Skipping {file} (File not found)")
            continue
            
        print(f"Processing {file}...")
        try:
            # low_memory=False helps with mixed types in large files
            # on_bad_lines='skip' prevents crashing on corrupt rows
            df = pd.read_csv(file, low_memory=False, on_bad_lines='skip')
            
            # 1. Intelligent Column Detection
            # Normalize column names to lowercase for searching
            cols_lower = [c.lower() for c in df.columns]
            
            # Find URL column
            url_col = None
            possible_url_names = ['url', 'address', 'website', 'domain']
            for name in possible_url_names:
                if name in cols_lower:
                    url_col = df.columns[cols_lower.index(name)]
                    break
            
            if not url_col:
                print(f"  -> ❌ Could not find URL column in {file}. Skipping.")
                continue

            # Find Label column
            label_col = None
            possible_label_names = ['label', 'type', 'class', 'status', 'phishing']
            for name in possible_label_names:
                if name in cols_lower:
                    label_col = df.columns[cols_lower.index(name)]
                    break
            
            if not label_col:
                print(f"  -> ❌ Could not find Label column in {file}. Skipping.")
                continue
            
            # 2. Extract and Normalize
            temp_df = pd.DataFrame()
            temp_df['url'] = df[url_col]
            temp_df['label'] = df[label_col].apply(normalize_label)
            
            # Remove any rows where URL is missing/empty
            temp_df.dropna(subset=['url'], inplace=True)
            
            all_data.append(temp_df)
            print(f"  -> ✅ Added {len(temp_df)} rows.")
            
        except Exception as e:
            print(f"  -> ❌ Error reading {file}: {e}")

    # 3. Combine and Save
    if all_data:
        print("Merging all dataframes...")
        master_df = pd.concat(all_data, ignore_index=True)
        
        # Drop duplicates to avoid bias
        initial_count = len(master_df)
        master_df.drop_duplicates(subset=['url'], inplace=True)
        dropped_count = initial_count - len(master_df)
        
        print("="*40)
        print(f"MERGE COMPLETE")
        print(f"Total Unique URLs: {len(master_df)}")
        print(f"Duplicates Removed: {dropped_count}")
        print("-" * 20)
        print(f"Class Distribution:\n{master_df['label'].value_counts()}")
        print("="*40)
        
        master_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved merged data to: {OUTPUT_FILE}")
    else:
        print("No data could be merged. Please check your file paths.")

if __name__ == "__main__":
    merge_datasets()