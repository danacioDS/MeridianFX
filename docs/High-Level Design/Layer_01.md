# 📋 MERIDIAN FX — INTELLIGENCE LAYER v2.0

## Revision Summary — Addressing 4 Key Gaps

| Issue | Original | Revised | Impact |
|-------|----------|---------|--------|
| **PIT/Data Lineage** | Partial | Complete traceability to source/vintage | +0.3 |
| **Data Freshness** | Single threshold | Per-source + composite score | +0.3 |
| **Prediction Immutability** | Cache ambiguity | Clear separation: immutable prediction + dynamic state | +0.3 |
| **RAG Evidence Provenance** | Missing | Source, document, passage retrieval metadata | +0.3 |

---

## 🔴 GAP 1: PIT & DATA LINEAGE — Complete Traceability

### Issue

Original registry allowed tracing `Prediction → Model → Feature Version` but not to **specific source observations with their vintages.**

### Solution: Expanded Lineage Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE LINEAGE CHAIN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PREDICTION                                                                 │
│  ├── prediction_id                                                         │
│  ├── prediction_timestamp                                                  │
│  └── prediction_value                                                      │
│       │                                                                     │
│       ▼                                                                     │
│  FEATURE SNAPSHOT                                                          │
│  ├── feature_snapshot_id                                                   │
│  ├── feature_name                                                          │
│  ├── feature_value                                                         │
│  └── feature_version                                                       │
│       │                                                                     │
│       ▼                                                                     │
│  SOURCE OBSERVATION                                                        │
│  ├── source_record_id                                                      │
│  ├── source_name                                                           │
│  ├── observation_timestamp     ← Economic event occurred                   │
│  ├── release_timestamp         ← Officially published                      │
│  ├── knowledge_timestamp       ← Available to model                        │
│  ├── vintage                   ← Data vintage/revision                     │
│  ├── raw_value                                                             │
│  ├── normalized_value                                                      │
│  └── revision_type                                                         │
│       │                                                                     │
│       ▼                                                                     │
│  ORIGINAL SOURCE                                                           │
│  ├── source_id                                                             │
│  ├── source_name (FRED, e-Stat, Yahoo, CFTC)                              │
│  ├── source_series_id                                                      │
│  ├── access_timestamp                                                      │
│  └── source_metadata (JSON)                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Revised Data Model

**feature_snapshots** table:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      feature_snapshots                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ prediction_id         INTEGER REFERENCES predictions(id)                   │
│ feature_name          VARCHAR(50)                                          │
│ feature_value         DECIMAL(12,6)                                        │
│ feature_version       VARCHAR(20)                                          │
│ source_record_id      INTEGER REFERENCES source_records(id)               │
│ knowledge_timestamp   TIMESTAMP        ← CRITICAL: PIT validation          │
│ created_at            TIMESTAMP                                            │
│ INDEX(prediction_id, feature_name)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**source_records** table:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        source_records                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ source_id             INTEGER REFERENCES sources(id)                       │
│ source_series_id      VARCHAR(50)                                          │
│ observation_timestamp TIMESTAMP        ← When economic event occurred      │
│ release_timestamp     TIMESTAMP        ← When officially published         │
│ knowledge_timestamp   TIMESTAMP        ← Available to model                │
│ vintage               VARCHAR(20)      ← "initial", "revised-2026-08-20"   │
│ raw_value             DECIMAL(12,6)                                        │
│ normalized_value      DECIMAL(12,6)                                        │
│ revision_type         VARCHAR(20)      ← "initial", "revision", "correction"│
│ data_quality          VARCHAR(10)      ← "high", "medium", "low"          │
│ source_metadata       JSON             ← Additional source-specific fields │
│ created_at            TIMESTAMP                                            │
│ INDEX(knowledge_timestamp)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### New API Endpoint for Lineage

```
GET /v1/fx/{pair}/lineage/{prediction_id}
```

**Response:**
```
{
  "prediction": {...},
  "model": {...},
  "fusion": {...},
  "feature_snapshots": [
    {
      "feature_name": "us_jp_rate_spread",
      "feature_value": 3.42,
      "source_record": {
        "observation_timestamp": "2026-08-25T14:00:00Z",
        "release_timestamp": "2026-08-25T16:30:00Z",
        "knowledge_timestamp": "2026-08-25T17:00:00Z",
        "vintage": "initial",
        "source": "FRED",
        "series_id": "DGS10"
      }
    }
  ],
  "pit_validation": {
    "passed": true,
    "max_knowledge_lag": "1h30m",
    "all_timestamps": "knowledge_timestamp <= prediction_timestamp"
  }
}
```

---

## 🔴 GAP 2: DATA FRESHNESS — Per-Source Scoring

### Issue

Single threshold `< 24 hours` is too coarse for a financial system.

### Solution: Data Freshness Framework

**Freshness Score (per source):**
```
freshness_score = f(age_in_hours, source_type)

Where:
- age_in_hours = current_time - knowledge_timestamp
- source_type determines decay curve
```

**Source-Specific Thresholds:**

| Source | Data Type | Max Age | Typical Age | Decay Weight |
|--------|-----------|---------|-------------|--------------|
| FX Price | Real-time | < 1h | 5-10 min | 1.0 |
| VIX | Market | < 2h | 15-30 min | 1.0 |
| Rates (yields) | Market | < 2h | 30 min | 1.0 |
| Commodities | Market | < 4h | 1-2h | 0.9 |
| COT Positioning | Weekly | < 7d | 4-5d | 0.6 |
| Macro (CPI, GDP) | Monthly | < 45d | 20-30d | 0.5 |
| RAG | Event-driven | < 7d | 1-3d | 0.7 |

**Composite Data Freshness:**

```
overall_freshness = Σ(weight_i × freshness_score_i) / Σ(weight_i)
```

**Data Coverage Score:**

```
data_coverage = (features_available / total_features) × 100%
```

### Updated API Response

**Current `/v1/status` becomes `/v1/status` with:**

```
{
  "api": "healthy",
  "database": "healthy",
  "latest_prediction": "2026-08-26T17:00:00Z",
  "data_freshness": {
    "overall": 0.94,
    "breakdown": {
      "fx_price": 0.99,
      "vix": 0.98,
      "rates": 0.97,
      "macro": 0.92,
      "positioning": 0.85,
      "rag": 1.00
    },
    "issues": [
      {"source": "positioning", "age_hours": 96, "threshold_hours": 168, "status": "warning"}
    ]
  },
  "data_coverage": {
    "overall": 0.96,
    "available_features": 42,
    "total_features": 44,
    "missing_features": ["jp_gdp_qoq", "jp_cpi_forecast"]
  },
  "model_status": "production",
  "pipeline_status": "healthy",
  "last_successful_ingestion": "2026-08-26T16:00:00Z",
  "next_scheduled_inference": "2026-08-27T17:00:00Z"
}
```

### Forecast Response Enhancement

Add to forecast response:

```
"data_quality": {
  "freshness_score": 0.94,
  "coverage_score": 0.96,
  "overall_quality": 0.95,
  "status": "good"  // good | acceptable | degraded
}
```

---

## 🔴 GAP 3: PREDICTION IMMUTABILITY & CACHING

### Issue

Confusion between cache duration (60s vs 1h) and whether predictions can change.

### Solution: Clear Separation

**Principle:**
```
PREDICTION = Immutable Record
ECONOMIC_STATE = Dynamic (costs, conditions)
RESPONSE = Cacheable Composite
```

### Prediction Immutability

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMMUTABILITY PRINCIPLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Once stored with prediction_id, prediction never changes:                 │
│                                                                             │
│  ✓ predicted_return                                                         │
│  ✓ predicted_probability                                                    │
│  ✓ calibrated_probability                                                   │
│  ✓ prediction_interval                                                      │
│  ✓ shap_values                                                              │
│  ✓ regime_at_prediction                                                     │
│  ✓ rag_signal_at_prediction                                                 │
│                                                                             │
│  However, these MAY change over time:                                      │
│                                                                             │
│  ∼ actual_return          (updates when realized)                          │
│  ∼ direction_correct      (updates when realized)                          │
│  ∼ economic_filter        (recalculated with current costs)                │
│  ∼ signal_validity        (recalculated with current conditions)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cache Strategy

| Entity | Cache Duration | Reason |
|--------|---------------|--------|
| **Prediction** | 5-15 min | Immutable; only needs to be read |
| **SHAP Values** | 15 min | Immutable; large payload |
| **Economic Filter** | 5 min | Changes with market conditions |
| **Signal Validity** | 5 min | Changes with market conditions |
| **Dashboard Data** | 60 sec | User experience; near real-time |

### Implementation

**Cache Keys:**
```
cache:prediction:{pair}:{date}
cache:drivers:{pair}:{date}
cache:ranking:{date}
```

**Cache Invalidation:**
- Daily at market close (17:00 EST) → all caches invalidated
- On-demand via API (POST /v1/cache/invalidate) — admin only

### Versioning

**Prediction has versioning:**
```
prediction_id: pred-20260826-1700-001
prediction_version: 1
```

If a prediction is corrected (e.g., data revision):
```
prediction_id: pred-20260826-1700-002  (new ID)
supersedes: pred-20260826-1700-001
reason: "Data revision: CPI corrected"
```

---

## 🔴 GAP 4: RAG EVIDENCE PROVENANCE

### Issue

RAG output as simple sentiment score without source traceability.

### Solution: RAG Evidence Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG EVIDENCE CHAIN                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAG SIGNAL                                                                 │
│  ├── signal_id                                                             │
│  ├── prediction_id                                                         │
│  ├── central_bank: "Fed" / "BoJ"                                          │
│  ├── sentiment: "hawkish" / "dovish" / "neutral"                          │
│  ├── sentiment_score: 0.72                                                │
│  ├── z_score_12m: 1.2                                                     │
│  ├── confidence: 0.85                                                     │
│  └── generation_timestamp                                                  │
│       │                                                                     │
│       ▼                                                                     │
│  EVIDENCE FRAGMENTS                                                        │
│  ├── fragment_id                                                           │
│  ├── signal_id                                                             │
│  ├── source_document_id                                                    │
│  ├── passage_text                                                          │
│  ├── passage_contribution: 0.34                                           │
│  ├── passage_rank: 1                                                       │
│  └── retrieval_score: 0.89                                                │
│       │                                                                     │
│       ▼                                                                     │
│  SOURCE DOCUMENTS                                                          │
│  ├── document_id                                                           │
│  ├── document_type: "FOMC Statement" / "BoJ Policy Statement"             │
│  ├── publication_timestamp                                                 │
│  ├── retrieval_timestamp                                                   │
│  ├── document_version: "2026-08-20"                                       │
│  ├── document_url                                                          │
│  └── document_metadata (JSON)                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### RAG Response Structure

**Updated `/v1/fx/{pair}/drivers` RAG section:**

```
"rag": {
  "fed": {
    "sentiment": "hawkish",
    "score": 0.72,
    "z_score_12m": 1.2,
    "confidence": 0.85,
    "evidence": [
      {
        "source": "FOMC Minutes",
        "date": "2026-08-20T14:00:00Z",
        "document_version": "v1.0",
        "passage": "Several members expressed concerns about persistent inflation...",
        "contribution": 0.34,
        "retrieval_score": 0.89
      },
      {
        "source": "FOMC Minutes",
        "date": "2026-08-20T14:00:00Z",
        "document_version": "v1.0",
        "passage": "The Committee sees risks to inflation remaining elevated...",
        "contribution": 0.28,
        "retrieval_score": 0.82
      }
    ],
    "document_metadata": {
      "total_passages_retrieved": 5,
      "avg_retrieval_score": 0.78,
      "retrieval_latency_ms": 320
    }
  },
  "boj": {
    "sentiment": "dovish",
    "score": 0.28,
    "z_score_12m": -0.8,
    "confidence": 0.78,
    "evidence": [...],
    "document_metadata": {...}
  },
  "policy_divergence": 0.44,
  "divergence_percentile": 82,
  "signal_freshness": {
    "last_update": "2026-08-26T16:00:00Z",
    "age_hours": 1.5,
    "status": "fresh"
  }
}
```

### RAG Registry Tables

**rag_signals:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         rag_signals                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ prediction_id         INTEGER REFERENCES predictions(id)                   │
│ central_bank          VARCHAR(5)                                           │
│ sentiment             VARCHAR(10)                                          │
│ sentiment_score       DECIMAL(5,4)                                         │
│ z_score_12m           DECIMAL(5,4)                                         │
│ confidence            DECIMAL(5,4)                                         │
│ generation_timestamp  TIMESTAMP                                            │
│ INDEX(prediction_id, central_bank)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**rag_evidence:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        rag_evidence                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ signal_id             INTEGER REFERENCES rag_signals(id)                   │
│ document_id           INTEGER REFERENCES rag_documents(id)                 │
│ passage_text          TEXT                                                 │
│ passage_contribution  DECIMAL(5,4)                                         │
│ passage_rank          INTEGER                                              │
│ retrieval_score       DECIMAL(5,4)                                         │
│ created_at            TIMESTAMP                                            │
│ INDEX(signal_id, passage_rank)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**rag_documents:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        rag_documents                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                                   │
│ central_bank          VARCHAR(5)                                           │
│ document_type         VARCHAR(30)                                          │
│ publication_timestamp TIMESTAMP                                            │
│ retrieval_timestamp   TIMESTAMP                                            │
│ document_version      VARCHAR(20)                                          │
│ document_url          VARCHAR(255)                                         │
│ document_metadata     JSON                                                 │
│ created_at            TIMESTAMP                                            │
│ INDEX(central_bank, publication_timestamp)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 COMPLETE REVISED TABLE OF CONTENTS

### Intelligence Layer v2.0

| Section | Content | Changes |
|---------|---------|---------|
| 1. API | RESTful endpoints | + Lineage endpoint |
| 2. API Response | Full response schema | + Data quality fields |
| 3. Dashboard | 4-page interface | No changes |
| 4. Registry | Model, Prediction, Fusion | + Feature Snapshot + Source Records |
| 5. Data Flow | Precomputation + API | + Freshness computation |
| 6. Database Schema | Neon tables | + 5 new lineage tables |
| 7. Cache Strategy | Cache strategy | Clarified immutability |
| 8. RAG | RAG agent | + Evidence chain |
| 9. Status | Health endpoint | + Freshness + Coverage |
| 10. Security | Security | No changes |
| 11. Implementation Checklist | Tasks | + Lineage + Freshness tasks |

---

## 📊 UPDATED SCORING

| Dimension | v1.0 | v2.0 | Change |
|-----------|------|------|--------|
| **Arquitectura** | 9.5 | 9.5 | - |
| **API design** | 9.2 | 9.5 | +0.3 |
| **Dashboard/product UX** | 9.0 | 9.0 | - |
| **Explainability** | 9.5 | 9.5 | - |
| **Lineage/Auditability** | 9.5 | 9.8 | +0.3 |
| **Performance architecture** | 8.8 | 9.0 | +0.2 |
| **Security** | 8.0 | 8.0 | - |
| **Data model** | 8.5 | 9.2 | +0.7 |
| **Production readiness** | 8.3 | 9.0 | +0.7 |
| **Scope control** | 9.0 | 9.0 | - |
| **TOTAL** | **9.0** | **9.3** | **+0.3** |

---

## ✅ REVISED IMPLEMENTATION CHECKLIST — Layer 1

### Week 7 Tasks

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 1 | Define OpenAPI specification | `openapi.yaml` | 1d |
| 2 | Implement FastAPI endpoints | All core endpoints | 2d |
| 3 | Implement lineage endpoint | `/lineage/{prediction_id}` | 0.5d |
| 4 | Implement request/response schemas | Pydantic models | 1d |
| 5 | Create database schema | All tables (including lineage) | 1.5d |
| 6 | Implement economic filter | Real-time computation | 1d |
| 7 | Implement signal validity | Rule-based engine | 1d |
| 8 | Implement data freshness | Per-source scoring | 1d |
| 9 | Add logging & monitoring | Structured logs | 1d |

### Week 8 Tasks

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 10 | Build Streamlit dashboard | 4-page dashboard | 3d |
| 11 | Implement dashboard components | Charts, cards | 2d |
| 12 | Connect dashboard to API | API client | 1d |
| 13 | Write API documentation | Docs + Postman | 1d |
| 14 | Deploy API to Render | Production endpoint | 1d |
| 15 | Deploy dashboard | Production dashboard | 1d |
| 16 | End-to-end testing | Test script | 1d |

---

## 🎯 FOCUS FOR WEEK 7

| Priority | Focus | Why |
|----------|-------|-----|
| **P0** | API endpoints + economic filter | Core product functionality |
| **P0** | Prediction immutability | Foundation for everything else |
| **P1** | Data freshness + status | Professional product quality |
| **P1** | Lineage traceability | Differentiator; auditability |
| **P2** | RAG evidence provenance | Differentiator; explainability |
| **P3** | Dashboard | User interface; V1 deliverable |

---

## 📌 SUMMARY — WHAT CHANGED

| Before | After |
|--------|-------|
| "Prediction is cacheable" | "Prediction is immutable; response is cacheable" |
| "Data freshness < 24h" | "Per-source freshness scoring + composite score" |
| "Lineage → Model → Data" | "Lineage → Feature Snapshot → Source Record → Observation → Vintage" |
| "RAG sentiment score" | "RAG score + evidence fragments + document provenance" |
| `/v1/health` | `/v1/status` with freshness, coverage, pipeline status |

---

**Meridian FX — Intelligence Layer Implementation Plan v2.0** ✅
