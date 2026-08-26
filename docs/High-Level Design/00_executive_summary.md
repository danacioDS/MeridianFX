# 📋 MERIDIAN FX — EXECUTIVE SUMMARY

## Overview

**Meridian FX** is a financial intelligence system for foreign exchange markets that transforms market, macroeconomic, and textual data into **actionable, traceable, explainable, and evaluable intelligence**.

Its purpose is to turn market noise into practical financial intelligence for traders, analysts, and risk managers.
---
MERIDIAN FX — Documentation
│
├── 📋 00 — Executive Summary
│   ├── Vision
│   ├── Core Principles
│   ├── Product Scope
│   └── Roadmap Overview
│
├── 📐 01 — System Architecture & Build Strategy
│   ├── System Architecture
│   ├── Data Flow
│   ├── AI/ML Components
│   ├── Agent Architecture
│   └── Build Strategy
│
├── 📊 02 — Product Specification
│   ├── Product Overview
│   ├── UI/UX & Dashboard
│   ├── Output Specification
│   └── Data Contracts
│
├── 🚀 03 — Implementation Roadmap
│   ├── MVP
│   ├── V2 — Intelligence
│   ├── V3 — Advanced Analytics
│   └── V4 — Evaluation & Learning
│
└── 📚 04 — Glossary & Definitions
    ├── Financial Terms
    ├── ML/AI Terms
    ├── Metrics
    └── Formulas
---

## The Problem It Solves

| Challenge                            | Meridian Solution                                                         |
| ------------------------------------ | ------------------------------------------------------------------------- |
| Predictions without explanation      | SHAP + RAG + Macro Regime to **explain the "why"**                        |
| Signals without traceability         | Model, Prediction, and Fusion Records for **complete auditability**       |
| Uncalibrated probabilities           | Statistical calibration (Platt/Isotonic) for **meaningful probabilities** |
| Signals without economic filtering   | Economic Filter with transaction costs for **actionable signals**         |
| Models without continuous evaluation | Separate model vs. strategy evaluation with **degradation detection**     |

---

## 4-Layer Architecture + Governance

```text
┌─────────────────────────────────────────────────────────────┐
│                   1. INTELLIGENCE LAYER                     │
│       API · Dashboard · Morning Brief · Registry            │
├─────────────────────────────────────────────────────────────┤
│                   2. DECISION ENGINE                        │
│       Dynamic Signal Fusion · Ranking · Economic Filter     │
├─────────────────────────────────────────────────────────────┤
│                   3. RESEARCH LAYER                         │
│   Quant Models · Macro Models · RAG · Backtesting           │
├─────────────────────────────────────────────────────────────┤
│                    4. DATA LAYER                            │
│      Raw Data · Normalization · Feature Engineering         │
├─────────────────────────────────────────────────────────────┤
│              CROSS-CUTTING: GOVERNANCE / MLOps              │
│ Versioning · Lineage · Experiment Tracking · Monitoring     │
└─────────────────────────────────────────────────────────────┘
```

**Fundamental Principle:** `knowledge_timestamp <= prediction_timestamp` — no future information leakage.

---

## 4 Levels of Intelligence Output

### Level 1 — Forecast (Per Currency Pair)

* Direction (bullish/bearish/neutral)
* Calibrated probability
* Expected return and prediction interval
* Economic Filter with Net Return and Edge Ratio
* **Actionable?** (Yes/No)

### Level 2 — Drivers & Explanation (Per Currency Pair)

* SHAP: contribution of each feature
* Macro Regime (US, Japan, Risk, Growth)
* RAG: central bank sentiment (Fed/BoJ)
* Executive Narrative (2–3 paragraphs)
* Risks and event sensitivity

### Level 3 — Global Intelligence (Multi-Asset)

* Currency-pair opportunity rankings
* Divergences (rates, monetary policy, positioning)
* Cross-asset correlations
* Early warnings and alerts
* Economic calendar

### Level 4 — Evaluation & Learning (Audit)

* Model metrics (DA, AUC, Brier, ECE)
* Strategy metrics (Sharpe, Drawdown, Profit Factor)
* Performance by regime
* Degradation and drift detection

---

## Sequential Experimentation

| Experiment | Component               | Purpose                     |
| ---------- | ----------------------- | --------------------------- |
| E0         | Random Walk             | Baseline benchmark          |
| E0b        | Random Walk + Drift     | Robust baseline             |
| E1a        | ARIMA                   | Time-series model           |
| E1b        | Elastic Net             | Linear control model        |
| E2a        | XGBoost                 | Non-linear model            |
| E2b        | XGBoost + Constraints   | Economically informed model |
| E3         | + Market Features       | VIX, COT, Gold, Oil         |
| E4         | + Macro Regime          | Macroeconomic context       |
| E5         | + Central Bank RAG      | Central bank communications |
| E6         | Walk-Forward Retraining | Temporal adaptation         |
| E7         | Ensemble                | XGBoost + LSTM              |

---

## Implementation Roadmap

| Phase   | Scope                                                                                | Timeline  |
| ------- | ------------------------------------------------------------------------------------ | --------- |
| **MVP** | USD/JPY, EUR/USD, GBP/USD, USD/CNY · Forecast + SHAP + Basic Macro · API + Dashboard | 8 weeks   |
| **V2**  | + USD/MXN, USD/BRL · RAG Agent · Enhanced Macro                                      | 4–6 weeks |
| **V3**  | + USD/ARS, USD/BOB · Full Global Intelligence · Morning Brief                        | 4–6 weeks |
| **V4**  | Full Multi-Asset · Drift Detection · Complete Currency Radar                         | 4–6 weeks |

---

## Technology Stack

| Layer              | Technology                              |
| ------------------ | --------------------------------------- |
| **Data**           | PostgreSQL / TimescaleDB, S3/MinIO, DVC |
| **ML**             | XGBoost, SHAP, MLflow, Python           |
| **API**            | FastAPI + Uvicorn                       |
| **Dashboard**      | Streamlit                               |
| **Infrastructure** | Docker, Render (512 MB), Neon           |
| **Data Sources**   | FRED, e-Stat, Yahoo Finance, CFTC       |

---

## MVP Success Metrics

| Metric                  | Minimum Target | Rationale                                         |
| ----------------------- | -------------: | ------------------------------------------------- |
| Directional Accuracy    |          > 52% | Beat the 50% random-walk baseline                 |
| Net Sharpe Ratio        |          > 0.3 | Demonstrate economic significance                 |
| Calibration Error (ECE) |         < 0.05 | Reliable probability estimates                    |
| Edge Ratio              |          > 2.0 | Justify transaction costs through sufficient edge |

---

## Guiding Principles

| Principle             | Implementation                                     |
| --------------------- | -------------------------------------------------- |
| **Data First**        | Data → Features → Models                           |
| **Leakage-Free**      | `knowledge_timestamp <= prediction_timestamp`      |
| **Hypothesis-Driven** | Every component must justify its incremental value |
| **Reproducible**      | Same code + same data = same experiment            |
| **Traceable**         | Prediction → Model → Features → Data → Source      |
| **Observable**        | Metrics, logs, alerts, and drift detection         |

---

## Value Proposition

Meridian FX **does not simply produce predictions** — it produces **financial intelligence** that is:

✅ **Actionable** — An economic filter determines whether a signal is worth trading.
✅ **Explainable** — SHAP, macroeconomic context, and RAG explain *why*.
✅ **Traceable** — Complete lineage from source data to prediction.
✅ **Evaluable** — Separate metrics for model performance and strategy performance.

---

**Meridian FX — Executive Summary v1.0** ✅
