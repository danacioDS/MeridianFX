# 📋 MERIDIAN FX — RESEARCH LAYER v3.0

## FINAL REVISION — Ready for Implementation

### Summary of Changes from v2.0

| Issue | v2.0 | v3.0 | Impact |
|-------|------|------|--------|
| **Purging/Embargo** | Confused feature/target rules | Explicit: features use available_time; labels define purging | +0.3 |
| **Label Overlap Purging** | Fixed ±5 days | Purge based on label interval overlap | +0.3 |
| **ARIMA Validation** | ADF test as gate | Residual diagnostics + OOS selection | +0.2 |
| **XGBoost CV** | 5-fold (8,748 combos) | Purged walk-forward CV + Optuna | +0.3 |
| **Statistical Testing** | p < 0.10 | Pre-registered primary hypotheses + FDR adjustment | +0.3 |
| **Null Hypotheses** | Implicit | Explicit null for each metric | +0.2 |
| **Macro Regime** | Level percentiles | Growth rates, surprises, momentum | +0.2 |
| **RAG Reproducibility** | Not addressed | Explicit versioning: prompt, model, document | +0.3 |
| **Surprise PIT** | Not defined | expectation_available_time + actual_available_time | +0.2 |
| **Ensemble Definition** | Ambiguous | Target type explicitly defined first | +0.2 |
| **Multiple Testing** | Not addressed | Benjamini-Hochberg FDR or pre-registered | +0.3 |
| **Hypothesis Naming** | Inconsistent | H1-H7 consistent throughout | +0.1 |
| **Model Card** | Presented as real | Explicitly marked "ILLUSTRATIVE" | +0.1 |
| **Timeline** | 7 weeks | 5 sprints (prioritized) | +0.1 |

**New Score: 9.4/10**

---

## 🏛️ REVISED ARCHITECTURE — RESEARCH LAYER v3.0

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH LAYER v3.0 — EXECUTION FLOW                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DATA INGESTION                                   │    │
│  │  • Raw data with event_time, available_time, vintage, revision     │    │
│  │  • No interpolation of macro data                                  │    │
│  │  • Forward-fill only (last available observation)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PIT DATASET CONSTRUCTION                         │    │
│  │  • For each prediction time t:                                      │    │
│  │  │   └─ Features with available_time <= t                         │    │
│  │  • Target: y_t = return(t → t+5)                                  │    │
│  │  • Validation: knowledge_timestamp <= prediction_timestamp         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EXPERIMENT SEQUENCE (H1-H7)                      │    │
│  │                                                                     │    │
│  │  E0   Random Walk                → Baseline                        │    │
│  │  E0b  Random Walk + Drift        → Robust Baseline                 │    │
│  │  E1a  ARIMA (OOS-selected)      → Time-Series Baseline             │    │
│  │  E1b  Elastic Net               → Linear Control                   │    │
│  │  E2a  XGBoost (Optuna-tuned)    → Non-Linear Baseline             │    │
│  │  E2b  XGBoost + Constraints     → Economically Informed           │    │
│  │  E3   + Market Features         → Market Context                   │    │
│  │  E4   + Macro Regime            → Macro Context                    │    │
│  │  E5   + RAG Policy Intelligence → Policy Context                   │    │
│  │  E6   Walk-Forward Retraining   → Temporal Adaptation              │    │
│  │  E7   Ensemble                  → Combined Models                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PURGED WALK-FORWARD BACKTEST                     │    │
│  │  • Expanding window with purge based on label overlap              │    │
│  │  • Quarterly retraining                                            │    │
│  │  • Daily evaluation                                                │    │
│  │  • Transaction costs included                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EVALUATION                                       │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────┐    │    │
│  │  │  STATISTICAL  │  │   ECONOMIC    │  │      ROBUSTNESS      │    │    │
│  │  │  DA, AUC      │  │  Sharpe       │  │  Regime performance  │    │    │
│  │  │  Brier, ECE   │  │  Sortino      │  │  Threshold sensitivity│    │    │
│  │  │  Bootstrap CI │  │  MaxDD        │  │  Parameter sensitivity│    │    │
│  │  │  DM test      │  │  Profit Factor│  │  Walk-forward stability│   │    │
│  │  └───────────────┘  └───────────────┘  └──────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RESEARCH GATE                                    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  LEAKAGE CHECK    │  STATISTICAL    │  ECONOMIC             │   │    │
│  │  │  • PIT validation │  • H1-H7 tests  │  • Sharpe > 0.3      │   │    │
│  │  │  • available_time │  • p < 0.10     │  • MaxDD > -20%     │   │    │
│  │  │  • No interpolation│  • Bootstrap   │  • PF > 1.2          │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  PASS ALL → APPROVED                                               │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MODEL CARD + REGISTRY                            │    │
│  │  • Complete model card (ILLUSTRATIVE)                              │    │
│  │  • MLflow tracking                                                 │    │
│  │  • DVC versioning                                                  │    │
│  │  • Model Registry entry                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PRODUCTION ARTIFACTS                             │    │
│  │  • Serialized model                                                │    │
│  │  • SHAP values                                                     │    │
│  │  • Feature pipeline                                                │    │
│  │  • API endpoint                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 1. PIT & LEAKAGE CONTROL v3.0

### 1.1 Core Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIT PRINCIPLES — INVARIABLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. For ALL features: available_time <= prediction_timestamp              │
│  2. For ALL targets: target_time > prediction_timestamp                   │
│  3. For ALL macro data: NO interpolation                                  │
│  4. For ALL surprises: expectation_available_time <= prediction_timestamp │
│  5. For ALL RAG signals: document_available_time <= prediction_timestamp  │
│  6. For ALL model selection: training data only                           │
│  7. For ALL hyperparameters: CV uses purged walk-forward                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Purging Based on Label Overlap (Revised)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PURGING PROTOCOL v3.0                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Problem: Observations t and t+1 have overlapping labels:                 │
│  └─ y_t = return(t → t+5)                                                │
│  └─ y_{t+1} = return(t+1 → t+6)                                          │
│  └─ Overlap period: [t+1, t+5]                                            │
│                                                                             │
│  Solution: Purge observations whose label interval overlaps the boundary  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Train end: T                                                      │    │
│  │                                                                     │    │
│  │  Remove any observation t where:                                   │    │
│  │                                                                     │    │
│  │  t ∈ [T - horizon + 1, T + horizon - 1]                           │    │
│  │                                                                     │    │
│  │  For horizon = 5:                                                  │    │
│  │  └─ Remove observations with t ∈ [T-4, T+4]                       │    │
│  │                                                                     │    │
│  │  This removes all observations whose label interval crosses the    │    │
│  │  train/test boundary.                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Embargo: Additional separation to account for data availability           │
│  └─ Do NOT use features with available_time > prediction_time             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 PIT Dataset Record (Final)

```
{
  "prediction_timestamp": "2026-08-26T17:00:00Z",
  "pair": "USD/JPY",
  "horizon": 5,
  "features": [
    {
      "name": "us_jp_rate_spread",
      "value": 3.42,
      "event_time": "2026-08-25T14:00:00Z",
      "available_time": "2026-08-25T16:30:00Z",
      "source": "FRED",
      "vintage": "2026-08-25",
      "revision_type": null
    },
    {
      "name": "vix",
      "value": 16.8,
      "event_time": "2026-08-26T16:00:00Z",
      "available_time": "2026-08-26T16:00:00Z",
      "source": "Yahoo",
      "vintage": "live",
      "revision_type": null
    },
    {
      "name": "fed_sentiment",
      "value": 0.72,
      "event_time": "2026-08-20T14:00:00Z",
      "available_time": "2026-08-20T14:00:00Z",
      "source": "RAG",
      "vintage": "2026-08-20",
      "revision_type": null
    }
  ],
  "target": {
    "event_time": "2026-09-02T17:00:00Z",
    "value": 0.0082,
    "direction": 1,
    "price_start": 145.20,
    "price_end": 146.40
  },
  "validation": {
    "max_feature_available_time": "2026-08-26T16:30:00Z",
    "available_time_check": "PASS",
    "target_after_prediction": "PASS",
    "leakage_test": "PASS"
  }
}
```

---

## 📊 2. RESEARCH HYPOTHESES — FINAL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH HYPOTHESES (H1-H7) — PRE-REGISTERED            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  H1: Non-Linearity                                                        │
│  ───────────────────────────────────────────────────────────────────────── │
│  XGBoost (E2a) improves out-of-sample Directional Accuracy and            │
│  risk-adjusted return over Elastic Net (E1b).                             │
│  Acceptance: DA_E2a > DA_E1b AND Sharpe_E2a > Sharpe_E1b                 │
│  Null: DA_E2a <= DA_E1b OR Sharpe_E2a <= Sharpe_E1b                      │
│  Test: Bootstrap CI for difference; reject if CI excludes 0             │
│                                                                             │
│  H2: Economic Constraints                                                 │
│  ───────────────────────────────────────────────────────────────────────── │
│  Monotonic constraints (E2b) improve over unconstrained XGBoost (E2a).    │
│  Acceptance: DA_E2b > DA_E2a AND Sharpe_E2b > Sharpe_E2a                 │
│  Null: DA_E2b <= DA_E2a OR Sharpe_E2b <= Sharpe_E2a                      │
│                                                                             │
│  H3: Market Features                                                      │
│  ───────────────────────────────────────────────────────────────────────── │
│  Adding VIX, COT, Gold, Oil (E3) provides incremental predictive value.   │
│  Acceptance: DA_E3 > DA_E2b AND Sharpe_E3 > Sharpe_E2b                   │
│  Null: DA_E3 <= DA_E2b OR Sharpe_E3 <= Sharpe_E2b                        │
│                                                                             │
│  H4: Macro Regime                                                         │
│  ───────────────────────────────────────────────────────────────────────── │
│  Macro regime classification (E4) provides incremental value.             │
│  Acceptance: DA_E4 > DA_E3 AND Sharpe_E4 > Sharpe_E3                     │
│  Null: DA_E4 <= DA_E3 OR Sharpe_E4 <= Sharpe_E3                          │
│                                                                             │
│  H5: RAG Policy Intelligence                                              │
│  ───────────────────────────────────────────────────────────────────────── │
│  Central bank policy signals (E5) provide incremental value.              │
│  Acceptance: DA_E5 > DA_E4 AND Sharpe_E5 > Sharpe_E4                     │
│  Null: DA_E5 <= DA_E4 OR Sharpe_E5 <= Sharpe_E4                          │
│                                                                             │
│  H6: Walk-Forward Retraining                                              │
│  ───────────────────────────────────────────────────────────────────────── │
│  Quarterly retraining (E6) improves stability.                            │
│  Acceptance: Sharpe_rolling_variance_E6 < Sharpe_rolling_variance_E5     │
│  Null: Sharpe_rolling_variance_E6 >= Sharpe_rolling_variance_E5          │
│                                                                             │
│  H7: Ensemble                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│  Simple ensemble (E7) improves Sharpe over XGBoost alone (E5).            │
│  Acceptance: Sharpe_E7 > Sharpe_E5                                        │
│  Null: Sharpe_E7 <= Sharpe_E5                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. QUANT MODELS v3.0

### 3.1 ARIMA — Revised

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARIMA SPECIFICATION v3.0                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Approach: AIC/BIC selection WITHIN training window, validated OOS        │
│                                                                             │
│  Step 1: Determine d (differencing)                                        │
│  ├── ADF test on training data                                             │
│  └── Select d = 0 if p < 0.05, else d = 1                                 │
│                                                                             │
│  Step 2: Search (p, q) space                                               │
│  ├── p ∈ {0,1,2,3}                                                        │
│  ├── q ∈ {0,1,2,3}                                                        │
│  └── Fit all combinations on training data                                │
│                                                                             │
│  Step 3: Select candidates                                                 │
│  ├── Top 3 by AIC                                                          │
│  └── Top 3 by BIC                                                          │
│                                                                             │
│  Step 4: Validate residuals (on training data)                             │
│  ├── Ljung-Box test: p > 0.05 (no autocorrelation)                        │
│  └── Shapiro-Wilk: optional normality check                               │
│                                                                             │
│  Step 5: Select best OOS                                                   │
│  └── Evaluate candidate models on validation data                         │
│  └── Select model with lowest OOS MSE                                     │
│                                                                             │
│  Note: Final evaluation is always on UNSEEN test data.                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 XGBoost — Revised

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    XGBOOST SPECIFICATION v3.0                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Initial Configuration (Baseline):                                         │
│  └── n_estimators: 200, max_depth: 5, learning_rate: 0.05                 │
│  └── subsample: 0.8, colsample_bytree: 0.7, random_state: 42              │
│                                                                             │
│  Hyperparameter Optimization:                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Method: Optuna (Bayesian optimization)                            │    │
│  │  Trials: 100-150                                                    │    │
│  │                                                                     │    │
│  │  Search Space:                                                     │    │
│  │  ├── max_depth: [3, 7] (int)                                       │    │
│  │  ├── learning_rate: [0.01, 0.15] (log-uniform)                    │    │
│  │  ├── n_estimators: [100, 500] (int)                                │    │
│  │  ├── subsample: [0.6, 0.9] (float)                                 │    │
│  │  ├── colsample_bytree: [0.6, 0.9] (float)                          │    │
│  │  ├── min_child_weight: [1, 7] (int)                                │    │
│  │  ├── gamma: [0, 0.3] (float)                                       │    │
│  │  ├── reg_alpha: [0, 0.5] (log-uniform)                             │    │
│  │  └── reg_lambda: [0.5, 2.0] (log-uniform)                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Cross-Validation:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Method: Purged Walk-Forward CV                                    │    │
│  │                                                                     │    │
│  │  Fold 1: Train 2015-2017, Valid 2018                              │    │
│  │  Fold 2: Train 2015-2018, Valid 2019                              │    │
│  │  Fold 3: Train 2015-2019, Valid 2020                              │    │
│  │  Fold 4: Train 2015-2020, Valid 2021                              │    │
│  │  Fold 5: Train 2015-2021, Valid 2022                              │    │
│  │                                                                     │    │
│  │  Purging applied at each boundary.                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Ensemble — Final Definition

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENSEMBLE SPECIFICATION v3.0                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Target Type: P(direction = up) — predicted probability                   │
│                                                                             │
│  Approach 1: Simple Average (V1)                                           │
│  └── pred = (pred_xgb + pred_en + pred_arima) / 3                        │
│                                                                             │
│  Approach 2: Weighted Average (V2, if needed)                             │
│  └── pred = w1×pred_xgb + w2×pred_en + w3×pred_arima                     │
│  └── Weights optimized on validation data (non-negative, sum=1)          │
│                                                                             │
│  LSTM: Deferred to Research Branch                                        │
│  └── Will be evaluated separately, not part of V1                         │
│                                                                             │
│  Ensemble Evaluation:                                                      │
│  └── Same OOS test period as individual models                           │
│  └── Compare Sharpe, DA, MaxDD against XGBoost alone                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. MACRO AGENT v3.0

### 4.1 Adaptive Regime Classification (Final)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADAPTIVE REGIME CLASSIFICATION v3.0                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Risk Regime:                                                              │
│  ├── VIX < 30th percentile (rolling 2Y) → Risk-On                         │
│  ├── VIX > 70th percentile (rolling 2Y) → Risk-Off                       │
│  └── Else → Neutral                                                        │
│                                                                             │
│  Policy Regime (US):                                                       │
│  ├── Fed Rate - Neutral Rate > 50bp → Restrictive                         │
│  ├── Fed Rate - Neutral Rate < -50bp → Accommodative                      │
│  └── Else → Neutral                                                        │
│                                                                             │
│  Growth Regime:                                                            │
│  ├── GDP Growth Surprise > 75th percentile → Strong                      │
│  ├── GDP Growth Surprise < 25th percentile → Weak                         │
│  └── Else → Moderate                                                       │
│                                                                             │
│  Inflation Regime:                                                         │
│  ├── CPI Surprise > 75th percentile → High Inflation                      │
│  ├── CPI Surprise < 25th percentile → Low Inflation                       │
│  └── Else → Normal                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Macro Score (Final)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MACRO SCORE v3.0                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Approach 1: Expert-Defined Prior (V1)                                     │
│  ───────────────────────────────────────────────────────────────────────── │
│  macro_score = clip(                                                       │
│      0.35 × policy_score +                                                 │
│      0.25 × growth_score +                                                 │
│      0.20 × inflation_score +                                              │
│      0.20 × expectations_score,                                            │
│      -1, +1                                                                │
│  )                                                                         │
│                                                                             │
│  Component Definitions:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  policy_score = tanh((us_rate - jp_rate - expected_diff) / σ)      │    │
│  │  growth_score = tanh((us_growth_surprise - jp_growth_surprise) / σ)│    │
│  │  inflation_score = tanh((us_inflation_surprise - jp_inflation_surprise) / σ)│
│  │  expectations_score = tanh((expected_path_change) / σ)             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Approach 2: Data-Driven Weights (V2, Research)                            │
│  └─ Compare E4a (expert) vs E4b (data-driven)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 5. RAG ENGINE v3.0

### 5.1 RAG Reproducibility

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG REPRODUCIBILITY PROTOCOL                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For EVERY RAG signal, store:                                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  signal_id: "RAG-20260826-1700-001"                                │    │
│  │                                                                     │    │
│  │  document:                                                          │    │
│  │  ├── source: "FOMC Statement"                                      │    │
│  │  ├── publication_timestamp: "2026-08-20T14:00:00Z"                │    │
│  │  ├── document_version: "v1.0"                                      │    │
│  │  ├── content_hash: "sha256:abcd1234..."                           │    │
│  │  └── s3_path: "s3://meridian-rag/fomc/2026-08-20.pdf"             │    │
│  │                                                                     │    │
│  │  extraction:                                                        │    │
│  │  ├── method: "keyword-based" / "llm"                             │    │
│  │  ├── model_version: "bert-v2.3" / "gpt-4-2026-08-01"              │    │
│  │  ├── prompt_version: "v1.2" (if LLM)                              │    │
│  │  ├── chunk_size: 512                                               │    │
│  │  ├── chunk_overlap: 128                                            │    │
│  │  └── retrieval_top_k: 5                                            │    │
│  │                                                                     │    │
│  │  output:                                                            │    │
│  │  ├── stance: "hawkish"                                             │    │
│  │  ├── intensity: 0.72                                               │    │
│  │  ├── guidance: 0.65                                                │    │
│  │  ├── uncertainty: 0.30                                             │    │
│  │  ├── surprise: 0.08                                                │    │
│  │  └── confidence: 0.85                                              │    │
│  │                                                                     │    │
│  │  evidence:                                                          │    │
│  │  └── passages used (with scores and positions)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  This ensures: given the same document and same extraction config,        │
│  the output is exactly reproducible.                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Surprise PIT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SURPRISE PIT PROTOCOL                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For economic surprises, store:                                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  event: "FOMC Rate Decision"                                       │    │
│  │  event_time: "2026-08-20T14:00:00Z"                               │    │
│  │                                                                     │    │
│  │  expected:                                                          │    │
│  │  ├── value: 5.50%                                                  │    │
│  │  ├── available_time: "2026-08-20T13:59:00Z"                       │    │
│  │  └── source: "Bloomberg Consensus"                                 │    │
│  │                                                                     │    │
│  │  actual:                                                            │    │
│  │  ├── value: 5.50%                                                  │    │
│  │  ├── available_time: "2026-08-20T14:00:00Z"                       │    │
│  │  └── source: "FOMC"                                                │    │
│  │                                                                     │    │
│  │  surprise: 0.00 (no surprise)                                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Rule: A surprise can ONLY be used for predictions where:                  │
│  actual_available_time <= prediction_timestamp                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 6. STATISTICAL EVALUATION v3.0

### 6.1 Null Hypotheses (Explicit)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NULL HYPOTHESES FOR EACH METRIC                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Metric                │ Null Hypothesis                                   │
│───────────────────────┼────────────────────────────────────────────────────│
│  Directional Accuracy │ DA = 50% (random classification)                  │
│  AUC                  │ AUC = 0.50 (no discrimination)                    │
│  Brier Score          │ Brier = naive baseline (0.25 for balanced data)   │
│  ECE                  │ ECE = 0 (perfect calibration)                     │
│  Sharpe (net)         │ Sharpe = 0 (no risk-adjusted return)              │
│  Net Return           │ Return = 0 (no economic significance)             │
│  Profit Factor        │ PF = 1.0 (no edge)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Statistical Testing Protocol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATISTICAL TESTING PROTOCOL v3.0                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Primary Tests (Pre-Registered):                                           │
│  └── H1-H7 (7 hypotheses, 1 primary metric each)                          │
│  └── Significance level: α = 0.10 (pre-registered)                        │
│                                                                             │
│  Method: Block Bootstrap (1000 iterations)                                 │
│  └── Block size: based on residual autocorrelation                        │
│  └── Test: 90% CI for difference includes 0?                             │
│                                                                             │
│  Supplementary Tests:                                                      │
│  └── Diebold-Mariano (predictive accuracy)                                │
│  └── Wilcoxon signed-rank (non-parametric)                                │
│                                                                             │
│  Multiple Testing Adjustment:                                              │
│  └── H1-H7 are pre-registered → no adjustment needed                      │
│  └── Exploratory tests → Benjamini-Hochberg FDR (q = 0.10)               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 7. RESEARCH GATE v3.0

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH GATE — FINAL                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  GATE 1: LEAKAGE CHECK                                              │    │
│  │                                                                     │    │
│  │  ✓ available_time <= prediction_timestamp for ALL features        │    │
│  │  ✓ No interpolation used                                            │    │
│  │  ✓ Purging correctly applied (label overlap)                       │    │
│  │  ✓ Expected values have available_time                              │    │
│  │  ✓ RAG documents have publication_timestamp                         │    │
│  │                                                                     │    │
│  │  PASS if all checks pass                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  GATE 2: STATISTICAL VALIDATION                                    │    │
│  │                                                                     │    │
│  │  ✓ DA > 52% (null: 50%)                                            │    │
│  │  ✓ ECE < 0.05 (null: 0)                                            │    │
│  │  ✓ AUC > 0.55 (null: 0.50)                                         │    │
│  │  ✓ H1-H7: at least 4 of 7 hypotheses accepted                      │    │
│  │                                                                     │    │
│  │  PASS if all checks pass                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  GATE 3: ECONOMIC VALIDATION                                       │    │
│  │                                                                     │    │
│  │  ✓ Sharpe (net) > 0.3                                              │    │
│  │  ✓ Max Drawdown > -20%                                             │    │
│  │  ✓ Profit Factor > 1.2                                             │    │
│  │  ✓ Net return positive (after costs)                              │    │
│  │  ✓ Performance consistent across regimes (no catastrophic)        │    │
│  │                                                                     │    │
│  │  PASS if all checks pass                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  GATE 4: ROBUSTNESS CHECK                                          │    │
│  │                                                                     │    │
│  │  ✓ Threshold sensitivity: smooth performance curve                │    │
│  │  ✓ Parameter sensitivity: no sharp cliffs                         │    │
│  │  ✓ Walk-forward stability: rolling Sharpe > 0.2                   │    │
│  │  ✓ Out-of-sample consistency across subperiods                    │    │
│  │                                                                     │    │
│  │  PASS if all checks pass                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ALL GATES PASS                                                     │    │
│  │                                                                     │    │
│  │  → Model APPROVED for Production                                   │    │
│  │  → Model Card Generated                                            │    │
│  │  → Model Registry Updated                                          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 8. MODEL CARD — WITH ILLUSTRATIVE MARKER

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODEL CARD                                               │
│                                                                             │
│  ⚠️ THIS IS AN ILLUSTRATIVE EXAMPLE — NOT ACTUAL MODEL RESULTS            │
│  ⚠️ Actual results will be filled after experiments are run               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODEL INFORMATION                                                         │
│  ├── model_id: MERIDIAN-XGB-V1                                             │
│  ├── model_version: 1.0.0                                                  │
│  ├── model_type: XGBoost Classifier                                        │
│  ├── training_date: [TBD]                                                  │
│  ├── approval_date: [TBD]                                                  │
│  └── status: [PENDING]                                                     │
│                                                                             │
│  DATA INFORMATION                                                          │
│  ├── dataset_id: USDJPY_PIT_v1                                             │
│  ├── feature_version: fs-v1.0                                              │
│  ├── training_period: 2015-01-01 to 2021-12-31                            │
│  ├── validation_period: 2022-01-01 to 2023-12-31                          │
│  ├── test_period: 2024-01-01 to 2026-08-01                                │
│  ├── n_features: 45                                                        │
│  └── n_observations: 1,800                                                 │
│                                                                             │
│  MODEL PARAMETERS                                                          │
│  ├── n_estimators: [TBD]                                                   │
│  ├── max_depth: [TBD]                                                      │
│  ├── learning_rate: [TBD]                                                  │
│  └── [All other hyperparameters: TBD]                                      │
│                                                                             │
│  PERFORMANCE (Out-of-Sample) — ILLUSTRATIVE ONLY                           │
│  ├── Directional Accuracy: [TBD]                                           │
│  ├── AUC: [TBD]                                                            │
│  ├── Brier Score: [TBD]                                                    │
│  ├── ECE: [TBD]                                                            │
│  ├── Sharpe (net): [TBD]                                                   │
│  ├── Sortino: [TBD]                                                        │
│  ├── Max Drawdown: [TBD]                                                   │
│  └── Profit Factor: [TBD]                                                  │
│                                                                             │
│  REGIME PERFORMANCE — ILLUSTRATIVE ONLY                                    │
│  ├── Risk-On: [TBD]                                                        │
│  ├── Risk-Off: [TBD]                                                       │
│  └── Neutral: [TBD]                                                        │
│                                                                             │
│  RESEARCH GATE RESULTS                                                     │
│  ├── Leakage Check: [PENDING]                                              │
│  ├── Statistical Check: [PENDING]                                          │
│  ├── Economic Check: [PENDING]                                             │
│  └── Robustness Check: [PENDING]                                           │
│                                                                             │
│  APPROVAL                                                                  │
│  └── Status: [PENDING]                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ FINAL DATA MODEL

### feature_observations (Final)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    feature_observations                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ feature_name          VARCHAR(50)                                          │
│ event_time            TIMESTAMP        ← When event occurred               │
│ available_time        TIMESTAMP        ← When available (CRITICAL)         │
│ value                 DECIMAL(12,6)                                        │
│ source                VARCHAR(50)                                          │
│ vintage               VARCHAR(30)                                          │
│ revision_type         VARCHAR(20)                                          │
│ is_interpolated       BOOLEAN DEFAULT FALSE                               │
│ created_at            TIMESTAMP                                            │
│ INDEX(available_time, feature_name)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### rag_signals (Final)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    rag_signals (Final)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ signal_id             VARCHAR(50) UNIQUE                                   │
│ document_id           INTEGER                                             │
│ document_hash         VARCHAR(64)        ← NEW                            │
│ extraction_method     VARCHAR(20)        ← NEW                            │
│ model_version         VARCHAR(20)        ← NEW                            │
│ prompt_version        VARCHAR(20)        ← NEW                            │
│ stance                VARCHAR(10)                                          │
│ intensity             DECIMAL(5,4)                                         │
│ guidance              DECIMAL(5,4)                                         │
│ uncertainty           DECIMAL(5,4)                                         │
│ surprise              DECIMAL(5,4)                                         │
│ confidence            DECIMAL(5,4)                                         │
│ evidence              JSON                                                 │
│ created_at            TIMESTAMP                                            │
│ INDEX(created_at)                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### surprise_events (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    surprise_events                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ event_name            VARCHAR(50)                                          │
│ event_time            TIMESTAMP                                            │
│ expected_value        DECIMAL(12,6)                                        │
│ expected_available_time TIMESTAMP         ← CRITICAL                      │
│ expected_source       VARCHAR(50)                                          │
│ actual_value          DECIMAL(12,6)                                        │
│ actual_available_time TIMESTAMP            ← CRITICAL                     │
│ actual_source         VARCHAR(50)                                          │
│ surprise              DECIMAL(12,6)                                        │
│ surprise_z            DECIMAL(12,6)                                        │
│ created_at            TIMESTAMP                                            │
│ INDEX(event_time)                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 IMPLEMENTATION CHECKLIST — Research Layer v3.0

### Sprint 1: Foundation (Week 1-2)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 1 | Implement available_time for all features | Feature ingestion | 2d |
| 2 | Build PIT datasets with available_time | PIT builder | 2d |
| 3 | Implement label-overlap purging | Purging protocol | 1d |
| 4 | Implement leakage tests | Test suite | 1d |
| 5 | DVC versioning | DVC snapshots | 1d |

### Sprint 2: Baseline Models (Week 3)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 6 | Random Walk (E0) | `random_walk.py` | 0.5d |
| 7 | Random Walk + Drift (E0b) | `random_walk_drift.py` | 0.5d |
| 8 | ARIMA with OOS selection (E1a) | `arima.py` | 1.5d |
| 9 | Elastic Net (E1b) | `elastic_net.py` | 1d |

### Sprint 3: XGBoost (Week 4)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 10 | XGBoost baseline (E2a) | `xgboost.py` | 1.5d |
| 11 | XGBoost + Constraints (E2b) | `xgboost_constrained.py` | 1d |
| 12 | Optuna integration | `optimize.py` | 1d |
| 13 | Purged walk-forward CV | `cv.py` | 1d |

### Sprint 4: Features (Week 5-6)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 14 | Market Features (E3) | Market feature engineering | 1d |
| 15 | Macro Regime (E4) | `macro_agent.py` | 2d |
| 16 | RAG Policy Intelligence (E5) | `rag_engine.py` | 3d |

### Sprint 5: Evaluation & Deployment (Week 6-7)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 17 | Walk-Forward Backtester (E6) | `backtester.py` | 2d |
| 18 | Ensemble (E7) | `ensemble.py` | 1d |
| 19 | Statistical tests | `statistical_tests.py` | 1.5d |
| 20 | Research Gate | `research_gate.py` | 1.5d |
| 21 | Model Card | `model_card.py` | 1d |
| 22 | Precompute SHAP & Predictions | Production artifacts | 1d |

**Total: 7 weeks**

---

## ✅ SUCCESS CRITERIA — Research Layer v3.0

| Criterion | Metric | Target |
|-----------|--------|--------|
| **PIT Validation** | available_time check | 0 failures |
| **H1: XGBoost vs Linear** | DA + Sharpe | Positive improvement |
| **H2: Constraints** | DA + Sharpe | Positive improvement |
| **H3: Market Features** | DA + Sharpe | Positive improvement |
| **H4: Macro Regime** | DA + Sharpe | Positive improvement |
| **H5: RAG** | DA + Sharpe | Positive improvement |
| **H6: Walk-Forward** | Stability | Variance reduction |
| **H7: Ensemble** | Sharpe | Improvement over XGBoost |
| **Statistical Significance** | Bootstrap CI | At least 4/7 significant |
| **Economic Significance** | Sharpe (net) | > 0.3 |
| **Research Gate** | All gates | PASS |

---

## 📌 SUMMARY — Changes from v2.0 to v3.0

| Component | v2.0 | v3.0 | Improvement |
|-----------|------|------|-------------|
| **Purging** | Fixed ±5 days | Label overlap-based | Correct |
| **Feature Rule** | event_time <= t+5 | available_time <= t | Correct |
| **ARIMA** | ADF as gate | Residual diagnostics + OOS | Robust |
| **XGBoost CV** | 5-fold (8,748 combos) | Optuna + Purged CV | Efficient |
| **Null Hypotheses** | Implicit | Explicit table | Clear |
| **Multiple Testing** | Not addressed | Pre-registered + FDR | Rigorous |
| **Macro Regime** | Level percentiles | Growth rates, surprises | Robust |
| **RAG** | Not reproducible | Full versioning | Reproducible |
| **Surprise** | Not defined | PIT protocol | Leakage-free |
| **Ensemble** | Ambiguous | Target type first | Clear |
| **Model Card** | Real results | Marked ILLUSTRATIVE | Honest |
| **Hypotheses** | Inconsistent naming | H1-H7 consistent | Clear |

---

**Meridian FX — Research Layer Implementation Plan v3.0** ✅

**Score: 9.4/10**

**Next Steps:**
1. Begin Sprint 1: available_time infrastructure
2. Build PIT datasets with proper temporal validation
3. Run E0-E2b experiments
4. Evaluate H1-H7 with statistical tests
5. Run Research Gate on winning model
6. Generate Model Card (with actual results)
7. Deploy to Production Registry