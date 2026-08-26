# 📋 MERIDIAN FX — LAYER 1: INTELLIGENCE DELIVERY LAYER

## SPECIFICATION v5.1 — FINAL FROZEN — IMPLEMENTATION READY

### Changes from v5.0

| # | Change                                                  | Justification                                            |
| - | ------------------------------------------------------- | -------------------------------------------------------- |
| 1 | **UNAVAILABLE vs NOT_ELIGIBLE resolved**                | Precise definitions of each state                        |
| 2 | **Explainability: Layer 1 does NOT generate narrative** | Narrative comes from Layer 3; Layer 1 only composes      |
| 3 | **Response contracts completed**                        | All endpoints have defined structures                    |
| 4 | **Prediction vs Decision lineage separated**            | Two distinct structures                                  |
| 5 | **Cache invalidation ≠ pipeline control**               | Explicit cache invalidation boundaries                   |
| 6 | **pipeline failed → HALTED refined**                    | Depends on intelligence availability                     |
| 7 | **Contracts are not a layer**                           | Explicit architectural declaration                       |
| 8 | **Layer 4 metrics/status**                              | Data Freshness and Prediction Coverage come from Layer 4 |

---

## 🏛️ 1. LAYER PURPOSE

```text
LAYER 1 — INTELLIGENCE DELIVERY LAYER

MISSION:
Compose and deliver financial intelligence,
without creating new intelligence.

ARCHITECTURAL PRINCIPLES:

1. Layer 1 can compose intelligence, but cannot create intelligence.
2. Layer 1 may aggregate status, but does not control system state.
3. Layer 1 MUST NOT calculate performance metrics.
   Layer 1 MAY aggregate and format performance metrics.
4. Layer 1 applies delivery policies, not business policies.
5. Layer 1 MUST NOT generate new analytical conclusions, interpretations,
   or causal claims. It formats and presents artifacts from lower layers.
6. Contracts are not an independent architectural layer.
   They define the interfaces, schemas, guarantees, and boundaries
   through which layers interact.

RESPONSIBILITIES:
1. Expose predictions and decisions through API
2. Compose explainability (drivers, SHAP, macro, RAG)
3. Provide complete traceability (lineage)
4. Present data quality (consumed from Layer 4)
5. Manage caching for performance
6. Report system status (consuming from lower layers)
7. Apply delivery policies (not business policies)

NOT RESPONSIBLE FOR:
- Calculating Data Quality (that is Layer 4)
- Validating PIT (that is Layer 4)
- Calculating Opportunity Score (that is Layer 2)
- Ranking opportunities (that is Layer 2)
- Evaluating model performance (that is Layer 4)
- Calculating performance metrics (that is Layer 4)
- Training models (that is Layer 3)
- Generating signals (that is Layer 2)
- Managing raw data (that is Layer 4)
- Deciding whether a signal is actionable (that is Layer 2)
- Activating/deactivating SAFE_MODE (that is a pipeline/control plane decision)
- Controlling system state (that is the control plane)
- Generating narrative/interpretation (that is Layer 3)
- Calculating Data Freshness (that is Layer 4)
- Calculating Prediction Coverage (that is Layer 4)
```

---

## 📊 2. CONCEPTUAL ARCHITECTURE (UNCHANGED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1 — ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         ┌──────────────────┐                               │
│                         │       USER       │                               │
│                         └────────┬─────────┘                               │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │       LAYER 1           │                             │
│                    │  INTELLIGENCE DELIVERY  │                             │
│                    │                         │                             │
│                    │  ┌───────────────────┐  │                             │
│                    │  │   API Gateway     │  │                             │
│                    │  └───────────────────┘  │                             │
│                    │  ┌───────────────────┐  │                             │
│                    │  │   Services        │  │                             │
│                    │  │  • Forecast       │  │                             │
│                    │  │  • Explainability │  │                             │
│                    │  │  • Ranking        │  │                             │
│                    │  │  • Lineage        │  │                             │
│                    │  │  • Status         │  │                             │
│                    │  └───────────────────┘  │                             │
│                    │  ┌───────────────────┐  │                             │
│                    │  │   Cache Layer     │  │                             │
│                    │  └───────────────────┘  │                             │
│                    │  ┌───────────────────┐  │                             │
│                    │  │   Response Builder│  │                             │
│                    │  └───────────────────┘  │                             │
│                    └────────────┬────────────┘                             │
│                                 │                                          │
│               READ-ONLY CONSUMPTION                                        │
│                                 │                                          │
│          ┌──────────────────────┼──────────────────────┐                   │
│          │                      │                      │                   │
│          ▼                      ▼                      ▼                   │
│   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐           │
│   │   LAYER 2   │        │   LAYER 3   │        │   LAYER 4   │           │
│   │   DECISION  │        │  RESEARCH   │        │ DATA/EVAL   │           │
│   │             │        │             │        │             │           │
│   │ Signals     │        │ Predictions │        │ Data        │           │
│   │ Fusion      │        │ Models      │        │ Quality     │           │
│   │ Policies    │        │ SHAP        │        │ Lineage     │           │
│   │ Opportunity │        │ RAG         │        │ PIT         │           │
│   │ Ranking     │        │ Narrative   │        │ Evaluation  │           │
│   │ Actionable  │        │             │        │ Health      │           │
│   └─────────────┘        └─────────────┘        └─────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. API ENDPOINTS

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    API ENDPOINTS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ENDPOINT                         │ METHOD │ PURPOSE               │    │
│  │───────────────────────────────────┼────────┼───────────────────────│    │
│  │  /v1/fx/{pair}/forecast           │ GET    │ Latest forecast       │    │
│  │  /v1/fx/{pair}/forecast/history   │ GET    │ Forecast history      │    │
│  │  /v1/fx/{pair}/drivers            │ GET    │ Driver explanation    │    │
│  │  /v1/fx/ranking                   │ GET    │ Opportunity ranking   │    │
│  │  /v1/fx/regime                    │ GET    │ Current regime        │    │
│  │  /v1/fx/performance/{pair}        │ GET    │ Performance metrics   │    │
│  │  /v1/fx/lineage/prediction/{id}   │ GET    │ Prediction lineage    │    │
│  │  /v1/fx/lineage/decision/{id}     │ GET    │ Decision lineage      │    │
│  │  /v1/status                       │ GET    │ System status         │    │
│  │  /v1/health                       │ GET    │ Simple health check   │    │
│  │  /v1/cache/invalidate             │ POST   │ Invalidate cache      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  AUTHENTICATION:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ENDPOINT                         │ AUTH       │ RATE LIMIT        │    │
│  │───────────────────────────────────┼────────────┼───────────────────│    │
│  │  /v1/fx/{pair}/forecast           │ Required   │ 60/min, 10 burst  │    │
│  │  /v1/fx/{pair}/forecast/history   │ Required   │ 30/min, 5 burst   │    │
│  │  /v1/fx/{pair}/drivers            │ Required   │ 60/min, 10 burst  │    │
│  │  /v1/fx/ranking                   │ Required   │ 30/min, 5 burst   │    │
│  │  /v1/fx/regime                    │ Required   │ 60/min, 10 burst  │    │
│  │  /v1/fx/performance/{pair}        │ Required   │ 30/min, 5 burst   │    │
│  │  /v1/fx/lineage/prediction/{id}   │ Required   │ 20/min, 3 burst   │    │
│  │  /v1/fx/lineage/decision/{id}     │ Required   │ 20/min, 3 burst   │    │
│  │  /v1/status                       │ Optional   │ 60/min, 10 burst  │    │
│  │  /v1/health                       │ None       │ No limit          │    │
│  │  /v1/cache/invalidate             │ Admin      │ 5/min, 1 burst    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. SERVICES

### 4.1 ForecastService (UNCHANGED)

```text
FUNCTION:
Retrieve and compose the latest forecast for a currency pair.

RESPONSIBILITIES:
1. Retrieve forecast from Layer 3 (PredictionRegistry)
2. Retrieve decision from Layer 2 (DecisionRegistry)
3. Retrieve data quality from Layer 4 (DataQualityRegistry)
4. Apply Delivery Policy (R1)
5. Manage cache

DELIVERY STATE DEFINITIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  ELIGIBLE       │ Intelligence exists and can be served                   │
│  NOT_ELIGIBLE   │ Intelligence exists but delivery constraints prevent    │
│                 │ actionable exposure (e.g., data quality degraded)       │
│  UNAVAILABLE    │ Required intelligence artifacts cannot be retrieved    │
│                 │ or are absent                                            │
└─────────────────────────────────────────────────────────────────────────────┘

CACHE:
TTL: 60 seconds
Invalidation: On new prediction, on data quality change
Fallback: Stale cache if fresh unavailable
```

### 4.2 ExplainabilityService (CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXPLAINABILITY SERVICE — CORRECTED                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FUNCTION:                                                                 │
│  Compose the drivers behind a prediction.                                 │
│                                                                             │
│  FUNDAMENTAL PRINCIPLE:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Layer 1 MUST NOT generate new analytical conclusions,             │    │
│  │  interpretations, or causal claims.                                │    │
│  │                                                                     │    │
│  │  Layer 1 composes and formats explanatory artifacts that are       │    │
│  │  produced by Layer 3 (SHAP, Macro Regime, RAG, Narrative).         │    │
│  │                                                                     │    │
│  │  Executive Narrative comes from Layer 3. Layer 1 does NOT         │    │
│  │  generate it using an LLM or other means.                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  RESPONSIBILITIES:                                                         │
│  1. Retrieve SHAP values from Layer 3                                     │
│  2. Retrieve Macro Regime from Layer 3                                    │
│  3. Retrieve RAG signals from Layer 3                                     │
│  4. Retrieve Executive Narrative from Layer 3                             │
│  5. Format and compose for presentation                                   │
│                                                                             │
│  DEPENDENCIES:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Operation                 │ Source      │ Purpose                 │    │
│  │───────────────────────────┼─────────────┼─────────────────────────│    │
│  │  get_shap_values          │ Layer 3     │ Feature contributions   │    │
│  │  get_macro_regime         │ Layer 3     │ Macro context           │    │
│  │  get_rag_signals          │ Layer 3     │ Central bank sentiment  │    │
│  │  get_narrative            │ Layer 3     │ Executive narrative     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  COMPOSITION:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. SHAP Values: Top 5 features (from Layer 3)                     │    │
│  │  2. Macro Regime: Risk, Policy, Growth, Inflation (from Layer 3)  │    │
│  │  3. RAG Signals: Fed and BoJ sentiment (from Layer 3)             │    │
│  │  4. Executive Narrative: 2-3 paragraph summary (from Layer 3)     │    │
│  │  5. Risks and Event Sensitivity (from Layer 3)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  CACHE: TTL: 300s, Invalidation: On new prediction                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 RankingService (UNCHANGED)

```text
FUNCTION:
Retrieve and format the opportunity ranking from Layer 2.

KEY PRINCIPLE:
Layer 1 does NOT calculate ranking.
Layer 1 retrieves and formats ranking from Layer 2.

CACHE: TTL: 60s, Invalidation: On new ranking cycle
```

### 4.4 LineageService (CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LINEAGE SERVICE — CORRECTED                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FUNCTION:                                                                 │
│  Provide complete traceability for a prediction or decision.              │
│                                                                             │
│  TWO LINEAGE TYPES:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  PREDICTION LINEAGE:                                                │    │
│  │  Prediction → Model → Features → Data → Source → Vintage           │    │
│  │                                                                     │    │
│  │  DECISION LINEAGE:                                                  │    │
│  │  Decision → Prediction → Model → Features → Data → Source → Vintage│    │
│  │                                                                     │
│  │  Each step includes:                                                │    │
│  │  ├── ID                                                             │    │
│  │  ├── Version                                                        │    │
│  │  ├── Timestamp                                                      │    │
│  │  └── Available time                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  DEPENDENCIES:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Operation                 │ Source      │ Purpose                 │    │
│  │───────────────────────────┼─────────────┼─────────────────────────│    │
│  │  get_prediction_lineage   │ Layer 4     │ Prediction traceability  │    │
│  │  get_decision_lineage     │ Layer 4     │ Decision traceability    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  CACHE: TTL: 3600s, Invalidation: Never (lineage is immutable)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 StatusService (CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATUS SERVICE — CORRECTED                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FUNCTION:
│  Report system status by aggregating status from all layers.
│                                                                             │
│  KEY PRINCIPLES:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Layer 1 may aggregate status, but does not control system state.  │    │
│  │  Layer 1 consumes SAFE_MODE, it does not activate it.              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  SAFE MODE STATE: ON | OFF | UNKNOWN                                       │
│                                                                             │
│  STATUS STRUCTURE:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Infrastructure Status (Layer 1):                                   │    │
│  │  ├── API: healthy | degraded | unhealthy                           │    │
│  │  ├── Database: healthy | degraded | unhealthy                       │    │
│  │  ├── Pipeline: healthy | degraded | failed                         │    │
│  │  └── Cache: healthy | degraded | unhealthy                           │    │
│  │                                                                     │
│  │  Intelligence Status (Lower layers):                                │    │
│  │  ├── Data Quality (Layer 4): good | acceptable | degraded          │    │
│  │  ├── Model Performance (Layer 4): healthy | warning | degraded     │    │
│  │  ├── Model Drift (Layer 4): healthy | warning | critical           │    │
│  │  ├── Decision Engine (Layer 2): valid | degraded | invalid         │    │
│  │  └── Safe Mode State: ON | OFF | UNKNOWN                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  SYSTEM STATUS RULES (R2 - CORRECTED):
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │
│  │  // Critical infrastructure (no intelligence can be delivered)     │
│  │  IF api == "unhealthy" OR database == "unhealthy":                 │
│  │      status = "HALTED"                                              │
│  │      reason = "Critical infrastructure unavailable"                │
│  │                                                                     │
│  │  // Pipeline failure: depends on intelligence availability         │
│  │  ELSE IF pipeline == "failed":                                     │
│  │      IF valid_intelligence_available:                              │
│  │          status = "DEGRADED"                                        │
│  │          reason = "Pipeline failed but valid intelligence exists"  │
│  │      ELSE:                                                         │
│  │          status = "HALTED"                                          │
│  │          reason = "Pipeline failed and no valid intelligence"      │
│  │                                                                     │
│  │  // SAFE_MODE is reported, NOT controlled by Layer 1               │
│  │  ELSE IF safe_mode_state == "ON":                                   │
│  │      status = "SAFE_MODE"                                           │
│  │      reason = "Intelligence degraded - reported by lower layers"   │
│  │                                                                     │
│  │  // If SAFE_MODE status is unknown                                 │
│  │  ELSE IF safe_mode_state == "UNKNOWN":                              │
│  │      status = "DEGRADED"                                            │
│  │      reason = "Security state unknown - assuming degraded"         │
│  │                                                                     │
│  │  // Intelligence degraded but not critical                         │
│  │  ELSE IF data_quality == "degraded"                                 │
│  │        OR model_performance == "degraded":                          │
│  │      status = "DEGRADED"                                            │
│  │      reason = "Reduced quality - signals served with warning"      │
│  │                                                                     │
│  │  ELSE:                                                              │
│  │      status = "ACTIVE"                                              │
│  │      reason = "System operating normally"                           │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  NOTE: Cache unhealthy does NOT produce HALTED.
│        Cache unhealthy produces DEGRADED (system operates without cache).
│                                                                             │
│  CACHE: TTL: 10s, Invalidation: On status change                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 5. DELIVERY POLICY (R1 — CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DELIVERY POLICY (R1 — CORRECTED)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE:
│  Determine whether a forecast can be delivered to the user.
│  This is a DELIVERY policy, not a business policy.
│                                                                             │
│  STATE DEFINITIONS:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  UNAVAILABLE    │ Required intelligence artifacts cannot be        │    │
│  │                 │ retrieved or are absent.                         │    │
│  │                 │ → HTTP 503 / structured error                    │    │
│  │                                                                     │    │
│  │  NOT_ELIGIBLE   │ Intelligence exists, but delivery constraints    │    │
│  │                 │ prevent actionable exposure.                     │    │
│  │                 │ → HTTP 200 with actionable: false                │    │
│  │                                                                     │    │
│  │  ELIGIBLE       │ Intelligence exists and can be served.           │    │
│  │                 │ → HTTP 200 with full forecast                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  RULES:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │
│  │  // Case 1: Intelligence artifacts unavailable (error)             │
│  │  IF decision == null OR data_quality == null:                      │
│  │      delivery_state = "UNAVAILABLE"                                │
│  │      reason = "Required intelligence unavailable"                  │
│  │      // HTTP 503                                                   │
│  │                                                                     │
│  │  // Case 2: Layer 2 decides not actionable                         │
│  │  ELSE IF decision.actionable == false:                             │
│  │      delivery_state = "NOT_ELIGIBLE"                               │
│  │      reason = decision.rejection_reason                            │
│  │      // HTTP 200 with actionable: false                            │
│  │                                                                     │
│  │  // Case 3: Layer 4 reports degraded quality                       │
│  │  ELSE IF data_quality.status == "degraded":                        │
│  │      delivery_state = "NOT_ELIGIBLE"                               │
│  │      reason = "DATA_QUALITY_DEGRADED"                              │
│  │      // HTTP 200 with actionable: false                            │
│  │                                                                     │
│  │  // Case 4: Acceptable quality (with warning)                      │
│  │  ELSE IF data_quality.status == "acceptable":                      │
│  │      delivery_state = "ELIGIBLE"                                   │
│  │      warning = "Data quality acceptable but reduced"               │
│  │                                                                     │
│  │  // Case 5: Everything OK                                          │
│  │  ELSE:                                                             │
│  │      delivery_state = "ELIGIBLE"                                   │
│  │      warning = null                                                │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                             │
│  NOTE: The mapping of data_quality.status to delivery_state is a          │
│        Layer 1 policy. Layer 4 produces the status;                      │
│        Layer 1 decides how it is translated into delivery.               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 6. CACHE LAYER (CORRECTED)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CACHE LAYER — CORRECTED                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE:
│  Improve performance by caching responses.
│                                                                             │
│  CACHE INVALIDATION ≠ PIPELINE CONTROL:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Cache invalidation:                                                │    │
│  │  └── removes delivery-layer cached representations                 │    │
│  │                                                                     │
│  │  It MUST NOT:                                                       │    │
│  │  ├── trigger inference                                              │    │
│  │  ├── trigger retraining                                             │    │
│  │  ├── alter decisions                                                │    │
│  │  ├── alter predictions                                              │    │
│  │  └── change system state                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  STRATEGY:
│  Cache Type: Write-through
│  Storage: Redis
│  Serialization: JSON
│  Key Pattern: service:endpoint:parameters
│                                                                             │
│  TTL BY ENDPOINT:
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ENDPOINT                         │ TTL    │ INVALIDATION          │    │
│  │───────────────────────────────────┼────────┼───────────────────────│    │
│  │  /v1/fx/{pair}/forecast           │ 60s    │ New prediction        │    │
│  │  /v1/fx/{pair}/forecast/history   │ 300s   │ New prediction        │    │
│  │  /v1/fx/{pair}/drivers            │ 300s   │ New prediction        │    │
│  │  /v1/fx/ranking                   │ 60s    │ New ranking cycle     │    │
│  │  /v1/fx/regime                    │ 60s    │ Regime change         │    │
│  │  /v1/fx/performance/{pair}        │ 3600s  │ Daily                 │    │
│  │  /v1/fx/lineage/prediction/{id}   │ 3600s  │ Never (immutable)     │    │
│  │  /v1/fx/lineage/decision/{id}     │ 3600s  │ Never (immutable)     │    │
│  │  /v1/status                       │ 10s    │ Status change         │    │
│  │  /v1/health                       │ None   │ N/A                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  FALLBACK:
│  If cache is unavailable:
│  ├── Log warning
│  ├── Serve from source
│  └── Status = DEGRADED (not HALTED)
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 7. RESPONSE STRUCTURES (COMPLETE)

### 7.1 ForecastResponse

```text
{
    prediction_id: str
    pair: str
    timestamp: datetime
    as_of: datetime

    delivery_state: "ELIGIBLE" | "NOT_ELIGIBLE" | "UNAVAILABLE"
    delivery_reason: str
    delivery_warning: str | null

    prediction: {
        direction: "BULLISH" | "BEARISH" | "NEUTRAL"
        probability: float
        expected_return: float
        expected_volatility: float
        prediction_interval: { lower: float, upper: float }
    } | null

    decision: {
        actionable: bool
        direction: "LONG" | "SHORT" | "NEUTRAL"
        confidence: float
        signal_strength: "weak" | "moderate" | "strong"
        edge_ratio: float
        net_return: float
        position_size: float
    } | null

    data_quality: DataQuality | null
    drivers: DriversResponse | null
    lineage: PredictionLineage | null
}
```

### 7.2 DriversResponse

```text
{
    prediction_id: str
    pair: str
    timestamp: datetime

    shap: [
        { feature: str, contribution: float, rank: int }
    ]

    macro_regime: {
        risk: "Risk-On" | "Neutral" | "Risk-Off"
        policy: "Restrictive" | "Neutral" | "Accommodative"
        growth: "Strong" | "Moderate" | "Weak"
        inflation: "High" | "Moderate" | "Low"
    }

    rag: {
        fed: { sentiment: float, expectation_gap: float }
        boj: { sentiment: float, expectation_gap: float }
    }

    narrative: str  // From Layer 3
    risks: [str]    // From Layer 3
    event_sensitivity: [str]  // From Layer 3
}
```

### 7.3 RankingResponse

```text
{
    snapshot_timestamp: datetime
    as_of: datetime

    opportunities: [
        {
            rank: int
            pair: str
            direction: "LONG" | "SHORT" | "NEUTRAL"
            opportunity_score: float
            edge_ratio: float
            actionable: bool
            confidence: float
            decision_quality: float
            position_size: float
            prediction_id: str
            decision_id: str
        }
    ]

    top_opportunity: str | null
    total_actionable: int
    total_pairs: int
}
```

### 7.4 PerformanceResponse

```text
{
    pair: str
    period: "1M" | "3M" | "6M" | "1Y" | "ALL"
    as_of: datetime

    statistical: {
        directional_accuracy: float
        auc: float
        brier_score: float
        ece: float
        log_loss: float
    }

    economic: {
        sharpe_ratio: float
        sharpe_net: float
        max_drawdown: float
        profit_factor: float
        win_rate: float
        total_return: float
    }

    regime_performance: [
        {
            regime: str
            sharpe: float
            da: float
            count: int
        }
    ]

    degradation: {
        current_sharpe: float
        historical_sharpe: float
        drift_detected: bool
        drift_severity: "none" | "warning" | "critical"
    }
}
```

### 7.5 LineageResponse (Prediction)

```text
{
    prediction_id: str
    pair: str
    timestamp: datetime

    lineage: {
        prediction: {
            id: str
            version: str
            timestamp: datetime
            as_of: datetime
        }
        model: {
            id: str
            version: str
            type: str
        }
        features: {
            snapshot_id: str
            version: str
            feature_count: int
            feature_list: [
                {
                    name: str
                    source: str
                    value: float
                    available_time: datetime
                    vintage: str
                }
            ]
        }
        data: {
            dataset_id: str
            version: str
            pit_validation: "PASS" | "FAIL"
        }
        source: {
            id: str
            name: str
            reference_period: str
            vintage_id: str
            vintage_time: datetime
            available_time: datetime
        }
    }
}
```

### 7.6 LineageResponse (Decision)

```text
{
    decision_id: str
    prediction_id: str
    pair: str
    timestamp: datetime

    lineage: {
        decision: {
            id: str
            version: str
            timestamp: datetime
            as_of: datetime
            actionable: bool
            rejection_reason: str | null
        }
        prediction: {
            id: str
            version: str
            timestamp: datetime
        }
        model: {
            id: str
            version: str
            type: str
        }
        features: {
            snapshot_id: str
            version: str
            feature_count: int
        }
        data: {
            dataset_id: str
            version: str
            pit_validation: "PASS" | "FAIL"
        }
        source: {
            id: str
            name: str
            reference_period: str
            vintage_id: str
            vintage_time: datetime
        }
        policy: {
            id: str
            version: str
        }
        fusion: {
            version: str
            weights: { quant, macro, rag }
        }
    }
}
```

### 7.7 StatusResponse

```text
{
    system_status: "ACTIVE" | "DEGRADED" | "SAFE_MODE" | "HALTED"
    reason: str
    timestamp: datetime

    infrastructure: {
        api: "healthy" | "degraded" | "unhealthy"
        database: "healthy" | "degraded" | "unhealthy"
        pipeline: "healthy" | "degraded" | "failed"
        cache: "healthy" | "degraded" | "unhealthy"
    }

    intelligence: {
        data_quality: {
            overall: float
            status: "good" | "acceptable" | "degraded"
        }  // From Layer 4
        model_performance: "healthy" | "warning" | "degraded"  // From Layer 4
        model_drift: "healthy" | "warning" | "critical"  // From Layer 4
        decision_validity: "valid" | "degraded" | "invalid"  // From Layer 2
        safe_mode_state: "ON" | "OFF" | "UNKNOWN"  // From Layers 2-4
    }

    metrics: {
        data_freshness: float  // From Layer 4
        prediction_coverage: float  // From Layer 4
    }

    latest_prediction: datetime | null
    last_successful_ingestion: datetime | null
    next_scheduled_inference: datetime | null
}
```

---

## 📊 8. SLA BY ENDPOINT

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SLA BY ENDPOINT                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ENDPOINT                         │ P95      │ P99      │ NOTES    │    │
│  │───────────────────────────────────┼──────────┼──────────┼──────────│    │
│  │  /v1/health                       │ < 50ms   │ < 100ms  │ Simple   │    │
│  │  /v1/status                       │ < 100ms  │ < 200ms  │ Aggreg.  │    │
│  │  /v1/fx/{pair}/forecast (cached)  │ < 100ms  │ < 200ms  │          │    │
│  │  /v1/fx/{pair}/forecast (no cache)│ < 200ms  │ < 500ms  │          │    │
│  │  /v1/fx/ranking                   │ < 150ms  │ < 300ms  │          │    │
│  │  /v1/fx/{pair}/drivers            │ < 200ms  │ < 400ms  │          │    │
│  │  /v1/fx/{pair}/forecast/history   │ < 300ms  │ < 600ms  │          │    │
│  │  /v1/fx/performance/{pair}        │ < 300ms  │ < 600ms  │          │    │
│  │  /v1/fx/lineage/prediction/{id}   │ < 500ms  │ < 1000ms │          │    │
│  │  /v1/fx/lineage/decision/{id}     │ < 500ms  │ < 1000ms │          │    │
│  │  Dashboard                        │ < 3s     │ < 5s     │ Full     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 9. ACCEPTANCE CRITERIA

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ACCEPTANCE CRITERIA                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  AREA                 │ CRITERION                │ TARGET          │    │
│  │───────────────────────┼──────────────────────────┼─────────────────│    │
│  │  Authentication       │ Protected endpoints      │ 100% auth       │    │
│  │  Authentication       │ Public endpoints         │ Explicit list   │    │
│  │  Rate Limiting        │ Requests per minute      │ 60/min, 10 burst│    │
│  │  Cache                │ Hit rate                 │ > 70%           │    │
│  │  Cache                │ TTL compliance           │ 100%            │    │
│  │  Forecast             │ Delivery Policy (R1)     │ Consistent      │    │
│  │  Forecast             │ Delivery State           │ ELIGIBLE/NOT    │    │
│  │  Status               │ System Status (R2)       │ Consistent      │    │
│  │  Status               │ SAFE_MODE                │ Consumption only│    │
│  │  Ranking              │ Order                    │ Layer 2 source  │    │
│  │  Lineage              │ Traceability             │ Complete+ver    │    │
│  │  Performance          │ Calculation              │ Layer 1 no calc │    │
│  │  PIT                  │ Validation               │ From Layer 4    │    │
│  │  Data Quality         │ Presentation             │ From Layer 4    │    │
│  │  Narrative            │ Generation               │ From Layer 3    │    │
│  │  Data Freshness       │ Calculation              │ From Layer 4    │    │
│  │  Prediction Coverage  │ Calculation              │ From Layer 4    │    │
│  │  SLA                  │ Per endpoint             │ See SLA table   │    │
│  │  Boundaries           │ Responsibilities         │ No violations   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 10. DASHBOARD PAGES (TECHNICAL)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD PAGES — TECHNICAL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NOTE: UX, navigation, filters, interaction, and visual hierarchy         │
│        belong to the Product LLD.                                          │
│                                                                             │
│  Layer 1 defines WHAT information is exposed and WHICH endpoints feed it. │
│                                                                             │
│  PAGE 1: GLOBAL OVERVIEW                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Sources:                                                      │    │
│  │  ├── /v1/fx/ranking (top 5)                                        │    │
│  │  ├── /v1/fx/regime                                                  │    │
│  │  ├── /v1/status (data quality)                                     │    │
│  │  └── Economic Calendar (from Layer 4)                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PAGE 2: FORECAST                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Sources:                                                      │    │
│  │  └── /v1/fx/{pair}/forecast                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PAGE 3: DRIVERS                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Sources:                                                      │    │
│  │  └── /v1/fx/{pair}/drivers                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PAGE 4: PERFORMANCE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Sources:                                                      │    │
│  │  └── /v1/fx/performance/{pair}                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 11. CONTRACTS WITH LOWER LAYERS

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTRACTS WITH LOWER LAYERS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NOTE: Contracts are NOT an independent layer.                             │
│        They define the interfaces, schemas, guarantees, and boundaries    │
│        through which layers interact.                                      │
│                                                                             │
│  LAYER 1 → LAYER 2:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Operation                         │ Purpose                       │    │
│  │────────────────────────────────────┼───────────────────────────────│    │
│  │  DecisionRegistry.get_by_prediction│ Retrieve decision             │    │
│  │  OpportunityRegistry.get_ranking   │ Retrieve ranked opportunities │    │
│  │  SafeModeRegistry.get_state        │ Retrieve safe mode state      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  LAYER 1 → LAYER 3:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Operation                         │ Purpose                       │    │
│  │────────────────────────────────────┼───────────────────────────────│    │
│  │  PredictionRegistry.get_latest     │ Retrieve latest prediction    │    │
│  │  PredictionRegistry.get_history    │ Retrieve prediction history   │    │
│  │  PredictionRegistry.get_shap       │ Retrieve SHAP values          │    │
│  │  PredictionRegistry.get_rag        │ Retrieve RAG signals          │    │
│  │  PredictionRegistry.get_narrative  │ Retrieve executive narrative  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  LAYER 1 → LAYER 4:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Operation                         │ Purpose                       │    │
│  │────────────────────────────────────┼───────────────────────────────│    │
│  │  DataQualityRegistry.get_status    │ Retrieve data quality         │    │
│  │  LineageRegistry.get_prediction    │ Retrieve prediction lineage   │    │
│  │  LineageRegistry.get_decision      │ Retrieve decision lineage     │    │
│  │  PerformanceRegistry.get_metrics   │ Retrieve performance metrics  │    │
│  │  PITRegistry.get_validation        │ Retrieve PIT validation       │    │
│  │  MetricsRegistry.get_freshness     │ Retrieve data freshness       │    │
│  │  MetricsRegistry.get_coverage      │ Retrieve prediction coverage  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 12. SUCCESS CRITERIA — LAYER 1

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SUCCESS CRITERIA — LAYER 1                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CRITERION                    │ TARGET                             │    │
│  │───────────────────────────────┼────────────────────────────────────│    │
│  │  API Latency (P95)            │ < 100ms (cached), < 200ms (uncached)│   │
│  │  API Latency (P99)            │ < 200ms (cached), < 500ms (uncached)│   │
│  │  Dashboard Load               │ < 3s                               │    │
│  │  Cache Hit Rate               │ > 70%                              │    │
│  │  Data Freshness               │ > 95% (from Layer 4)               │    │
│  │  Prediction Coverage          │ > 95% (from Layer 4)               │    │
│  │  Lineage Traceability         │ 100%                               │    │
│  │  Authentication Coverage      │ 100%                               │    │
│  │  Rate Limiting Compliance     │ 100%                               │    │
│  │  Status Accuracy              │ 100% (consistent with lower layers) │    │
│  │  Boundary Compliance          │ 0 violations                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📌 SUMMARY — CHANGES v5.0 → v5.1

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHANGES v5.0 → v5.1                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ✅ UNAVAILABLE vs NOT_ELIGIBLE resolved                                │
│     └── Precise definitions: UNAVAILABLE = artifacts missing              │
│     └── NOT_ELIGIBLE = exists but cannot be exposed                       │
│                                                                             │
│  2. ✅ Explainability: Layer 1 does NOT generate narrative                 │
│     └── Narrative comes from Layer 3                                       │
│     └── Layer 1 only composes and formats                                  │
│                                                                             │
│  3. ✅ Response contracts completed                                        │
│     └── DriversResponse, PerformanceResponse, LineageResponse (2 types)   │
│                                                                             │
│  4. ✅ Lineage: Prediction vs Decision separated                           │
│     └── /lineage/prediction/{id} and /lineage/decision/{id}               │
│     └── Distinct structures                                                │
│                                                                             │
│  5. ✅ Cache invalidation ≠ pipeline control                               │
│     └── Explicit boundaries: no inference trigger, retraining, etc.        │
│                                                                             │
│  6. ✅ pipeline failed → HALTED refined                                   │
│     └── Depends on intelligence availability                              │
│     └── If valid intelligence exists → DEGRADED                          │
│                                                                             │
│  7. ✅ Contracts are not a layer                                           │
│     └── Explicit architectural declaration                                │
│                                                                             │
│  8. ✅ Layer 4 metrics/status                                             │
│     └── Data Freshness and Prediction Coverage come from Layer 4          │
│     └── Model Performance and Model Drift come from Layer 4               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 FINAL EVALUATION — LAYER 1 v5.1

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FINAL EVALUATION — LAYER 1 v5.1                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DIMENSION                    │ v5.0  │ v5.1  │ CHANGE              │    │
│  │───────────────────────────────┼───────┼───────┼─────────────────────│    │
│  │  Purpose / Mission            │ 9.9   │ 9.9   │ —                   │    │
│  │  Layer boundaries             │ 9.9   │ 9.9   │ —                   │    │
│  │  Architecture                 │ 9.7   │ 9.8   │ +0.1                │    │
│  │  API design                   │ 9.7   │ 9.8   │ +0.1                │    │
│  │  Services                     │ 9.7   │ 9.8   │ +0.1                │    │
│  │  Delivery Policy              │ 9.5   │ 9.8   │ +0.3                │    │
│  │  Status model                 │ 9.5   │ 9.8   │ +0.3                │    │
│  │  Cache                        │ 9.6   │ 9.7   │ +0.1                │    │
│  │  Response contracts           │ 9.3   │ 9.8   │ +0.5                │    │
│  │  Lineage                      │ 9.5   │ 9.8   │ +0.3                │    │
│  │  Dashboard boundary           │ 9.4   │ 9.7   │ +0.3                │    │
│  │  Cross-layer contracts        │ 9.8   │ 9.8   │ —                   │    │
│  │  Implementation clarity       │ 9.4   │ 9.8   │ +0.4                │    │
│  │  ─────────────────────────────┼───────┼───────┼─────────────────────│    │
│  │  OVERALL                      │ 9.5   │ 9.8   │ +0.3                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 🔒 Meridian FX — Layer 1: Intelligence Delivery Layer

**SPECIFICATION v5.1 — FINAL FROZEN — IMPLEMENTATION READY**

---

## What Comes Next?

| Option | Description                                                       |
| ------ | ----------------------------------------------------------------- |
| **A**  | Cross-Cutting: Governance / MLOps (Registries, Monitoring, Drift) |
| **B**  | Product LLD: Signals, Lifecycle, Presentation                     |
| **C**  | Return to Layer 4: Data Layer (deepen)                            |

**Which do you prefer?** 🚀
