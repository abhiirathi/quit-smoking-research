"""
Categorize 1-2 star reviews into themes: complaints, bugs, feature requests,
monetization pain, content quality, etc. Also flags likely India-origin
reviews using language/currency/place signals since App Store reviews don't
always carry a country field post-scrape.

Reads:  data/reviews.csv
Writes: data/themes.csv, data/feature_requests.csv, data/summary.xlsx
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

import pandas as pd

from config import (
    APPS_CSV,
    FEATURE_REQUESTS_CSV,
    MONETIZATION_CSV,
    REVIEWS_CSV,
    SUMMARY_XLSX,
    THEMES_CSV,
)

# Theme keyword buckets. Each review may match multiple themes.
THEMES: dict[str, list[str]] = {
    "crashes_bugs": [
        "crash", "crashes", "crashing", "force close", "freezes", "freeze",
        "bug", "buggy", "glitch", "broken", "doesn't work", "does not work",
        "not working", "stopped working", "won't open", "won't load",
    ],
    "paywall_pricing": [
        "paywall", "expensive", "too costly", "overpriced", "rip off", "ripoff",
        "scam", "money grab", "greedy", "pay to", "locked behind", "cant afford",
        "can't afford", "waste of money", "not worth", "too much money",
        "charge", "charged", "refund",
    ],
    "subscription_issues": [
        "subscription", "auto renew", "auto-renew", "cancel subscription",
        "hard to cancel", "trial", "free trial", "billed", "billing",
        "charged again", "unauthorised", "unauthorized",
    ],
    "ads": [
        "ads", "advert", "advertisement", "too many ads", "ad heavy",
        "pop up", "popup", "annoying ads",
    ],
    "tracking_accuracy": [
        "counter wrong", "counter reset", "reset my progress", "lost progress",
        "lost my streak", "streak reset", "tracker wrong", "wrong count",
        "miscount", "inaccurate", "wrong time", "wrong date", "resets",
    ],
    "login_account": [
        "login", "log in", "sign in", "sign up", "signup", "password",
        "can't login", "cannot login", "account", "otp", "verification",
    ],
    "ui_ux": [
        "ugly", "confusing", "hard to use", "complicated", "cluttered",
        "bad design", "outdated", "slow", "laggy", "unintuitive",
    ],
    "content_quality": [
        "useless", "boring", "repetitive", "not helpful", "no help",
        "didn't help", "did not help", "shallow", "basic", "generic",
    ],
    "motivation_support": [
        "no motivation", "no support", "not motivating", "lonely",
        "no community", "need support", "need coach", "need therapist",
    ],
    "personalization": [
        "not personalized", "generic plan", "one size", "doesn't adapt",
        "no customization", "cant customize", "can't customize",
    ],
    "notifications": [
        "notification", "reminders", "no reminder", "too many notif",
        "spam notif",
    ],
    "data_privacy": [
        "privacy", "data", "tracking me", "sells data", "permissions",
    ],
    "offline": [
        "offline", "no internet", "requires internet", "needs internet",
    ],
    "hindi_regional_language": [
        "hindi", "english only", "regional language", "marathi", "tamil",
        "telugu", "bengali", "gujarati", "kannada", "malayalam", "punjabi",
    ],
    "india_context": [
        "india", "indian", "rupee", "rupees", "₹", "inr", "paytm", "upi",
        "bidi", "beedi", "gutkha", "paan", "hookah", "tobacco chewing",
    ],
}

# Phrases that indicate a *feature request* rather than a pure complaint.
FEATURE_REQUEST_PATTERNS = [
    r"\bplease add\b", r"\bshould (have|add|include)\b", r"\bneed[s]? to have\b",
    r"\bwish (it|there|you)\b", r"\bwould be (great|nice|better) if\b",
    r"\bcan you (add|include|make)\b", r"\bplease (make|include|provide)\b",
    r"\bhope you (add|include|make)\b", r"\bmissing\b", r"\bno option to\b",
    r"\bthere should be\b", r"\bplease give\b", r"\bkindly add\b",
    r"\brequest(?:ing)? (?:for|to add|a feature)\b", r"\bfeature request\b",
]
FEATURE_REQUEST_RE = re.compile("|".join(FEATURE_REQUEST_PATTERNS), re.IGNORECASE)

# India-origin signals (reviews don't come pre-tagged by country for App Store).
INDIA_SIGNALS = re.compile(
    r"\b(india|indian|rupee|rupees|inr|paytm|upi|bidi|beedi|gutkha|paan|hookah|hindi|"
    r"mumbai|delhi|bangalore|bengaluru|chennai|kolkata|hyderabad|pune|"
    r"gujarati|marathi|tamil|telugu|bengali|kannada|malayalam|punjabi)\b",
    re.IGNORECASE,
)


def tag_themes(text: str) -> list[str]:
    t = (text or "").lower()
    hits = []
    for theme, kws in THEMES.items():
        if any(kw in t for kw in kws):
            hits.append(theme)
    return hits


def is_feature_request(text: str) -> bool:
    return bool(FEATURE_REQUEST_RE.search(text or ""))


def is_india_signal(text: str) -> bool:
    return bool(INDIA_SIGNALS.search(text or ""))


def _extract_request_snippet(text: str) -> str:
    """Pull the sentence around the feature-request phrase."""
    if not text:
        return ""
    sents = re.split(r"(?<=[.!?])\s+", text)
    for s in sents:
        if FEATURE_REQUEST_RE.search(s):
            return s.strip()[:300]
    return text.strip()[:300]


def main() -> None:
    reviews = pd.read_csv(REVIEWS_CSV)
    if reviews.empty:
        print("No reviews to analyze.")
        return

    reviews["content"] = reviews["content"].fillna("").astype(str)
    reviews["title"] = reviews["title"].fillna("").astype(str)
    reviews["full_text"] = (reviews["title"] + ". " + reviews["content"]).str.strip()

    reviews["themes"] = reviews["full_text"].apply(tag_themes)
    reviews["is_feature_request"] = reviews["full_text"].apply(is_feature_request)
    reviews["india_signal"] = reviews["full_text"].apply(is_india_signal)

    # Overwrite reviews.csv with enriched columns so the dashboard can filter.
    reviews.drop(columns=["full_text"]).to_csv(REVIEWS_CSV, index=False)

    # Explode themes -> one row per (review, theme) for easy dashboard slicing.
    themes_long = reviews.explode("themes")
    themes_long = themes_long[themes_long["themes"].notna()]
    themes_long = themes_long.rename(columns={"themes": "theme"})
    themes_long.to_csv(THEMES_CSV, index=False)
    print(f"wrote {THEMES_CSV} ({len(themes_long)} theme-tagged rows)")

    # Feature requests file.
    fr = reviews[reviews["is_feature_request"]].copy()
    fr["request_snippet"] = fr["full_text"].apply(_extract_request_snippet)
    fr = fr[[
        "store", "app_id", "app_name", "rating", "date",
        "request_snippet", "full_text", "india_signal",
    ]]
    fr.to_csv(FEATURE_REQUESTS_CSV, index=False)
    print(f"wrote {FEATURE_REQUESTS_CSV} ({len(fr)} feature requests)")

    # Summary xlsx — one-stop workbook linking everything.
    apps = pd.read_csv(APPS_CSV) if APPS_CSV.exists() else pd.DataFrame()
    mon = pd.read_csv(MONETIZATION_CSV) if MONETIZATION_CSV.exists() else pd.DataFrame()

    theme_counts = (
        themes_long.groupby(["app_name", "theme"]).size()
        .reset_index(name="count")
        .sort_values(["app_name", "count"], ascending=[True, False])
    )
    overall_theme_counts = (
        themes_long.groupby("theme").size().reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    india_reviews = reviews[reviews["india_signal"]]

    with pd.ExcelWriter(SUMMARY_XLSX, engine="openpyxl") as w:
        if not apps.empty:
            apps.to_excel(w, sheet_name="apps", index=False)
        if not mon.empty:
            mon.to_excel(w, sheet_name="monetization", index=False)
        reviews.drop(columns=["full_text"]).to_excel(w, sheet_name="reviews_1_2_star", index=False)
        themes_long.to_excel(w, sheet_name="themes_long", index=False)
        theme_counts.to_excel(w, sheet_name="themes_by_app", index=False)
        overall_theme_counts.to_excel(w, sheet_name="themes_overall", index=False)
        fr.to_excel(w, sheet_name="feature_requests", index=False)
        india_reviews.drop(columns=["full_text"]).to_excel(w, sheet_name="india_reviews", index=False)
    print(f"wrote {SUMMARY_XLSX}")


if __name__ == "__main__":
    main()
