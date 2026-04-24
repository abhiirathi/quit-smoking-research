"""
Discover quit-smoking/vaping apps on Play Store + App Store (India),
capture metadata + monetization signals.

Outputs:
  data/apps.csv           - one row per app (both stores)
  data/monetization.csv   - monetization-focused view
"""
from __future__ import annotations

import re
import time
from typing import Any

import pandas as pd
from tqdm import tqdm

from config import (
    APPS_CSV,
    COUNTRY,
    LANG,
    MAX_APPS_PER_QUERY,
    MONETIZATION_CSV,
    SEARCH_QUERIES,
)

# ---------- Play Store ----------
from google_play_scraper import app as gp_app
from google_play_scraper import search as gp_search


def discover_play_apps() -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for q in SEARCH_QUERIES:
        try:
            results = gp_search(q, lang=LANG, country=COUNTRY, n_hits=MAX_APPS_PER_QUERY)
        except Exception as e:
            print(f"[play] search '{q}' failed: {e}")
            continue
        for r in results:
            app_id = r.get("appId")
            if not app_id or app_id in seen:
                continue
            seen[app_id] = {"appId": app_id, "query": q}
        time.sleep(0.5)

    rows: list[dict[str, Any]] = []
    for app_id, meta in tqdm(seen.items(), desc="play details"):
        try:
            d = gp_app(app_id, lang=LANG, country=COUNTRY)
        except Exception as e:
            print(f"[play] detail {app_id} failed: {e}")
            continue
        rows.append(
            {
                "store": "play",
                "app_id": app_id,
                "name": d.get("title"),
                "developer": d.get("developer"),
                "rating": d.get("score"),
                "ratings_count": d.get("ratings"),
                "reviews_count": d.get("reviews"),
                "installs": d.get("installs"),
                "price": d.get("price"),
                "free": d.get("free"),
                "contains_ads": d.get("adSupported"),
                "in_app_purchases": d.get("offersIAP"),
                "iap_range": d.get("inAppProductPrice"),
                "genre": d.get("genre"),
                "released": d.get("released"),
                "updated": d.get("updated"),
                "description": d.get("description"),
                "url": d.get("url"),
                "query": meta["query"],
            }
        )
        time.sleep(0.3)
    return rows


# ---------- App Store ----------
from app_store_scraper import AppStore
import requests


def _itunes_search(term: str) -> list[dict[str, Any]]:
    """Use the public iTunes search API to discover apps; app-store-scraper
    needs an app name+id, so we discover via iTunes first."""
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "country": COUNTRY,
        "media": "software",
        "limit": MAX_APPS_PER_QUERY,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"[appstore] itunes search '{term}' failed: {e}")
        return []


def discover_appstore_apps() -> list[dict[str, Any]]:
    seen: dict[int, dict[str, Any]] = {}
    for q in SEARCH_QUERIES:
        for r in _itunes_search(q):
            app_id = r.get("trackId")
            if not app_id or app_id in seen:
                continue
            seen[app_id] = {**r, "query": q}
        time.sleep(0.5)

    rows: list[dict[str, Any]] = []
    for app_id, r in seen.items():
        iap_flag = any(
            "in-app" in f.lower() or "inapp" in f.lower()
            for f in (r.get("features") or [])
        )
        rows.append(
            {
                "store": "appstore",
                "app_id": app_id,
                "name": r.get("trackName"),
                "bundle_id": r.get("bundleId"),
                "developer": r.get("artistName"),
                "rating": r.get("averageUserRating"),
                "ratings_count": r.get("userRatingCount"),
                "reviews_count": r.get("userRatingCount"),
                "installs": None,
                "price": r.get("price"),
                "free": (r.get("price") or 0) == 0,
                "contains_ads": None,
                "in_app_purchases": iap_flag,
                "iap_range": None,
                "genre": r.get("primaryGenreName"),
                "released": r.get("releaseDate"),
                "updated": r.get("currentVersionReleaseDate"),
                "description": r.get("description"),
                "url": r.get("trackViewUrl"),
                "query": r["query"],
            }
        )
    return rows


# ---------- Monetization extraction from description ----------
PRICE_PATTERNS = [
    r"(?:₹|rs\.?|inr)\s?\d[\d,]*(?:\.\d+)?",
    r"\$\s?\d[\d,]*(?:\.\d+)?",
    r"€\s?\d[\d,]*(?:\.\d+)?",
    r"£\s?\d[\d,]*(?:\.\d+)?",
]
PLAN_KEYWORDS = [
    "monthly", "weekly", "yearly", "annual", "lifetime",
    "premium", "pro", "subscription", "free trial", "trial",
    "auto-renew", "auto renew",
]


def extract_monetization(description: str) -> dict[str, Any]:
    text = (description or "").lower()
    prices: list[str] = []
    for p in PRICE_PATTERNS:
        prices.extend(re.findall(p, text, flags=re.IGNORECASE))
    plans = [k for k in PLAN_KEYWORDS if k in text]
    return {
        "prices_mentioned": "; ".join(sorted(set(prices))) if prices else "",
        "plan_keywords": "; ".join(sorted(set(plans))) if plans else "",
        "mentions_subscription": "subscription" in text or "subscribe" in text,
        "mentions_trial": "trial" in text,
        "mentions_lifetime": "lifetime" in text,
    }


def main() -> None:
    print("Discovering Play Store apps...")
    play_rows = discover_play_apps()
    print(f"  found {len(play_rows)} apps")

    print("Discovering App Store apps...")
    appstore_rows = discover_appstore_apps()
    print(f"  found {len(appstore_rows)} apps")

    df = pd.DataFrame(play_rows + appstore_rows)
    if df.empty:
        print("No apps discovered.")
        return

    mon = df["description"].fillna("").apply(extract_monetization).apply(pd.Series)
    df = pd.concat([df, mon], axis=1)

    df.to_csv(APPS_CSV, index=False)
    print(f"wrote {APPS_CSV}")

    mon_cols = [
        "store", "app_id", "name", "developer", "rating", "ratings_count",
        "installs", "price", "free", "contains_ads", "in_app_purchases",
        "iap_range", "prices_mentioned", "plan_keywords",
        "mentions_subscription", "mentions_trial", "mentions_lifetime", "url",
    ]
    df[mon_cols].to_csv(MONETIZATION_CSV, index=False)
    print(f"wrote {MONETIZATION_CSV}")


if __name__ == "__main__":
    main()
