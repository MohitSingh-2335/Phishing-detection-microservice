import pandas as pd
import os

# --- CONFIGURATION ---
# List your 4 CSV filenames here
CSV_FILES = [
    'data/data.csv', 
    'data/malicious_phish.csv', 
    'data/phishing_site_urls.csv',
    'data/URL Classification.csv'
]
OUTPUT_FILE = 'data/master_dataset.csv'

def normalize_label(value):
    """
    Converts various label formats (bad, malicious, phishing, 1) into 1 (Unsafe).
    Converts (good, benign, safe, 0) into 0 (Safe).
    """
    s = str(value).lower().strip()
    unsafe_keywords = ['bad', 'phishing', 'malicious', 'malware', 'defacement', 'spam', '1']
    if s in unsafe_keywords:
        return 1
    return 0

def merge_datasets():
    all_data = []

    for file in CSV_FILES:
        if not os.path.exists(file):
            print(f"Skipping {file} (Not found)")
            continue
            
        print(f"Processing {file}...")
        try:
            df = pd.read_csv(file)
            
            # 1. Find the URL column (it might be named 'url', 'URL', 'address', etc.)
            cols = [c.lower() for c in df.columns]
            if 'url' in cols:
                url_col = df.columns[cols.index('url')]
            elif 'address' in cols:
                url_col = df.columns[cols.index('address')]
            else:
                print(f"  -> Could not find URL column in {file}. Skipping.")
                continue

            # 2. Find the Label column
            if 'label' in cols:
                label_col = df.columns[cols.index('label')]
            elif 'type' in cols:
                label_col = df.columns[cols.index('type')]
            elif 'class' in cols:
                label_col = df.columns[cols.index('class')]
            else:
                print(f"  -> Could not find Label column in {file}. Skipping.")
                continue
            
            # 3. Standardize and Select only what we need
            temp_df = pd.DataFrame()
            temp_df['url'] = df[url_col]
            temp_df['label'] = df[label_col].apply(normalize_label)
            
            all_data.append(temp_df)
            print(f"  -> Added {len(temp_df)} rows.")
            
        except Exception as e:
            print(f"  -> Error reading {file}: {e}")

    # 4. Combine and Save
    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
        # Drop duplicates to avoid bias
        master_df.drop_duplicates(subset=['url'], inplace=True)
        
        print("="*30)
        print(f"TOTAL MERGED ROWS: {len(master_df)}")
        print(f"Breakdown:\n{master_df['label'].value_counts()}")
        
        master_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved merged data to: {OUTPUT_FILE}")
    else:
        print("No data could be merged.")

if __name__ == "__main__":
    merge_datasets()