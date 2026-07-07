# Steam Games Analysis

Analysis of ~122,000 Steam games: how price, genre, business model, and release timing relate to player ratings and engagement.

**Stack:** PostgreSQL, Python (pandas, matplotlib, seaborn), SQL (CTEs, window functions, percentile aggregates)

## Data

[Steam Games Dataset (Kaggle)](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset), ~122,000 games from the Steam Web API. Raw CSV (~389 MB) is not committed; see [`data/README.md`](data/README.md).

The source CSV header merges two fields (`Discount` and `DLC count`) into one name, so the header has 39 names but rows have 40 fields, shifting every column after position 7. Handled at load time by passing explicit column names (`header=0, names=[...]`) instead of editing the raw file. Details in [`notebooks/01_etl_clean.py`](notebooks/01_etl_clean.py).

## Pipeline

1. **Profile** ([`notebooks/00_explore_data.py`](notebooks/00_explore_data.py)) - column types, missing-value counts per column.
2. **ETL** ([`notebooks/01_etl_clean.py`](notebooks/01_etl_clean.py)) - load raw CSV, select 24 columns, fix column shift, parse dates/booleans, drop rows missing `app_id` or `release_date`, export cleaned CSV.
3. **Load** ([`sql/00_schema.sql`](sql/00_schema.sql)) - typed PostgreSQL table (`NUMERIC` for prices, `DATE`, `BOOLEAN` for platform flags).
4. **Analyze** ([`sql/`](sql/)) - five queries.
5. **Visualize** ([`notebooks/02_vis.py`](notebooks/02_vis.py)) - reads from PostgreSQL via SQLAlchemy, renders charts with seaborn.

Filter used throughout: only games with 50+ reviews, to keep ratios statistically meaningful. Median and standard deviation reported alongside mean, because the data is right-skewed and the mean alone is often misleading.

## Results

### Q1 - Price vs rating
Finding 1: [Query](sql/Q1-price-rating-correlation.sql)
Higher price does NOT mean better ratings. Positive review ratio follows an inverted-U curve, peaking at the $5-15 bracket (81.4%) and declining for premium titles. The $60+ segment scored lowest (68.6%), though with a small sample (n=31). This suggests a "sweet spot" for well received games in the mid-low price range, possibly reflecting buyer expectations scaling with price.

### Q2 - Genre vs rating
Finding 2: [Query](sql/Q2-category-analysis.sql)
Genre barely predicts rating with two exceptions. Most genres cluster tightly between 0.76-0.80 average positive ratio, meaning genre is a weak predictor of reception. Two genres break the pattern downward: MMO (0.674) and Violent (0.649). MMOs likely suffer from their live service nature (server issues, monetization, abandonment) and high player expectations, while the Violent tag has a small sample (n=127). Indie, Adventure, and Casual are the most numerous categories. They sit at the top, consistent with Steam's indie dominated catalog and the price findings from Q1.

### Q3 - Free-to-play vs paid
Finding 3: [Query](sql/Q3-free-to-paid-receipt.sql)
Free to play games show 2.4× higher average reviews and 2× higher average playtime than paid games. But the medians tell the opposite story: typical F2P and paid games have nearly identical review counts (238 vs 239), and typical F2P playtime is 8× lower (17 min vs 146 min). The averages are inflated by a handful of F2P mega-hits (CS:GO, Dota 2) with millions of reviews and thousands of hours. The median reveals the truth: the typical F2P game is installed and abandoned within 17 minutes, while paid games with their upfront cost filtering for genuine interest retain players far longer. F2P also scores lower on ratings (0.762 vs 0.789). Zero price barrier drives downloads but not commitment.

### Q4 - Release timing
Finding 4: [Query](sql/Q4-release-date-factor.sql)
Release timing barely affects ratings, but strongly affects reach. Average rating is essentially flat across the year (0.775–0.792, a 1.7 point spread), meaning launch month doesn't determine how well a game is received, but quality does. Review counts, however, vary sharply: August released games average 8,578 reviews vs January's 3,121 (2.7×). Using dual RANK() window functions revealed that the best months for ratings and popularity diverge. December ranks #1 in both (holiday effect), but August tops popularity while sitting mid-pack (#8) on ratings, and May produces well rated but low-reach games (#2 rating, #9 popularity). Takeaway for developers: timing won't fix a mediocre game's reviews, but it can meaningfully affect visibility.

### Q5 - Top 1% profile
Finding 5: [Query](sql/Q5-top-profile.sql)
The top 1% is a different universe and it confirms every prior finding. The 307 most reviewed games (top 1%) average 289,297 reviews vs 1,958 for the rest, that's a 148× gap, revealing Steam's dynamics. These elite games are priced at $9.92 on average within the $5-15 "sweet spot" identified in Finding 1 and score higher (0.882 vs 0.784), are played 7× longer (74h vs 10h), and are disproportionately F2P (17.3% vs 13.2%). The F2P overrepresentation confirms Finding 3: while the typical F2P game is abandoned in minutes, the F2P mega hits dominate the top tier.

## Repository

```
steam-games-analysis/
├── data/            # dataset download instructions (CSV not committed)
├── sql/             # schema + 5 analysis queries
├── notebooks/       # profiling, ETL, visualization scripts
└── dashboard/       # exported charts
```

## Reproduce

1. Download `games.csv` from Kaggle into `data/`.
2. Create table: `psql -d steam_analysis -f sql/00_schema.sql`
3. Run ETL: `python notebooks/01_etl_clean.py`
4. Load: `\copy games FROM 'data/games_clean.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8')`
5. Run queries in `sql/`, or `python notebooks/02_vis.py` for charts (set `STEAM_DB_PASSWORD` first).
