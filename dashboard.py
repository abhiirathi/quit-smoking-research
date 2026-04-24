"""
Streamlit dashboard over the scraped + analyzed data.

Run:
    streamlit run research/dashboard.py
"""
from __future__ import annotations

import ast

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    APPS_CSV,
    FEATURE_REQUESTS_CSV,
    MONETIZATION_CSV,
    REVIEWS_CSV,
    THEMES_CSV,
)

st.set_page_config(
    page_title="Quit-Smoking App Landscape — India",
    layout="wide",
)


@st.cache_data
def load():
    apps = pd.read_csv(APPS_CSV) if APPS_CSV.exists() else pd.DataFrame()
    reviews = pd.read_csv(REVIEWS_CSV) if REVIEWS_CSV.exists() else pd.DataFrame()
    themes = pd.read_csv(THEMES_CSV) if THEMES_CSV.exists() else pd.DataFrame()
    mon = pd.read_csv(MONETIZATION_CSV) if MONETIZATION_CSV.exists() else pd.DataFrame()
    fr = pd.read_csv(FEATURE_REQUESTS_CSV) if FEATURE_REQUESTS_CSV.exists() else pd.DataFrame()
    return apps, reviews, themes, mon, fr


apps, reviews, themes, monetization, feature_requests = load()

st.title("Quit-Smoking / Vaping App Landscape — India")
st.caption("Scraped from Play Store + App Store. 1–2★ reviews only. Built to spot what existing apps get wrong.")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    stores = st.multiselect("Store", ["play", "appstore"], default=["play", "appstore"])
    india_only = st.checkbox("India-signal reviews only", value=False,
                             help="Reviews mentioning India, Indian cities, rupees, regional languages, bidi, paan, etc.")
    app_options = sorted(reviews["app_name"].dropna().unique().tolist()) if not reviews.empty else []
    selected_apps = st.multiselect("Apps", app_options, default=app_options)


def _filter(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "store" in out.columns:
        out = out[out["store"].isin(stores)]
    if "app_name" in out.columns and selected_apps:
        out = out[out["app_name"].isin(selected_apps)]
    if india_only and "india_signal" in out.columns:
        out = out[out["india_signal"] == True]  # noqa: E712
    return out


f_reviews = _filter(reviews)
f_themes = _filter(themes)
f_fr = _filter(feature_requests)

tabs = st.tabs([
    "Overview",
    "Complaint themes",
    "Feature requests",
    "Monetization",
    "India lens",
    "Raw reviews",
])

# ---------- Overview ----------
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Apps discovered", len(apps))
    c2.metric("1–2★ reviews", len(f_reviews))
    if not f_reviews.empty:
        c3.metric("Apps with complaints", f_reviews["app_name"].nunique())
    if not f_fr.empty:
        c4.metric("Feature requests", len(f_fr))

    st.subheader("Worst-rated apps (by volume of 1–2★ reviews)")
    if not f_reviews.empty:
        vol = (
            f_reviews.groupby(["app_name", "store"]).size()
            .reset_index(name="bad_reviews")
            .sort_values("bad_reviews", ascending=False)
            .head(25)
        )
        fig = px.bar(vol, x="bad_reviews", y="app_name", color="store", orientation="h")
        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rating distribution across discovered apps")
    if not apps.empty:
        fig = px.histogram(apps, x="rating", color="store", nbins=20)
        st.plotly_chart(fig, use_container_width=True)

# ---------- Complaint themes ----------
with tabs[1]:
    st.subheader("Top complaint themes (all filtered reviews)")
    if not f_themes.empty:
        top = (
            f_themes.groupby("theme").size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        fig = px.bar(top, x="count", y="theme", orientation="h")
        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Themes per app (heatmap)")
        pivot = (
            f_themes.groupby(["app_name", "theme"]).size()
            .reset_index(name="count")
            .pivot(index="app_name", columns="theme", values="count")
            .fillna(0)
        )
        if not pivot.empty:
            fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Reds")
            fig.update_layout(height=max(400, 22 * len(pivot)))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Browse reviews by theme")
        theme_pick = st.selectbox("Theme", sorted(f_themes["theme"].unique()))
        sub = f_themes[f_themes["theme"] == theme_pick][
            ["app_name", "store", "rating", "date", "content"]
        ].head(200)
        st.dataframe(sub, use_container_width=True, height=500)

# ---------- Feature requests ----------
with tabs[2]:
    st.subheader("Feature requests extracted from 1–2★ reviews")
    if not f_fr.empty:
        per_app = (
            f_fr.groupby("app_name").size().reset_index(name="requests")
            .sort_values("requests", ascending=False).head(25)
        )
        fig = px.bar(per_app, x="requests", y="app_name", orientation="h")
        fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            f_fr[["app_name", "store", "rating", "request_snippet", "india_signal", "date"]],
            use_container_width=True,
            height=600,
        )
    else:
        st.info("No feature requests matched the current filters.")

# ---------- Monetization ----------
with tabs[3]:
    st.subheader("Monetization across competitor apps")
    if not monetization.empty:
        mon = monetization.copy()
        if stores:
            mon = mon[mon["store"].isin(stores)]

        c1, c2, c3 = st.columns(3)
        c1.metric("Free apps", int((mon["free"] == True).sum()))  # noqa: E712
        c2.metric("With in-app purchases", int((mon["in_app_purchases"] == True).sum()))  # noqa: E712
        c3.metric("Mention subscription in desc.", int((mon["mentions_subscription"] == True).sum()))  # noqa: E712

        st.markdown("**Per-app monetization table**")
        show_cols = [
            "store", "name", "developer", "rating", "ratings_count",
            "free", "price", "contains_ads", "in_app_purchases", "iap_range",
            "prices_mentioned", "plan_keywords", "mentions_subscription",
            "mentions_trial", "mentions_lifetime", "url",
        ]
        show_cols = [c for c in show_cols if c in mon.columns]
        st.dataframe(mon[show_cols], use_container_width=True, height=600)

        st.markdown("**Plan keyword frequency across descriptions**")
        kw_series = mon["plan_keywords"].fillna("").str.split("; ").explode()
        kw_series = kw_series[kw_series.str.len() > 0]
        if len(kw_series):
            kc = kw_series.value_counts().reset_index()
            kc.columns = ["keyword", "count"]
            fig = px.bar(kc, x="count", y="keyword", orientation="h")
            fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

# ---------- India lens ----------
with tabs[4]:
    st.subheader("India-signal reviews")
    st.caption("Reviews mentioning India-specific words (cities, rupees, regional languages, bidi/paan/gutkha, etc.).")
    india = reviews[reviews.get("india_signal") == True] if not reviews.empty else pd.DataFrame()  # noqa: E712
    if not india.empty:
        c1, c2 = st.columns(2)
        c1.metric("India-signal reviews", len(india))
        c2.metric("Apps with India complaints", india["app_name"].nunique())

        india_themes = themes[themes.get("india_signal") == True] if not themes.empty else pd.DataFrame()  # noqa: E712
        if not india_themes.empty:
            top = (
                india_themes.groupby("theme").size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            fig = px.bar(top, x="count", y="theme", orientation="h",
                         title="Themes in India-signal reviews")
            fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            india[["app_name", "store", "rating", "date", "content"]].head(500),
            use_container_width=True, height=600,
        )
    else:
        st.info("No India-signal reviews yet. Run the pipeline first.")

# ---------- Raw reviews ----------
with tabs[5]:
    st.subheader("Raw 1–2★ reviews")
    if not f_reviews.empty:
        search = st.text_input("Search within review text")
        data = f_reviews
        if search:
            data = data[data["content"].fillna("").str.contains(search, case=False)]
        st.dataframe(
            data[["app_name", "store", "rating", "date", "content"]],
            use_container_width=True, height=700,
        )
        st.download_button(
            "Download filtered reviews as CSV",
            data.to_csv(index=False).encode(),
            "reviews_filtered.csv",
        )
