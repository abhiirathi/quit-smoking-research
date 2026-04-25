# The Dopamine Wedge — Product Strategy

> "They are something that they don't care about if they have the urge to smoke. They don't use these apps because they don't work for them." — user interview

## The thesis in one sentence

**Every existing quit-smoking app fights nicotine. We fight dopamine.** Nicotine is the chemical, dopamine is the addiction. Solve dopamine and the cigarette becomes pointless.

## Why every competitor fails

Our competitive scan of 87 apps mapped 63 features across 11 categories. Distribution:

| Category | What they offer | Dopamine relevance |
|---|---|---|
| Tracking | Money saved, days smoke-free, cigarettes avoided | ❌ Counters don't release dopamine |
| Gamification | Streaks, badges, levels | ❌ Visual rewards, not chemical |
| Coping | Breathing, meditation, journaling | ❌ Calms parasympathetic — wrong system |
| Education | Articles, videos, tips | ❌ Information ≠ neurotransmitter |
| Coaching | AI coach, plans | ❌ Words don't substitute reward |

**0 of 87 apps target the dopamine reward system directly.** This is the white space.

## The interview gave us the architecture

From the notes, three timescales matter:

1. **The 5-minute craving moment** — brain is screaming for a dopamine hit, *right now*
2. **The 30-day withdrawal window** — baseline dopamine is depleted, brain feels flat, irritated, bored
3. **The 90-day rewiring window** — receptors regrow, new reward pathways consolidate

Existing apps treat (1) as a willpower problem and ignore (2) and (3) entirely. We build for all three.

---

## What we build — 3-layer product

### Layer 1 — The Dopamine Loop (acute craving)

**The single most important feature in the app.** When craving hits, replace the cigarette dopamine with a *real* dopamine hit from a non-harmful source. The mechanic is variable-reward (the same loop slot machines, Instagram, and Tinder use — proven to be dopaminergic).

**MVP version:**

A giant **CRAVE** button on the home screen and as a home/lock-screen widget. One tap delivers a randomized 30–60 second rewarding experience:

| Reward type | Why it gives a dopamine hit | Cost to us |
|---|---|---|
| **Spin the wheel — real ₹ cashback** (₹1–₹50, ~80% land on ₹1–2, rare ₹50) | Variable monetary reward = strongest known artificial dopamine trigger | ₹3–5 avg per craving × frequency cap |
| **Scratch card** — reveal a tip, a quote, or a real prize | Variable reveal mechanic is what makes scratch cards addictive | ~free |
| **Tap rhythm "phantom puff"** — 30-sec breath + tap mini-game; high score increases the streak shield | Rhythm + score progression = micro-dopamine | free |
| **Live "high-five"** — anonymous user who's also resisting right now sends a 👊 | Social validation = oxytocin + dopamine | free, peer-driven |
| **Audio reward** — 60-sec curated song / standup clip / interesting fact | Predictable hit but novelty is dopaminergic | content licensing |
| **Streak-saver fireworks** — visceral celebration when craving passes | Loss-aversion + reward burst | free |

**The randomness is the point.** A predictable reward (you always get ₹2) becomes boring in 2 days. A variable reward (you might get ₹50 this time) is what addicts the brain. We hijack the same mechanism nicotine uses.

**Brutal-honesty companion**: after the reward, the app says: *"That dopamine bump you just got was real. The cigarette gives you a similar one. We just gave it to you for free, in 60 seconds, with no lung damage. Do this every craving and your brain learns the substitute."*

### Layer 2 — Dopamine Repair Protocol (30-day baseline reset)

Address the underlying dopamine deficit so the user *needs* the cigarette less. Based on functional-nutrition research (Dr. Eric Berg / Huberman Lab — both India-popular).

A **daily dopamine-stack checklist** the user can ✓ off each morning. Not gamified; clinical:

- ☐ Magnesium Glycinate 200–400mg (evening) — *we link to Amazon, affiliate revenue*
- ☐ L-Theanine 100–200mg (morning) — *Amazon affiliate*
- ☐ 10 min direct sunlight before 9 AM — *raises dopamine baseline (Huberman protocol)*
- ☐ Cold water face splash or 30-sec cold shower — *2–3× dopamine baseline elevation, sustained*
- ☐ Protein-forward breakfast (tyrosine = dopamine precursor) — *food-list explicit*
- ☐ 30-min walk outdoors — *aerobic exercise restores receptor sensitivity*
- ☐ Phone in another room after 10 PM — *sleep is when receptors regrow*
- ☐ No short-form video until afternoon — *cuts competing dopamine sources*

Show this as a calendar of dots. The dots don't track *days smoke-free* (which competitors do). They track *days you ran the protocol*. Different metric, different psychology — focuses on what's controllable.

**Education layer**: 60-second daily explainer (not articles — videos in Hindi/English) on *why* each step works. "Why cold water raises dopamine for 4 hours." "Why magnesium calms nicotine cravings."

### Layer 3 — Trigger Interception (the conditioned-habit loop)

The interview lists clear trigger windows:
- Morning wake-up
- Work focus break
- Post-meal
- Stress/frustration spike
- Boredom

User marks their personal triggers in onboarding. The app **proactively intercepts** them:

- **Morning trigger**: alarm doubles as the app — wake-up screen is the dopamine spin (tied to a 60-sec sun-exposure prompt)
- **Work focus trigger**: optional Pomodoro mode — every 25 min the app prompts a 90-sec dopamine reset (cold splash + spin) instead of a cigarette break
- **Stress trigger**: phone detects stress patterns (HRV via wearable, or self-logged) → push notification offers a Layer-1 reward
- **Boredom trigger**: time-based — if the user opens Instagram/YouTube during a logged craving window, an overlay nudges them to do the 60-sec dopamine loop first

This turns the app from "open it when you remember" to "the app is in your trigger moments."

---

## What we explicitly do NOT build

Based on the interview + our complaint scan, we cut features that competitors waste resources on:

- ❌ "You saved ₹4,200" — money saved counters are user #1 non-motivator per the interview
- ❌ Generic motivational quotes — no dopamine value
- ❌ Days smoke-free as the primary metric — too easy to break, too painful when broken, doesn't reflect the user's *effort*
- ❌ Long article library — people don't read in a craving
- ❌ Forum/community as a primary feature — only as Layer-1 high-five (small, fast)
- ❌ Hypnosis audio — folk-remedy, no evidence
- ❌ Nicotine-only patches/NRT focus — addresses the chemical, not the wiring

---

## Monetization that aligns with the strategy

The cashback reward + supplement affiliate model gives us **two revenue paths that actively help the user**, vs. competitor subscriptions that feel like extortion (35% of bad-review complaints):

1. **Affiliate revenue on Magnesium Glycinate, L-Theanine, etc.** via Amazon India — user buys what helps them, we earn 4–8%, no subscription friction
2. **One-time "Pro Pack" — ₹999 lifetime** unlocks higher cashback caps, premium audio rewards, wearable integration. **Lifetime, not subscription** (only 2.3% of competitors offer this — direct response to the #1 complaint)
3. **Optional ₹49/month "Sponsor a quitter" tier** — older quit-success users sponsor newer ones, get social-status badge in the high-five feature

No paywall in the first 7 days. The Layer-1 dopamine loop is the addictive feature — let the user get hooked on the substitute *before* asking for money.

---

## Competitive moat

| Asset | How it compounds |
|---|---|
| **Per-user reward-response data** | We learn which dopamine reward (cash/sound/social/game) works best per user → ML personalization gets better with scale → competitors can't replicate without years of data |
| **Indian payment rails (UPI cashback)** | Foreign apps can't do micro-cashback in India easily; we can |
| **Dopamine-repair content library in Hindi + English** | Educational moat — 100+ 60-sec videos, all original |
| **Trigger detection model** | The longer a user is in-app, the better we predict their personal craving windows |

---

## What we ship in v1 (next 90 days)

Pick the smallest version that proves the core thesis:

1. **CRAVE button** with 3 reward types: Spin (cashback ₹1-10 capped), Scratch card, Phantom Puff breath game
2. **Daily Dopamine Stack** — 5-item checklist, no supplements yet, just the free behaviors (sun / cold / walk / protein / sleep)
3. **Trigger onboarding** — pick your 3 triggers; we send 1 push per trigger window with a CRAVE prompt
4. **Brutal-honesty copy throughout** — no "you saved ₹2,400!" anywhere
5. **One-time ₹999 Pro Pack** for higher cashback caps + Amazon supplement bundle

That's it. Don't build community, don't build a coach, don't build hypnosis, don't build articles. Build the dopamine loop, prove that frequency-of-craving-button-presses correlates with quit success, then expand.

---

## How this maps to the data

| Insight from interview | Insight from our scrape | Product feature |
|---|---|---|
| Dopamine, not nicotine, is the addiction | 0/87 apps target dopamine | **CRAVE button** with variable reward |
| Counters and badges don't help in the craving moment | "Money saved" is the #1 advertised feature (54% of apps) | We deprecate it from the home screen |
| Subscriptions feel like a scam | 19.5% of all bad reviews are paywall complaints; only 2.3% of apps offer lifetime | **₹999 lifetime** as the headline price |
| Boredom is reason #2 | "Distraction games" exists in only 2.3% of apps | **Phantom Puff mini-game** + audio rewards |
| Triggers are time-based and predictable | "Trigger identification" exists in 32% of apps but only as a *list*, never as proactive interception | **Trigger Interception** notifications |
| Underlying dopamine deficit | 0 apps mention magnesium, L-theanine, sun, cold | **Daily Dopamine Stack** |
| Vaping is harder than cigarettes | Only 37% of apps support vaping at all | We make vaping a first-class supported habit |

The interview and the scrape independently arrived at the same product. That's the strongest signal you can get pre-build.
