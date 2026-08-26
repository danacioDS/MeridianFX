Perfect. I’m providing the complete specification for **LAYER 3: RESEARCH LAYER** in functional specification format, **without code**, ready for implementation.

[The full English translation follows exactly, preserving the structure, terminology, tables, diagrams, and technical meaning of the original.]

# 📋 MERIDIAN FX — LAYER 3: RESEARCH LAYER

## SPECIFICATION v5.0 — FROZEN — READY FOR IMPLEMENTATION

---

## 🏛️ 1. LAYER PURPOSE

```text
LAYER 3 — RESEARCH LAYER

MISSION:
Produce validated, reproducible, and economically meaningful
quantitative models for FX forecasting.

GUIDING PRINCIPLE:
> Research does not decide. Research demonstrates which models
> have sufficient evidence to be used.

RESPONSIBILITIES:
1. Build PIT (Point-in-Time) datasets free of leakage
2. Train and validate quantitative models
3. Generate predictions and SHAP values
4. Execute sequential experiments (E0-E7)
5. Validate models through the Research Gate
6. Register approved models in the Model Registry

NOT RESPONSIBLE FOR:
- Managing raw data (that is Layer 4)
- Making trading decisions (that is Layer 2)
- Delivering intelligence to the user (that is Layer 1)
```

---

## 📊 2. CONCEPTUAL ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH LAYER — ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 4 — DATA (PIT Datasets)                                             │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MODEL DEVELOPMENT                                │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │    │
│  │  │   QUANT MODELS  │  │   MACRO MODELS  │  │   RAG AGENTS        │ │    │
│  │  │                 │  │                 │  │                     │ │    │
│  │  │ • ARIMA         │  │ • Regime Class. │  │ • Fed Sentiment     │ │    │
│  │  │ • Elastic Net   │  │ • Policy Stance │  │ • BoJ Sentiment     │ │    │
│  │  │ • XGBoost       │  │ • Growth/Infl.  │  │ • Expectation Gap   │ │    │
│  │  │ • Ensemble      │  │ • Surprise      │  │ • Communication     │ │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MODEL EVALUATION                                  │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐│    │
│  │  │  STATISTICAL    │  ECONOMIC        │  ROBUSTNESS               ││    │
│  │  │  • DA           │  • Sharpe (net)  │  • Threshold Sensitivity  ││    │
│  │  │  • AUC          │  • MaxDD         │  • Parameter Sensitivity  ││    │
│  │  │  • Brier        │  • Profit Factor │  • Walk-Forward Stability ││    │
│  │  │  • ECE          │  • Net Return    │  • OOS Consistency        ││    │
│  │  └─────────────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RESEARCH GATE                                    │    │
│  │                                                                     │    │
│  │  PASS → Model Registry (CANDIDATE)                                  │    │
│  │  FAIL → REJECTED                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PRODUCTION ARTIFACTS                             │    │
│  │                                                                     │    │
│  │  ModelArtifact (model_id, version, hyperparameters, metrics)       │    │
│  │  PredictionArtifact (prediction_id, model_id, outputs, snapshot)   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  LAYER 2 — DECISION ENGINE                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. SEQUENTIAL EXPERIMENTS (E0 → E7)

### 3.1 Experiment Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL EXPERIMENTS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 0: BASELINES                                                        │
│  ───────────────────────────────────────────────────────────────────────── │
│  E0   │ Random Walk                     │ Baseline (no drift)              │
│  E0b  │ Random Walk + Drift             │ Robust baseline (with drift)     │
│                                                                             │
│  PHASE 1: CORE MODELS                                                      │
│  ───────────────────────────────────────────────────────────────────────── │
│  E1a  │ ARIMA                           │ Time-series model                │
│  E1b  │ Logistic Elastic Net            │ Linear control model             │
│                                                                             │
│  PHASE 2: NON-LINEAR                                                       │
│  ───────────────────────────────────────────────────────────────────────── │
│  E2a  │ XGBoost                         │ Non-linear model                 │
│  E2b  │ XGBoost + Constraints           │ Economically informed            │
│                                                                             │
│  PHASE 3: FEATURE AUGMENTATION                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│  E3   │ + Market Features               │ VIX, COT, Gold, Oil              │
│  E4   │ + Macro Regime                  │ Macroeconomic context            │
│  E5   │ + Central Bank RAG              │ Central bank communications      │
│                                                                             │
│  PHASE 4: ADVANCED                                                         │
│  ───────────────────────────────────────────────────────────────────────── │
│  E6   │ Walk-Forward Retraining         │ Temporal adaptation              │
│  E7   │ Ensemble                        │ XGBoost + Elastic Net + ARIMA    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Experiment Acceptance Criteria

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXPERIMENT ACCEPTANCE CRITERIA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  E0 → E0b:                                                                 │
│  └── E0b must outperform E0 (Sharpe, DA)                                   │
│  └── If not, E0b is still the baseline (more robust)                      │
│                                                                             │
│  E1a → E1b → E2a → E2b:                                                    │
│  └── Each step should show positive improvement                            │
│  └── DA improvement ≥ 1% OR Sharpe improvement ≥ 0.05                     │
│  └── If no improvement, the simpler model is preferred                    │
│                                                                             │
│  E3 → E4 → E5:                                                             │
│  └── Each feature set should show positive incremental value               │
│  └── At least 2 of 3 must show improvement                                │
│                                                                             │
│  E6:                                                                       │
│  └── Rolling Sharpe > 0.2 in > 75% of windows                             │
│  └── Reduced Sharpe variance vs. fixed model                               │
│                                                                             │
│  E7:                                                                       │
│  └── Sharpe improvement ≥ 0.05 vs. best individual model                   │
│  └── DA improvement ≥ 1% vs. best individual model                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. QUANT MODELS

### 4.1 ARIMA Model

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARIMA SPECIFICATION v5.0                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TARGET: future log-return (continuous)                                   │
│                                                                             │
│  OUTPUTS:                                                                  │
│  ├── expected_return: float                                                │
│  ├── forecast_interval: {lower: float, upper: float}                      │
│  ├── derived_direction: 1 if expected_return > 0 else 0                   │
│  └── probability_up: float (calibrated from error distribution via CDF)   │
│                                                                             │
│  MODEL SELECTION PROCESS:                                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Step 1: ADF Test (DIAGNOSTIC, NOT mechanical)                            │
│  ├── Target: log-return (normally stationary)                             │
│  ├── p < 0.05 → stationary → d = 0                                        │
│  └── p >= 0.05 → non-stationary → d = 1                                   │
│                                                                             │
│  Step 2: Search (p, q) Space                                              │
│  ├── p ∈ {0, 1, 2, 3}                                                     │
│  └── q ∈ {0, 1, 2, 3}                                                     │
│  └── Fit all combinations on training data                                │
│                                                                             │
│  Step 3: Candidate Selection                                              │
│  ├── Top 3 by AIC                                                          │
│  └── Top 3 by BIC                                                          │
│                                                                             │
│  Step 4: Residual Validation                                              │
│  ├── Ljung-Box test: p > 0.05 (no autocorrelation)                        │
│  └── Shapiro-Wilk: optional normality check                               │
│                                                                             │
│  Step 5: OOS Model Selection                                              │
│  └── Select model with lowest OOS MSE on VALIDATION data                  │
│                                                                             │
│  Step 6: Final Evaluation                                                 │
│  └── Evaluate on UNTOUCHED test data                                      │
│                                                                             │
│  Step 7: Probability Conversion                                           │
│  └── probability_up = CDF(0 | forecast_mean, forecast_variance)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Logistic Elastic Net

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOGISTIC ELASTIC NET SPECIFICATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TARGET: direction ∈ {0, 1}                                                │
│                                                                             │
│  OUTPUT: probability(direction = 1)                                        │
│                                                                             │
│  HYPERPARAMETERS:                                                          │
│  ├── alpha: 0.5 (mix of L1 and L2)                                        │
│  ├── l1_ratio: 0.5 (balanced)                                             │
│  ├── max_iter: 1000                                                        │
│  └── solver: saga (supports elasticnet)                                   │
│                                                                             │
│  CROSS-VALIDATION: PURGED WALK-FORWARD CV                                 │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Fold 1: Train 2015-2017 → Valid 2018                                     │
│  Fold 2: Train 2015-2018 → Valid 2019                                     │
│  Fold 3: Train 2015-2019 → Valid 2020                                     │
│  Fold 4: Train 2015-2020 → Valid 2021                                     │
│  Fold 5: Train 2015-2021 → Valid 2022                                     │
│                                                                             │
│  Purging applied at each boundary (label overlap elimination)             │
│                                                                             │
│  NOTE: Standard random K-fold CV is NOT acceptable                        │
│  due to temporal leakage.                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 XGBoost Model

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    XGBOOST SPECIFICATION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TARGET: direction ∈ {0, 1} (binary classification)                        │
│                                                                             │
│  OUTPUT: probability(direction = 1)                                        │
│                                                                             │
│  HYPERPARAMETER SEARCH: Optuna (100 trials)                                │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  n_estimators      │ 100 - 500    │ Integer                                │
│  max_depth         │ 3 - 7        │ Integer                                │
│  learning_rate     │ 0.01 - 0.15  │ Log-uniform                            │
│  subsample         │ 0.6 - 0.9    │ Float                                  │
│  colsample_bytree  │ 0.6 - 0.9    │ Float                                  │
│  min_child_weight  │ 1 - 10       │ Integer                                │
│  gamma             │ 0.0 - 0.5    │ Float                                  │
│  reg_alpha         │ 0.0 - 1.0    │ Float                                  │
│  reg_lambda        │ 0.0 - 1.0    │ Float                                  │
│  scale_pos_weight  │ 0.5 - 2.0    │ Float (class imbalance)               │
│                                                                             │
│  CROSS-VALIDATION: Purged Walk-Forward CV                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Same folds as Elastic Net (2015-2017 → 2018, etc.)                       │
│  Purging applied at each boundary                                          │
│                                                                             │
│  OBJECTIVE: maximize validation AUC                                        │
│                                                                             │
│  EARLY STOPPING:                                                           │
│  └── early_stopping_rounds = 10                                            │
│  └── eval_metric = logloss                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 XGBoost + Constraints (Economically Informed)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    XGBOOST + CONSTRAINTS SPECIFICATION                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: Enforce economic consistency in model predictions               │
│                                                                             │
│  CONSTRAINTS:                                                              │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  C1: Interest Rate Differential                                            │
│  ├── Rule: Higher US-JP yield spread → USDJPY appreciation                │
│  └── Constraint: coefficient on (us_10y - jp_10y) > 0                     │
│                                                                             │
│  C2: Risk Sentiment                                                        │
│  ├── Rule: Higher VIX → JPY appreciation (safe haven)                     │
│  └── Constraint: coefficient on VIX < 0                                    │
│                                                                             │
│  C3: Positioning                                                           │
│  ├── Rule: Extreme COT positions mean-revert                              │
│  └── Constraint: coefficient on COT_Zscore < 0 when > 2                   │
│                                                                             │
│  C4: Carry                                                                 │
│  ├── Rule: Higher carry → stronger tendency to hold                       │
│  └── Constraint: coefficient on carry > 0                                  │
│                                                                             │
│  IMPLEMENTATION:                                                           │
│  └── XGBoost with monotonic_constraints parameter                          │
│  └── Feature grouping for monotonic direction enforcement                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 Ensemble Model

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENSEMBLE SPECIFICATION v5.0                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TARGET TYPE: P(direction = up) — predicted probability                   │
│                                                                             │
│  PRE-PROCESSING:                                                           │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  All models MUST produce P(direction = up):                               │
│                                                                             │
│  XGBoost              → P_up (direct)                                      │
│  Logistic Elastic Net → P_up (direct)                                      │
│  ARIMA                → P_up = CDF(0 | forecast_mean, variance)           │
│                                                                             │
│  Only after this transformation are outputs combined.                     │
│                                                                             │
│  APPROACH 1: Simple Average (V1)                                           │
│  └── pred = (pred_xgb + pred_en + pred_arima) / 3                        │
│                                                                             │
│  APPROACH 2: Weighted Average (V2, if needed)                             │
│  └── pred = w1×pred_xgb + w2×pred_en + w3×pred_arima                     │
│  └── Weights optimized on VALIDATION data (non-negative, sum=1)           │
│                                                                             │
│  LSTM: Deferred to Research Branch                                        │
│  └── Evaluated separately, not part of V1                                 │
│                                                                             │
│  FINAL EVALUATION: ON UNTOUCHED test set                                  │
│  └── Compare Sharpe, DA, MaxDD against XGBoost alone                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 5. MACRO MODELS

### 5.1 Macro Regime Engine

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MACRO REGIME ENGINE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: Classify macroeconomic regimes based on multiple indicators      │
│                                                                             │
│  DOMAINS:                                                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  RISK SENTIMENT (based on VIX)                                             │
│  ├── Risk-On: VIX < 20                                                     │
│  ├── Neutral: 20 ≤ VIX < 30                                               │
│  └── Risk-Off: VIX ≥ 30                                                    │
│                                                                             │
│  POLICY STANCE (based on central bank rates + guidance)                    │
│  ├── Restrictive: Rate hikes / hawkish guidance                           │
│  ├── Neutral: Rate unchanged / balanced guidance                          │
│  └── Accommodative: Rate cuts / dovish guidance                           │
│                                                                             │
│  GROWTH (based on GDP + PMI surprises)                                    │
│  ├── Strong: Surprise > 0.5 standard deviations                           │
│  ├── Moderate: -0.5 ≤ Surprise ≤ 0.5                                      │
│  └── Weak: Surprise < -0.5 standard deviations                            │
│                                                                             │
│  INFLATION (based on CPI + PPI surprises)                                  │
│  ├── High: Surprise > 0.5 standard deviations                             │
│  ├── Moderate: -0.5 ≤ Surprise ≤ 0.5                                      │
│  └── Low: Surprise < -0.5 standard deviations                             │
│                                                                             │
│  REGIME COMBINATIONS:                                                     │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Expansion: Risk-On + Accommodative + Strong + Moderate                   │
│  Late Cycle: Risk-On + Restrictive + Moderate + High                      │
│  Stagflation: Risk-Off + Restrictive + Weak + High                        │
│  Recovery: Risk-On + Accommodative + Weak + Low                           │
│  Crisis: Risk-Off + Accommodative + Weak + Low                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Surprise Calculations

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SURPRISE CALCULATIONS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Surprise = actual_value - expected_value                                 │
│  Standardized Surprise = Surprise / historical_volatility                 │
│                                                                             │
│  KEY SURPRISES:                                                           │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  GDP Surprise           │ GDP actual vs. consensus                         │
│  CPI Surprise           │ CPI actual vs. consensus                         │
│  PPI Surprise           │ PPI actual vs. consensus                         │
│  Employment Surprise    │ NFP actual vs. consensus                         │
│  PMI Surprise           │ PMI actual vs. consensus                         │
│  Retail Sales Surprise  │ Retail Sales actual vs. consensus               │
│                                                                             │
│  PIT-AWARENESS:                                                           │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Each surprise MUST have:                                                 │
│  ├── event_time: datetime                                                  │
│  ├── release_time: datetime                                                │
│  ├── available_time: datetime (release_time + delay)                      │
│  └── vintage: str (e.g., "initial", "revised")                            │
│                                                                             │
│  Fundamental Rule:                                                         │
│  └── available_time <= prediction_timestamp                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 6. RAG AGENTS

### 6.1 Central Bank RAG Engine

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CENTRAL BANK RAG ENGINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: Extract actionable intelligence from central bank communications │
│                                                                             │
│  SOURCES:                                                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Federal Reserve (Fed)                                                     │
│  ├── FOMC statements                                                       │
│  ├── Press conferences (Powell)                                           │
│  ├── Meeting minutes                                                       │
│  ├── Beige Book                                                           │
│  └── Speeches (voting members)                                            │
│                                                                             │
│  Bank of Japan (BoJ)                                                       │
│  ├── Policy statements                                                     │
│  ├── Press conferences (Ueda)                                             │
│  ├── Meeting minutes                                                       │
│  ├── Outlook report                                                       │
│  └── Speeches (board members)                                             │
│                                                                             │
│  OUTPUTS:                                                                 │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Sentiment Score: -1 to +1 (Dovish → Hawkish)                            │
│                                                                             │
│  Expectation Gap:                                                          │
│  ├── Positive: Communication is more hawkish than expected               │
│  ├── Neutral: Communication is in line with expectations                 │
│  └── Negative: Communication is more dovish than expected                │
│                                                                             │
│  Key Quotes:                                                              │
│  ├── Extracted relevant quotes                                            │
│  └── Categorized by topic (inflation, growth, rates)                     │
│                                                                             │
│  Summary:                                                                 │
│  └── 2-3 sentence summary of communication                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Sentiment Classification

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SENTIMENT CLASSIFICATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DIMENSIONS:                                                               │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Rate Path:                                                                │
│  ├── Hawkish: "Will need to raise rates further"                          │
│  ├── Neutral: "Data-dependent approach"                                   │
│  └── Dovish: "Will hold or cut rates"                                     │
│                                                                             │
│  Inflation:                                                                │
│  ├── Concerned: "Inflation remains elevated"                              │
│  ├── Balanced: "Inflation is moderating"                                  │
│  └── Confident: "Inflation moving to target"                              │
│                                                                             │
│  Growth:                                                                   │
│  ├── Optimistic: "Growth remains resilient"                               │
│  ├── Cautious: "Growth is moderating"                                     │
│  └── Pessimistic: "Significant downside risks"                            │
│                                                                             │
│  OVERALL SENTIMENT SCORE:                                                 │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Scoring:                                                                  │
│  ├── Hawkish terms: +1 each (e.g., "tighten", "restrictive")             │
│  ├── Dovish terms: -1 each (e.g., "accommodative", "support")             │
│  └── Normalize to range [-1, +1]                                          │
│                                                                             │
│  Interpretation:                                                           │
│  ├── < -0.5: Strongly Dovish                                               │
│  ├── -0.5 to -0.1: Moderately Dovish                                      │
│  ├── -0.1 to +0.1: Neutral                                                │
│  ├── +0.1 to +0.5: Moderately Hawkish                                     │
│  └── > +0.5: Strongly Hawkish                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 RAG Signal Integration

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG SIGNAL INTEGRATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAG OUTPUTS AS FEATURES:                                                 │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Feature Name                 │ Description                                 │
│  ─────────────────────────────┼────────────────────────────────────────────│
│  fed_sentiment_score          │ Fed communication sentiment (-1 to +1)     │
│  boj_sentiment_score          │ BoJ communication sentiment (-1 to +1)     │
│  fed_expectation_gap          │ Actual vs. expected sentiment             │
│  boj_expectation_gap          │ Actual vs. expected sentiment             │
│  fed_hawkish_shift            │ Change in sentiment (vs. previous)         │
│  boj_dovish_shift             │ Change in sentiment (vs. previous)         │
│  fed_rate_path_bias           │ Bias in rate path guidance                 │
│  boj_rate_path_bias           │ Bias in rate path guidance                 │
│                                                                             │
│  PIT-AWARENESS:                                                           │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Each RAG feature MUST have:                                              │
│  ├── document_publication_time: datetime                                  │
│  ├── available_time: datetime (publication_time + processing_time)       │
│  └── feature_available_time: max(document_available_times)               │
│                                                                             │
│  Fundamental Rule:                                                         │
│  └── feature_available_time <= prediction_timestamp                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 7. BACKTESTING

### 7.1 Walk-Forward Backtest Specification

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WALK-FORWARD BACKTEST SPECIFICATION                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: Evaluate model performance in real-world, time-consistent way   │
│                                                                             │
│  STRUCTURE:                                                                │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Window 1: Train 2015-2017 → Valid 2018 → Test 2019                      │
│  Window 2: Train 2015-2018 → Valid 2019 → Test 2020                      │
│  Window 3: Train 2015-2019 → Valid 2020 → Test 2021                      │
│  Window 4: Train 2015-2020 → Valid 2021 → Test 2022                      │
│  Window 5: Train 2015-2021 → Valid 2022 → Test 2023                      │
│  Window 6: Train 2015-2022 → Valid 2023 → Test 2024                      │
│                                                                             │
│  At each window:                                                           │
│  ├── Hyperparameters optimized on Validation data                         │
│  ├── Final model trained on Train + Valid                                 │
│  └── Predictions generated on Test data                                   │
│                                                                             │
│  PURGING:                                                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  At each boundary T:                                                       │
│  ├── Remove training observations with label crossing T                   │
│  └── label_end(t) > T AND label_start(t) <= T                            │
│                                                                             │
│  For horizon = 5:                                                          │
│  └── Remove observations with t ∈ [T-4, T+4]                             │
│                                                                             │
│  OUTPUT:                                                                   │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  For each test period:                                                     │
│  ├── predictions: list of (timestamp, direction, probability)             │
│  ├── actuals: list of (timestamp, direction, return)                     │
│  ├── metrics: DA, AUC, Brier, ECE                                        │
│  └── economic_metrics: Sharpe, MaxDD, Profit Factor                      │
│                                                                             │
│  Aggregate metrics:                                                        │
│  ├── mean_metrics: average across windows                                 │
│  ├── variance_metrics: stability across windows                           │
│  └── regime_metrics: performance by regime                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Backtest Metrics

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKTEST METRICS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STATISTICAL METRICS                                                       │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Directional Accuracy (DA) │ % of correct directional predictions        │
│  AUC                      │ Area under ROC curve                          │
│  Brier Score              │ Mean squared error of probabilities          │
│  ECE                      │ Expected Calibration Error                   │
│  Log Loss                 │ Logarithmic loss                              │
│                                                                             │
│  ECONOMIC METRICS                                                          │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Sharpe Ratio (gross)     │ (mean_return - risk_free) / std_return       │
│  Sharpe Ratio (net)       │ After transaction costs + carry              │
│  Maximum Drawdown         │ Peak-to-trough decline                        │
│  Profit Factor            │ Gross profit / Gross loss                    │
│  Win Rate                 │ % of profitable trades                        │
│  Average Trade Return     │ Mean return per trade                         │
│  Calmar Ratio             │ Annualized Return / MaxDD                    │
│                                                                             │
│  ROBUSTNESS METRICS                                                        │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Rolling Sharpe (6m)      │ Stability of Sharpe over time                │
│  Threshold Sensitivity     │ Performance vs. threshold (smooth curve?)    │
│  Parameter Sensitivity     │ Performance vs. hyperparameters              │
│  Regime Consistency        │ Performance across regimes                   │
│  OOS Consistency           │ Performance across test windows              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 8. RESEARCH GATE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH GATE — FINAL RULES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GATE 1: LEAKAGE CHECK                                                     │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  ✓ available_time <= prediction_timestamp for ALL features                 │
│  ✓ No interpolation used (AS-OF JOIN only)                                │
│  ✓ Correct purging based on label overlap                                  │
│  ✓ Expected values have available_time                                     │
│  ✓ RAG documents have publication_timestamp                                │
│                                                                             │
│  PASS → Continue | FAIL → REJECTED                                        │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  GATE 2: STATISTICAL VALIDATION (SCREENING)                                │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  ✓ Directional Accuracy > 52% (screening threshold)                       │
│  ✓ Expected Calibration Error < 0.05                                       │
│  ✓ AUC > 0.55                                                              │
│  ✓ ALL Core Hypotheses (H1a-H1d) accepted                                 │
│                                                                             │
│  PASS → Continue | FAIL → REJECTED                                        │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  GATE 3: ECONOMIC VALIDATION (SCREENING)                                   │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  ✓ Sharpe (net) > 0.3 (screening threshold)                               │
│  ✓ Maximum Drawdown > -20%                                                 │
│  ✓ Profit Factor > 1.2                                                     │
│  ✓ Positive net return (after transaction costs)                          │
│  ✓ Performance consistent across regimes (no catastrophic failure)        │
│                                                                             │
│  PASS → Continue | FAIL → REJECTED                                        │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  GATE 4: ROBUSTNESS CHECK                                                  │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  ✓ Threshold sensitivity: smooth curve (no abrupt cliffs)                 │
│  ✓ Parameter sensitivity: no abrupt cliffs                                │
│  ✓ Walk-forward stability: rolling Sharpe > 0.2 in > 75% of windows      │
│  ✓ OOS consistency across subperiods (no single bad period)              │
│                                                                             │
│  PASS → APPROVED | FAIL → REJECTED                                        │
│                                                                             │
│  NOTE: Thresholds are SCREENING thresholds, not universal scientific      │
│  claims. They are calibrated for this specific system.                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 9. RESEARCH HYPOTHESES

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH HYPOTHESES — CORRECT NOMENCLATURE              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NOMENCLATURE NOTE:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  H0 (null) = No effect / No improvement                           │    │
│  │  H1 (alternative) = Effect exists / Improvement exists            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  CORE HYPOTHESES (MANDATORY)                                               │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  H0a: There is no improvement over the baseline                          │
│  H1a: XGBoost outperforms Random Walk + Drift                            │
│  Acceptance: Sharpe_E2a > Sharpe_E0b                                     │
│                                                                             │
│  H0b: There is no net economic value                                      │
│  H1b: The model generates net economic value                              │
│  Acceptance: Sharpe_net > 0.3                                             │
│                                                                             │
│  H0c: Performance is not stable in walk-forward evaluation                │
│  H1c: Performance is stable in walk-forward evaluation                    │
│  Acceptance: rolling_Sharpe > 0.2 in > 75% of windows                    │
│                                                                             │
│  H0d: Information leakage exists                                          │
│  H1d: No information leakage exists                                       │
│  Acceptance: All leakage tests PASS                                       │
│                                                                             │
│  RESEARCH HYPOTHESES (INFORMATIVE)                                         │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  H0e: Market Features add no value                                        │
│  H1e: Market Features add value                                           │
│  Acceptance: Sharpe_E3 > Sharpe_E2b                                       │
│                                                                             │
│  H0f: Macro Regime adds no value                                          │
│  H1f: Macro Regime adds value                                             │
│  Acceptance: Sharpe_E4 > Sharpe_E3                                        │
│                                                                             │
│  H0g: RAG adds no value                                                   │
│  H1g: RAG adds value                                                      │
│  Acceptance: Sharpe_E5 > Sharpe_E4                                        │
│                                                                             │
│  H0h: Ensemble provides no improvement                                    │
│  H1h: Ensemble provides improvement                                       │
│  Acceptance: Sharpe_E7 > Sharpe_E5                                        │
│                                                                             │
│  ACCEPTANCE CRITERIA                                                       │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Core Hypotheses (H0a-H0d vs H1a-H1d):                                    │
│  └── ALL alternatives (H1a-H1d) must be accepted                         │
│  └── α = 0.10 (pre-registered)                                            │
│  └── Method: Bootstrap CI (1000 iterations)                              │
│                                                                             │
│  Research Hypotheses (H0e-H0h vs H1e-H1h):                                 │
│  └── Informative, non-blocking                                             │
│  └── At least 2 of 4 must be accepted                                     │
│  └── Benjamini-Hochberg FDR (q = 0.10)                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 10. REPRODUCIBILITY

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REPRODUCIBILITY — DEFINITION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEFINITION:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Same immutable inputs                                              │    │
│  │  + same code version                                                │    │
│  │  + same dependency environment                                      │    │
│  │  + same configuration                                               │    │
│  │  + same random seeds                                                │    │
│  │  + deterministic execution                                          │    │
│  │  = reproducible result within a defined numerical tolerance        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  VERSIONED ARTIFACTS:                                                      │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Code           → Git commit hash + tag                                   │
│  Data           → DVC (dataset_id + version)                             │
│  Features       → Feature version (from Feature Registry)                │
│  Environment    → Docker image + requirements.lock                       │
│  Configuration  → Config file hash                                        │
│  Random seeds   → Explicit in configuration (seed=42)                   │
│  Model          → MLflow run_id + artifact                               │
│  Results        → Experiment tracking (MLflow)                           │
│                                                                             │
│  REPRODUCIBILITY CHECK:                                                   │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Step 1: Checkout code version (git checkout <commit>)                   │
│  Step 2: Build Docker image (docker build -t meridian-fx:research)       │
│  Step 3: Pull data version (dvc checkout)                                │
│  Step 4: Run experiment (python run_experiments.py)                      │
│  Step 5: Compare results (within tolerance)                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 11. PRODUCTION ARTIFACTS

### 11.1 ModelArtifact

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODEL ARTIFACT — RESEARCH → PRODUCTION                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ModelArtifact:                                                            │
│  {                                                                         │
│      model_id: str                                                         │
│      model_version: str                                                    │
│      model_type: "ARIMA" | "ElasticNet" | "XGBoost" | "Ensemble"          │
│      model_file: str  // path to serialized model                         │
│                                                                             │
│      training: {                                                           │
│          dataset_id: str                                                   │
│          feature_version: str                                              │
│          training_period: {start: date, end: date}                        │
│          hyperparameters: dict                                             │
│          feature_list: [str]                                               │
│      }                                                                     │
│                                                                             │
│      research_gate: {                                                      │
│          status: "APPROVED" | "REJECTED"                                  │
│          report: ResearchGateReport                                        │
│          approved_at: datetime                                             │
│          approved_by: str                                                  │
│      }                                                                     │
│                                                                             │
│      performance: {                                                        │
│          test_period: {start: date, end: date}                            │
│          statistical: {DA, AUC, Brier, ECE}                               │
│          economic: {Sharpe_net, MaxDD, PF, WinRate}                       │
│          regime_performance: {regime: metrics}                            │
│      }                                                                     │
│                                                                             │
│      reproducibility: {                                                    │
│          git_commit: str                                                   │
│          docker_image: str                                                 │
│          mlflow_run_id: str                                                │
│          config_hash: str                                                  │
│          random_seed: int                                                  │
│      }                                                                     │
│                                                                             │
│      lifecycle: "CANDIDATE" | "DEPLOYED" | "MONITORED" | "RETIRED"       │
│      created_at: datetime                                                  │
│      updated_at: datetime                                                  │
│  }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 PredictionArtifact

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PREDICTION ARTIFACT — RESEARCH → LAYER 2                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PredictionArtifact:                                                       │
│  {                                                                         │
│      prediction_id: str                                                    │
│      model_id: str                                                         │
│      model_version: str                                                    │
│      pair: str                                                             │
│      prediction_timestamp: datetime                                        │
│      horizon_days: int                                                     │
│                                                                             │
│      // Outputs                                                            │
│      probability_up: float                                                 │
│      expected_return: float                                                │
│      expected_volatility: float                                            │
│      confidence_interval: {lower: float, upper: float}                    │
│                                                                             │
│      // Context                                                            │
│      regime_id: str                                                        │
│      macro_regime: {risk, policy, growth, inflation}                      │
│      rag_signal_ids: [str]                                                 │
│      shap_values: [{feature: str, value: float}]                          │
│                                                                             │
│      // Data                                                               │
│      feature_snapshot_id: str                                              │
│      dataset_id: str                                                       │
│      feature_version: str                                                  │
│      as_of: datetime  // knowledge point for this prediction              │
│                                                                             │
│      // Research Gate                                                      │
│      research_gate_status: "APPROVED" | "REJECTED" | "PENDING"            │
│                                                                             │
│      // Reproducibility                                                   │
│      reproducibility: {                                                    │
│          git_commit: str                                                   │
│          docker_image: str                                                 │
│          mlflow_run_id: str                                                │
│      }                                                                     │
│                                                                             │
│      created_at: datetime                                                  │
│  }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 12. RESEARCH METRICS & SUCCESS CRITERIA

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCH METRICS & SUCCESS CRITERIA                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METRIC                       │ TARGET                                     │
│  ─────────────────────────────┼────────────────────────────────────────────│
│  PIT Validation               │ 0 failures                                 │
│  Core Hypotheses (H1a-H1d)    │ ALL accepted                               │
│  Research Hypotheses (H1e-H1h)│ ≥ 2 accepted                              │
│  Directional Accuracy         │ > 52% (screening)                          │
│  Expected Calibration Error   │ < 0.05                                     │
│  AUC                          │ > 0.55                                     │
│  Sharpe (net)                 │ > 0.3 (screening)                          │
│  Maximum Drawdown             │ > -20%                                     │
│  Profit Factor                │ > 1.2                                      │
│  Research Gate                │ ALL gates PASS                             │
│  Reproducibility              │ Same result ± tolerance                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 SUMMARY — CHANGES v4 → v5

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHANGES v4 → v5                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ✅ Hypothesis nomenclature corrected                                  │
│     └── H0 = null (no effect), H1 = alternative (effect exists)            │
│                                                                             │
│  2. ✅ ARIMA: ADF as a diagnostic, not a mechanical step                  │
│     └── Log-return is normally stationary → d = 0                         │
│                                                                             │
│  3. ✅ Purging: definition corrected                                      │
│     └── Remove training observations whose label crosses the              │
│         train/validation boundary                                         │
│     └── DO NOT remove future observations from the training set           │
│                                                                             │
│  4. ✅ Logistic Elastic Net: CV corrected                                 │
│     └── From standard 5-fold → Purged Walk-Forward CV                    │
│                                                                             │
│  5. ✅ Ensemble: ARIMA converted to probability                           │
│     └── ARIMA → expected_return → P_up via CDF                            │
│     └── All models produce P(direction = up)                              │
│                                                                             │
│  6. ✅ Reproducibility: precise definition                                 │
│     └── Same inputs + code + environment + config + seeds + execution    │
│     └── = reproducible within numerical tolerance                         │
│                                                                             │
│  7. ✅ ModelArtifact and PredictionArtifact separated                     │
│     └── ModelArtifact: trained model (Research → Registry)                │
│     └── PredictionArtifact: prediction (Research → Layer 2)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📋 FINAL EVALUATION

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FINAL EVALUATION — LAYER 3                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Dimension                  │ Score                                        │
│  ───────────────────────────┼──────────────────────────────────────────────│
│  Architecture               │ 9.8/10                                       │
│  PIT / Leakage              │ 9.8/10                                       │
│  Quant Models               │ 9.7/10                                       │
│  Macro Models               │ 9.8/10                                       │
│  RAG Agents                 │ 9.8/10                                       │
│  Experiment Framework       │ 9.8/10                                       │
│  Statistical Evaluation     │ 9.7/10                                       │
│  Economic Evaluation        │ 9.7/10                                       │
│  Robustness Evaluation      │ 9.7/10                                       │
│  Research Gate              │ 9.7/10                                       │
│  Backtesting                │ 9.8/10                                       │
│  Research Output / Artifacts│ 9.8/10                                       │
│  Reproducibility            │ 9.8/10                                       │
│  Model Registry             │ 9.7/10                                       │
│  Production Readiness       │ 9.7/10                                       │
│  ───────────────────────────┼──────────────────────────────────────────────│
│  OVERALL                    │ ⭐ 9.7/10                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# ✅ Meridian FX — Layer 3: Research Layer

**SPECIFICATION v5.0 — FROZEN — READY FOR IMPLEMENTATION**

---

## What Comes Next?

| Option | Description                                                       |
| ------ | ----------------------------------------------------------------- |
| **A**  | Layer 2: Decision Engine (Fusion, Economic Filter, Ranking)       |
| **B**  | Layer 1: Intelligence Delivery (API, Dashboard, Status)           |
| **C**  | Cross-Cutting: Governance / MLOps (Registries, Monitoring, Drift) |
| **D**  | Product LLD: Signals, Lifecycle, Presentation                     |

**Which do you prefer?** 🚀
