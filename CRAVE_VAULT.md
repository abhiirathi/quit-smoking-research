# Crave Vault — the in-app wallet for "deposit instead of smoke"

> Each time you feel the urge to smoke, you tap a button and **deposit the cost of that cigarette into your Crave Vault** instead. The money grows. The cigarette doesn't.

This is the single best behavioral feature we've found. It hits four neurological triggers at once: **endowment effect** (the money is mine now), **loss aversion** (taking it out feels like losing), **anticipation** (vault grows visibly), and **dopamine of accumulation** (Indian gold/savings instinct).

But "wallet that holds user money" in India = RBI compliance. Here's how we ship it without a license.

---

## The hard regulatory question

If our app **custodies user funds**, we need an RBI Prepaid Payment Instrument (PPI) license:
- Small PPI: ₹10,000 cap, KYC-light, 24-month expiry
- Full KYC PPI: ₹2L cap, full KYC, AML compliance
- **Net-worth requirement: ₹5 Cr to apply, ₹15 Cr within 3 years**
- 6–12 month application timeline, ongoing audits

We are not doing this for v1. Here's how we get the same UX without holding a single rupee on our balance sheet.

---

## Three architectures — pick your path

### Path A — Virtual Vault (no real money) ❌

Users "deposit" a fake number that's just a counter. Used for in-app premium unlocks.

**Pros:** zero compliance.
**Cons:** competitors already do this with "money saved" counters. **Per the user interviews, this is exactly what doesn't work.** Skip.

### Path B — Sweep Vault (recommended for v1) ✅

Each craving deposit triggers a **UPI auto-debit** that moves money from user's bank → **user's own savings vehicle** (mutual fund, digital gold, RD). **We never touch the money.** We're a facilitator, not a custodian.

This is the exact model **Jar (jar.app)** uses — they hit **₹3,500 Cr+ AUM in 3 years** off micro-savings sweeps. Validated playbook.

**Pros:**
- ❌ No PPI license needed
- ✅ User's money grows (8–10% liquid fund / gold appreciation) — beats any cashback we could offer
- ✅ Compliance via partner (AMC / bank / gold provider already licensed)
- ✅ Tax efficient (investment, not idle wallet)
- ✅ The dopamine narrative writes itself: *"every time you don't smoke, you build wealth"*
- ✅ Indian audience trusts gold + MF more than app wallets

**Cons:** requires partner integration (Smallcase / Groww / Augmont) and one-time KYC.

**Build this.**

### Path C — Real Wallet (PPI license) — phase 2

Once we hit scale (₹10 Cr ARR, 500k+ MAU), we apply for full PPI. Lets us offer cashback, rewards, off-ramp purchases (supplements, NRT) directly from vault. Adds 12 months and ₹5 Cr capital — earned, not the starting point.

---

## The recommended UX (Path B)

**Onboarding (one time):**

1. User picks their **vault destination** during signup:
   - 🪙 **Digital Gold** (partner: Augmont / MMTC-PAMP / SafeGold) — most popular in India, emotional resonance, ~10% historical return
   - 💰 **Liquid Mutual Fund** (partner: ICICI Prudential Liquid Fund or Groww via Bharat Bill API) — instant redemption, ~7% return
   - 🏦 **Recurring Deposit** (partner: small finance bank) — locked, fixed return, lowest perceived risk
   - 💸 **Charity** (partner: Give.do / GiveIndia) — for the spiritually motivated
   - 🎯 **Quit Pact Escrow** (premium feature — see PREMIUM_DOPAMINE_FEATURES.md)

2. One-time **UPI Autopay mandate** for amounts up to ₹15,000/month (RBI cap on UPI mandate).

3. Done. From now on, every CRAVE tap is a one-tap deposit.

**The craving moment:**

```
┌─────────────────────────────────┐
│        🚬 CRAVING?              │
│                                 │
│   How much would this cost?     │
│                                 │
│   [ ₹15 ]  [ ₹50 ]  [ ₹100 ]    │
│        [ Custom: ___ ]          │
│                                 │
│   ➜ Tap to deposit to your     │
│     🪙 Gold Vault               │
│                                 │
│   ▰▰▰▰▰▰▰▱▱▱  73% of           │
│              your goal          │
└─────────────────────────────────┘
```

After tap:
- UPI debits user's account → goes to their vault destination
- Animation: vault counter ticks up with satisfying sound + visual
- Real-time gram count / fund unit count update
- Streak grows, milestone progress visible

**The vault screen:**

```
🪙 Your Crave Vault
─────────────────
0.487 g of 24K gold
≈ ₹3,420 today

📈 +12% since you started
🔥 47 cravings deposited
⏳ 23 days locked

[ Deposit again ]    [ Withdraw ]
```

---

## Withdrawal & lock mechanics (the moat)

This is where the dopamine architecture compounds:

| Lock duration | Bonus | Withdrawal |
|---|---|---|
| **Flex** (no lock) | 0% | Anytime, free |
| **30-day commit** | +1% bonus from us | Penalty if early withdraw (₹50 or 5%) |
| **90-day commit** | +3% bonus | Locked till date |
| **Quit Pact mode** | +5% bonus | If relapse → vault goes to charity (anti-charity multiplier optional) |

The bonus is funded by our supplement margins + brokerage trail commissions, not from the user's principal. Net positive economics for us at scale.

---

## Revenue model (us)

We don't earn on user deposits directly. We earn on:

| Source | Margin | Notes |
|---|---|---|
| **MF distribution trail** | 0.25–1% AUM/year | Partner with AMC; they pay us trail commission |
| **Digital gold spread** | 1–2% on each transaction | Augmont/MMTC partnership |
| **Premium tier** (₹999 lifetime) | high | Pro Pack unlocks higher daily caps, lock bonuses |
| **Insurance cross-sell** | ₹500–₹2,000/policy | Trigger when vault crosses ₹X |
| **Charity transaction fee** | 0% (we eat this) | Brand value > revenue here |

At 100k active depositors averaging ₹500/month sweep:
- Total monthly inflow: ₹5 Cr
- Annual AUM accumulated: ~₹60 Cr
- Trail revenue: ~₹30L–60L/year just from sweep AUM
- That's *additional* to subscription/tournament revenue, not in place of

---

## Partner shortlist (real names, India)

| Partner | What they provide | Status |
|---|---|---|
| **Augmont** | Digital gold rails, gram-level fractional buys | Partner-friendly, 24-hour onboarding |
| **MMTC-PAMP** | Government-backed gold | Premium brand, slower partner ops |
| **Smallcase** | Wealth + MF platform with API | API-first, used by 50+ apps |
| **Niyo / Fi Money** | Account aggregator + savings | Easier UPI mandate flow |
| **NSDL Payments Bank** | Nodal account if we ever go PPI route | For phase 2 |
| **Razorpay / Cashfree** | UPI Autopay infrastructure | Cheaper than going direct |
| **Setu / Decentro** | Account Aggregator + UPI mandate APIs | India-native, fintech-grade |

**Recommended stack for MVP:** Razorpay UPI Autopay + Augmont (gold) + Smallcase (MF) — gives users 2 vault choices on day 1, full sweep mechanic, no custodial liability.

---

## v1 build plan (next 60 days)

### Week 1–2 — Foundations
- Razorpay UPI Autopay integration (mandate creation + debit triggers)
- Augmont API integration (digital gold buy/sell on user's behalf)
- KYC flow (PAN + Aadhaar, served by Razorpay's KYC API)

### Week 3–4 — UX
- Vault destination picker (onboarding step)
- One-tap CRAVE deposit flow (₹15 / ₹50 / ₹100 / custom)
- Vault screen (live gram count, ₹ value, % change)
- Notification: "Your vault grew ₹47 today"

### Week 5–6 — Lock & commit
- 30/90-day lock toggle
- Bonus-on-completion mechanic (we credit the bonus from our wallet at maturity)
- Withdrawal flow with bank transfer

### Week 7–8 — Polish
- Streak integration (CRAVE deposits feed the main streak)
- Milestone unlocks (₹1,000 in vault → unlock supplement first-month free)
- Sharing (WhatsApp share card: "I haven't smoked for 23 days, my Vault: ₹3,420")

---

## What this unlocks

The Crave Vault becomes the **gravitational center of the app**. Every other feature feeds it:

- **CRAVE button** → Vault deposit
- **Daily Dopamine Stack** completion → bonus deposit (we credit ₹1)
- **Focus Arena** winnings → optional auto-deposit to vault
- **Quit Pact** stake → held in vault as escrow
- **Voice coach** → "your daughter says deposit, don't smoke"
- **Insurance partnership** → vault size becomes the qualifier for premium discounts

It's the **flywheel** that makes every other feature stickier. Without it, the app is a collection of features. With it, the app is a **vehicle for getting wealthier by not smoking** — and that's a story worth paying for.

---

## What competitors do (and why this is wide open)

Of 87 competitor apps in our scrape:
- 0 offer a real-money vault
- 47 offer a "money saved" counter (which the user interviews said is useless)
- 0 partner with gold or MF providers
- 0 use UPI auto-debit for behavioral commitment

**This is uncontested ground.** The closest analog (Jar) has proven the architecture works at ₹3,500 Cr scale — they just haven't applied it to addiction. We do.

---

## What we explicitly do NOT do in v1

- ❌ Custody user money on our balance sheet (no PPI license — phase 2)
- ❌ Lending / interest products (no NBFC license)
- ❌ Stocks / equity (no SEBI broker license)
- ❌ Cross-border / FX (compliance nightmare)
- ❌ Crypto (regulatory limbo, India-hostile)

Stick to: **gold, MF, RD, charity.** All four are settled regulatory ground.
