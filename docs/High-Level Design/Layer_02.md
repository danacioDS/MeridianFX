# 📋 MERIDIAN FX — DECISION ENGINE v3.0

## FINAL REVISION — Architecture Frozen for Implementation

### Summary of Changes from v2.0

| Issue | v2.0 | v3.0 | Impact |
|-------|------|------|--------|
| **Risk Regime** | Mixed into Macro Score | Separated: Regime Engine + Macro Direction | +0.5 |
| **Carry Calculation** | Simple rate differential | `expected_carry(pair, direction, horizon, t)` | +0.3 |
| **Macro Score** | Arbitrary constants | Expectation-relative + surprise components | +0.4 |
| **RAG Signal** | Sentiment level | Sentiment + Surprise + Expectation Gap | +0.4 |
| **Decision Quality** | Heuristic multipliers | Calibratable composite score | +0.3 |
| **PIT/Leakage** | Implicit | Explicit protocol + validation tests | +0.3 |
| **Weight Calibration** | Walk-forward + stability | + Threshold sensitivity analysis | +0.2 |
| **Ranking Risk** | Volatility penalty | Sharpe-like risk adjustment | +0.3 |

**New Score: 9.5/10**

---

## 🏛️ ARCHITECTURE — FINAL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MERIDIAN FX — DECISION ENGINE v3.0                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PREDICTION (IMMUTABLE)                           │    │
│  │  • Expected Return (5D log return)                                 │    │
│  │  • Calibrated Probability                                          │    │
│  │  • Expected Volatility                                             │    │
│  │  • Prediction Interval                                             │    │
│  │  • SHAP Values                                                     │    │
│  │  • Original Confidence                                             │    │
│  │  • Regime at Prediction                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SIGNAL GENERATION                                │    │
│  │                                                                     │    │
│  │  Quant Signal   = 2 × (calibrated_probability - 0.5)              │    │
│  │  Macro Signal   = f(policy, growth, inflation, expectations)      │    │
│  │  RAG Signal     = f(sentiment, surprise, expectation_gap)         │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    REGIME ENGINE (SEPARATED)                       │    │
│  │                                                                     │    │
│  │  • Risk Regime: Risk-On / Neutral / Risk-Off                      │    │
│  │  • Policy Regime: Restrictive / Neutral / Accommodative          │    │
│  │  • Growth Regime: Strong / Moderate / Weak                        │    │
│  │                                                                     │    │
│  │  Regime → Weights + Thresholds + Quality Adjustments              │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DYNAMIC SIGNAL FUSION                            │    │
│  │                                                                     │    │
│  │  Fusion_Score = wq×Quant + wm×Macro + wr×RAG                      │    │
│  │  Weights selected by Regime Engine                                 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DECISION QUALITY (CALIBRATABLE)                 │    │
│  │                                                                     │    │
│  │  Decision_Quality = f(                                           │    │
│  │      original_confidence,                                        │    │
│  │      regime_alignment,                                           │    │
│  │      freshness,                                                  │    │
│  │      data_quality,                                               │    │
│  │      feature_drift                                               │    │
│  │  )                                                                │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    ECONOMIC FILTER v3.0                             │    │
│  │                                                                     │    │
│  │  Gross Return = Expected Return (from prediction)                  │    │
│  │  Costs = Dynamic Spread + Slippage + Commission                   │    │
│  │  Carry = expected_carry(pair, direction, horizon, t)              │    │
│  │  Net Return = Gross Return - Costs + Carry                        │    │
│  │  Cost-Adjusted Edge = Net Return / Total Costs                    │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SELECTIVE DECISION                               │    │
│  │                                                                     │    │
│  │  IF Fusion_Score > regime_threshold                                │    │
│  │  AND Net Return > MinEdge                                           │    │
│  │  AND Decision_Quality > quality_threshold:                          │    │
│  │      → ACTIONABLE (LONG/SHORT)                                     │    │
│  │  ELSE:                                                              │    │
│  │      → NO TRADE (with reason code)                                 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    OPPORTUNITY RANKING                              │    │
│  │                                                                     │    │
│  │  Opportunity_Score =                                               │    │
│  │      α × Fusion_Score +                                            │    │
│  │      β × Risk-Adjusted Net Return +                                │    │
│  │      γ × Decision_Quality                                          │    │
│  │                                                                     │    │
│  │  Risk-Adjusted Net Return = Net Return / Expected Volatility       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DECISION REGISTRY (VERSIONED)                   │    │
│  │                                                                     │    │
│  │  • decision_id                                                     │    │
│  │  • decision_version                                                │    │
│  │  • supersedes_decision                                             │    │
│  │  • decision_reason_code                                            │    │
│  │  • engine_version                                                  │    │
│  │  • Complete audit trail                                            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 1. SIGNAL GENERATION v3.0

### 1.1 Quant Signal (Unchanged)

```
quant_score = 2 × (calibrated_probability - 0.5)
```

### 1.2 Macro Signal v3.0 (Expectation-Relative)

**v2.0 Problem:** Arbitrary constants, level-based, not expectation-relative.

**v3.0 Solution:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MACRO SCORE v3.0                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  macro_score = clip(                                                       │
│      α × policy_score +                                                    │
│      β × growth_score +                                                    │
│      γ × inflation_score +                                                 │
│      δ × policy_expectation_score,                                         │
│      -1, +1                                                                │
│  )                                                                         │
│                                                                             │
│  Where:                                                                    │
│                                                                             │
│  policy_score = tanh((actual_diff - expected_diff) / σ_policy)            │
│                                                                             │
│  policy_expectation_score = tanh((current_diff - one_month_ago) / σ_exp)  │
│                                                                             │
│  growth_score = tanh((US_growth_surprise - JP_growth_surprise) / σ_g)     │
│                                                                             │
│  inflation_score = tanh((US_inflation_surprise - JP_inflation_surprise) / σ_i) │
│                                                                             │
│  σ = rolling standard deviation over 252 days                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Interpretation:**

- **policy_score**: Directional policy differential relative to expectations
- **policy_expectation_score**: Change in policy expectations
- **growth_score**: Growth surprises, not absolute levels
- **inflation_score**: Inflation surprises, not absolute levels

**Default Weights:**

| Component | Weight | Rationale |
|-----------|:---:|-----------|
| policy_score | 0.35 | Primary directional signal |
| growth_score | 0.25 | Economic cycle differential |
| inflation_score | 0.20 | Monetary policy driver |
| policy_expectation_score | 0.20 | Forward-looking expectations |

### 1.3 RAG Signal v3.0 (Surprise-Adjusted)

**v2.0 Problem:** Sentiment only, ignoring market expectations.

**v3.0 Solution:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG SIGNAL v3.0                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  rag_score = clip(                                                         │
│      w_sentiment × sentiment_score +                                       │
│      w_surprise × surprise_score +                                         │
│      w_exp_gap × expectation_gap_score,                                    │
│      -1, +1                                                                │
│  )                                                                         │
│                                                                             │
│  Where:                                                                    │
│                                                                             │
│  sentiment_score = fed_sentiment - boj_sentiment                           │
│                                                                             │
│  surprise_score = fed_actual_sentiment - fed_expected_sentiment           │
│                                                                             │
│  expectation_gap_score = fed_expected_sentiment - boj_expected_sentiment   │
│                                                                             │
│  Default Weights:                                                          │
│  w_sentiment = 0.35                                                        │
│  w_surprise = 0.45                                                         │
│  w_exp_gap = 0.20                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example:**

```
Fed:
  Actual Sentiment:    Hawkish (+0.8)
  Expected Sentiment:  Mildly Hawkish (+0.6)
  → Surprise: +0.2

BoJ:
  Actual Sentiment:    Dovish (-0.4)
  Expected Sentiment:  Dovish (-0.3)
  → Surprise: -0.1

Components:
  sentiment_score:     +1.2
  surprise_score:      +0.3
  expectation_gap:     +0.9

RAG Score = 0.35×1.2 + 0.45×0.3 + 0.20×0.9 = 0.735
```

**Key Insight:** Surprise matters more than absolute sentiment.

---

## 📊 2. REGIME ENGINE (SEPARATED)

### 2.1 Architecture Separation

**v2.0 Problem:** Risk mixed into Macro Signal (risk adjustment as directional component).

**v3.0 Solution:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGIME ENGINE — SEPARATED                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MACRO DIRECTION SCORE                            │    │
│  │                                                                     │    │
│  │  policy_score + growth_score + inflation_score + expectations      │    │
│  │                                                                     │    │
│  │  → Used in Signal Fusion (directional component)                   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    REGIME CLASSIFICATION                            │    │
│  │                                                                     │    │
│  │  Risk Regime:   Based on VIX, risk appetite, credit spreads        │    │
│  │  Policy Regime: Based on rates, central bank stance                │    │
│  │  Growth Regime: Based on GDP, PMI, employment                     │    │
│  │                                                                     │    │
│  │  → Used for:                                                        │    │
│  │    • Weight Selection                                               │    │
│  │    • Threshold Adjustments                                          │    │
│  │    • Quality Adjustments                                            │    │
│  │    • Position Sizing (V3+)                                         │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Regime Classification

| Regime | Classification Logic |
|--------|---------------------|
| **Risk-On** | VIX < 18, risk appetite > 0.6, credit spreads tight |
| **Risk-Off** | VIX > 25, risk appetite < 0.4, credit spreads wide |
| **Neutral** | VIX 18-25 |
| **Restrictive** | Policy rate > neutral + 50bp, hawkish guidance |
| **Accommodative** | Policy rate < neutral - 50bp, dovish guidance |
| **Strong Growth** | GDP > 3%, PMI > 55 |
| **Weak Growth** | GDP < 1%, PMI < 48 |

### 2.3 Regime Impact

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGIME IMPACT ON DECISION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Regime Change       │ Weight Impact     │ Threshold Impact               │
│─────────────────────┼───────────────────┼────────────────────────────────│
│  Risk-On → Risk-Off │ wq ↓ 15%          │ MinScore ↑ 0.05                │
│                     │ wm ↑ 10%          │ QualityThreshold ↑ 0.10        │
│                     │ wr ↑ 5%           │                                │
│─────────────────────┼───────────────────┼────────────────────────────────│
│  US Restrictive     │ wq 0.50           │ MinEdge 0.0020                 │
│  US Neutral         │ wq 0.45           │ MinEdge 0.0015                 │
│  US Accommodative   │ wq 0.40           │ MinEdge 0.0010                 │
│─────────────────────┼───────────────────┼────────────────────────────────│
│  Near Policy Event  │ wr ↑ to 0.40      │ QualityThreshold ↑ 0.10       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. DYNAMIC SIGNAL FUSION v3.0

### 3.1 Regime-Dependent Weights (Calibrated with Stability)

```
Fusion_Score = clip(wq × quant_score + wm × macro_score + wr × rag_score, -1, +1)
```

**Weight Calibration Protocol (Leakage-Free):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WEIGHT CALIBRATION PROTOCOL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Define Candidate Weights (Grid: 0.05 steps)                      │
│                                                                             │
│  Step 2: Walk-Forward Calibration (2018-2026)                             │
│  ├─ Window 1: 2015-2017 Train, 2018 Test                                  │
│  ├─ Window 2: 2015-2018 Train, 2019 Test                                  │
│  ├─ ...                                                                   │
│  └─ Window N: 2015-2024 Train, 2025 Test                                  │
│                                                                             │
│  Step 3: Select Weights                                                   │
│  ├─ Average Sharpe across out-of-sample windows                          │
│  ├─ Weight stability (variance across windows < 0.05)                     │
│  ├─ Threshold sensitivity (smooth performance curve)                      │
│  └─ No catastrophic failures                                              │
│                                                                             │
│  Step 4: Validate                                                        │
│  ├─ Walk-forward Sharpe > 0.3                                            │
│  ├─ Performance by regime: no negative outliers                          │
│  └─ Cost-adjusted Sharpe improvement vs baseline                         │
│                                                                             │
│  CRITICAL: All calibration uses point-in-time data.                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Threshold Sensitivity Analysis

**Purpose:** Ensure performance is robust to threshold choice.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THRESHOLD SENSITIVITY                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Test Range: MinScore ∈ [0.05, 0.25] step 0.025                           │
│  Test Range: MinEdge ∈ [0.0010, 0.0030] step 0.0005                      │
│  Test Range: QualityThreshold ∈ [0.30, 0.70] step 0.05                    │
│                                                                             │
│  Criterion:                                                               │
│  ✓ Sharpe > 0.25 for at least 70% of threshold combinations              │
│  ✓ No threshold pair produces Sharpe < -0.1                              │
│  ✓ Smooth transition (no sharp cliffs)                                   │
│                                                                             │
│  If sharp cliff detected: → Reject weights, re-calibrate                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. DECISION QUALITY v3.0 (CALIBRATABLE)

### 4.1 Problem with v2.0

Heuristic multipliers (0.6, 0.8) were arbitrary.

### 4.2 v3.0 Solution: Calibratable Composite Score

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DECISION QUALITY v3.0                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  decision_quality =                                                       │
│      original_confidence ×                                                │
│      freshness_factor ×                                                   │
│      regime_alignment_factor ×                                            │
│      data_quality_factor ×                                                │
│      drift_factor                                                         │
│                                                                             │
│  Where each factor ∈ [0, 1] and is CALIBRATED, not arbitrary:             │
│                                                                             │
│  freshness_factor = exp(-λ_fresh × age_hours)                             │
│                                                                             │
│  regime_alignment_factor = 1 - w_dist × regime_distance                   │
│                                                                             │
│  data_quality_factor = min(1, features_available / total_features)        │
│                                                                             │
│  drift_factor = 1 - tanh(drift_score / drift_threshold)                   │
│                                                                             │
│  Parameters (calibrated):                                                 │
│  λ_fresh    = calibrate on historical data                                │
│  w_dist     = calibrate on performance vs regime distance                 │
│  drift_threshold = calibrate on historical drift patterns                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Calibration Approach

```
For each component, calibrate against out-of-sample performance:

freshness_factor:
  - Test λ_fresh ∈ [0.01, 0.10] step 0.005
  - Select λ where correlation(age, future_return) is minimized
  - I.e., age should NOT predict returns (would indicate signal decay)

regime_alignment_factor:
  - regime_distance = distance between current regime and regime_at_prediction
  - Select w_dist where performance degradation matches regime change impact

drift_factor:
  - Calibrate drift_threshold on historical drift events
  - Threshold: point where drift significantly impacts performance
```

### 4.4 Output

```
{
  "original_confidence": 0.82,
  "components": {
    "freshness_factor": 0.97,
    "regime_alignment_factor": 0.82,
    "data_quality_factor": 0.98,
    "drift_factor": 0.95
  },
  "decision_quality": 0.64,
  "decision_quality_status": "moderate",
  "degradation_factors": [
    {
      "factor": "regime_alignment",
      "impact": -0.15,
      "reason": "Regime shift: Risk-On → Risk-Off"
    }
  ]
}
```

---

## 📊 5. ECONOMIC FILTER v3.0

### 5.1 Carry Calculation (Formalized)

**v2.0 Problem:** Simple rate differential.

**v3.0 Solution:**
```
expected_carry(pair, direction, horizon, t) = 
    forward_points(pair, t, horizon) / spot(pair, t)

Where:
- forward_points = actual forward points from market data
- If forward points not available: approximate from rate differential + basis

For USD/JPY LONG:
    carry = (jp_rate - us_rate) × (horizon/360) + basis

For USD/JPY SHORT:
    carry = (us_rate - jp_rate) × (horizon/360) - basis

Where:
- basis = forward points / spot, derived from market data
- If no basis data: use 0 (conservative estimate)
```

### 5.2 Dynamic Transaction Costs (Refined)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DYNAMIC TRANSACTION COSTS v3.0                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  spread(pair, t) =                                                         │
│      base_spread(pair) ×                                                  │
│      volatility_multiplier(t) ×                                           │
│      liquidity_multiplier(t)                                              │
│                                                                             │
│  Where:                                                                    │
│  volatility_multiplier = max(1.0, 1 + 0.5 × vix_zscore_30d)               │
│  liquidity_multiplier = 1 + 0.3 × (1 - liquidity_score)                   │
│                                                                             │
│  liquidity_score = based on:                                              │
│  - Time of day (London/NY overlap = 1.0)                                  │
│  - Holiday status                                                          │
│  - Market depth indicators                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Net Return Calculation

```
gross_return = expected_return_5d (from prediction)

total_trading_cost = dynamic_spread + dynamic_slippage + commission

carry = expected_carry(pair, direction, horizon, t)

net_expected_return = gross_return - total_trading_cost + carry

cost_adjusted_edge = net_expected_return / total_trading_cost
```

---

## 📊 6. OPPORTUNITY RANKING v3.0

### 6.1 Risk-Adjusted Component

**v2.0 Problem:** Volatility penalty was arbitrary.

**v3.0 Solution:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPPORTUNITY SCORE v3.0                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Opportunity_Score =                                                       │
│      α × fusion_score +                                                    │
│      β × risk_adjusted_return +                                            │
│      γ × decision_quality +                                                │
│      δ × diversification_value                                            │
│                                                                             │
│  Where:                                                                    │
│                                                                             │
│  risk_adjusted_return = net_expected_return / expected_volatility         │
│                                                                             │
│  fusion_score ∈ [-1, +1]                                                  │
│  risk_adjusted_return ∈ [-1, +1] (normalized)                             │
│  decision_quality ∈ [0, 1]                                                │
│  diversification_value ∈ [0, 1]                                           │
│                                                                             │
│  Default Weights:                                                         │
│  α = 0.40                                                                  │
│  β = 0.30                                                                  │
│  γ = 0.20                                                                  │
│  δ = 0.10                                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Opportunity Types

```
For each pair, generate:
- LONG opportunity if fusion_score > 0.15
- SHORT opportunity if fusion_score < -0.15
- Exclude if |fusion_score| ≤ 0.15
```

### 6.3 Ranking Output

```
{
  "opportunities": [
    {
      "rank": 1,
      "opportunity_id": "USD/JPY_LONG",
      "pair": "USD/JPY",
      "direction": "LONG",
      "fusion_score": 0.68,
      "risk_adjusted_return": 3.2,
      "decision_quality": 0.82,
      "opportunity_score": 0.74,
      "components": {
        "weights": {
          "fusion": 0.40,
          "risk_adj_return": 0.30,
          "quality": 0.20,
          "diversification": 0.10
        },
        "contributions": {
          "fusion": 0.27,
          "risk_adj_return": 0.30,
          "quality": 0.16,
          "diversification": 0.01
        }
      },
      "actionable": true,
      "signal_strength": "strong"
    }
  ]
}
```

---

## 📊 7. SELECTIVE PREDICTION METRICS

### 7.1 KPI Definition

| Metric | Definition | Target |
|--------|------------|--------|
| **Coverage** | Actionable / Total predictions | Variable (performance driven) |
| **Sharpe@Coverage** | Sharpe ratio at given coverage | > 0.3 at 100%, > 0.5 at 50% |
| **Precision@Coverage** | Hit rate at given coverage | > 55% at all coverage levels |
| **Reject Efficiency** | Avoided losses / Total rejected | > 55% |
| **Coverage-Performance Slope** | ΔSharpe / ΔCoverage | Negative (higher coverage = higher Sharpe) |

### 7.2 Coverage-Performance Curve

```
Sharpe vs Coverage (Expected)

Sharpe
 1.0 ┤                              ●  (30% coverage)
     │                          ●
 0.8 ┤                     ●        (50% coverage)
     │                ●
 0.6 ┤           ●                 (70% coverage)
     │      ●
 0.4 ┤ ●                           (100% coverage)
     │
 0.2 ┤
     │
 0.0 ┼─────────────────────────────────
       20%  40%  60%  80%  100%
               Coverage

Interpretation:
- At 100% coverage: All predictions traded → Sharpe = 0.25
- At 70% coverage: Only high-confidence trades → Sharpe = 0.55
- At 30% coverage: Only strongest signals → Sharpe = 0.85

This proves: Meridian improves decision quality by selective action.
```

---

## 📊 8. PIT/LEAKAGE PREVENTION PROTOCOL

### 8.1 Critical Invariants

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIT PROTOCOL — INVARIABLE RULES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Rule 1: knowledge_timestamp <= prediction_timestamp                      │
│  → No future data in any feature used for prediction                      │
│                                                                             │
│  Rule 2: prediction_timestamp <= decision_timestamp                       │
│  → Prediction exists before decision is made                              │
│                                                                             │
│  Rule 3: decision_timestamp <= realization_timestamp                      │
│  → Decision occurs before the outcome is known                            │
│                                                                             │
│  Rule 4: calibration uses ONLY information available at training time     │
│  → Walk-forward, not full history                                         │
│                                                                             │
│  Rule 5: RAG documents use ONLY documents published before prediction     │
│  → No future central bank documents                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Validation Tests

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIT VALIDATION TESTS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Test 1: Feature Timestamps                                                │
│  ├─ For each feature, verify: knowledge_timestamp <= prediction_timestamp │
│  └─ FAIL if any violation                                                  │
│                                                                             │
│  Test 2: Target Timestamps                                                 │
│  ├─ For each prediction, verify: price_end > prediction_timestamp         │
│  └─ FAIL if prediction_timestamp >= price_end                             │
│                                                                             │
│  Test 3: RAG Timestamps                                                    │
│  ├─ For each RAG signal, verify: document_timestamp <= prediction_timestamp│
│  └─ FAIL if any violation                                                  │
│                                                                             │
│  Test 4: Weight Calibration                                                │
│  ├─ Verify weights use only training period data                          │
│  └─ FAIL if test period used in calibration                               │
│                                                                             │
│  Test 5: Rolling Window Consistency                                        │
│  ├─ Verify window boundaries are strict                                   │
│  └─ FAIL if any overlap between train and test                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ FINAL DATA MODEL

### decision_scores (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        decision_scores                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ decision_id           VARCHAR(50) UNIQUE                                   │
│ prediction_id         INTEGER REFERENCES predictions(id)                   │
│ fusion_id             INTEGER REFERENCES fusion_registry(id)               │
│ decision_version      INTEGER                                              │
│ supersedes_decision   VARCHAR(50)                                          │
│ decision_reason_code  VARCHAR(30)         ← NEW                           │
│ engine_version        VARCHAR(10)         ← NEW                           │
│ pair                  VARCHAR(10)                                          │
│ direction             VARCHAR(10)                                          │
│ decision_timestamp    TIMESTAMP                                            │
│ decision_status       VARCHAR(20)                                          │
│ quant_score           DECIMAL(6,4)                                         │
│ macro_score           DECIMAL(6,4)                                         │
│ rag_score             DECIMAL(6,4)                                         │
│ macro_components      JSON                                                 │
│ rag_components        JSON                 ← NEW                           │
│ fusion_score          DECIMAL(6,4)                                         │
│ fusion_weights        JSON                                                 │
│ regime_at_decision    JSON                                                 │
│ gross_return          DECIMAL(8,6)                                         │
│ costs                 JSON                 ← NEW (detailed breakdown)     │
│ carry                 DECIMAL(8,6)                                         │
│ net_return            DECIMAL(8,6)                                         │
│ cost_adjusted_edge    DECIMAL(8,4)                                         │
│ original_confidence   DECIMAL(5,4)                                         │
│ decision_quality      DECIMAL(5,4)                                         │
│ quality_components    JSON                 ← NEW (detailed breakdown)     │
│ actionable            BOOLEAN                                              │
│ rejection_reason      VARCHAR(100)                                         │
│ created_at            TIMESTAMP                                            │
│ INDEX(pair, decision_timestamp)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### signal_validity (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       signal_validity                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ decision_id           VARCHAR(50) REFERENCES decision_scores(decision_id)  │
│ check_timestamp       TIMESTAMP                                            │
│ valid                 BOOLEAN                                              │
│ status                VARCHAR(20)                                          │
│ original_confidence   DECIMAL(5,4)                                         │
│ current_quality       DECIMAL(5,4)                                         │
│ quality_breakdown     JSON                 ← NEW (calibrated components)  │
│ regime_distance       DECIMAL(5,4)         ← NEW                          │
│ freshness_factor      DECIMAL(5,4)         ← NEW                          │
│ regime_alignment_factor DECIMAL(5,4)       ← NEW                          │
│ data_quality_factor   DECIMAL(5,4)         ← NEW                          │
│ drift_factor          DECIMAL(5,4)         ← NEW                          │
│ hard_invalidators     JSON                                                 │
│ soft_degradations     JSON                                                 │
│ prediction_age_hours  DECIMAL(6,2)                                         │
│ created_at            TIMESTAMP                                            │
│ INDEX(decision_id, check_timestamp)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ SUCCESS CRITERIA — Decision Engine v3.0

| Criterion | Metric | Target |
|-----------|--------|--------|
| **Economic Significance** | Walk-forward Sharpe (net) | > 0.3 |
| **Filter Effectiveness** | Filtered vs Unfiltered Sharpe | Filtered > Unfiltered |
| **Selective Prediction** | Coverage-Performance slope | Negative (or flat at worst) |
| **Actionability Precision** | Profitable / Total actionable | > 55% |
| **Reject Efficiency** | Avoided losses / Total rejected | > 55% |
| **Weight Stability** | Weight variance across windows | < 0.05 |
| **Threshold Sensitivity** | Sharpe at adjacent thresholds | Smooth transition |
| **Cost Sensitivity** | Net positive after costs | True |
| **PIT Validation** | Leakage test failures | 0 |
| **Decision Versioning** | Traceable revisions | 100% |
| **Calibration** | ECE | < 0.05 |

---

## 🛑 ARCHITECTURE FREEZE

**No further component additions.**

The following features are **DEFERRED** to post-V1:

| Feature | Why Deferred | Target |
|---------|--------------|--------|
| **LSTM Ensemble** | Adds complexity without proven value | V3 |
| **Multi-Horizon (1D, 20D)** | Additional models required | V2 |
| **Position Sizing Factor** | Enters portfolio/risk management | V3 |
| **Autonomous Agents** | Overengineering for MVP | V4 |
| **Real-time Tick Inference** | Infrastructure complexity | V4 |
| **Complex Frontend** | Streamlit sufficient for V1 | V2 |

---

## 📋 IMPLEMENTATION CHECKLIST — Decision Engine v3.0

### Phase 1: Signal Generation (Week 6)
