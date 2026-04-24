"""
Pull 1-2 star reviews for each discovered app (India locale).

Reads:  data/apps.csv
Writes: data/reviews.csv
"""
from __future__ import annotations

import time
from typing import Any

import pandas as pd
from tqdm import tqdm

from config import (
    APPS_CSV,
    COUNTRY,
    LANG,
    MAX_REVIEWS_PER_APP,
    REVIEWS_CSV,
)

import requests

from google_play_scraper import Sort, reviews as gp_reviews


def fetch_play_reviews(app_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        # NEWEST sort surfaces fresher complaints; we cap total count.
        result, _ = gp_reviews(
            app_id,
            lang=LANG,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=MAX_REVIEWS_PER_APP,
        )
    except Exception as e:
        print(f"[play reviews] {app_id} failed: {e}")
        return out

    for r in result:
        score = r.get("score")
        if score not in (1, 2):
            continue
        out.append(
            {
                "store": "play",
                "app_id": app_id,
                "rating": score,
                "title": None,
                "content": r.get("content"),
                "user": r.get("userName"),
                "date": r.get("at"),
                "thumbs_up": r.get("thumbsUpCount"),
                "app_version": r.get("reviewCreatedVersion"),
            }
        )
    return out


def fetch_appstore_reviews(app_id: int, app_name: str) -> list[dict[str, Any]]:
    """Use Apple's public customer-reviews RSS JSON feed directly. Paginates
    across pages 1..10 (Apple caps at 10, ~50 reviews each)."""
    out: list[dict[str, Any]] = []
    headers = {"User-Agent": "Mozilla/5.0"}
    per_page_cap = max(1, MAX_REVIEWS_PER_APP // 50)
    for page in range(1, min(11, per_page_cap + 2)):
        url = (
            f"https://itunes.apple.com/{COUNTRY}/rss/customerreviews/"
            f"page={page}/id={int(app_id)}/sortby=mostrecent/json"
        )
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                break
            data = r.json()
        except Exception as e:
            print(f"[appstore reviews] {app_name} page {page} failed: {e}")
            break
        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            break
        # First entry is app metadata; reviews follow.
        for e in entries[1:] if isinstance(entries, list) else []:
            try:
                score = int(e.get("im:rating", {}).get("label", 0))
            except Exception:
                continue
            if score not in (1, 2):
                continue
            out.append(
                {
                    "store": "appstore",
                    "app_id": app_id,
                    "rating": score,
                    "title": e.get("title", {}).get("label"),
                    "content": e.get("content", {}).get("label"),
                    "user": e.get("author", {}).get("name", {}).get("label"),
                    "date": e.get("updated", {}).get("label"),
                    "thumbs_up": None,
                    "app_version": e.get("im:version", {}).get("label"),
                }
            )
        time.sleep(0.3)
    return out


def _slug(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


def main() -> None:
    apps = pd.read_csv(APPS_CSV)
    all_reviews: list[dict[str, Any]] = []

    for _, row in tqdm(list(apps.iterrows()), desc="reviews"):
        store = row["store"]
        app_id = row["app_id"]
        name = row.get("name", "")
        if store == "play":
            revs = fetch_play_reviews(str(app_id))
        else:
            revs = fetch_appstore_reviews(int(app_id), _slug(name))
        for r in revs:
            r["app_name"] = name
        all_reviews.extend(revs)
        time.sleep(0.4)

    df = pd.DataFrame(all_reviews)
    if df.empty:
        print("No 1-2 star reviews collected.")
        df = pd.DataFrame(columns=[
            "store", "app_id", "app_name", "rating", "title", "content",
            "user", "date", "thumbs_up", "app_version"
        ])
    df.to_csv(REVIEWS_CSV, index=False)
    print(f"wrote {REVIEWS_CSV} ({len(df)} rows)")


if __name__ == "__main__":
    main()
