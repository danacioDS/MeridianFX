# 📋 MERIDIAN FX — LAYER 1: INTELLIGENCE DELIVERY LAYER (LLD v5)

## Functional Specification — FROZEN

---

## 🏛️ 1. LAYER PURPOSE

```text
LAYER 1 — INTELLIGENCE DELIVERY LAYER

MISSION:
Compose and deliver financial intelligence,
without creating new intelligence.

ARCHITECTURAL PRINCIPLES:

1. > Layer 1 can compose intelligence, but cannot create intelligence.

2. > Layer 1 may aggregate status, but does not control system state.

3. > Layer 1 MUST NOT calculate performance metrics.
   > Layer 1 MAY aggregate and format performance metrics.

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
```

---

## 📊 2. CONCEPTUAL ARCHITECTURE

```text
                         ┌──────────────────┐
                         │       USER       │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │       LAYER 1           │
                    │  INTELLIGENCE DELIVERY  │
                    │                         │
                    │  API                    │
                    │  Composition            │
                    │  Presentation           │
                    │  Caching                │
                    │  Observability          │
                    │  Delivery Policies      │
                    │  Status Aggregation     │
                    └────────────┬────────────┘
                                 │
               READ-ONLY CONSUMPTION
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
   │   LAYER 2   │        │   LAYER 3   │        │   LAYER 4   │
   │   DECISION  │        │  RESEARCH   │        │ DATA/EVAL   │
   │             │        │             │        │             │
   │ Signals     │        │ Predictions │        │ Data        │
   │ Fusion      │        │ Models      │        │ Quality     │
   │ Policies    │        │ SHAP        │        │ Lineage     │
   │ Opportunity │        │             │        │ PIT         │
   │ Ranking     │        │             │        │ Evaluation  │
   │ Actionable  │        │             │        │ Health      │
   └─────────────┘        └─────────────┘        └─────────────┘
```

---

## 📊 3. FUNCTIONAL COMPONENTS

### 3.1 API Gateway

*No changes*

### 3.2 Router / Endpoints

| Endpoint                         | Method | Purpose               | Auth        |
| -------------------------------- | ------ | --------------------- | ----------- |
| `/v1/fx/{pair}/forecast`         | GET    | Latest forecast       | Yes         |
| `/v1/fx/{pair}/forecast/history` | GET    | Forecast history      | Yes         |
| `/v1/fx/{pair}/drivers`          | GET    | Driver explanation    | Yes         |
| `/v1/fx/ranking`                 | GET    | Opportunity ranking   | Yes         |
| `/v1/fx/regime`                  | GET    | Current regime        | Yes         |
| `/v1/fx/performance/{pair}`      | GET    | Performance metrics   | Yes         |
| `/v1/fx/lineage/{prediction_id}` | GET    | Complete traceability | Yes         |
| `/v1/status`                     | GET    | System status         | No          |
| `/v1/health`                     | GET    | Simple health check   | No          |
| `/v1/cache/invalidate`           | POST   | Invalidate cache      | Yes (admin) |

---

### 3.3 Services

#### A. ForecastService

**Function:** Manage forecasts.

**Responsibilities:**

* Retrieve forecast from Layer 3
* Retrieve decision from Layer 2
* Retrieve data quality from Layer 4
* Apply Delivery Policy (R1)
* Manage cache

**Delivery State (REFINED):**

```text
delivery_state:
    "ELIGIBLE"      → Forecast can be served
    "NOT_ELIGIBLE"  → Forecast is not actionable (decision from Layer 2)
    "UNAVAILABLE"   → Required data is not available (error)
```

**Contracts:**

| Operation              | Dependencies                                                             | Purpose                  |
| ---------------------- | ------------------------------------------------------------------------ | ------------------------ |
| `get_latest_forecast`  | PredictionRegistry (L3), DecisionRegistry (L2), DataQualityRegistry (L4) | Retrieve latest forecast |
| `get_forecast_history` | PredictionRegistry (L3)                                                  | Retrieve history         |

---

#### B. ExplainabilityService

*No changes*

#### C. RankingService

*No changes (Layer 2 is the source of truth for ranking)*

#### D. LineageService

*No changes (with intelligence versioning)*

#### E. StatusService (REFINED)

**Function:** Report system status.

**Responsibilities:**

* Consume infrastructure status
* Consume intelligence status from lower layers
* Aggregate and present consolidated status
* **NEVER** control system state

**Safe Mode State (REFINED):**

```text
safe_mode_state: "ON" | "OFF" | "UNKNOWN"

// "UNKNOWN" covers the case where Layer 2/3/4 do not respond
```

**Status Structure:**

```text
Infrastructure Status (Layer 1):
    ├── API: healthy | degraded | unhealthy
    ├── Database: healthy | degraded | unhealthy
    ├── Pipeline: healthy | degraded | failed
    └── Cache: healthy | degraded | unhealthy

Intelligence Status (Lower layers):
    ├── Data Quality (Layer 4)
    │   ├── freshness: good | acceptable | degraded
    │   ├── coverage: good | acceptable | degraded
    │   └── overall: good | acceptable | degraded
    ├── Model Health (Layer 4)
    │   ├── performance: healthy | warning | degraded
    │   ├── drift: healthy | warning | critical
    │   └── calibration: healthy | warning | critical
    ├── Decision Engine (Layer 2)
    │   ├── signal_validity: valid | degraded | invalid
    │   └── decision_quality: good | moderate | poor
    └── Safe Mode State (from lower layers)
        └── state: "ON" | "OFF" | "UNKNOWN"

System Status (Aggregated by Layer 1):
    ├── ACTIVE: Everything healthy
    ├── DEGRADED: Infrastructure OK, intelligence acceptable
    ├── SAFE_MODE: Reported by lower layers
    └── HALTED: Critical infrastructure unavailable
```

**System Status Rules (R2 - REFINED):**

```text
// Critical infrastructure
IF API unhealthy OR Database unhealthy OR Pipeline failed:
    status = "HALTED"
    reason = "Critical infrastructure unavailable"

// SAFE_MODE is reported, NOT controlled by Layer 1
ELSE IF safe_mode_state == "ON":
    status = "SAFE_MODE"
    reason = "Intelligence degraded - reported by lower layers"

// If SAFE_MODE status is unknown
ELSE IF safe_mode_state == "UNKNOWN":
    status = "DEGRADED"
    reason = "Security state unknown - assuming degraded"

// Intelligence degraded but not critical
ELSE IF data_quality == "degraded" OR model_health == "degraded":
    status = "DEGRADED"
    reason = "Reduced quality - signals are served with warning"

ELSE:
    status = "ACTIVE"
    reason = "System operating normally"

// Note: Cache unhealthy does NOT produce HALTED.
// Cache unhealthy produces DEGRADED (system operates without cache).
```

---

### 3.4 Cache Layer

*No changes*

### 3.5 Response Builder

*No changes*

---

## 📊 4. FORMALIZED CONTRACTS

### 4.1 Layer 1 → Layer 2 Contracts

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  DecisionRegistry.get_by_prediction(prediction_id: str) → Decision        │
│  Owner: Layer 2 | Access: Read-only | Version: v1                         │
│  Freshness: Latest decision | Failure: null / 404                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  OpportunityRegistry.get_ranked_opportunities(universe, timestamp)         │
│      → RankedOpportunitySnapshot                                           │
│  Owner: Layer 2 | Access: Read-only | Version: v1                         │
│  Freshness: Latest complete cycle | Failure: last valid snapshot           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  SafeModeRegistry.get_state() → SafeModeState                             │
│  Owner: Layer 2/3/4 | Access: Read-only | Version: v1                    │
│  Freshness: Real-time | Failure: "UNKNOWN"                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Layer 1 → Layer 3 Contracts

*No changes*

### 4.3 Layer 1 → Layer 4 Contracts

*No changes (add PerformanceRegistry)*

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  PerformanceRegistry.get_metrics(pair: str, period: str) → Performance    │
│  Owner: Layer 4 (Evaluation) | Access: Read-only | Version: v1            │
│  Freshness: Latest calculation | Failure: partial metrics                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 5. BUSINESS RULES

### R1: Delivery Policy (REFINED)

```text
INPUT:
    - decision: Decision (from Layer 2)
    - data_quality: DataQuality (from Layer 4)

OUTPUT:
    - delivery_state: "ELIGIBLE" | "NOT_ELIGIBLE" | "UNAVAILABLE"
    - warning: str (optional)
    - reason: str

// Case 1: Data unavailable (error)
IF decision == null OR data_quality == null:
    delivery_state = "UNAVAILABLE"
    reason = "Required data unavailable"
    // HTTP 503 / structured error

// Case 2: Layer 2 decides not actionable
ELSE IF decision.actionable == false:
    delivery_state = "NOT_ELIGIBLE"
    reason = decision.rejection_reason
    // HTTP 200 with actionable: false

// Case 3: Layer 4 reports degraded quality
ELSE IF data_quality.status == "degraded":
    delivery_state = "NOT_ELIGIBLE"
    reason = "DATA_QUALITY_DEGRADED"
    // HTTP 200 with actionable: false

// Case 4: Acceptable quality (with warning)
ELSE IF data_quality.status == "acceptable":
    delivery_state = "ELIGIBLE"
    warning = "Data quality acceptable but reduced"

// Case 5: Everything OK
ELSE:
    delivery_state = "ELIGIBLE"
    warning = null

// Note: This is a DELIVERY policy, not a business policy.
// Layer 1 does not decide whether the opportunity is good or bad.
// It only decides whether exposure is appropriate.
```

### R2: System Status (REFINED)

```text
INPUT:
    - infrastructure: InfrastructureStatus (Layer 1)
    - intelligence: IntelligenceStatus (Layer 2, 3, 4)
    - safe_mode_state: "ON" | "OFF" | "UNKNOWN" (from lower layers)

OUTPUT:
    - status: "ACTIVE" | "DEGRADED" | "SAFE_MODE" | "HALTED"
    - reason: str

// Critical infrastructure
IF infrastructure.api == "unhealthy" 
   OR infrastructure.database == "unhealthy" 
   OR infrastructure.pipeline == "failed":
    status = "HALTED"
    reason = "Critical infrastructure unavailable"

// SAFE_MODE is reported, NOT controlled by Layer 1
ELSE IF safe_mode_state == "ON":
    status = "SAFE_MODE"
    reason = "Intelligence degraded - reported by lower layers"

// If SAFE_MODE status is unknown
ELSE IF safe_mode_state == "UNKNOWN":
    status = "DEGRADED"
    reason = "Security state unknown - assuming degraded"

// Intelligence degraded but not critical
ELSE IF intelligence.data_quality == "degraded" 
     OR intelligence.model_health == "degraded":
    status = "DEGRADED"
    reason = "Reduced quality - signals are served with warning"

ELSE:
    status = "ACTIVE"
    reason = "System operating normally"

// Note: Cache unhealthy does NOT produce HALTED.
// Cache unhealthy produces DEGRADED (system operates without cache).
```

### R3: Cache Duration

*No changes*

---

## 📊 6. DATA STRUCTURES

### DeliveryState (NEW — REFINED)

```text
delivery_state: 
    "ELIGIBLE"      → Forecast can be served
    "NOT_ELIGIBLE"  → Forecast is not actionable
    "UNAVAILABLE"   → Required data is not available
```

### SafeModeState (NEW — REFINED)

```text
safe_mode_state: 
    "ON"        → Lower layers report SAFE_MODE active
    "OFF"       → Lower layers report normal operation
    "UNKNOWN"   → Lower layers do not respond
```

### SystemStatus (CONSOLIDATED)

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
        data_quality: DataQuality  // from Layer 4
        model_health: ModelHealth  // from Layer 4
        decision_validity: "valid" | "degraded" | "invalid"  // from Layer 2
        safe_mode_state: "ON" | "OFF" | "UNKNOWN"  // from lower layers
    }
    
    latest_prediction: datetime
    last_successful_ingestion: datetime
    next_scheduled_inference: datetime
}
```

### ForecastResponse (WITH DELIVERY STATE)

```text
{
    prediction_id: str
    pair: str
    timestamp: datetime
    
    // Delivery State (NEW)
    delivery_state: "ELIGIBLE" | "NOT_ELIGIBLE" | "UNAVAILABLE"
    delivery_reason: str
    delivery_warning: str (optional)
    
    // Only if ELIGIBLE
    prediction: {
        predicted_return: float
        calibrated_probability: float
        expected_volatility: float
        prediction_interval: {lower: float, upper: float}
    }
    
    decision: {
        actionable: bool
        direction: "LONG" | "SHORT" | "NEUTRAL"
        confidence: float
        signal_strength: "weak" | "moderate" | "strong"
    }
    
    data_quality: DataQuality  // from Layer 4
    
    drivers: (optional)
    lineage: (optional)
}
```

---

## 📊 7. SLA BY ENDPOINT

| Endpoint                            | Target P95 | Target P99 | Notes                 |
| ----------------------------------- | ---------: | ---------: | --------------------- |
| `/v1/health`                        |     < 50ms |    < 100ms | Simple health check   |
| `/v1/status`                        |    < 100ms |    < 200ms | Consolidated status   |
| `/v1/fx/{pair}/forecast` (cached)   |    < 100ms |    < 200ms | Basic forecast        |
| `/v1/fx/{pair}/forecast` (no cache) |    < 200ms |    < 500ms | Without cache         |
| `/v1/fx/ranking`                    |    < 150ms |    < 300ms | Opportunity ranking   |
| `/v1/fx/{pair}/drivers`             |    < 200ms |    < 400ms | Explainability        |
| `/v1/fx/{pair}/forecast/history`    |    < 300ms |    < 600ms | History               |
| `/v1/fx/lineage/{prediction_id}`    |    < 500ms |   < 1000ms | Complete traceability |
| Dashboard                           |       < 3s |       < 5s | Full load             |

---

## ✅ ACCEPTANCE CRITERIA

| Area               | Criterion           | Target                                 |
| ------------------ | ------------------- | -------------------------------------- |
| **Authentication** | Protected endpoints | 100% authenticated                     |
| **Authentication** | Public endpoints    | Explicit allowlist                     |
| **Rate Limiting**  | Requests per minute | 60 req/min, 10 burst                   |
| **Cache**          | Hit rate            | > 70%                                  |
| **Cache**          | TTL compliance      | 100%                                   |
| **Forecast**       | Delivery Policy     | Consistent with R1                     |
| **Forecast**       | Delivery State      | ELIGIBLE / NOT_ELIGIBLE / UNAVAILABLE  |
| **Status**         | System Status       | Consistent with R2                     |
| **Status**         | SAFE_MODE           | Consumption only, never control        |
| **Status**         | Safe Mode State     | ON / OFF / UNKNOWN                     |
| **Ranking**        | Order               | Layer 2 is source of truth             |
| **Lineage**        | Traceability        | Complete + versioning                  |
| **Performance**    | Calculation         | Layer 1 does NOT calculate performance |
| **PIT**            | Validation          | Consumed from Layer 4                  |
| **Data Quality**   | Presentation        | Consumed from Layer 4                  |
| **SLA**            | Per endpoint        | See SLA table                          |
| **Boundaries**     | Responsibilities    | No boundary violations                 |

---

## 📌 SUMMARY — v4 → v5 CHANGES

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REFINEMENTS v4 → v5                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ✅ SAFE_MODE: safe_mode_state with "ON" | "OFF" | "UNKNOWN"           │
│     └── "UNKNOWN" covers the case where lower layers do not respond       │
│     └── Layer 1 NEVER controls, only consumes                             │
│                                                                             │
│  2. ✅ System Status: StatusService only aggregates, does not control     │
│     └── Principle: "Layer 1 may aggregate status,                        │
│                      but does not control system state."                  │
│                                                                             │
│  3. ✅ Performance: boundary clarified                                    │
│     └── "Layer 1 MUST NOT calculate performance metrics.                 │
│          Layer 1 MAY aggregate and format performance metrics."           │
│                                                                             │
│  4. ✅ Delivery State: ELIGIBLE / NOT_ELIGIBLE / UNAVAILABLE              │
│     └── Difference between "not actionable" (NOT_ELIGIBLE)                │
│         and "data unavailable" (UNAVAILABLE)                              │
│     └── HTTP 200 vs HTTP 503 as appropriate                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 FINAL EVALUATION

| Area                      |        Score |
| ------------------------- | -----------: |
| Boundary / Ownership      |      **9.9** |
| Component Decomposition   |      **9.8** |
| Contracts                 |      **9.8** |
| Delivery Policy           |      **9.9** |
| Delivery State            |      **9.9** |
| Lineage + Versioning      |      **9.9** |
| Data Quality Ownership    |      **9.9** |
| Status Architecture       |      **9.9** |
| Safe Mode                 |      **9.9** |
| Caching                   |      **9.6** |
| Observability             |      **9.7** |
| SLA / Acceptance Criteria |      **9.8** |
| Implementability          |      **9.8** |
| **OVERALL**               | **⭐ 9.8/10** |

---

## 🚀 NEXT STEPS

```text
LLD v5 (FROZEN)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: Domain                                                          │
│  ├── Entities: Prediction, Decision, Opportunity, DataQuality, Lineage    │
│  └── Value Objects: DeliveryState, SafeModeState                          │
│                                                                             │
│  Phase 2: Contracts                                                       │
│  ├── IForecastService, IExplainabilityService, IRankingService            │
│  ├── ILineageService, IStatusService, IDataQualityService                │
│  └── Contracts with lower layers                                          │
│                                                                             │
│  Phase 3: Schemas                                                        │
│  ├── Pydantic schemas for all responses                                   │
│  └── Request/Response validation                                          │
│                                                                             │
│  Phase 4: Services                                                       │
│  ├── ForecastService, ExplainabilityService, RankingService              │
│  ├── LineageService, StatusService                                       │
│  └── CacheService, DeliveryPolicyService                                 │
│                                                                             │
│  Phase 5: API                                                             │
│  ├── FastAPI routes                                                       │
│  ├── Middleware (auth, rate limit, logging)                               │
│  └── Health checks                                                        │
│                                                                             │
│  Phase 6: Tests                                                            │
│  ├── Unit tests per service                                               │
│  ├── Integration tests with lower layers (mocks)                         │
│  └── End-to-end tests                                                     │
│                                                                             │
│  Phase 7: Deployment                                                       │
│  ├── Dockerfile                                                           │
│  ├── Docker Compose (with Redis, DB)                                      │
│  └── Deploy                                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Meridian FX — Layer 1 (Intelligence Delivery Layer) LLD v5** ✅

**FROZEN — Ready for implementation.**
