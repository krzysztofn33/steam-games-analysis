"""
ETL: Steam games dataset
Cleans the raw csv and exports a ready to load PSQL file.
"""

import pandas as pd
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
RAW_CSV = REPO_DIR / "data" / "games.csv"
CLEAN_CSV = REPO_DIR / "data" / "games_clean.csv"

# Source CSV has a malformed header: "Discount" and "DLC count" are merged
# into one name "DiscountDLC count", so the header has 39 names but data rows
# have 40 fields.

correct_names = [
    'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU',
    'Required age', 'Price', 'Discount', 'DLC count', 'About the game',
    'Supported languages', 'Full audio languages', 'Reviews', 'Header image',
    'Website', 'Support url', 'Support email', 'Windows', 'Mac', 'Linux',
    'Metacritic score', 'Metacritic url', 'User score', 'Positive', 'Negative',
    'Score rank', 'Achievements', 'Recommendations', 'Notes',
    'Average playtime forever', 'Average playtime two weeks',
    'Median playtime forever', 'Median playtime two weeks',
    'Developers', 'Publishers', 'Categories', 'Genres', 'Tags',
    'Screenshots', 'Movies'
]
df = pd.read_csv((RAW_CSV), low_memory=False, header=0, names=correct_names)
print(f"loaded {len(df):,} rows, {len(df.columns)} col")

import csv

with open(RAW_CSV, encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f"Liczba nazw w nagłówku: {len(header)}")
    for i in range(3):
        row = next(reader)
        print(f"Wiersz {i}: liczba pól = {len(row)}")

columns_map = {
    'AppID':                    'app_id',
    'Name':                     'name',
    'Release date':             'release_date',
    'Estimated owners':         'estimated_owners',
    'Peak CCU':                 'peak_ccu',
    'Required age':             'required_age',
    'Price':                    'price',
    'About the game':           'about_the_game',
    'DLC count':                'dlc_count',
    'Supported languages':      'supported_languages',
    'Windows':                  'windows',
    'Mac':                      'mac',
    'Linux':                    'linux',
    'Metacritic score':         'metacritic_score',
    'Positive':                 'positive',
    'Negative':                 'negative',
    'Achievements':             'achievements',
    'Recommendations':          'recommendations',
    'Average playtime forever': 'average_playtime',
    'Median playtime forever':  'median_playtime',
    'Developers':               'developers',
    'Publishers':               'publishers',
    'Categories':               'categories',
    'Genres':                   'genres',
    'Header image':             'header_image',
    'Tags':                     'tags',
}

missing = [col for col in columns_map.keys() if col not in df.columns]
if missing: 
    print(f"Warning: Missing columns in CSV: {missing}")
    print(f"Available columns: {list(df.columns)}")
    raise SystemExit("cannot proceed - missing columns")

df = df[list(columns_map.keys())].rename(columns=columns_map)
print(f"After column selection: {df.shape}")

#handle release date
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce', format='mixed')

for col in ['windows', 'mac', 'linux']:
    df[col] = df[col].astype(str).str.lower().map({'true': True, 'false': False})

df['required_age'] = df['required_age'].astype('Int64')

print("\nNaN counts in key columns:")
print(df[['release_date', 'price', 'positive', 'negative', 'metacritic_score', 'app_id']].isna().sum())

# Drop rows missing primary key or release date
before = len(df)
df = df.dropna(subset=['app_id', 'release_date'])
after = len(df)
print(f"\nDropped {before - after:,} rows (missing app_id or release_date)")

df['app_id'] = df['app_id'].astype(int)

print(f"Final dataset: {len(df):,} rows")

# Export cleaned CSV
print(f"\nWriting {CLEAN_CSV} ...")
df.to_csv(CLEAN_CSV, index=False)
print(f"Done. Output size: {CLEAN_CSV.stat().st_size / 1024 / 1024:.1f} MB")