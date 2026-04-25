"""
Extract advertised features from each competitor app's description.

Builds a taxonomy of ~60 canonical features that quit-smoking/vaping apps
typically offer, then scans each app's description for evidence of each.

Outputs:
  data/features.csv         - long format: one row per (app, feature, evidence)
  data/features_matrix.csv  - wide: rows=apps, cols=features, values=0/1
  data/features_summary.csv - feature -> apps_with_count, % of apps offering it
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

from config import APPS_CSV, DATA_DIR

# ---- Canonical feature taxonomy ---------------------------------------------
# (category, feature_name, regex patterns / keywords)
# Each pattern is matched case-insensitively against the description.

FEATURES: list[tuple[str, str, list[str]]] = [
    # ---------- Tracking & counters ----------
    ("Tracking", "Cigarettes avoided counter",
     [r"cigarettes? (?:not )?(?:smoked|avoided|saved)", r"smoke[- ]?free counter",
      r"how many cigarettes", r"counter", r"stick(?:s)? avoided"]),
    ("Tracking", "Money saved tracker",
     [r"money saved", r"save(?:d)? money", r"savings? tracker", r"how much money",
      r"financial savings", r"save (?:up to )?\$"]),
    ("Tracking", "Time since last cigarette",
     [r"time since (?:your )?last", r"smoke[- ]?free (?:for|since|time)",
      r"days? (?:smoke[- ]?free|without)", r"clean time", r"streak"]),
    ("Tracking", "Life regained / time saved",
     [r"life regained", r"life expectancy", r"years? (?:added|gained)",
      r"life saved", r"time gained"]),
    ("Tracking", "Craving logger",
     [r"log(?:ging)? (?:cravings|urges)", r"track cravings",
      r"craving (?:diary|log|tracker|journal)"]),
    ("Tracking", "Slip / relapse logger",
     [r"slip(?:s|ped)?", r"relapse", r"reset (?:the )?counter",
      r"log a (?:cigarette|smoke)"]),

    # ---------- Health & body ----------
    ("Health", "Health milestones / recovery timeline",
     [r"health (?:milestones|benefits|improvements|recovery)",
      r"body (?:recovery|healing|repairs)", r"lung (?:recovery|capacity|healing)",
      r"heart rate (?:normalizes|recovery)", r"medical timeline",
      r"every (?:hour|day|week|month)"]),
    ("Health", "Lung capacity / breath tracking",
     [r"lung capacity", r"breath(?:ing)? test", r"lung (?:health|function)",
      r"oxygen level"]),
    ("Health", "Apple Health integration",
     [r"apple health", r"healthkit"]),
    ("Health", "Google Fit / Health Connect integration",
     [r"google fit", r"health connect"]),
    ("Health", "Wearable / smartwatch support",
     [r"apple watch", r"wearos", r"wear os", r"smartwatch", r"fitbit"]),

    # ---------- Behavioral / coping tools ----------
    ("Coping", "Cravings panic button",
     [r"panic button", r"emergency (?:button|help)", r"craving sos",
      r"i need help", r"crav(?:ing|e) right now"]),
    ("Coping", "Urge surfing / craving timer",
     [r"urge surf", r"craving (?:timer|countdown)", r"ride (?:the|out) (?:the )?craving",
      r"crave (?:lasts|fades)"]),
    ("Coping", "Breathing exercises",
     [r"breathing exercise", r"breathe (?:deep|in|with)", r"box breathing",
      r"deep breath", r"pranayama"]),
    ("Coping", "Meditation / mindfulness",
     [r"meditation", r"mindful(?:ness)?", r"guided meditation"]),
    ("Coping", "Distraction games / mini-games",
     [r"mini[- ]?game", r"distraction game", r"play (?:a |the )?game",
      r"puzzle game"]),
    ("Coping", "Journal / diary",
     [r"\bjournal\b", r"\bdiary\b", r"daily reflection", r"write down"]),
    ("Coping", "Mood tracking",
     [r"mood track", r"track your mood", r"mood log", r"emotion track"]),
    ("Coping", "Trigger identification",
     [r"\btrigger(?:s)?\b", r"identify (?:your )?triggers",
      r"avoid (?:your )?triggers"]),

    # ---------- Coaching & program ----------
    ("Coaching", "AI coach / chatbot",
     [r"\bai (?:coach|companion|assistant|chatbot)?\b", r"chatbot",
      r"virtual coach", r"smart assistant"]),
    ("Coaching", "Human coach / therapist",
     [r"human (?:coach|therapist)", r"certified (?:coach|counselor)",
      r"1[- ]?on[- ]?1 coach", r"personal coach", r"licensed therapist"]),
    ("Coaching", "Personalized quit plan",
     [r"personali[sz]ed (?:plan|program|quit)", r"custom (?:plan|program)",
      r"tailored (?:plan|program)", r"your own plan"]),
    ("Coaching", "Daily missions / tasks",
     [r"daily (?:missions?|tasks?|challenges?)", r"daily lesson",
      r"today's (?:task|mission|lesson)"]),
    ("Coaching", "Hypnosis / hypnotherapy audio",
     [r"hypnosis", r"hypnotherapy", r"hypnotic"]),
    ("Coaching", "CBT (cognitive behavioral therapy)",
     [r"\bcbt\b", r"cognitive behavioral", r"behavioral therapy"]),
    ("Coaching", "NLP techniques",
     [r"\bnlp\b", r"neuro[- ]?linguistic"]),
    ("Coaching", "Allen Carr / Easy Way method",
     [r"allen carr", r"easy way"]),

    # ---------- Education ----------
    ("Education", "Articles / lessons / tips",
     [r"\barticles?\b", r"\blessons?\b", r"daily tips", r"\btips and tricks\b",
      r"read more"]),
    ("Education", "Videos",
     [r"\bvideos?\b", r"video (?:lessons?|courses?)", r"watch (?:our|a) video"]),
    ("Education", "Audio / podcast",
     [r"\baudio\b", r"\bpodcast", r"audio (?:lessons?|stories)"]),
    ("Education", "Quizzes / assessments",
     [r"\bquiz(?:zes)?\b", r"\bassessment\b", r"questionnaire", r"diagnostic test"]),

    # ---------- Social & community ----------
    ("Social", "Community / forum",
     [r"\bcommunity\b", r"\bforum\b", r"discussion (?:board|group)",
      r"connect with others"]),
    ("Social", "Buddy / accountability partner",
     [r"\bbuddy\b", r"accountability (?:partner|buddy)", r"quit partner",
      r"pair up"]),
    ("Social", "Success stories / testimonials",
     [r"success stor(?:ies|y)", r"testimonial", r"real stories"]),
    ("Social", "Anonymous / pseudonymous posting",
     [r"\banonymous(?:ly)?\b", r"\bpseudonym\b"]),
    ("Social", "Group chat",
     [r"\bgroup chat\b", r"\bchat rooms?\b"]),

    # ---------- Gamification ----------
    ("Gamification", "Streaks",
     [r"\bstreak(?:s)?\b", r"day streak", r"keep your streak"]),
    ("Gamification", "Achievements / badges",
     [r"\bachievement(?:s)?\b", r"\bbadges?\b", r"\bmedal(?:s)?\b",
      r"\btrophie?(?:s)?\b"]),
    ("Gamification", "Levels / XP",
     [r"\blevel up\b", r"\bxp\b", r"experience points"]),
    ("Gamification", "Challenges",
     [r"\bchallenges?\b", r"weekly challenge", r"30[- ]?day challenge"]),
    ("Gamification", "Rewards / points",
     [r"\brewards?\b", r"\bpoints\b(?: system)?", r"redeem"]),

    # ---------- Reminders & motivation ----------
    ("Engagement", "Smart notifications / reminders",
     [r"\breminders?\b", r"\bnotifications?\b", r"smart (?:reminders?|notifs?)",
      r"push notification"]),
    ("Engagement", "Motivational quotes",
     [r"motivational quote", r"daily (?:quote|inspiration|motivation)",
      r"inspiring quote"]),
    ("Engagement", "Daily check-in",
     [r"daily check[- ]?in", r"check in (?:every )?day", r"morning check"]),

    # ---------- Vaping / nicotine specifics ----------
    ("Nicotine", "Vaping support",
     [r"\bvap(?:e|ing)\b", r"\be[- ]?cigarettes?\b", r"juul", r"\bpods?\b"]),
    ("Nicotine", "Nicotine reduction / step-down",
     [r"nicotine (?:reduction|taper|step[- ]?down|level)",
      r"gradual(?:ly)? (?:quit|reduce)", r"reduce nicotine",
      r"taper(?:ing)?"]),
    ("Nicotine", "NRT (patches / gum) tracking",
     [r"\bnrt\b", r"nicotine replacement", r"\bpatches?\b", r"\bgum\b",
      r"\blozenges?\b", r"\binhaler\b"]),
    ("Nicotine", "Cold turkey method",
     [r"cold turkey", r"quit (?:all )?at once"]),

    # ---------- Other substances ----------
    ("Other substances", "Alcohol support",
     [r"\balcohol\b", r"\bdrinking\b", r"\bsobriety\b"]),
    ("Other substances", "Cannabis / weed support",
     [r"\bcannabis\b", r"\bmarijuana\b", r"\bweed\b", r"\bthc\b"]),
    ("Other substances", "Caffeine / sugar / general habit",
     [r"\bcaffeine\b", r"\bsugar\b", r"any (?:bad )?habit"]),

    # ---------- Privacy & data ----------
    ("Privacy", "Data export / backup",
     [r"export (?:your )?data", r"\bbackup\b", r"data backup",
      r"download your data"]),
    ("Privacy", "Cloud sync",
     [r"\bcloud sync\b", r"sync (?:across )?devices", r"icloud sync"]),
    ("Privacy", "End-to-end / private",
     [r"end[- ]?to[- ]?end", r"private(?:ly)?", r"no (?:tracking|ads)"]),

    # ---------- UX / platform ----------
    ("UX", "Home screen widget",
     [r"\bwidget(?:s)?\b", r"home screen widget", r"lock screen widget"]),
    ("UX", "Dark mode",
     [r"\bdark mode\b", r"\bdark theme\b"]),
    ("UX", "Multi-language",
     [r"multi[- ]?language", r"available in \d+ languages",
      r"available in (?:english|spanish|french|german|hindi|arabic)"]),
    ("UX", "Hindi / Indian language support",
     [r"\bhindi\b", r"\bmarathi\b", r"\btamil\b", r"\btelugu\b",
      r"\bbengali\b", r"\bgujarati\b", r"\bkannada\b", r"\bmalayalam\b",
      r"\bpunjabi\b"]),
    ("UX", "Offline support",
     [r"\boffline\b", r"works without internet", r"no internet (?:required|needed)"]),

    # ---------- Monetization ----------
    ("Monetization", "Free tier",
     [r"\bfree (?:tier|version|forever|to use)\b", r"100% free", r"completely free"]),
    ("Monetization", "Free trial",
     [r"free trial", r"\d+[- ]?day trial", r"try (?:it )?free"]),
    ("Monetization", "Lifetime purchase option",
     [r"lifetime (?:access|purchase|plan|deal)", r"one[- ]?time (?:purchase|payment)",
      r"pay once"]),
    ("Monetization", "Subscription",
     [r"\bsubscription\b", r"\bsubscribe\b", r"monthly plan", r"yearly plan",
      r"\b/month\b", r"\b/year\b"]),
    ("Monetization", "Money-back guarantee",
     [r"money[- ]?back guarantee", r"refund (?:guarantee|policy)"]),
]


def detect_features(description: str) -> list[dict[str, Any]]:
    text = (description or "").replace("\n", " ")
    if not text.strip():
        return []
    out: list[dict[str, Any]] = []
    for category, name, patterns in FEATURES:
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                # Pull a small evidence snippet around the match.
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 80)
                snippet = text[start:end].strip()
                out.append({
                    "category": category,
                    "feature": name,
                    "matched_phrase": m.group(0),
                    "evidence": snippet,
                })
                break  # one hit per feature is enough
    return out


def main() -> None:
    if not APPS_CSV.exists():
        print("apps.csv missing — run scrape_apps.py first.")
        return

    apps = pd.read_csv(APPS_CSV)
    long_rows: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []

    for _, app in apps.iterrows():
        feats = detect_features(str(app.get("description") or ""))
        feat_names = {f["feature"] for f in feats}
        for f in feats:
            long_rows.append({
                "store": app.get("store"),
                "app_id": app.get("app_id"),
                "app_name": app.get("name"),
                "developer": app.get("developer"),
                "rating": app.get("rating"),
                "ratings_count": app.get("ratings_count"),
                "url": app.get("url"),
                **f,
            })
        matrix_rows.append({
            "store": app.get("store"),
            "app_name": app.get("name"),
            "rating": app.get("rating"),
            "ratings_count": app.get("ratings_count"),
            "feature_count": len(feat_names),
            **{name: int(name in feat_names) for _, name, _ in FEATURES},
        })

    long_df = pd.DataFrame(long_rows)
    matrix_df = pd.DataFrame(matrix_rows)

    long_df.to_csv(DATA_DIR / "features.csv", index=False)
    matrix_df.to_csv(DATA_DIR / "features_matrix.csv", index=False)

    # Summary: how many apps offer each feature.
    if not long_df.empty:
        per_feat = long_df.drop_duplicates(["app_name", "feature"])
        summary = (
            per_feat.groupby(["category", "feature"]).size()
            .reset_index(name="apps_offering")
        )
        summary["pct_apps"] = (summary["apps_offering"] / len(apps) * 100).round(1)
        summary = summary.sort_values(
            ["category", "apps_offering"], ascending=[True, False]
        )
        summary.to_csv(DATA_DIR / "features_summary.csv", index=False)
    else:
        pd.DataFrame(columns=["category", "feature", "apps_offering", "pct_apps"]) \
            .to_csv(DATA_DIR / "features_summary.csv", index=False)

    print(f"wrote {DATA_DIR / 'features.csv'} ({len(long_df)} rows)")
    print(f"wrote {DATA_DIR / 'features_matrix.csv'} ({len(matrix_df)} apps)")
    print(f"wrote {DATA_DIR / 'features_summary.csv'}")


if __name__ == "__main__":
    main()
