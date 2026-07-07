import pandas as pd
from pathlib import Path


REPO_DIR = Path(__file__).parent.parent
RAW_CSV = REPO_DIR / "data" / "games.csv"

df = pd.read_csv(RAW_CSV, low_memory=False)
print(f"Loaded {len(df):,} rows, {len(df.columns)} columns\n")

print("-All columns-")
print(df.dtypes)

print("-Missing values - full set-")
nan_counts = df.isna().sum()
nan_pct = (nan_counts / len(df) * 100).round(1)
nan_summary = pd.DataFrame({
    'nan_count': nan_counts,
    'nan_pct': nan_pct,
    'non_null': len(df) - nan_counts
})
nan_summary = nan_summary.sort_values('nan_pct', ascending=False)
print(nan_summary.to_string())

print('-empty strings-')
string_cols = df.select_dtypes(include=['object']).columns
for col in string_cols:
    empty_count = (df[col].astype(str).str.strip() == '').sum()
    if empty_count > 0:
        pct = empty_count / len(df) * 100
        print(f"  {col}: {empty_count:,} empty strings ({pct:.1f}%)")
