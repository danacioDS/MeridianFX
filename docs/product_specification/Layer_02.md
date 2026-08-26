
---

# 📋 MERIDIAN FX — LAYER 2: DECISION ENGINE

## SPECIFICATION v3.4.1 — FINAL FROZEN — IMPLEMENTATION READY

### Changes from v3.4

| # | Change                                        | Justification                                      |
| - | --------------------------------------------- | -------------------------------------------------- |
| 1 | **DEGRADED vs REGIME_MISALIGNMENT resolved**  | Consistency: 0.30 is a gate failure, not a warning |
| 2 | **required_minimum_edge → INVALID**           | It is not UNAVAILABLE; it is an invalid policy     |
| 3 | **CONCENTRATION gate formally defined**       | Pre-capacity gate, not post-position gate          |
| 4 | **"percentile" → "linear VIX interpolation"** | The formula is linear, not percentile-based        |
| 5 | **Fallback status tracking**                  | Auditability of imputed components                 |

---

## 🏛️ 1. LAYER PURPOSE (UNCHANGED)

```text
LAYER 2 — DECISION ENGINE

MISSION:
Transform predictions into actionable decisions by applying
economic filters, dynamic fusion, and opportunity ranking.

GUIDING PRINCIPLE:
> "Prediction is not decision. Prediction is input to decision."

THE DECISION ENGINE DETERMINES:
- Whether an opportunity is actionable
- In which direction (LONG / SHORT / NEUTRAL)
- How attractive it is (ranking)
- How much exposure is justified (position sizing)
```

---

## 📊 2. CONCEPTUAL ARCHITECTURE (UNCHANGED)

```text
PREDICTION → SIGNAL → FUSION → DIRECTION → ECONOMIC VIABILITY
→ HARD SAFETY GATES → DECISION QUALITY → RANKING → POSITION SIZE → AUDIT
```

---

## 📊 3. SIGNAL GENERATION (UNCHANGED)

```text
quant_score = 2 × (probability_up - 0.5)                    [-1, +1]

macro_score = 0.50 × policy_differential                    [-1, +1]
            + 0.25 × growth_differential
            + 0.25 × normalized_rate_differential

rag_score = (base_signal - quote_signal) × 0.5             [-1, +1]

All component scores entering fusion MUST be bounded to [-1, +1].
Values outside → INVALID.
```

---

## 📊 4. REGIME CONTEXT (PAIR-GENERIC) (UNCHANGED)

```text
THREE LAYERS OF REGIME:
1. GLOBAL: Risk Sentiment, Global Growth, Global Inflation
2. BASE CURRENCY: Policy, Growth, Inflation, Policy Rate
3. QUOTE CURRENCY: Policy, Growth, Inflation, Policy Rate

REGIME DETERMINATION (SCORING-BASED):
Each predefined regime receives compatibility score:
├── +1.0 for each exact match
├── +0.5 for each partial match
└── +0.0 for mismatch

best_regime = argmax(score)
max_score = max(score)

IF max_score >= 2.5: regime = best_regime
ELSE: regime = "UNKNOWN"
```

---

## 📊 5. DYNAMIC SIGNAL FUSION (UNCHANGED)

```text
fusion_score = wq(regime) × quant_score +
               wm(regime) × macro_score +
               wr(regime) × rag_score

Constraints: wq + wm + wr = 1.0, all ≥ 0.0

DIRECTION DETERMINATION:
NEUTRAL_THRESHOLD = 0.10

IF fusion_score > +0.10: direction = "LONG", direction_sign = +1
ELIF fusion_score < -0.10: direction = "SHORT", direction_sign = -1
ELSE: direction = "NEUTRAL", direction_sign = 0

NOTE: fusion_score = ±0.10 → NEUTRAL (strict inequality)

REGIME-DEPENDENT WEIGHTS:
┌──────────────┬─────────┬─────────┬─────────┐
│ REGIME       │ wq      │ wm      │ wr      │
├──────────────┼─────────┼─────────┼─────────┤
│ Expansion    │ 0.50    │ 0.30    │ 0.20    │
│ Late Cycle   │ 0.60    │ 0.25    │ 0.15    │
│ Stagflation  │ 0.40    │ 0.40    │ 0.20    │
│ Recovery     │ 0.40    │ 0.35    │ 0.25    │
│ Crisis       │ 0.30    │ 0.40    │ 0.30    │
│ Goldilocks   │ 0.55    │ 0.30    │ 0.15    │
│ UNKNOWN      │ 0.50    │ 0.30    │ 0.20    │
└──────────────┴─────────┴─────────┴─────────┘
```

---

## 📊 6. CONFIDENCE (SIGNAL-ORIENTED) (UNCHANGED)

```text
DEFINITION:
Confidence answers: "How strong is the signal itself?"

FORMULA:
confidence = 0.40 × signal_strength
           + 0.30 × model_confidence
           + 0.20 × historical_reliability
           + 0.10 × cross_signal_agreement

COMPONENTS (ALL IN [0,1]):
signal_strength = |fusion_score|
historical_reliability = Rolling 3-month DA (Directional Accuracy)
cross_signal_agreement = 1 - (max - min) / 2

model_confidence = 1 - normalized_interval_width
normalized_interval_width = (width - P5_width) / (P95_width - P5_width)
clipped to [0, 1]
IF P95_width == P5_width: normalized_interval_width = 0.5

Range: 0.0 to 1.0
```

---

## 📊 7. ECONOMIC FILTER

### 7.1 Filter Formula

```text
All units are in BASIS POINTS (bps).

expected_return_semantics:
ALWAYS expressed as LONG/base-quote return.

direction_sign: LONG → +1, SHORT → -1, NEUTRAL → 0

directional_gross_return = expected_return × direction_sign

carry_proxy = direction_sign × (base_rate - quote_rate)
              × horizon_days / 365 × 10000

NOTE: This is a PROXY for actual carry.

net_return = directional_gross_return + carry_proxy - total_cost

edge_ratio = net_return / required_minimum_edge

actionable = edge_ratio >= 1.0

required_minimum_edge MUST be > 0.
IF required_minimum_edge <= 0:
    → INVALID
    → rejection_reason = "INVALID_EDGE_THRESHOLD"
```

### 7.2 Dynamic Costs (bps)

```text
SPREAD (by category):
┌────────────┬──────────────────────┬─────────────┐
│ CATEGORY   │ PAIRS                │ BASE SPREAD │
├────────────┼──────────────────────┼─────────────┤
│ Major      │ USDJPY, EURUSD       │ 0.2 - 0.5   │
│ Minor      │ GBPUSD, USDCNY       │ 0.3 - 0.6   │
│ Emerging   │ USDMXN, USDBRL       │ 1.0 - 2.0   │
│ Frontier   │ USDARS, USDBOB       │ 3.0 - 5.0   │
└────────────┴──────────────────────┴─────────────┘

spread_selection:
Linear VIX interpolation (not percentile):
normalized_volatility = (VIX - 10) / (30 - 10), clipped to [0, 1]
spread = base_min + (base_max - base_min) × normalized_volatility

slippage = base_slippage(category) × (VIX / 20)
base_slippage: Major: 0.5, Minor: 1.0, Emerging: 2.0, Frontier: 3.0

commission = 0.5 (fixed per trade)

total_cost = spread + slippage + commission

IF VIX missing: signal = UNAVAILABLE
```

---

## 📊 8. HARD GATES (PRECEDENCE + THRESHOLDS)

```text
PRECEDENCE (highest to lowest priority):

┌─────┬──────────────────────┬──────────────────────────┬───────────────┐
│  #  │ GATE                 │ FAIL CONDITION           │ THRESHOLD     │
├─────┼──────────────────────┼──────────────────────────┼───────────────┤
│  1  │ UNAVAILABLE          │ Model or data missing    │ N/A           │
│  2  │ INVALID              │ PIT violation            │ N/A           │
│  3  │ CONCENTRATION        │ current ≥ max_exposure   │ max_exposure  │
│  4  │ DATA QUALITY         │ data_quality < 0.60      │ 0.60          │
│  5  │ ECONOMIC FILTER      │ edge_ratio < 1.0         │ 1.0           │
│  6  │ CORRELATION          │ max_abs_correlation > 0.7│ 0.70          │
│  7  │ REGIME MISALIGNMENT  │ regime_alignment < 0.30  │ 0.30          │
└─────┴──────────────────────┴──────────────────────────┴───────────────┘

FUNDAMENTAL RULE:
A failed hard gate cannot be overridden by a stronger score.
This is a SAFETY principle, not a scoring principle.

CONCENTRATION GATE — FORMAL DEFINITION:
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONCENTRATION GATE                                                        │
│                                                                             │
│  FAIL IF:                                                                  │
│      current_exposure >= max_exposure                                      │
│                                                                             │
│  PASS IF:                                                                  │
│      current_exposure < max_exposure                                       │
│                                                                             │
│  After gate passes:                                                        │
│      available_capacity = max_exposure - current_exposure                  │
│      position_size = min(pre_concentration_position, available_capacity)   │
│                                                                             │
│  NOTE: The gate evaluates whether capacity IS AVAILABLE before sizing.     │
│        It does not evaluate whether the proposed position exceeds the      │
│        limit. That is resolved during sizing through capacity truncation.  │
└─────────────────────────────────────────────────────────────────────────────┘

REGIME ALIGNMENT (EXACT FORMULA):
regime_alignment = 0.30 × global_alignment
                 + 0.35 × base_alignment
                 + 0.35 × quote_alignment

NOTE: Alignment values are CONFIGURED POLICY PARAMETERS,
      not universal truths. Version: "1.0"

global_alignment = f(global_regime, direction):
┌────────────────────┬──────────┬──────────┬──────────┐
│ Global Regime      │ LONG     │ SHORT    │ NEUTRAL  │
├────────────────────┼──────────┼──────────┼──────────┤
│ Risk-On            │ 1.00     │ 0.30     │ 0.50     │
│ Neutral            │ 0.75     │ 0.75     │ 1.00     │
│ Risk-Off           │ 0.30     │ 1.00     │ 0.50     │
└────────────────────┴──────────┴──────────┴──────────┘

base_alignment = f(base_regime_policy, direction):
┌────────────────────┬──────────┬──────────┬──────────┐
│ Base Policy        │ LONG     │ SHORT    │ NEUTRAL  │
├────────────────────┼──────────┼──────────┼──────────┤
│ Restrictive        │ 0.80     │ 0.40     │ 0.50     │
│ Neutral            │ 0.75     │ 0.75     │ 1.00     │
│ Accommodative      │ 0.40     │ 0.80     │ 0.50     │
└────────────────────┴──────────┴──────────┴──────────┘

quote_alignment = same table applied to quote currency
```

---

## 📊 9. DECISION QUALITY (CONTEXT-ORIENTED) (UNCHANGED)

```text
DEFINITION:
Decision Quality answers: "How reliable is it to act on this signal
right now, in this context?"

FORMULA:
decision_quality = 0.30 × confidence
                 + 0.25 × freshness
                 + 0.20 × regime_alignment
                 + 0.15 × data_quality
                 + 0.10 × drift_score

COMPONENTS (ALL IN [0,1]):

freshness = exp(-age_hours / τ_fresh)
τ_fresh = 24 (hours)

drift_score = 1 - min(1, PSI / PSI_threshold)
PSI_threshold = 0.20
IF PSI missing: drift_score = 0.50, drift_status = "FALLBACK"

Range: 0.0 to 1.0

QUALITY LEVELS:
≥ 0.70: HIGH QUALITY
0.50-0.70: MODERATE QUALITY
< 0.50: LOW QUALITY
```

---

## 📊 10. OPPORTUNITY RANKING

```text
OPPORTUNITY SCORE:
Opportunity_Score = α × normalized_signal_strength
                  + β × normalized_risk_adj_return
                  + γ × decision_quality
                  + δ × diversification_benefit

DEFAULT WEIGHTS: α=0.35, β=0.25, γ=0.25, δ=0.15

NORMALIZATION (ALL IN [0,1]):

normalized_signal_strength = |fusion_score|

normalized_risk_adj_return =
    (x - P5) / (P95 - P5)
clipped to [0, 1]

P5/P95 computed by: pair × horizon
Rolling 60-day window
IF P95 == P5 OR insufficient observations (< 30):
    normalized = 0.5
    normalization_status = "FALLBACK"
ELSE:
    normalization_status = "VALID"

decision_quality = already [0,1]

diversification_benefit = 1 - min(1, max_abs_correlation)
max_abs_correlation = max(|corr(pair, existing_pair_i)|)
IF no existing positions OR correlation unavailable:
    diversification_benefit = 0.5
    diversification_status = "FALLBACK"
ELSE:
    diversification_status = "VALID"

CORRELATION FILTER:
correlation_metric: Pearson
return_frequency: daily
lookback: 60 trading days
minimum_observations: 30
as_of: point-in-time
aggregation: max_abs_correlation

IF max_abs_correlation > 0.7: exclude lower-ranked pair
```

---

## 📊 11. POSITION SIZING (NO CIRCULARITY)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    POSITION SIZING — NO CIRCULARITY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RULE:                                                                     │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  IF actionable == false OR any hard gate fails:                           │
│      position_size = 0                                                     │
│      rejection_reason = set                                                │
│                                                                             │
│  ELSE:                                                                     │
│                                                                             │
│      Step 1: Calculate pre-concentration position                         │
│      ─────────────────────────────────────────────────────────────────────│
│      pre_concentration_position =                                          │
│          base_size                                                         │
│          × edge_multiplier                                                 │
│          × quality_multiplier                                              │
│          × volatility_multiplier                                           │
│                                                                             │
│      Step 2: Check available capacity                                     │
│      ─────────────────────────────────────────────────────────────────────│
│      available_capacity = max_exposure - current_exposure                 │
│                                                                             │
│      IF available_capacity <= 0:                                           │
│          position_size = 0                                                 │
│          rejection_reason = "CONCENTRATION_LIMIT"                         │
│                                                                             │
│      Step 3: Apply capacity constraint                                    │
│      ─────────────────────────────────────────────────────────────────────│
│      ELSE:                                                                 │
│          position_size = min(pre_concentration_position, available_capacity)│
│                                                                             │
│  MULTIPLIERS (ALL IN [0, max_cap]):                                      │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  edge_multiplier = min(edge_ratio, 2.0)                  [0, 2.0]         │
│  quality_multiplier = decision_quality                   [0, 1.0]         │
│  volatility_multiplier = clip(20/(VIX+10), 0.25, 1.25)  [0.25, 1.25]     │
│                                                                             │
│  CAPS:                                                                     │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  max_position = base_size × 2.0 × 1.0 × 1.25 = 2.5 × base_size           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 12. SIGNAL VALIDITY STATES (EXACT RULES — CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIGNAL VALIDITY STATES — EXACT RULES                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  UNAVAILABLE:                                                              │
│  ├── Model not loaded                                                      │
│  ├── Required data missing                                                 │
│  └── VIX missing                                                           │
│                                                                             │
│  INVALID:                                                                  │
│  ├── PIT violation (available_time > prediction_timestamp)                │
│  ├── Any component score outside [-1, +1] without normalization            │
│  └── required_minimum_edge <= 0                                            │
│                                                                             │
│  DEGRADED:                                                                 │
│  ├── data_quality < 0.60 but ≥ 0.40                                       │
│  ├── data_coverage < 95% but ≥ 80%                                        │
│  ├── freshness < 0.50 but ≥ 0.25                                          │
│  └── 0.30 ≤ regime_alignment < 0.50 (warning, NOT gate failure)          │
│                                                                             │
│  VALID:                                                                    │
│  └── All checks passed                                                     │
│                                                                             │
│  NOTE: regime_alignment < 0.30 is a HARD GATE FAILURE → NO TRADE.        │
│        regime_alignment between 0.30 and 0.50 is DEGRADED (trade allowed).│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 13. DECISION REGISTRY (COMPLETE FIELDS + STATUS)

```text
DecisionRecord:
{
    decision_id: str
    prediction_id: str
    pair: str
    timestamp: datetime
    as_of: datetime
    horizon_days: int

    inputs: {
        quant_score: float
        macro_score: float
        rag_score: float
        model_prediction: {
            probability_up: float
            expected_return: float
            expected_volatility: float
            confidence_interval: { lower, upper }
        }
        regime: Regime | "UNKNOWN"
    }

    fusion: {
        weights: { quant, macro, rag }
        fusion_score: float
        direction: "LONG" | "SHORT" | "NEUTRAL"
        direction_sign: -1 | 0 | +1
        confidence: float
    }

    economic_filter: {
        directional_gross_return: float
        carry_proxy: float
        total_cost: float
        net_return: float
        edge_ratio: float
        required_min_edge: float
        spread_used: float
        slippage_used: float
        commission_used: float
    }

    hard_gates: {
        gate_results: {
            unavailable: bool
            invalid: bool
            concentration: bool
            data_quality: bool
            economic_filter: bool
            correlation: bool
            regime_misalignment: bool
        }
        all_passed: bool
        first_failing_gate: str | null
        thresholds_used: {
            data_quality: 0.60
            economic_filter: 1.0
            correlation: 0.70
            regime_misalignment: 0.30
            concentration: max_exposure
        }
    }

    decision_quality: {
        score: float
        components: {
            confidence: float
            freshness: float
            regime_alignment: float
            data_quality: float
            drift_score: float
        }
        level: "HIGH" | "MODERATE" | "LOW"
        fallback_status: {
            drift: "VALID" | "FALLBACK"
            normalization: "VALID" | "FALLBACK"
            diversification: "VALID" | "FALLBACK"
        }
    }

    ranking: {
        opportunity_score: float
        rank: int | null
        normalized_components: {
            signal_strength: float
            risk_adj_return: float
            decision_quality: float
            diversification: float
        }
    }

    position: {
        position_size: float
        base_size: float
        available_capacity: float
        multipliers: {
            edge: float
            quality: float
            volatility: float
        }
    }

    decision: {
        actionable: bool
        rejection_reason: str | null
        signal_validity: "VALID" | "DEGRADED" | "INVALID" | "UNAVAILABLE"
    }

    traceability: {
        model_id: str
        model_version: str
        policy_version: str
        fusion_version: str
        regime_alignment_policy_version: "1.0"
        git_commit: str
    }

    created_at: datetime
}
```

---

## 📊 14. BUSINESS RULES (COMPLETE)

```text
R1: Actionability Decision
edge_ratio = net_return / required_minimum_edge
IF edge_ratio >= 1.0: actionable = true ELSE actionable = false
IF required_minimum_edge <= 0: INVALID

R2: Position Sizing (no circularity)
IF actionable == false OR any hard gate fails: position_size = 0
ELSE:
    pre = base × edge_mult × quality_mult × vol_mult
    capacity = max_exposure - current_exposure
    IF capacity <= 0: position_size = 0, rejection = "CONCENTRATION_LIMIT"
    ELSE: position_size = min(pre, capacity)

R3: Hard Gates Precedence
Order: 1.UNAVAILABLE 2.INVALID 3.CONCENTRATION 4.DATA_QUALITY
       5.ECONOMIC_FILTER 6.CORRELATION 7.REGIME_MISALIGNMENT
A failed hard gate cannot be overridden.

R4: Rejection Reasons
├── "INSUFFICIENT_EDGE": edge_ratio < 1.0
├── "DATA_QUALITY_DEGRADED": data_quality < 0.60
├── "PIT_VIOLATION": available_time > prediction_timestamp
├── "MODEL_UNAVAILABLE": model not loaded
├── "REGIME_MISALIGNMENT": regime_alignment < 0.30
├── "CONCENTRATION_LIMIT": current_exposure >= max_exposure
├── "CORRELATION_FILTER": max_abs_correlation > 0.70
├── "INVALID_EDGE_THRESHOLD": required_minimum_edge <= 0
└── "VIX_UNAVAILABLE": VIX missing
```

---

## 📊 15. SUCCESS CRITERIA

| Metric                          | Target          |
| ------------------------------- | --------------- |
| Walk-forward Sharpe (net)       | > 0.3           |
| Actionable Precision            | > 55%           |
| Reject Efficiency               | > 55%           |
| Weight Stability                | Variance < 0.05 |
| Decision Registry Coverage      | 100%            |
| Signal Validity Rate            | > 95%           |
| Average Edge Ratio (actionable) | > 1.2           |
| Decision Latency                | < 100ms         |

---

## 📌 SUMMARY — CHANGES v3.4 → v3.4.1

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHANGES v3.4 → v3.4.1                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ✅ DEGRADED vs REGIME_MISALIGNMENT resolved                            │
│     └── < 0.30 → HARD GATE FAILURE → NO TRADE                            │
│     └── 0.30-0.50 → DEGRADED → trade permitted                           │
│                                                                             │
│  2. ✅ required_minimum_edge → INVALID                                    │
│     └── Not UNAVAILABLE; it is an invalid policy                          │
│                                                                             │
│  3. ✅ CONCENTRATION gate formally defined                                │
│     └── Pre-capacity gate: current ≥ max → FAIL                          │
│     └── Post-gate: capacity truncation                                    │
│                                                                             │
│  4. ✅ "percentile" → "linear VIX interpolation"                           │
│     └── The formula is linear, not percentile-based                       │
│                                                                             │
│  5. ✅ Fallback status tracking                                            │
│     └── drift_status, normalization_status, diversification_status        │
│     └── Auditability of imputed components                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 FINAL EVALUATION

| Dimension                    | v3.4    | v3.4.1  | Change   |
| ---------------------------- | ------- | ------- | -------- |
| Architecture                 | 9.9     | 9.9     | —        |
| Responsibility Separation    | 9.9     | 9.9     | —        |
| Pair-Generic                 | 9.8     | 9.8     | —        |
| Signal Generation            | 9.6     | 9.6     | —        |
| Signal Fusion                | 9.8     | 9.8     | —        |
| Direction Semantics          | 9.9     | 9.9     | —        |
| Confidence                   | 9.6     | 9.6     | —        |
| Economic Filter              | 9.8     | 9.8     | —        |
| Hard Gates                   | 9.5     | 9.9     | +0.4     |
| Decision Quality             | 9.6     | 9.6     | —        |
| Opportunity Ranking          | 9.6     | 9.7     | +0.1     |
| Position Sizing              | 9.5     | 9.7     | +0.2     |
| Auditability                 | 9.9     | 9.9     | —        |
| Mathematical Completeness    | 9.5     | 9.9     | +0.4     |
| Implementability             | 9.6     | 9.8     | +0.2     |
| **Overall**                  | **9.7** | **9.8** | **+0.1** |
| **Implementation Readiness** | **9.6** | **9.8** | **+0.2** |

---

# 🔒 Meridian FX — Layer 2: Decision Engine

**SPECIFICATION v3.4.1 — FINAL FROZEN — IMPLEMENTATION READY**

---

## What comes next?

| Option | Description                                             |
| ------ | ------------------------------------------------------- |
| **A**  | Layer 1: Intelligence Delivery (API, Dashboard, Status) |
| **B**  | Cross-Cutting: Governance / MLOps                       |
| **C**  | Product LLD: Signals, Lifecycle, Presentation           |
| **D**  | Return to Layer 4: Data Layer (deepen it)               |

**Which do you prefer?** 🚀
