"""Shared config for the research pipeline."""
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Search queries used to discover competitor apps on both stores.
SEARCH_QUERIES = [
    "quit smoking",
    "stop smoking",
    "quit vaping",
    "stop vaping",
    "smoke free",
    "nicotine quit",
    "cigarette tracker",
    "quit tobacco",
]

# Country / language targeting — Indian market focus.
COUNTRY = "in"
LANG = "en"

# Caps so we don't scrape forever.
MAX_APPS_PER_QUERY = 15      # top N apps per search query per store
MAX_REVIEWS_PER_APP = 300    # cap reviews fetched per app (we filter to 1-2 star after)
REVIEW_BATCH_SIZE = 100

# Output files
APPS_CSV = DATA_DIR / "apps.csv"
MONETIZATION_CSV = DATA_DIR / "monetization.csv"
REVIEWS_CSV = DATA_DIR / "reviews.csv"
THEMES_CSV = DATA_DIR / "themes.csv"
FEATURE_REQUESTS_CSV = DATA_DIR / "feature_requests.csv"
SUMMARY_XLSX = DATA_DIR / "summary.xlsx"
