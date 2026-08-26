# 📋 MERIDIAN FX — COMPLETE IMPLEMENTATION PLAN

## All Layers — Final Specifications

This is the **complete, finalized** implementation plan for Meridian FX across all layers. Each layer is specified and ready for implementation.

---

## 🏛️ SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MERIDIAN FX — COMPLETE ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              CROSS-CUTTING: GOVERNANCE / MLOps v2.0                 │    │
│  │                                                                     │    │
│  │  Versioning · Lineage · Registries · Environment · Policies        │    │
│  │  Monitoring · Drift · Alerting · Kill Switch · Runbooks             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│        ┌───────────────────────────┼───────────────────────────┐           │
│        │                           │                           │           │
│        ▼                           ▼                           ▼           │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐     │
│  │ LAYER 4     │            │ LAYER 3     │            │ LAYER 2     │     │
│  │ DATA LAYER  │───PIT──────│ RESEARCH    │───MODEL───│ DECISION    │     │
│  │ v3.0        │            │ LAYER v3.0  │            │ ENGINE v3.0 │     │
│  │             │            │             │            │             │     │
│  │ • Raw Data  │            │ • Quant     │            │ • Fusion    │     │
│  │ • PIT       │            │ • Macro     │            │ • Filter    │     │
│  │ • Features  │            │ • RAG       │            │ • Validity  │     │
│  │ • Vintage   │            │ • Backtest  │            │ • Ranking   │     │
│  └─────────────┘            └─────────────┘            └─────────────┘     │
│        │                           │                           │           │
│        └───────────────────────────┼───────────────────────────┘           │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 1: INTELLIGENCE LAYER v2.0                 │    │
│  │                                                                     │    │
│  │  API · Dashboard · Morning Brief · Registry · Data Quality          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 LAYER 4: DATA LAYER v3.0

**Score: 9.4/10 | Status: READY FOR IMPLEMENTATION**

### Architecture

```
Raw Sources (FRED, e-Stat, Yahoo, CFTC)
    │
    ▼
Normalization (unified schema, timestamps, vintages)
    │
    ▼
Observations + Vintages (reference_period, release_time, available_time, vintage_time)
    │
    ▼
PIT-Aware Feature Engineering (spreads, returns, surprises, z-scores)
    │
    ▼
PIT Builder (vintage-aware, available_time <= prediction_timestamp)
    │
    ▼
USDJPY_PIT_v1.0 (data.parquet + manifest + lineage + validation + quality)
```

### Key Principles

| Principle | Implementation |
|-----------|---------------|
| **PIT Invariant** | `available_time <= prediction_timestamp` |
| **No Interpolation** | AS-OF JOIN only; forward-fill, never interpolate |
| **Vintage Awareness** | Macro data has multiple vintages; market data has observation + available_time |
| **PIT Propagation** | Derived features propagate `available_time = max(input_available_times)` |
| **Immutable Raw** | Raw data never modified, only appended |
| **Reproducible** | DVC versioning for every dataset |

### Core Tables

**feature_observations:**
```
id, feature_name, event_time, available_time, value, source, vintage, revision_type
```

**vintages:**
```
vintage_id, observation_id, series_name, reference_period, vintage_time, value, revision_type
```

**pit_datasets (Parquet + DVC):**
```
prediction_id, prediction_timestamp, pair, horizon_days,
feature_* (with available_time metadata),
target_return, target_direction,
max_available_time, pit_check
```

### V0 Scope (First Implementation)

```
Pair: USD/JPY only
Sources: FRED (US 10Y, US 2Y, VIX) + e-Stat (JP 10Y) + Yahoo (USD/JPY) + CFTC (JPY positioning)
Features: 8 core features with PIT propagation
```

### V0 Success Criteria

| Criterion | Target |
|-----------|--------|
| PIT Availability | 0 violations |
| PIT Propagation | 0 mismatches |
| Vintage Correctness | 100% |
| Validation Report | All 5 tests PASS |

---

## 📋 LAYER 3: RESEARCH LAYER v3.0

**Score: 9.4/10 | Status: READY FOR IMPLEMENTATION**

### Architecture

```
PIT Datasets (USDJPY_PIT_v1.0, EURUSD_PIT_v1.0, ...)
    │
    ▼
Experiment Sequence (E0 → E7)
    │
    ▼
Evaluation (Statistical + Economic + Robustness)
    │
    ▼
Research Gate (Leakage + Statistical + Economic + Robustness)
    │
    ▼
Model Registry (Approved models → Production)
```

### Research Hypotheses (H1-H7)

| Hypothesis | Test | Acceptance |
|------------|------|------------|
| **H1**: XGBoost > Elastic Net | DA, Sharpe | Positive improvement |
| **H2**: Constraints > Unconstrained | DA, Sharpe | Positive improvement |
| **H3**: Market Features add value | DA, Sharpe | Positive improvement |
| **H4**: Macro Regime adds value | DA, Sharpe | Positive improvement |
| **H5**: RAG adds value | DA, Sharpe | Positive improvement |
| **H6**: Walk-forward improves stability | Sharpe variance | Lower variance |
| **H7**: Ensemble improves Sharpe | Sharpe | > XGBoost alone |

### Model Specifications

**XGBoost (Primary):**
```
n_estimators: 100-500 (Optuna)
max_depth: 3-7
learning_rate: 0.01-0.15
subsample: 0.6-0.9
colsample_bytree: 0.6-0.9
CV: Purged Walk-Forward
```

**ARIMA (Baseline):**
```
p ∈ {0,1,2,3}, d ∈ {0,1}, q ∈ {0,1,2,3}
Selection: AIC/BIC within training window
```

**Elastic Net (Linear Control):**
```
alpha: 0.5, l1_ratio: 0.5
```

**Ensemble (V1):**
```
Simple average of XGBoost + Elastic Net + ARIMA
(LSTM deferred to V2)
```

### Research Gate

```
GATE 1: LEAKAGE CHECK → available_time validation, no interpolation
GATE 2: STATISTICAL → DA > 52%, ECE < 0.05, AUC > 0.55
GATE 3: ECONOMIC → Sharpe > 0.3, MaxDD > -20%, PF > 1.2
GATE 4: ROBUSTNESS → Threshold sensitivity, Parameter sensitivity

ALL PASS → APPROVED
```

### Success Criteria

| Criterion | Target |
|-----------|--------|
| H1 Acceptance | DA +1%, Sharpe +0.10 |
| H2-H5 Acceptance | Positive incremental value |
| Statistical Significance | At least 4/7 hypotheses |
| Economic Significance | Sharpe (net) > 0.3 |
| Research Gate | All gates PASS |

---

## 📋 LAYER 2: DECISION ENGINE v3.0

**Score: 9.4/10 | Status: READY FOR IMPLEMENTATION**

### Architecture

```
Prediction (Immutable)
    │
    ▼
Signal Generation (Quant + Macro + RAG)
    │
    ▼
Regime Engine (Risk, Policy, Growth, Inflation)
    │
    ▼
Dynamic Signal Fusion (Regime-dependent weights)
    │
    ▼
Decision Quality (Calibratable composite score)
    │
    ▼
Economic Filter (Gross - Costs + Carry)
    │
    ▼
Selective Decision (Actionable / No Trade)
    │
    ▼
Opportunity Ranking (All pairs scored)
```

### Core Components

**Signal Generation:**
```
Quant Score = 2 × (calibrated_probability - 0.5)
Macro Score = f(policy, growth, inflation, expectations)
RAG Score = f(sentiment, surprise, expectation_gap)
```

**Regime Engine (Separated):**
```
Risk: VIX percentiles
Policy: US/JAPAN stance
Growth: GDP surprises
Inflation: CPI surprises
```

**Fusion:**
```
Fusion_Score = wq×Quant + wm×Macro + wr×RAG
Weights: Regime-dependent, calibrated, stability-constrained
```

**Economic Filter:**
```
Gross Return = expected_return_5d
Total Cost = dynamic_spread + slippage + commission
Carry = expected_carry(pair, direction, horizon, t)
Net Return = Gross - Costs + Carry
cost_adjusted_edge = Net Return / Total Cost
Actionable = Net Return > MinEdge AND |Fusion_Score| > Threshold
```

**Decision Quality:**
```
Decision_Quality = original_confidence × freshness × regime_alignment × data_quality × drift
```

**Opportunity Ranking:**
```
Opportunity_Score = α×Fusion + β×Risk-Adjusted Return + γ×Quality + δ×Diversification
```

### Success Criteria

| Criterion | Target |
|-----------|--------|
| Walk-forward Sharpe (net) | > 0.3 |
| Actionable Precision | > 55% |
| Reject Efficiency | > 55% |
| Weight Stability | Variance < 0.05 |
| Coverage-Performance Curve | Positive slope |

---

## 📋 LAYER 1: INTELLIGENCE LAYER v2.0

**Score: 9.3/10 | Status: READY FOR IMPLEMENTATION**

### Architecture

```
API (REST endpoints)
    │
    ▼
Dashboard (Streamlit, 4 pages)
    │
    ▼
Registry (Model + Prediction + Fusion)
    │
    ▼
Data Quality (Freshness + Coverage + Status)
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/fx/{pair}/forecast` | GET | Latest forecast + economic filter |
| `/v1/fx/{pair}/forecast/history` | GET | Historical forecasts |
| `/v1/fx/{pair}/drivers` | GET | SHAP + Macro + RAG explanation |
| `/v1/fx/ranking` | GET | All pairs ranked |
| `/v1/fx/regime` | GET | Current regime |
| `/v1/fx/performance/{pair}` | GET | Model & strategy metrics |
| `/v1/fx/lineage/{prediction_id}` | GET | Complete lineage |
| `/v1/status` | GET | System health + freshness |

### Dashboard Pages

| Page | Purpose |
|------|---------|
| **Global Overview** | What is happening in the market? |
| **Forecast** | What does Meridian expect? |
| **Drivers** | Why? |
| **Performance** | How good has Meridian been? |

### Data Quality (Integrated)

```
Data Freshness Score (per source + composite)
Data Coverage Score (features available)
Critical Features Status (ALL available → forecast)
Data Status: GOOD / DEGRADED / CRITICAL
```

### Success Criteria

| Criterion | Target |
|-----------|--------|
| API Latency (P95) | < 100ms |
| Dashboard Load | < 3s |
| Data Freshness | > 95% |
| Prediction Coverage | > 95% |
| Lineage Traceability | 100% |

---

## 📋 CROSS-CUTTING: GOVERNANCE / MLOps v2.0

**Score: 9.6/10 | Status: READY FOR IMPLEMENTATION**

### Core Components

```
Versioning: Git + DVC + MLflow + Environment + Registries
Lineage: Prediction → Model → Features → Data → Source → Vintage
Registries: Model, Prediction, Fusion, Decision, Feature, Policy, Data
Monitoring: Data quality, Model performance, Drift, Costs
Alerting: INFO → WARNING → ERROR → CRITICAL with Runbooks
Kill Switch: ACTIVE → DEGRADED → SAFE_MODE → HALTED
```

### Registries

| Registry | Primary Key | Purpose |
|----------|-------------|---------|
| **Model** | model_id | Track model versions + performance |
| **Prediction** | prediction_id | Every prediction with lineage |
| **Fusion** | fusion_id | Fusion weights + calibration |
| **Decision** | decision_id | Every decision + rejection reason |
| **Feature** | feature_id | Feature definitions + lineage |
| **Policy** | policy_id | Economic filter + thresholds |
| **Data** | dataset_id | PIT dataset versions |

### Versioning Matrix

| Artifact | Format | Tool |
|----------|--------|------|
| Code | Git commit + tag | Git |
| Data | Major.Minor | DVC |
| Features | Major.Minor | Registry |
| Environment | Major.Minor.Patch | Docker + Env |
| Model | Major.Minor.Patch | MLflow |
| Prediction | YYYYMMDD-HHMM-XXX | Registry |

### Drift Detection

```
Feature Drift: PSI + KS + Wasserstein
Prediction Drift: Mean Shift + Calibration + Distribution
Performance Drift: Sharpe + DA + PF
Regime-Conditioned: Thresholds per regime
```

### Implementation Phases

| Phase | Scope | Tasks |
|-------|-------|-------|
| **Phase 1** | Core Governance MVP | Git + DVC + MLflow + Prediction Registry + Environment + Basic Quality |
| **Phase 2** | Advanced Registries | Feature + Fusion + Decision + Policy Registry |
| **Phase 3** | Monitoring & Controls | Drift + Cost + Alerting + Kill Switch |

---

## 🗺️ COMPLETE IMPLEMENTATION ROADMAP

### Phase 0: Foundation (Weeks 1-2)

```
Layer 4: Data Layer V0
├── Raw ingestion (FRED, e-Stat, Yahoo, CFTC)
├── Normalization (vintages, timestamps)
├── PIT-Aware Features (spread, return, zscore)
├── PIT Builder (USDJPY_PIT_v0)
└── Validation (5 tests PASS)

Governance (Phase 1 start)
├── Git setup
├── DVC integration
├── Environment versioning
└── Basic data quality
```

**Deliverable:** `USDJPY_PIT_v0.parquet` + validation report

---

### Phase 1: Models (Weeks 3-4)

```
Layer 3: Research Layer (E0-E2b)
├── Random Walk (E0, E0b)
├── ARIMA (E1a)
├── Elastic Net (E1b)
├── XGBoost (E2a)
├── XGBoost + Constraints (E2b)
└── MLflow tracking

Governance (Phase 1 continue)
└── Prediction Registry schema
```

**Deliverable:** E0-E2b results + MLflow runs

---

### Phase 2: Features & Signals (Weeks 5-6)

```
Layer 3: Research Layer (E3-E5)
├── Market Features (E3)
├── Macro Regime (E4)
├── RAG Policy Intelligence (E5)
└── Research Gate (Leakage + Statistical + Economic)

Layer 2: Decision Engine (start)
├── Signal Fusion
├── Economic Filter
└── Decision Quality

Governance (Phase 2)
├── Feature Registry
├── Fusion Registry
└── Decision Registry
```

**Deliverable:** E5 model + Research Gate PASS

---

### Phase 3: Backtest & Decision (Weeks 6-7)

```
Layer 3: Research Layer (E6-E7)
├── Walk-Forward Retraining (E6)
├── Ensemble (E7)
└── Model Card + Registry

Layer 2: Decision Engine (complete)
├── Regime Engine
├── Dynamic Fusion (calibrated)
├── Economic Filter (dynamic costs + carry)
├── Signal Validity
└── Opportunity Ranking

Layer 1: Intelligence Layer (start)
├── API endpoints
├── Dashboard structure
└── Data quality integration
```

**Deliverable:** Approved model + Decision Engine

---

### Phase 4: Product (Weeks 7-8)

```
Layer 1: Intelligence Layer (complete)
├── FastAPI (8 endpoints)
├── Streamlit Dashboard (4 pages)
├── Data Freshness + Coverage
├── Lineage endpoints
└── Status endpoints

Governance (Phase 3)
├── Multi-metric drift detection
├── Alerting + Runbooks
├── Cost monitoring
└── Kill Switch
```

**Deliverable:** Production-ready Meridian FX

---

## 📁 COMPLETE REPOSITORY STRUCTURE

```
meridian-fx/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── README.md
│
├── config/
│   ├── settings.py
│   ├── features.yaml
│   ├── models.yaml
│   └── policies.yaml
│
├── src/
│   ├── data/
│   │   ├── ingestion/          # FRED, e-Stat, Yahoo, CFTC
│   │   ├── normalization/      # Vintages, timestamps
│   │   ├── features/           # Market, Macro, Positioning
│   │   └── pit/               # PIT Builder + validation
│   │
│   ├── models/
│   │   ├── random_walk.py      # E0, E0b
│   │   ├── arima.py           # E1a
│   │   ├── elastic_net.py     # E1b
│   │   ├── xgboost.py        # E2a, E2b
│   │   └── ensemble.py        # E7
│   │
│   ├── research/
│   │   ├── macro_agent.py     # Regime classification
│   │   ├── rag_engine.py      # Central bank signals
│   │   └── backtester.py      # Walk-forward
│   │
│   ├── decision/
│   │   ├── fusion.py          # Dynamic fusion
│   │   ├── filter.py          # Economic filter
│   │   ├── validity.py        # Signal validity
│   │   └── ranking.py         # Opportunity ranking
│   │
│   ├── governance/
│   │   ├── registries/        # Model, Prediction, Fusion, Decision
│   │   ├── monitoring/        # Data quality, Drift, Cost
│   │   ├── alerts/           # Alerting + Runbooks
│   │   └── kill_switch.py    # System status
│   │
│   └── api/
│       ├── routes/           # forecast, drivers, ranking, lineage
│       ├── schemas/          # Pydantic models
│       └── app.py           # FastAPI
│
├── dashboard/
│   ├── app.py
│   └── pages/               # Global, Forecast, Drivers, Performance
│
├── tests/
│   ├── test_data/          # PIT validation, lineage
│   ├── test_models/        # E0-E7
│   ├── test_decision/      # Fusion, Filter, Ranking
│   └── test_api/           # Endpoints
│
├── scripts/
│   ├── ingest_all.py
│   ├── build_pit.py
│   ├── train_models.py
│   ├── backtest.py
│   └── seed_db.py
│
├── data/ (DVC-tracked)
│   ├── raw/
│   ├── normalized/
│   └── pit/
│
├── models/ (MLflow)
│   └── xgb-v1.2.0.pkl
│
└── docs/
    ├── api/              # OpenAPI
    ├── adrs/             # Architecture Decision Records
    └── runbooks/         # Incident response
```

---

## ✅ COMPLETE SUCCESS CRITERIA

### Layer 4: Data Layer

| Criterion | Target |
|-----------|--------|
| PIT Availability | 0 violations |
| PIT Propagation | 0 mismatches |
| Vintage Correctness | 100% |
| Validation Report | 5 tests PASS |

### Layer 3: Research Layer

| Criterion | Target |
|-----------|--------|
| H1-H7 | At least 4 accepted |
| Statistical Significance | 90% CI excludes null |
| Economic Significance | Sharpe (net) > 0.3 |
| Research Gate | All gates PASS |

### Layer 2: Decision Engine

| Criterion | Target |
|-----------|--------|
| Walk-forward Sharpe (net) | > 0.3 |
| Actionable Precision | > 55% |
| Reject Efficiency | > 55% |
| Weight Stability | Variance < 0.05 |

### Layer 1: Intelligence Layer

| Criterion | Target |
|-----------|--------|
| API Latency (P95) | < 100ms |
| Dashboard Load | < 3s |
| Data Freshness | > 95% |
| Lineage Traceability | 100% |

### Governance / MLOps

| Criterion | Target |
|-----------|--------|
| Lineage Completeness | 100% |
| Environment Reproducibility | Same code + data + env = same outputs |
| Registry Coverage | 100% |
| Drift Detection | 3 metrics (PSI + KS + Wasserstein) |
| Alert Actionability | 100% with runbooks |
| Kill Switch | 4 status levels |

---

## 📌 MERIDIAN FX — COMPLETE SPECIFICATION SUMMARY

### Philosophy

> **Meridian does not produce predictions. It produces actionable, traceable, explainable, and evaluable financial intelligence.**

### Core Principles

| Principle | Implementation |
|-----------|---------------|
| **Data First** | Data → Features → Models |
| **Leakage-Free** | `available_time <= prediction_timestamp` |
| **Prediction ≠ Decision** | Prediction is immutable; Decision is dynamic |
| **Reject Option** | "No trade" is a valid decision |
| **Reproducible** | Same code + same data + same environment = same result |
| **Traceable** | Prediction → Model → Features → Data → Source → Vintage |
| **Observable** | Metrics, logs, alerts, drift detection |

### Key Differentiators

1. **Point-in-Time Data** — Every feature has `available_time`; no look-ahead bias
2. **Complete Lineage** — Every prediction traceable to source vintage
3. **Selective Decision** — Meridian can say "No Trade"
4. **Economic Filter** — Costs + carry determine actionability
5. **Regime-Adaptive** — Weights adjust to market conditions
6. **Auditable** — Prediction + Decision + Fusion registries
7. **Research-Grade** — Hypotheses tested with statistical significance

### Implementation Status

| Layer | Version | Score | Status |
|-------|---------|-------|--------|
| Layer 4: Data | v3.0 | 9.4/10 | ✅ Ready |
| Layer 3: Research | v3.0 | 9.4/10 | ✅ Ready |
| Layer 2: Decision | v3.0 | 9.4/10 | ✅ Ready |
| Layer 1: Intelligence | v2.0 | 9.3/10 | ✅ Ready |
| Governance / MLOps | v2.0 | 9.6/10 | ✅ Ready |

**ALL LAYERS ARE READY FOR IMPLEMENTATION.**

---

## 🚀 NEXT ACTIONS

### Immediate (Week 1)

1. **Set up infrastructure**
   ```bash
   docker-compose up -d
   git init
   dvc init
   ```

2. **Implement Data Layer V0**
   ```bash
   python scripts/ingest_all.py --pair USDJPY
   python scripts/build_pit.py --pair USDJPY --output USDJPY_PIT_v0
   python scripts/validate_pit.py --dataset USDJPY_PIT_v0
   ```

3. **Verify PIT validation passes**
   ```bash
   Validation Report:
   ├── test_1_feature_availability: PASS
   ├── test_2_vintage_selection: PASS
   ├── test_3_pit_propagation: PASS
   ├── test_4_target_timing: PASS
   └── test_5_no_interpolation: PASS
   ```

### Immediate (Week 2)

4. **Run baseline models**
   ```bash
   python scripts/train_models.py --experiment E0
   python scripts/train_models.py --experiment E0b
   python scripts/train_models.py --experiment E1a
   python scripts/train_models.py --experiment E1b
   ```

5. **Run XGBoost**
   ```bash
   python scripts/train_models.py --experiment E2a --optimize
   ```

### Immediate (Week 3)

6. **Add features progressively** (E3, E4, E5)
7. **Run walk-forward backtest** (E6)
8. **Run ensemble** (E7)

### Immediate (Week 4)

9. **Implement Decision Engine**
10. **Implement API + Dashboard**
11. **Implement Governance (Phase 1)**

---

**MERIDIAN FX — COMPLETE IMPLEMENTATION PLAN** ✅

**All layers specified. All principles defined. Ready for execution.**

**"From Market Noise to Actionable FX Intelligence."**