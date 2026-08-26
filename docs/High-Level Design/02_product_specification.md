# 📊 MERIDIAN FX — Product Specification

**Version 1.0 — Render Product (512 MB) with Neon Database**

---

## 📌 PRODUCT GUIDING PRINCIPLE

> **"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."**

**The product answers 5 fundamental questions:**

1. **What is happening in the market?** → Global Overview
2. **What does Meridian expect?** → Forecast Dashboard
3. **Why?** → Drivers & Explanation
4. **Is it worth acting?** → Economic Filter
5. **How good has Meridian been?** → Performance Dashboard

---

## 🗑️ DEFERRED FEATURES (POST-MVP)

| Feature                                             | Reason                                  | When It Returns    |
| --------------------------------------------------- | --------------------------------------- | ------------------ |
| **RAG Agent (NLP/LLM)**                             | High memory and CPU consumption         | V2                 |
| **Multi-Currency (more than 4 pairs)**              | Multiplies models and data requirements | V2                 |
| **Global Intelligence (correlations, divergences)** | Additional complexity                   | V2/V3              |
| **Automatic Morning Brief**                         | Not essential for the demo              | V3                 |
| **MLflow in production**                            | Consumes ~150 MB                        | Local/offline only |
| **Complex Prediction Registry**                     | Additional database infrastructure      | V2                 |
| **Multi-Horizon (1D, 20D)**                         | Additional models required              | V2                 |
| **Position Sizing Factor**                          | Enters portfolio/risk management        | V3                 |
| **Signal Stability / Quality**                      | Additional metrics and complexity       | V2                 |

---

## 🏗️ SYSTEM ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MERIDIAN FX — ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    NEON (External Database)                        │    │
│  │                                                                     │    │
│  │  PostgreSQL                                                         │    │
│  │  ├── features (latest available data)                              │    │
│  │  ├── predictions (precomputed offline)                             │    │
│  │  ├── shap_explanations (precomputed offline)                       │    │
│  │  └── performance_metrics (precomputed offline)                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RENDER (Application Server)                     │    │
│  │                                                                     │    │
│  │  FastAPI + Uvicorn (1 worker)                                      │    │
│  │  ├── Model Loader (XGBoost, 4 pairs)                              │    │
│  │  ├── Feature Engine (queries Neon)                                 │    │
│  │  ├── Economic Filter (real-time calculation)                       │    │
│  │  ├── Signal Validity (invalidation conditions)                      │    │
│  │  └── API Endpoints                                                 │    │
│  │                                                                     │    │
│  │  Dashboard (separate or static)                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

| Principle                   | Implementation                                                            |
| --------------------------- | ------------------------------------------------------------------------- |
| **Inference-Only**          | Render only performs inference; training is never performed in production |
| **Precomputed SHAP**        | SHAP values are calculated offline and served from Neon                   |
| **Precomputed Predictions** | Predictions are generated offline and stored in Neon                      |
| **On-Demand Models**        | Models are loaded only when needed                                        |
| **Small Connection Pool**   | Maximum of 3 simultaneous connections to Neon                             |

---

# 📱 1. GLOBAL OVERVIEW

### Main View (Entry Screen)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 MERIDIAN FX — GLOBAL INTELLIGENCE                          2026-08-25  │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Data: Fresh · 08:00 UTC · ✅ 98% coverage · ⚡ 42ms inference          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🌍 MARKET REGIME                                                  │    │
│  │                                                                     │    │
│  │  🟢 RISK-ON          VIX: 16.8       Risk Appetite: 0.72 ↑        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🏆 TOP OPPORTUNITIES                                              │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #1  USD/JPY    📈 BULLISH    68%    +0.82%    🟢 ACTIONABLE │   │    │
│  │  │      Net: +0.62%    Edge: 3.1x                               │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #2  EUR/USD    📉 BEARISH    32%    -0.45%    ⚪ NO EDGE    │   │    │
│  │  │      Net: -0.12%    Signal: Weak                              │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #3  GBP/USD    📉 BEARISH    38%    -0.35%    ⚪ NO EDGE    │   │    │
│  │  │      Net: -0.08%    Signal: Weak                              │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #4  USD/CNY    📈 BULLISH    55%    +0.28%    ⚪ NO EDGE    │   │    │
│  │  │      Net: +0.02%    Signal: Weak                              │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ EARLY WARNINGS                                                 │    │
│  │                                                                     │    │
│  │  ⚠️  JPY short positioning at 1-year extreme (z-score: -2.1)      │    │
│  │  ℹ️  Risk-on regime confirmed (VIX < 18)                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📅 KEY EVENTS TODAY                                               │    │
│  │                                                                     │    │
│  │  🔴 14:00 EST   FOMC Minutes Release                               │    │
│  │  🟡 08:30 EST   US Durable Goods Orders                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📊 2. FORECAST DASHBOARD

### Detail View (USD/JPY)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 MERIDIAN FX — FORECAST DASHBOARD                       USD/JPY        │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Data: Fresh · 08:00 UTC · ✅ 98% coverage · ⚡ 42ms inference          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📈 FORECAST                                                       │    │
│  │                                                                     │    │
│  │  Direction:      📈 BULLISH                                        │    │
│  │  Probability:    68% (calibrated)                                  │    │
│  │  Horizon:        5D                                                │    │
│  │  Model Version:  xgb-v2.3                                          │    │
│  │                                                                     │    │
│  │  Expected Return:  +0.82%                                          │    │
│  │  95% Prediction Interval: [-0.31%, +1.95%]                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  💰 ECONOMIC FILTER                                                │    │
│  │                                                                     │    │
│  │  Gross Return:    +0.82%                                            │    │
│  │  Total Costs:     -0.20%  (Spread: 0.10% · Slippage: 0.05% · Fees: 0.05%) │
│  │  Net Return:      +0.62%                                            │    │
│  │  Edge Ratio:      3.1x                                             │    │
│  │  Minimum Edge:    +0.20%                                            │    │
│  │                                                                     │    │
│  │  🟢 ACTIONABLE                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ SIGNAL VALIDITY                                                │    │
│  │                                                                     │    │
│  │  Bullish thesis remains valid while:                                │    │
│  │  • US-JP yield spread remains > 2.5%                               │    │
│  │  • VIX remains < 22                                                │    │
│  │  • BoJ policy divergence persists                                  │    │
│  │                                                                     │    │
│  │  Invalidated if:                                                   │    │
│  │  • Yield spread reverses materially                                │    │
│  │  • Risk regime shifts to Risk-Off                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 🔍 3. DRIVERS & EXPLANATION

### Detail View (USD/JPY)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 MERIDIAN FX — DRIVERS & EXPLANATION                      USD/JPY        │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Data: Fresh · 08:00 UTC · ✅ 98% coverage · ⚡ 42ms inference          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📊 KEY DRIVERS                                                    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #1 US-JP Yield Spread   ▲ +0.31     Value: 3.42%           │   │    │
│  │  │  ████████████████████████████████████████░░░░░░░░░░░░░░     │   │    │
│  │  │  Contribution: 42%                                           │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #2 VIX                   ▼ -0.18     Value: 16.8           │   │    │
│  │  │  ████████████████████████████████████████░░░░░░░░░░░░░░     │   │    │
│  │  │  Contribution: 24%                                           │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  #3 JPY Positioning        ▼ -0.12     Value: z-score -2.1  │   │    │
│  │  │  ████████████████████████████████████████░░░░░░░░░░░░░░     │   │    │
│  │  │  Contribution: 16%                                           │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🌍 MACRO REGIME                                                   │    │
│  │                                                                     │    │
│  │  US:      Restrictive                                              │    │
│  │  Japan:   Accommodative                                            │    │
│  │  Risk:    Risk-On                                                  │    │
│  │  Growth:  Moderate                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📄 POLICY SIGNAL (Fed vs BoJ)                                     │    │
│  │                                                                     │    │
│  │  Fed:   Hawkish (0.72)   ↑ +0.08                                   │    │
│  │  BoJ:   Dovish  (0.28)   ↓ -0.04                                   │    │
│  │                                                                     │    │
│  │  Policy Divergence: HIGH                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🔴 KEY RISKS                                                      │    │
│  │                                                                     │    │
│  │  • Sharp increase in global risk aversion (medium probability)     │    │
│  │  • Unexpected BoJ intervention (low probability)                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📊 4. PERFORMANCE DASHBOARD

### Historical Performance

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔍 MERIDIAN FX — PERFORMANCE DASHBOARD                   2026-08-25     │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Data: Fresh · 08:00 UTC · ✅ 98% coverage · ⚡ 42ms inference          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📈 MODEL PERFORMANCE (USD/JPY, 5D, 2022-2026)                     │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Metric              Value     vs Benchmark    Status         │   │    │
│  │  ├──────────────────────────────────────────────────────────────┤   │    │
│  │  │  Directional Acc.    56.7%     +6.6%          ✅ Good        │   │    │
│  │  │  AUC                 0.59      +0.09          ✅ Good        │   │    │
│  │  │  Brier Score         0.22      -0.03          ✅ Good        │   │    │
│  │  │  N                   420       -              ✅ Good        │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📊 STRATEGY PERFORMANCE                                            │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Metric              Value     vs Benchmark    Status         │   │    │
│  │  ├──────────────────────────────────────────────────────────────┤   │    │
│  │  │  Net Return (ann.)   5.4%      +5.7%          ✅ Good        │   │    │
│  │  │  Sharpe (net)        0.71      +0.69          ✅ Good        │   │    │
│  │  │  Max Drawdown        -7.2%     -0.9%          ✅ Good        │   │    │
│  │  │  Profit Factor       1.42      +0.32          ✅ Good        │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🎯 CALIBRATION (ECE: 0.03 ✅)                                      │    │
│  │                                                                     │    │
│  │  100% ┤                                                             │    │
│  │       │  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●                     │    │
│  │   80% ┤  ●            ●                                            │    │
│  │       │      ●              ●                                      │    │
│  │   60% ┤            ●              ●                                │    │
│  │       │                  ●              ●                          │    │
│  │   40% ┤                        ●              ●                    │    │
│  │       │                              ●              ●              │    │
│  │   20% ┤                                    ●              ●        │    │
│  │       │                                          ●              ●  │    │
│  │    0% ┼───────────────────────────────────────────────────────────  │    │
│  │       0%     20%     40%     60%     80%     100%                  │    │
│  │                                                                     │    │
│  │  ● Ideal Calibration    ○ Meridian FX                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📉 CUMULATIVE RETURN (2022-2026)                                   │    │
│  │                                                                     │    │
│  │  30% ┤                                                             │    │
│  │      │  ╭─────────────────────────────────────────────────╮       │    │
│  │  20% ┤  │  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │       │    │
│  │      │  │              ╭───╮  ╭──╮                        │       │    │
│  │  10% ┤  │              │   │  │  │  ╭─╮                  │       │    │
│  │      │  │              │   │  │  │  │ │                   │       │    │
│  │   0% ┤  │              │   │  │  │  │ │                   │       │    │
│  │      │  │              │   │  │  │  │ │                   │       │    │
│  │ -10% ┤  │              │   │  │  │  │ │                   │       │    │
│  │      │  │              │   │  │  │  │ │                   │       │    │
│  │ -20% ┤  │              │   │  │  │  │ │                   │       │    │
│  │      │  ╰─────────────────────────────────────────────────╯       │    │
│  │      └─────────────────────────────────────────────────────────     │    │
│  │        2022   2023   2024   2025   2026                             │    │
│  │                                                                     │    │
│  │  ● Meridian FX (Sharpe: 0.71)    ○ Random Walk (Sharpe: 0.02)     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📊 ESTIMATED MEMORY CONSUMPTION

### With PostgreSQL on Neon (External)

| Component              |    Estimated Memory |
| ---------------------- | ------------------: |
| FastAPI + Python       |            60–90 MB |
| XGBoost + NumPy/Pandas |           80–130 MB |
| In-memory data         |            30–60 MB |
| PostgreSQL             | **0 MB (external)** |
| System/runtime         |           50–100 MB |
| **Total**              |     **~220–380 MB** |
| **Margin over 512 MB** |     **~132–292 MB** |

✅ **Operational target: keep Meridian below ~250–300 MB**

---

# 🗺️ IMPLEMENTATION ROADMAP

### MVP (Deliverable 1) — 4 Pairs

```text
✅ Pairs: USD/JPY, EUR/USD, GBP/USD, USD/CNY
✅ Global Overview (basic)
✅ Forecast Dashboard (complete)
✅ Drivers & Explanation (SHAP + basic macro)
✅ Economic Filter
✅ Performance Dashboard (basic)
✅ Signal Validity
✅ Neon Database (external)
✅ SHAP precomputed offline
✅ Predictions precomputed offline
```

### V2 (Deliverable 2)

```text
➕ USD/MXN, USD/BRL
➕ RAG Agent (Fed/BoJ)
➕ Enhanced Macro Regime
➕ Model Agreement
```

### V3 (Deliverable 3)

```text
➕ USD/ARS, USD/BOB
➕ Advanced Global Intelligence
➕ Morning Brief
```

---

# 🎯 QUESTIONS MERIDIAN ANSWERS

| # | Question                              | Module                |
| - | ------------------------------------- | --------------------- |
| 1 | **What is happening in the market?**  | Global Overview       |
| 2 | **What does Meridian expect?**        | Forecast Dashboard    |
| 3 | **Why?**                              | Drivers & Explanation |
| 4 | **Is it worth acting?**               | Economic Filter       |
| 5 | **What could invalidate the signal?** | Signal Validity       |
| 6 | **How good has Meridian been?**       | Performance Dashboard |

---

**Meridian FX — Optimized Product Mockup v1.0 (Neon Edition)** ✅

This version is ready to use as the **English master specification** for the MVP/product documentation.
