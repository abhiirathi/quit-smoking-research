# Quit-Smoking / Vaping Competitor Research

Scrapes Play Store + App Store for quit-smoking/vaping apps in the **Indian market**, pulls 1–2★ reviews, clusters complaints & feature requests into themes, and ships a Streamlit dashboard for exploration.

Outputs live in `research/data/` — the dashboard reads them directly, and `summary.xlsx` is a single workbook you can open in Excel/Numbers.

## One-time setup

```bash
cd research
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the pipeline

```bash
# from repo root
python research/run_all.py
```

This runs three stages (expect ~10–20 min depending on network):

1. `scrape_apps.py` — discover competitor apps on both stores, capture pricing/IAP/ads/subscription signals.
2. `scrape_reviews.py` — pull recent reviews per app, keep only 1★ + 2★.
3. `analyze_themes.py` — tag each review with theme buckets (crashes, paywall, tracking accuracy, ads, motivation, personalization, India context, etc.), extract feature requests, emit `summary.xlsx`.

You can also run any stage individually:

```bash
python research/scrape_apps.py
python research/scrape_reviews.py
python research/analyze_themes.py
```

## Launch the dashboard

```bash
streamlit run research/dashboard.py
```

Tabs:

- **Overview** — worst-rated apps by volume of 1–2★ reviews.
- **Complaint themes** — top themes overall, app-vs-theme heatmap, browse reviews by theme.
- **Feature requests** — what users are begging competitors to add.
- **Monetization** — price, IAP, ads, subscription plan language per app.
- **India lens** — reviews mentioning Indian cities, rupees, regional languages, bidi/paan/gutkha, etc.
- **Raw reviews** — searchable table + CSV export.

## Notes on India targeting

- Play Store + App Store searches are scoped via `country="in"`.
- The App Store review API does not expose reviewer country post-fetch, so we flag likely-Indian reviews via text signals (cities, rupees, regional language names, India-specific tobacco terms). Use the **India lens** tab and the "India-signal reviews only" filter.

## Tuning

Edit `config.py`:

- `SEARCH_QUERIES` — add niche terms (e.g., "bidi", "gutkha", "tobacco de-addiction").
- `MAX_APPS_PER_QUERY` — widen the funnel.
- `MAX_REVIEWS_PER_APP` — we filter to 1–2★ after fetching, so raise this to surface more low-star reviews per app.

## Data files

| File | What it contains |
|---|---|
| `data/apps.csv` | Every discovered app, both stores, with metadata + monetization extraction from descriptions |
| `data/monetization.csv` | Monetization-focused projection |
| `data/reviews.csv` | All 1–2★ reviews, one row per review |
| `data/themes.csv` | Long format: one row per (review, theme) |
| `data/feature_requests.csv` | Reviews flagged as feature requests, with the extracted snippet |
| `data/summary.xlsx` | All of the above as an Excel workbook |
