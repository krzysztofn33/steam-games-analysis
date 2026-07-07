"""
Visualizations for Steam Games Analysis.
Reads data from PostgreSQL and produces charts for the key findings.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from pathlib import Path

# --- Setup ---
REPO_DIR = Path(__file__).parent.parent
OUTPUT_DIR = REPO_DIR / "dashboard" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Database connection - password from environment variable (never hardcoded)
DB_PASSWORD = os.environ.get("STEAM_DB_PASSWORD")
if not DB_PASSWORD:
    raise SystemExit("Set STEAM_DB_PASSWORD environment variable first")

engine = create_engine(
    f"postgresql+psycopg2://postgres:{DB_PASSWORD}@localhost:5432/steam_analysis"
)

# Global style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 150

# --- Chart 1: Price bracket vs positive ratio (box plot) ---
print("Building Chart 1: price vs ratings...")

query_1 = """
    SELECT
        CASE
            WHEN price = 0 THEN 'Free'
            WHEN price < 5 THEN '$0-5'
            WHEN price < 15 THEN '$5-15'
            WHEN price < 30 THEN '$15-30'
            WHEN price < 60 THEN '$30-60'
            ELSE '$60+'
        END AS price_bucket,
        positive::FLOAT / (positive + negative) AS positive_ratio
    FROM games
    WHERE (positive + negative) >= 50
"""

df1 = pd.read_sql(query_1, engine)

# Order buckets logically (not alphabetically)
bucket_order = ['Free', '$0-5', '$5-15', '$15-30', '$30-60', '$60+']

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(
    data=df1,
    x='price_bucket',
    y='positive_ratio',
    order=bucket_order,
    ax=ax,
    showfliers=False,   # hide outlier dots for cleaner look
    palette='viridis'
)
ax.set_title('Positive Review Ratio by Price Bracket', fontsize=14, fontweight='bold')
ax.set_xlabel('Price Bracket', fontsize=11)
ax.set_ylabel('Positive Reviews / Total Reviews', fontsize=11)
ax.set_ylim(0, 1)

plt.tight_layout()
output_path = OUTPUT_DIR / "chart_1_price_vs_rating.png"
plt.savefig(output_path, bbox_inches='tight')
plt.close()
print(f"Saved: {output_path}")

# --- Chart 2: Genre ranking (horizontal bar) ---
print("Building Chart 2: genre ranking...")

query_2 = """
    WITH genre_split AS (
        SELECT
            positive::FLOAT / (positive + negative) AS positive_ratio,
            TRIM(UNNEST(STRING_TO_ARRAY(genres, ','))) AS genre
        FROM games
        WHERE genres IS NOT NULL
          AND (positive + negative) >= 50
    )
    SELECT
        genre,
        AVG(positive_ratio) AS avg_ratio,
        COUNT(*) AS games_count
    FROM genre_split
    GROUP BY genre
    HAVING COUNT(*) >= 100
    ORDER BY avg_ratio DESC
"""
df2 = pd.read_sql(query_2, engine)

fig, ax = plt.subplots(figsize=(10, 8))
sns.barplot(
    data=df2,
    x='avg_ratio',      # oś X = wartość (poziomy słupek)
    y='genre',          # oś Y = nazwa gatunku
    ax=ax,
    palette='viridis',
    hue='genre',        # koloruj po gatunku
    legend=False        # bez legendy (nazwy są już na osi Y)
)
ax.set_title('Average Positive Ratio by Genre', fontsize=14, fontweight='bold')
ax.set_xlabel('Average Positive Ratio')
ax.set_ylabel('')                # nazwy gatunków mówią same za siebie
ax.set_xlim(0.6, 0.85)           # zoom na istotny zakres, żeby różnice były widoczne

fig.savefig(OUTPUT_DIR / "chart_2_genre_ranking.png", bbox_inches='tight', dpi=150)
plt.close(fig)
print("Saved chart 2")

# --- Chart 3: F2P vs Paid - how mean hides the truth (grouped bar) ---
print("Building Chart 3: F2P vs Paid mean vs median...")

query_3 = """
    SELECT
        CASE WHEN price = 0 THEN 'Free-to-Play' ELSE 'Paid' END AS model,
        AVG(average_playtime) AS mean_playtime,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY average_playtime) AS median_playtime
    FROM games
    WHERE (positive + negative) >= 50
    GROUP BY CASE WHEN price = 0 THEN 'Free-to-Play' ELSE 'Paid' END
"""
df3 = pd.read_sql(query_3, engine)

# Reshape data from wide to long format for grouped bars
# Before: one row per model, columns mean/median
# After: one row per (model, statistic) pair - seaborn likes this shape
df3_long = df3.melt(
    id_vars='model',
    value_vars=['mean_playtime', 'median_playtime'],
    var_name='statistic',
    value_name='minutes'
)
# Nicer labels
df3_long['statistic'] = df3_long['statistic'].map({
    'mean_playtime': 'Mean',
    'median_playtime': 'Median'
})

fig, ax = plt.subplots(figsize=(9, 6))
sns.barplot(
    data=df3_long,
    x='model',
    y='minutes',
    hue='statistic',    # dwa słupki obok siebie (Mean, Median) per model
    ax=ax,
    palette=['#e07a5f', '#3d5a80']   # dwa kontrastowe kolory
)
ax.set_title('Average Playtime: Mean vs Median by Business Model',
             fontsize=14, fontweight='bold')
ax.set_xlabel('')
ax.set_ylabel('Playtime (minutes)')
ax.legend(title='Statistic')

# Add value labels on top of each bar
for container in ax.containers:
    ax.bar_label(container, fmt='%.0f', padding=3, fontsize=10)

fig.savefig(OUTPUT_DIR / "chart_3_f2p_mean_vs_median.png", bbox_inches='tight', dpi=150)
plt.close(fig)
print("Saved chart 3")