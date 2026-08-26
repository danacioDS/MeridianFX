# 📊 MERIDIAN FX — Minimum Viable Product

---


## 📌 CORE PRINCIPLE

> **"Meridian does not produce predictions. It produces actionable, traceable, explainable, and evaluable financial intelligence."**

The system transforms macro, market, and textual data into **four concrete output levels** for each currency pair, the global macro context, and the broader market landscape.

---

## 🎯 OUTPUT ARCHITECTURE (4 Levels)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MERIDIAN FX — OUTPUTS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              LEVEL 1 — FORECAST (Per Currency)                      │    │
│  │     Direction · Calibrated Probability · Expected Return            │    │
│  │     + Volatility · Prediction Intervals · Actionability             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │           LEVEL 2 — DRIVERS & EXPLANATION (Per Currency)            │    │
│  │     SHAP · Macro Regime + Stability · RAG + Sensitivity            │    │
│  │     + Risks · Executive Narrative                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │           LEVEL 3 — GLOBAL INTELLIGENCE (Multi-Asset)              │    │
│  │     Rankings · Divergences · Cross-Correlations                    │    │
│  │     + Early Warnings · Macro Context · Calendar                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │           LEVEL 4 — EVALUATION & LEARNING (Audit)                  │    │
│  │     Prediction vs Reality · Calibration · Performance by Regime    │    │
│  │     + Aggregated Metrics · Degradation Detection                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📋 LEVEL 1 — FORECAST (Per Currency)

**Purpose:** Answer *"What is going to happen to this currency, and with what certainty?"*

### Conceptual Structure

```text
FORECAST
├── Identification
│   ├── pair: "USD/JPY"
│   ├── timestamp: UTC
│   └── horizon: "5D"
│
├── Central Prediction
│   ├── direction: bullish / bearish / neutral
│   ├── raw_probability: 0.74 (model output)
│   ├── calibrated_probability: 0.68 (statistically calibrated)
│   ├── expected_return: 0.0082 (log return)
│   └── expected_return_pct: 0.82%
│
├── Uncertainty Quantification
│   ├── volatility
│   │   ├── expected_vol_annualized: 0.12
│   │   ├── expected_vol_horizon: 0.023
│   │   └── volatility_regime: normal / elevated / extreme
│   ├── prediction_interval (distribution)
│   │   ├── lower_10p: -0.0080
│   │   ├── median: 0.0082
│   │   └── upper_10p: 0.0230
│   └── prediction_interval_95
│       ├── lower: -0.0031
│       └── upper: 0.0195
│
└── Economic Filter (Actionability)
    ├── gross_return: 0.0082
    ├── total_cost: 0.0020 (spread + commission + slippage)
    ├── net_return: 0.0062
    ├── minimum_edge: 0.0020
    ├── edge_ratio: 3.1 (net_return / total_cost)
    ├── actionable: true / false
    ├── signal_strength: weak / moderate / strong
    └── position_sizing_factor: 0.75 (0-1, optional in MVP)
```

### Key Definitions

| Concept                    | Definition                                                 | Notes                         |
| -------------------------- | ---------------------------------------------------------- | ----------------------------- |
| **Raw Probability**        | Direct model output                                        | May be biased                 |
| **Calibrated Probability** | Transformed via Platt/Isotonic                             | Statistically meaningful      |
| **Expected Return**        | Mean of predictive distribution                            | Log-return                    |
| **Expected Volatility**    | Standard deviation over horizon                            | Annualized then scaled        |
| **Prediction Interval**    | Range where future return falls with specified probability | Based on full distribution    |
| **Total Cost**             | Spread + Commission + Slippage                             | Combined friction estimate    |
| **Net Return**             | Return after all costs                                     | The final economic criterion  |
| **Edge Ratio**             | Net Return / Total Cost                                    | > 2 indicates meaningful edge |

### Probability Definition

```text
P(return_horizon > 0 | I_t)
```

Where `I_t` represents all information available at time `t`.

---

# 📋 LEVEL 2 — DRIVERS & EXPLANATION (Per Currency)

**Purpose:** Answer *"Why does Meridian predict this?"*

### Conceptual Structure

```text
DRIVERS & EXPLANATION
├── Quantitative Drivers (SHAP)
│   ├── Feature 1: us_jp_rate_spread
│   │   ├── value: 3.42
│   │   ├── contribution: 0.31 (absolute)
│   │   ├── contribution_pct: 42.0%
│   │   ├── direction: positive
│   │   └── z_score_1y: 1.8
│   ├── Feature 2: vix
│   │   ├── value: 16.8
│   │   ├── contribution: -0.18
│   │   ├── contribution_pct: 24.0%
│   │   ├── direction: negative
│   │   └── z_score_1y: -0.6
│   └── ... (top 5 features)
│
├── Macro Regime
│   ├── us_regime: restrictive
│   ├── jp_regime: accommodative
│   ├── growth_regime: moderate
│   ├── risk_regime: risk_on
│   ├── inflation_regime: normal
│   ├── regime_confidence: 0.85
│   ├── regime_stability_score: 0.72
│   └── regime_transition_risk: low / medium / high
│
├── RAG Signal (Central Banks)
│   ├── fed_sentiment: hawkish
│   ├── fed_score: 0.72
│   ├── fed_zscore_12m: 1.2
│   ├── boj_sentiment: dovish
│   ├── boj_score: 0.28
│   ├── boj_zscore_12m: -0.8
│   ├── policy_divergence: 0.44
│   ├── divergence_percentile_12m: 82%
│   ├── forward_guidance_change: 0.15
│   ├── surprise_vs_previous: 0.08
│   └── document_metadata
│       ├── source: FOMC
│       ├── published_at: 2026-08-20T14:00:00Z
│       └── document_type: minutes
│
├── Event Sensitivity
│   ├── fed_meeting: 0.32 (estimated impact)
│   ├── boj_meeting: 0.28
│   ├── us_cpi: 0.25
│   ├── geopolitical: 0.18
│   └── regime_switch_impact
│       ├── risk_off_to_risk_on: 0.15
│       ├── accommodative_to_restrictive: 0.22
│       └── intervention: 0.35
│
└── Executive Narrative
    ├── narrative: "2-3 paragraph executive summary"
    ├── key_factors: ["Factor 1", "Factor 2", "Factor 3"]
    └── risks: [
        {"risk": "Description", "probability": "low/medium/high", "impact": "low/medium/high"}
    ]
```

### Important Methodological Note

> **SHAP contribution represents model attribution, not economic causality.**

SHAP indicates how much a feature contributed to the model's output for that specific observation, not that the feature caused the market movement.

---

# 📋 LEVEL 3 — GLOBAL INTELLIGENCE (Multi-Asset)

**Purpose:** Answer *"What is happening in the broader market?"*

### Conceptual Structure

```text
GLOBAL INTELLIGENCE
├── Global Risk
│   ├── regime: risk_on / risk_off / neutral
│   ├── vix_level: 16.8
│   ├── vix_percentile_1y: 32%
│   ├── risk_appetite_score: 0.72 (0-1)
│   ├── risk_appetite_trend: improving / stable / deteriorating
│   └── systemic_risk_indicator: 0.18 (0-1)
│
├── Currency Rankings
│   ├── strongest: [
│   │   {"pair": "USD/MXN", "score": 0.82, "probability": 0.76, "actionable": true},
│   │   {"pair": "USD/JPY", "score": 0.74, "probability": 0.68, "actionable": true}
│   │ ]
│   └── weakest: [
│       {"pair": "EUR/USD", "score": -0.58, "probability": 0.32, "actionable": true}
│       ]
│
├── Cross-Correlations
│   ├── usd_strength_correlation
│   │   ├── USD/JPY: 0.82
│   │   ├── USD/MXN: 0.78
│   │   └── EUR/USD: -0.85
│   ├── risk_sensitivity
│   │   ├── USD/JPY: 0.72
│   │   └── USD/MXN: 0.85
│   └── independent_signals
│       └── [Pairs with signals uncorrelated with USD strength]
│
├── Divergences
│   ├── interest_rate
│   │   ├── pair: USD/JPY
│   │   ├── description: "Widening US-JP yield differential at 3.42%"
│   │   ├── divergence_score: 0.78
│   │   └── percentile_1y: 92%
│   ├── policy
│   │   ├── pair: USD/JPY
│   │   ├── divergence_score: 0.71
│   │   └── percentile_1y: 85%
│   └── positioning
│       ├── pair: USD/JPY
│       ├── divergence_score: 0.62
│       └── percentile_1y: 95%
│
├── Early Warnings
│   ├── [1]: VIX_signal
│   │   ├── alert: "VIX dropped below 18, risk-on regime confirmed"
│   │   └── severity: info
│   ├── [2]: positioning_alert
│   │   ├── alert: "JPY short positioning at 1-year extreme"
│   │   └── severity: warning
│   └── [3]: policy_divergence
│       ├── alert: "Fed-BoJ divergence at 92nd percentile"
│       └── severity: info
│
└── Macro Context
    ├── global_growth: moderate
    ├── global_growth_trend: stable
    ├── global_inflation: normalizing
    ├── global_inflation_trend: improving
    ├── key_events_today: [List of relevant events]
    └── economic_calendar: [Upcoming events with impact]
```

### Scoring Framework

The `score` for each pair is calculated as:

```text
Score = 
    w1 * Quant_Signal
    + w2 * Macro_Regime_Score
    + w3 * RAG_Policy_Score
    + w4 * Positioning_Score
    + w5 * Risk_Regime_Score
    + w6 * Momentum_Score

Where:
- w1 + w2 + w3 + w4 + w5 + w6 = 1.0
- Weights are calibrated out-of-sample using walk-forward evaluation
- Each signal is normalized to [-1, +1]
- Final score ∈ [-1, +1]
```

---

# 📋 LEVEL 4 — EVALUATION & LEARNING (Audit)

**Purpose:** Answer *"How good was Meridian at predicting this?"*

### Conceptual Structure

```text
EVALUATION & LEARNING
├── Per Prediction
│   ├── prediction_id: "pred-20260825-1700-001"
│   ├── status: pending / realized
│   ├── forecast: {direction, probability, expected_return}
│   ├── realized: {return, direction, return_pct} (if realized)
│   └── evaluation: {
│       direction_correct: true/false,
│       absolute_error: 0.0009,
│       brier_score: 0.1024,
│       calibration_error: 0.03
│   }
│
├── Model Evaluation Metrics
│   ├── Directional Accuracy
│   ├── AUC
│   ├── Brier Score
│   ├── Log Loss
│   ├── Expected Calibration Error (ECE)
│   └── Calibration Curve
│
├── Strategy Evaluation Metrics
│   ├── Sharpe Ratio
│   ├── Sortino Ratio
│   ├── Maximum Drawdown
│   ├── Profit Factor
│   ├── Net Return
│   └── Information Coefficient
│
├── Performance by Regime
│   ├── Risk-On: {DA, Sharpe, Drawdown}
│   ├── Risk-Off: {DA, Sharpe, Drawdown}
│   └── Neutral: {DA, Sharpe, Drawdown}
│
└── Degradation Detection
    ├── model_drift_score: 0.12 (threshold > 0.3)
    ├── feature_drift_detected: false
    ├── performance_drop_detected: false
    └── alert: none
```

### Model vs Strategy Evaluation

```text
MODEL EVALUATION (Statistical)
├── Directional Accuracy
├── AUC
├── Brier Score
├── Log Loss
├── Expected Calibration Error
└── Calibration Curve

STRATEGY EVALUATION (Economic)
├── Net Return
├── Sharpe Ratio
├── Sortino Ratio
├── Maximum Drawdown
├── Profit Factor
└── Hit Rate
```

### Purpose of Level 4

1. **Close the loop:** Meridian learns from its errors
2. **Auditability:** Every prediction can be evaluated
3. **Transparency:** Users see historical performance
4. **Early detection:** Model degradation identified before impacting production
5. **Continuous improvement:** Calibration updated periodically

---

# 🔄 OUTPUT GENERATION FLOW

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT GENERATION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [INPUTS]                                                                   │
│  Market Data · Macro Data · Text Data · Positioning · Regime               │
│                                    │                                        │
│                                    ▼                                        │
│  [FEATURE GENERATION]                                                       │
│  Features → PIT Join → Validation → Feature Store                         │
│                                    │                                        │
│                                    ▼                                        │
│  [MODEL INFERENCE]                                                          │
│  Quant Model → SHAP → Macro Agent → RAG Agent                            │
│                                    │                                        │
│                                    ▼                                        │
│  [DECISION ENGINE]                                                          │
│  Signal Fusion → Economic Filter → Decision Score                         │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          OUTPUTS                                     │   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │   │
│  │  │  LEVEL 1    │  │  LEVEL 2    │  │        LEVEL 3              │  │   │
│  │  │  FORECAST   │  │  DRIVERS &  │  │    GLOBAL INTELLIGENCE      │  │   │
│  │  │             │  │ EXPLANATION │  │                             │  │   │
│  │  │ Direction   │  │ SHAP        │  │ Currency Rankings           │  │   │
│  │  │ Probability │  │ Macro       │  │ Divergences                 │  │   │
│  │  │ Return      │  │ RAG         │  │ Early Warnings              │  │   │
│  │  │ Volatility  │  │ Risks       │  │ Macro Context               │  │   │
│  │  │ Actionable  │  │ Narrative   │  │ Economic Calendar           │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      LEVEL 4 — EVALUATION ENGINE                     │   │
│  │                                                                      │   │
│  │  Realized Returns → Performance Metrics → Calibration → Learning    │   │
│  │                                                                      │   │
│  │  Output: Performance Dashboard · Drift Alerts · Updated Calibration │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# ✅ OUTPUT QUALITY CRITERIA

| Criterion          | Description                                | Validation                                    |
| ------------------ | ------------------------------------------ | --------------------------------------------- |
| **Temporality**    | All outputs have UTC timestamp             | `knowledge_timestamp <= generation_timestamp` |
| **Traceability**   | Every output has complete lineage          | Prediction ID → Model → Features → Data       |
| **Consistency**    | Forecasts vs actuals auditable             | Prediction Registry                           |
| **Explainability** | Every output has SHAP or RAG rationale     | Visualizations generated                      |
| **Actionability**  | `actionable` flag indicates tradability    | Net Return > Minimum Edge                     |
| **Calibration**    | Probabilities are statistically meaningful | Brier Score, ECE                              |
| **Robustness**     | Performance consistent across regimes      | Regime-based analysis                         |

---

# 📊 OUTPUTS BY USER PROFILE

| User Profile            | Primary Outputs                                        | Format             | Frequency                     |
| ----------------------- | ------------------------------------------------------ | ------------------ | ----------------------------- |
| **All Users**           | Forecast, Actionability                                | Dashboard          | Post-ingestion                |
| **Quant Analysts**      | Drivers, SHAP, RAG, Sensitivity                        | Dashboard / JSON   | Post-ingestion                |
| **Investors / Traders** | Forecasts, Rankings, Divergences                       | Dashboard / Brief  | Daily                         |
| **Risk Managers**       | Correlations, Early Warnings, Sensitivity              | Dashboard / Alerts | Post-ingestion / Event-driven |
| **Executives**          | Global Intelligence, Morning Brief                     | Brief / PDF        | Daily                         |
| **ML Researchers**      | Evaluation Metrics, Performance by Regime, Calibration | Dashboard / JSON   | Post-realization              |
| **Auditors**            | Complete Lineage, Prediction Registry                  | Database           | On-demand                     |

---

# 📐 FORMAL MATHEMATICAL DEFINITIONS

## 1. Forecast & Calibration

**Calibrated Probability:**

```text
P_cal = f(P_raw)  [Platt Scaling / Isotonic Regression]
```

**Expected Return:**

```text
E[R] = E[log(S_{t+h} / S_t) | I_t]
```

**Scaled Volatility:**

```text
σ_h = σ_annual * sqrt(h / 252)
```

## 2. Economic Actionability Filter

**Net Return:**

```text
R_net = E[R] - Spread - Slippage - Commission
```

**Total Cost:**

```text
Total_Cost = Spread + Slippage + Commission
```

**Edge Ratio:**

```text
Edge_Ratio = R_net / Total_Cost
```

**Actionability Criterion:**

```text
Actionable = R_net > MinEdge
```

## 3. Evaluation Metrics

**Directional Accuracy:**

```text
DA = (1/N) * Σ I(sign(y_pred) == sign(y_real))
```

**Brier Score:**

```text
Brier = (1/N) * Σ (P_pred - y_real)²
```

**Expected Calibration Error (ECE):**

```text
ECE = Σ_{b=1}^{B} (n_b/N) * |accuracy_b - confidence_b|
```

**Sharpe Ratio:**

```text
Sharpe = (E[R_p] - R_f) / σ_p * sqrt(252)
```

## 4. Global Intelligence

**Pair Score:**

```text
Score_pair = Σ w_i * Signal_i
```

**Cross-Correlation:**

```text
Correlation = Corr(Returns_pair1, Returns_pair2)
```

**Divergence Score:**

```text
Divergence = Signal_i - Historical_Percentile(Signal_i)
```

**Independence Score:**

```text
Independence = 1 - |Correlation(Signal, Market_Factor)|
```

---

# 🗺️ ROADMAP & DELIVERY PRIORITIES

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         IMPLEMENTATION ROADMAP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [MVP — Deliverable 1]                                                     │
│  ├── Level 1: Complete Forecast                                           │
│  ├── Level 2: SHAP + Basic Macro                                          │
│  └── Level 4: Basic Evaluation (DA, Sharpe)                               │
│                                                                             │
│                                    ▼                                        │
│                                                                             │
│  [V2 — Deliverable 2]                                                      │
│  ├── Level 2: Complete RAG                                                │
│  ├── Level 3: Basic Global Intelligence (Rankings)                        │
│  └── Level 4: Calibration                                                 │
│                                                                             │
│                                    ▼                                        │
│                                                                             │
│  [V3 — Deliverable 3]                                                      │
│  ├── Level 3: Correlations, Divergences, Early Warnings                   │
│  ├── Level 4: Performance by Regime                                       │
│  └── Morning Brief                                                        │
│                                                                             │
│                                    ▼                                        │
│                                                                             │
│  [V4 — Deliverable 4]                                                      │
│  ├── Level 3: Full Multi-Asset                                            │
│  ├── Level 4: Drift Detection                                             │
│  └── Complete Currency Radar                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📋 DATA PROVENANCE & QUALITY

## Data Provenance (Internal Metadata)

```text
DATA PROVENANCE
├── source: Original data source
├── source_timestamp: When data was published
├── ingestion_timestamp: When Meridian ingested it
├── knowledge_timestamp: When data became available to the model
├── revision_timestamp: When data was revised
├── availability_timestamp: When data was actually accessible
└── data_quality_status: high / medium / low
```

## Data Quality Score

```text
DATA QUALITY
├── market_data_quality: high / medium / low
├── macro_data_quality: high / medium / low
├── text_data_quality: high / medium / low
├── missing_features_count: 0
├── stale_features_count: 1
└── overall_quality_score: 0.94 (0-1)
```

---

# 🎯 SUMMARY

| Aspect              | Meridian FX Outputs                                          |
| ------------------- | ------------------------------------------------------------ |
| **Level 1**         | Forecast with uncertainty and economic filter                |
| **Level 2**         | Drivers with SHAP, Macro, RAG, and narrative                 |
| **Level 3**         | Global intelligence with rankings, divergences, correlations |
| **Level 4**         | Evaluation with model and strategy metrics                   |
| **Core Principles** | Actionable · Explainable · Traceable · Evaluable             |
| **MVP Scope**       | Levels 1-2 (partial) + Level 4 (basic)                       |
| **Target Users**    | Analysts · Traders · Risk Managers · Executives · Auditors   |

---

**Meridian FX — Output Specification Document v2.1** ✅
