"""
Streamlit dashboard over the scraped + analyzed data.

Run:
    streamlit run research/dashboard.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    APPS_CSV,
    DATA_DIR,
    FEATURE_REQUESTS_CSV,
    MONETIZATION_CSV,
    REVIEWS_CSV,
    THEMES_CSV,
)

FEATURES_CSV = DATA_DIR / "features.csv"
FEATURES_MATRIX_CSV = DATA_DIR / "features_matrix.csv"
FEATURES_SUMMARY_CSV = DATA_DIR / "features_summary.csv"

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
    feats = pd.read_csv(FEATURES_CSV) if FEATURES_CSV.exists() else pd.DataFrame()
    feats_matrix = pd.read_csv(FEATURES_MATRIX_CSV) if FEATURES_MATRIX_CSV.exists() else pd.DataFrame()
    feats_summary = pd.read_csv(FEATURES_SUMMARY_CSV) if FEATURES_SUMMARY_CSV.exists() else pd.DataFrame()
    return apps, reviews, themes, mon, fr, feats, feats_matrix, feats_summary


apps, reviews, themes, monetization, feature_requests, features, features_matrix, features_summary = load()

# ---------- Column configs (wide text columns, clickable cells expand) ----------
REVIEW_COLS = {
    "content": st.column_config.TextColumn("review", width="large", help="Full review text — click the cell to expand in a modal."),
    "full_text": st.column_config.TextColumn("full text", width="large"),
    "request_snippet": st.column_config.TextColumn("request", width="large", help="The sentence in the review that looks like a feature request."),
    "title": st.column_config.TextColumn("title", width="medium"),
    "app_name": st.column_config.TextColumn("app", width="medium"),
    "description": st.column_config.TextColumn("description", width="large"),
    "iap_range": st.column_config.TextColumn("iap range", width="small"),
    "prices_mentioned": st.column_config.TextColumn("prices mentioned", width="medium"),
    "plan_keywords": st.column_config.TextColumn("plan keywords", width="medium"),
    "url": st.column_config.LinkColumn("store link", width="small"),
}


def show_df(df: pd.DataFrame, *, height: int = 520, key: str | None = None) -> None:
    """Render a dataframe with wide text columns + a companion 'Full review inspector'
    so users can read any cell end-to-end without truncation."""
    if df.empty:
        st.info("No rows for the current filters.")
        return
    col_cfg = {c: cfg for c, cfg in REVIEW_COLS.items() if c in df.columns}
    st.dataframe(
        df,
        column_config=col_cfg,
        hide_index=True,
        width="stretch",
        height=height,
    )

    # Inspector — pick any row, read the full text wrapped in a container.
    text_col = next((c for c in ("content", "full_text", "request_snippet", "description") if c in df.columns), None)
    if text_col is None:
        return
    with st.expander(f"🔍 Inspect a single row (full text, no truncation)", expanded=False):
        options = list(df.index)
        labels = []
        for i in options:
            row = df.loc[i]
            app = str(row.get("app_name", row.get("name", "")))[:40]
            snippet = str(row.get(text_col, ""))[:60].replace("\n", " ")
            rating = row.get("rating", "")
            labels.append(f"#{i} — {app} — ★{rating} — {snippet}…")
        pick = st.selectbox("Row", options, format_func=lambda i: labels[options.index(i)], key=f"pick_{key or text_col}")
        row = df.loc[pick]
        meta_cols = [c for c in ("app_name", "store", "rating", "date", "user") if c in df.columns]
        cols = st.columns(len(meta_cols)) if meta_cols else []
        for c, col in zip(meta_cols, cols):
            col.metric(c, str(row[c])[:40])
        st.markdown("**Full text**")
        st.text_area(
            label="review",
            value=str(row.get(text_col, "")),
            height=280,
            label_visibility="collapsed",
            key=f"ta_{key or text_col}_{pick}",
        )


st.title("Quit-Smoking / Vaping App Landscape — India")
st.caption("Scraped from Play Store (India locale). 1–2★ reviews only. Built to spot what existing apps get wrong.")

# ---------- Sidebar filters ----------
with st.sidebar:
    st.header("Filters")
    stores = st.multiselect("Store", ["play", "appstore"], default=["play", "appstore"])
    india_only = st.checkbox(
        "India-signal reviews only",
        value=False,
        help="Reviews mentioning India, Indian cities, rupees, regional languages, bidi/paan/gutkha, etc.",
    )
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
    return out.reset_index(drop=True)


f_reviews = _filter(reviews)
f_themes = _filter(themes)
f_fr = _filter(feature_requests)

tabs = st.tabs([
    "Overview",
    "Features",
    "Strategy",
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
        st.plotly_chart(fig, width="stretch")

    st.subheader("Rating distribution across discovered apps")
    if not apps.empty:
        fig = px.histogram(apps, x="rating", color="store", nbins=20)
        st.plotly_chart(fig, width="stretch")

# ---------- Features (NEW) ----------
with tabs[1]:
    st.subheader("What features are competitor apps offering?")
    st.caption(
        "Detected from each app's Play Store description against a taxonomy of "
        f"~{0 if features_summary.empty else features_summary['feature'].nunique()} canonical features. "
        "Use this to spot table-stakes (everyone has it) vs. differentiation opportunities (almost no one has it)."
    )

    if features_summary.empty or features_matrix.empty:
        st.info("Run `extract_features.py` to populate this tab.")
    else:
        n_apps = len(features_matrix)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Apps analyzed", n_apps)
        c2.metric("Distinct features tracked", features_summary["feature"].nunique())
        c3.metric("Avg features per app", round(features_matrix["feature_count"].mean(), 1))
        c4.metric("Categories", features_summary["category"].nunique())

        # ---- Top features (table stakes) ----
        st.markdown("#### Table-stakes — features ≥30% of apps offer")
        st.caption("If we don't have these on day one, we'll feel incomplete.")
        ts = features_summary[features_summary["pct_apps"] >= 30].sort_values("pct_apps", ascending=True)
        if not ts.empty:
            fig = px.bar(
                ts, x="pct_apps", y="feature", color="category", orientation="h",
                hover_data=["apps_offering"], text="pct_apps",
            )
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig.update_layout(height=max(300, 28 * len(ts)), xaxis_title="% of apps offering")
            st.plotly_chart(fig, width="stretch")

        # ---- Differentiation opportunities ----
        st.markdown("#### Differentiation opportunities — features ≤10% of apps offer")
        st.caption("Cheap-to-build features that almost no competitor advertises. Strong wedge candidates.")
        opp = features_summary[features_summary["pct_apps"] <= 10].sort_values("pct_apps", ascending=True)
        if not opp.empty:
            fig = px.bar(
                opp, x="pct_apps", y="feature", color="category", orientation="h",
                hover_data=["apps_offering"], text="pct_apps",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(height=max(300, 28 * len(opp)), xaxis_title="% of apps offering")
            st.plotly_chart(fig, width="stretch")

        # ---- Features by category ----
        st.markdown("#### All features by category")
        cat_pick = st.selectbox(
            "Filter by category",
            ["(all)"] + sorted(features_summary["category"].unique().tolist()),
        )
        s = features_summary if cat_pick == "(all)" else features_summary[features_summary["category"] == cat_pick]
        s = s.sort_values("pct_apps", ascending=False)
        st.dataframe(
            s,
            column_config={
                "feature": st.column_config.TextColumn("feature", width="large"),
                "category": st.column_config.TextColumn("category", width="medium"),
                "apps_offering": st.column_config.NumberColumn("# apps"),
                "pct_apps": st.column_config.ProgressColumn(
                    "% of apps offering", format="%.1f%%", min_value=0, max_value=100,
                ),
            },
            hide_index=True, width="stretch", height=500,
        )

        # ---- Per-app drill-down ----
        st.markdown("#### Drill-down: which features does a specific app advertise?")
        app_options = sorted(features_matrix["app_name"].dropna().unique().tolist())
        app_pick = st.selectbox("App", app_options, key="feat_app_pick")
        if app_pick:
            evid = features[features["app_name"] == app_pick][
                ["category", "feature", "matched_phrase", "evidence", "url"]
            ].drop_duplicates(["category", "feature"]).reset_index(drop=True)
            row = features_matrix[features_matrix["app_name"] == app_pick].iloc[0]
            cA, cB, cC = st.columns(3)
            cA.metric("Features advertised", int(row["feature_count"]))
            cB.metric("Store rating", row.get("rating"))
            cC.metric("Ratings count", int(row.get("ratings_count") or 0))
            st.dataframe(
                evid,
                column_config={
                    "feature": st.column_config.TextColumn("feature", width="medium"),
                    "category": st.column_config.TextColumn("category", width="small"),
                    "matched_phrase": st.column_config.TextColumn("matched phrase", width="small"),
                    "evidence": st.column_config.TextColumn("evidence (description excerpt)", width="large"),
                    "url": st.column_config.LinkColumn("store"),
                },
                hide_index=True, width="stretch", height=520,
            )

        # ---- App × feature heatmap ----
        st.markdown("#### App × Feature heatmap")
        st.caption("Green = the app advertises this feature. White = no evidence in description.")
        feat_cols = [c for c in features_matrix.columns
                     if c not in {"store", "app_name", "rating", "ratings_count", "feature_count"}]
        if feat_cols:
            heat = features_matrix.set_index("app_name")[feat_cols]
            fig = px.imshow(
                heat,
                aspect="auto",
                color_continuous_scale=[[0, "#ffffff"], [1, "#16a34a"]],
            )
            fig.update_layout(height=max(500, 18 * len(heat)), xaxis_tickangle=-45)
            st.plotly_chart(fig, width="stretch")

# ---------- Strategy (NEW) ----------
with tabs[2]:
    st.header("🎯 Our Strategy — The Dopamine Wedge")
    st.markdown(
        "> **Every existing app fights nicotine. We fight dopamine.** "
        "Our 87-app feature scan + user interviews independently confirmed: **0 of 87 apps target the dopamine reward system.** "
        "That is our wedge."
    )

    st.markdown("### The thesis in one chart")
    st.caption(
        "Our planned features (highlighted) vs. what the market currently offers. Anything below 10% is a differentiation opportunity."
    )

    # White-space chart: our planned features highlighted against existing % adoption.
    OUR_FEATURES = [
        ("CRAVE button (variable-reward dopamine loop)", "—", 0.0, "core"),
        ("Real-money skill tournaments (Focus Arena)", "—", 0.0, "premium"),
        ("Cravings panic button", "Coping", 3.4, "core"),
        ("Distraction games / mini-games", "Coping", 2.3, "core"),
        ("Mood tracking", "Coping", 1.1, "core"),
        ("Trigger interception (proactive)", "Coping", 32.2, "core"),
        ("Voice-cloned AI coach", "—", 0.0, "premium"),
        ("Daily Dopamine Stack (sun/cold/protein/walk)", "—", 0.0, "core"),
        ("Branded supplement subscription", "—", 0.0, "premium"),
        ("Skin-in-the-game commitment bet", "—", 0.0, "premium"),
        ("Photo-aging time machine", "—", 0.0, "premium"),
        ("Lifetime purchase option", "Monetization", 2.3, "core"),
        ("Money-back guarantee", "Monetization", 2.3, "core"),
        ("Anonymous community high-fives", "Social", 3.4, "core"),
        ("Hindi / Indian language support", "UX", 4.6, "core"),
        ("Offline support", "UX", 2.3, "core"),
    ]
    import pandas as _pd
    plan_df = _pd.DataFrame(OUR_FEATURES, columns=["feature", "category", "competitor_pct", "tier"])
    fig = px.bar(
        plan_df.sort_values("competitor_pct"),
        x="competitor_pct", y="feature", color="tier", orientation="h",
        color_discrete_map={"core": "#16a34a", "premium": "#7c3aed"},
        text="competitor_pct",
        hover_data={"category": True, "competitor_pct": ":.1f"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=max(420, 32 * len(plan_df)),
        xaxis_title="% of competitor apps offering this today",
        yaxis_title="",
        legend_title="our tier",
    )
    fig.add_vline(x=10, line_dash="dot", line_color="#dc2626",
                  annotation_text="Differentiation cutoff (≤10%)", annotation_position="top")
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # ---- Three pillars ----
    st.markdown("### Three product layers")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("#### ⚡ Layer 1 — Acute craving")
        st.markdown(
            "**The CRAVE button.** When craving hits, deliver a *real* dopamine hit in 30–60 sec via "
            "variable reward — UPI cashback spins, scratch cards, breath-rhythm game, live high-fives, "
            "audio rewards. The randomness is the point: same loop slot machines and Instagram use, "
            "redirected to break the cigarette cycle."
        )
    with p2:
        st.markdown("#### 🧬 Layer 2 — Baseline repair")
        st.markdown(
            "**Daily Dopamine Stack.** 5-item morning protocol (sun, cold, protein, walk, sleep) + "
            "branded supplement subscription (Magnesium Glycinate, L-Theanine, L-Tyrosine). "
            "Clinical, not gamified — focused on receptors regrowing over 30–90 days."
        )
    with p3:
        st.markdown("#### ⏰ Layer 3 — Trigger interception")
        st.markdown(
            "**Pre-empt cravings.** User marks 3 trigger windows in onboarding (morning, work break, "
            "post-meal, stress). App **proactively** intercepts those moments with the CRAVE flow — "
            "alarm, Pomodoro pings, stress-detection nudges. We're in the moment, not waiting to be opened."
        )

    st.divider()

    # ---- Premium features (revenue) ----
    st.markdown("### 💰 Premium features — what people will pay for")
    st.caption("Each rated 1–10 on dopamine value, willingness-to-pay (Indian market), and defensibility.")

    PREMIUM = [
        ("Focus Arena — skill-money tournaments", 9, 10, 8, "₹10–₹50/entry, 15–25% rake"),
        ("The Stack — branded supplements", 6, 9, 7, "₹799/mo subscription"),
        ("Voice-cloned AI coach (loved one's voice)", 10, 8, 9, "₹499 + ₹99/mo"),
        ("Quit Pact — commitment bet (loss aversion)", 8, 8, 6, "10% rake on each pact"),
        ("NRT-as-a-service — telehealth + gum delivery", 5, 9, 8, "₹1,499/mo"),
        ("Crave Band — HRV wearable partnership", 7, 7, 10, "₹2,999 + ₹99/mo"),
        ("Photo-aging time machine", 6, 6, 4, "₹199 / refresh"),
        ("Cohort betting pool — 10-friend pact", 8, 7, 5, "10% rake on pot"),
        ("Crave-line — ₹99 therapist hotline", 7, 6, 6, "₹49 take-rate per call"),
        ("Insurance premium discount partnership", 4, 8, 9, "₹500–₹2,000 per converted policy"),
    ]
    prem_df = _pd.DataFrame(PREMIUM, columns=["feature", "dopamine", "willingness_to_pay", "moat", "model"])
    prem_df["score"] = prem_df["dopamine"] + prem_df["willingness_to_pay"] + prem_df["moat"]
    prem_df = prem_df.sort_values("score", ascending=False).reset_index(drop=True)

    st.dataframe(
        prem_df,
        column_config={
            "feature": st.column_config.TextColumn("feature", width="large"),
            "dopamine": st.column_config.ProgressColumn("🧠 dopamine value", min_value=0, max_value=10, format="%d"),
            "willingness_to_pay": st.column_config.ProgressColumn("💰 willingness to pay", min_value=0, max_value=10, format="%d"),
            "moat": st.column_config.ProgressColumn("🛡️ moat", min_value=0, max_value=10, format="%d"),
            "model": st.column_config.TextColumn("revenue model", width="medium"),
            "score": st.column_config.NumberColumn("total", format="%d"),
        },
        hide_index=True, width="stretch", height=420,
    )

    st.markdown("**Top 3 to build first** (after the free CRAVE button is shipped):")
    st.markdown(
        "1. 🥇 **Focus Arena** — highest dopamine + WTP, fits Indian gaming culture (Dream11/MPL audience), defensible via the per-user game-response dataset\n"
        "2. 🥈 **The Stack** — recurring revenue, ~70% margin, the only feature addressing *baseline dopamine repair*\n"
        "3. 🥉 **Voice-cloned coach** — most emotionally sticky, off-the-shelf tech, no competitor has it"
    )

    st.divider()

    # ---- Pricing ladder ----
    st.markdown("### 🪜 Recommended pricing ladder")
    LADDER = [
        ("Free", "₹0", "CRAVE button (basic), Daily Dopamine Stack, 1 trigger", "Day 0–7"),
        ("Pro Pack (one-time)", "₹999 lifetime", "Higher cashback, all triggers, all reward types, scratch cards", "Day 7–30"),
        ("The Stack", "₹799/mo", "Branded supplements + adherence tracking", "Day 14+"),
        ("Focus Arena", "₹10–50/entry", "Real-money skill tournaments", "Daily power users"),
        ("Quit Pact", "₹500–₹5,000 stake", "Commitment bet escrow", "Day 14+"),
        ("Voice Coach", "₹499 + ₹99/mo", "Loved-one's voice cloned", "Parents, partners"),
        ("NRT-as-a-service", "₹1,499/mo", "Telehealth + gum/lozenge delivery", "Heavy smokers"),
        ("Crave Band", "₹2,999 + ₹99/mo", "Wearable + HRV craving detection", "Serious / tech-forward"),
    ]
    st.dataframe(
        _pd.DataFrame(LADDER, columns=["tier", "price", "includes", "target user"]),
        hide_index=True, width="stretch",
        column_config={"includes": st.column_config.TextColumn("includes", width="large")},
    )

    st.divider()

    # ---- What we explicitly DON'T build ----
    st.markdown("### 🚫 What we explicitly DON'T build")
    st.markdown("""
    Based on the 87-app scan + user interviews, we cut features competitors waste resources on:

    - ❌ **"You saved ₹4,200" counter** — interview literally says "they don't care"
    - ❌ **Days smoke-free as headline metric** — too easy to break, too punishing
    - ❌ **Generic motivational quotes** — zero dopamine value
    - ❌ **Long article library** — no one reads in a craving moment
    - ❌ **Hypnosis audio** — folk remedy, no evidence
    - ❌ **Subscription-only model** — 19.5% of all bad reviews are paywall complaints
    - ❌ **Forum / community as primary feature** — moderation hell, low value, dilutes the dopamine focus
    """)

    st.divider()

    # ---- Crave Vault ----
    st.markdown("### 🪙 The Crave Vault — deposit instead of smoke")
    st.markdown(
        "Each craving → user taps to deposit the cost of a cigarette into a real savings vehicle "
        "(digital gold, liquid MF, RD, or charity). **We never custody the money** — UPI Autopay "
        "sweeps it directly into the user's own product. Same playbook as Jar (₹3,500 Cr AUM in 3 years), "
        "applied to addiction. **No PPI license needed for v1.**"
    )

    v1, v2, v3 = st.columns(3)
    v1.metric("Competitor apps offering this", "0 / 87")
    v2.metric("Closest analog (Jar) AUM", "₹3,500 Cr")
    v3.metric("RBI license needed", "None (phase 1)")

    st.markdown("**Vault destinations** (user picks during onboarding — we facilitate, partners custody):")
    VAULTS = [
        ("🪙 Digital Gold", "Augmont / MMTC-PAMP / SafeGold", "~10% annual return", "Highest emotional resonance for Indian users"),
        ("💰 Liquid Mutual Fund", "ICICI Prudential / Smallcase / Groww", "~7% annual return", "Instant redemption, tax efficient"),
        ("🏦 Recurring Deposit", "Small finance bank partner", "~6% fixed", "Lowest perceived risk"),
        ("💸 Charity", "Give.do / GiveIndia", "n/a — pure giving", "Spiritual / commitment angle"),
        ("🎯 Quit Pact Escrow", "Internal", "+5% bonus", "Relapse → goes to anti-charity (premium)"),
    ]
    st.dataframe(
        _pd.DataFrame(VAULTS, columns=["destination", "partner", "return", "why this option"]),
        hide_index=True, width="stretch",
        column_config={"why this option": st.column_config.TextColumn("why this option", width="large")},
    )

    st.markdown("**Lock mechanic — the loss-aversion moat:**")
    LOCKS = [
        ("Flex (no lock)", "0%", "Anytime, free withdrawal"),
        ("30-day commit", "+1% bonus from us", "Penalty if early: ₹50 or 5%"),
        ("90-day commit", "+3% bonus", "Locked till date"),
        ("Quit Pact mode", "+5% bonus", "Relapse → vault goes to charity"),
    ]
    st.dataframe(
        _pd.DataFrame(LOCKS, columns=["lock duration", "bonus", "withdrawal rules"]),
        hide_index=True, width="stretch",
    )

    st.markdown("**Revenue at 100k depositors (₹500/mo avg sweep):**")
    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Monthly inflow", "₹5 Cr", help="Money flowing through to partners")
    rcol2.metric("Annual AUM accrued", "~₹60 Cr")
    rcol3.metric("Trail commission /yr", "₹30–60L", help="MF distribution + gold spread")

    st.info(
        "💡 **Why this is the gravitational center.** Every other feature feeds the vault: CRAVE → deposit, "
        "Daily Stack completion → bonus deposit, Focus Arena winnings → auto-deposit option, Quit Pact → vault escrow. "
        "The vault makes every other feature stickier."
    )

    st.divider()
    st.markdown(
        "📄 **Full spec docs in the repo:** "
        "[DOPAMINE_STRATEGY.md](https://github.com/abhiirathi/quit-smoking-research/blob/main/DOPAMINE_STRATEGY.md) · "
        "[PREMIUM_DOPAMINE_FEATURES.md](https://github.com/abhiirathi/quit-smoking-research/blob/main/PREMIUM_DOPAMINE_FEATURES.md) · "
        "[CRAVE_VAULT.md](https://github.com/abhiirathi/quit-smoking-research/blob/main/CRAVE_VAULT.md)"
    )

# ---------- Complaint themes ----------
with tabs[3]:
    st.subheader("Top complaint themes (all filtered reviews)")
    if not f_themes.empty:
        top = (
            f_themes.groupby("theme").size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        fig = px.bar(top, x="count", y="theme", orientation="h")
        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")

        st.subheader("Browse reviews by theme")
        theme_pick = st.selectbox("Theme", sorted(f_themes["theme"].unique()))
        sub = f_themes[f_themes["theme"] == theme_pick].reset_index(drop=True)
        show_df(
            sub[[c for c in ["app_name", "store", "rating", "date", "content"] if c in sub.columns]],
            key=f"themes_{theme_pick}",
        )

# ---------- Feature requests ----------
with tabs[4]:
    st.subheader("Feature requests extracted from 1–2★ reviews")
    if not f_fr.empty:
        per_app = (
            f_fr.groupby("app_name").size().reset_index(name="requests")
            .sort_values("requests", ascending=False).head(25)
        )
        fig = px.bar(per_app, x="requests", y="app_name", orientation="h")
        fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")

        show_df(
            f_fr[[c for c in ["app_name", "store", "rating", "request_snippet", "full_text", "india_signal", "date"] if c in f_fr.columns]],
            key="fr_table",
            height=600,
        )
    else:
        st.info("No feature requests matched the current filters.")

# ---------- Monetization ----------
with tabs[5]:
    st.subheader("Monetization across competitor apps")
    if not monetization.empty:
        mon = monetization.copy()
        if stores:
            mon = mon[mon["store"].isin(stores)]
        mon = mon.reset_index(drop=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Free apps", int((mon["free"] == True).sum()))  # noqa: E712
        c2.metric("With in-app purchases", int((mon["in_app_purchases"] == True).sum()))  # noqa: E712
        c3.metric("Mention subscription in desc.", int((mon["mentions_subscription"] == True).sum()))  # noqa: E712

        st.markdown("**Per-app monetization table** — click any cell to expand the full value.")
        show_cols = [
            "store", "name", "developer", "rating", "ratings_count",
            "free", "price", "contains_ads", "in_app_purchases", "iap_range",
            "prices_mentioned", "plan_keywords", "mentions_subscription",
            "mentions_trial", "mentions_lifetime", "url",
        ]
        show_cols = [c for c in show_cols if c in mon.columns]
        show_df(mon[show_cols], key="mon_table", height=620)

        st.markdown("**Plan keyword frequency across descriptions**")
        kw_series = mon["plan_keywords"].fillna("").str.split("; ").explode()
        kw_series = kw_series[kw_series.str.len() > 0]
        if len(kw_series):
            kc = kw_series.value_counts().reset_index()
            kc.columns = ["keyword", "count"]
            fig = px.bar(kc, x="count", y="keyword", orientation="h")
            fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, width="stretch")

# ---------- India lens ----------
with tabs[6]:
    st.subheader("India-signal reviews")
    st.caption("Reviews mentioning India-specific words (cities, rupees, regional languages, bidi/paan/gutkha, etc.).")
    india = reviews[reviews.get("india_signal") == True].reset_index(drop=True) if not reviews.empty else pd.DataFrame()  # noqa: E712
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
            st.plotly_chart(fig, width="stretch")

        show_df(
            india[[c for c in ["app_name", "store", "rating", "date", "content"] if c in india.columns]],
            key="india_table",
            height=620,
        )
    else:
        st.info("No India-signal reviews yet. Run the pipeline first.")

# ---------- Raw reviews ----------
with tabs[7]:
    st.subheader("Raw 1–2★ reviews")
    if not f_reviews.empty:
        search = st.text_input("Search within review text")
        data = f_reviews
        if search:
            data = data[data["content"].fillna("").str.contains(search, case=False)]
        data = data.reset_index(drop=True)
        show_df(
            data[[c for c in ["app_name", "store", "rating", "date", "content"] if c in data.columns]],
            key="raw_table",
            height=720,
        )
        st.download_button(
            "Download filtered reviews as CSV",
            data.to_csv(index=False).encode(),
            "reviews_filtered.csv",
        )
