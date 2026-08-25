# 🏗️ MERIDIAN FX — APPLICATION PRODUCTION STRATEGY (FINAL VERSION)

---

## 📌 Executive Summary

Meridian FX is a **quantitative financial intelligence platform** designed as a reproducible applied research system. This version incorporates all methodological and technical revisions, establishing a balance between **academic rigor**, **engineering pragmatism**, and **MVP focus**.

**Guiding principle:**

> **First demonstrate that Meridian generates incremental out-of-sample information. Then build the platform around that evidence.**

---

## 🏛️ Application Architecture

### High-Level Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MERIDIAN FX — PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │   DATA LAYER     │    │   MODEL LAYER    │    │   OUTPUT LAYER   │          │
│  │                  │    │                  │    │                  │          │
│  │  Raw Storage     │───▶│  Quant Agent     │───▶│  Dashboard       │          │
│  │  Normalized DB   │    │  Macro Agent     │    │  REST API        │          │
│  │  Feature Store   │    │  RAG Agent       │    │  Reports         │          │
│  │                  │    │  Decision Fusion │    │                  │          │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘          │
│           │                        │                        │                  │
│           ▼                        ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐          │
│  │                    SHARED INFRASTRUCTURE                         │          │
│  │  PostgreSQL/TimescaleDB + S3/MinIO + DVC + MLflow + Docker     │          │
│  └──────────────────────────────────────────────────────────────────┘          │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐          │
│  │                    GOVERNANCE & REPRODUCIBILITY                  │          │
│  │  Model Registry + Prediction Registry + Data Lineage            │          │
│  └──────────────────────────────────────────────────────────────────┘          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Conceptual Architecture (5 Engines)

```text
                 MERIDIAN FX
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      DATA         RESEARCH      CONTEXT
        │             │             │
        ↓             ↓             ↓
      PIT          QUANT          MACRO/RAG
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                DECISION ENGINE
                      ↓
                 INTELLIGENCE
                      ↓
              API / DASHBOARD
```

---

## 🧩 System Capabilities (By Priority)

### Core (Essential for MVP)

| Capability             | Description                           | Priority     |
| ---------------------- | ------------------------------------- | ------------ |
| **Point-in-Time Data** | Ingestion with vintages, anti-leakage | **Critical** |
| **Feature Store**      | Flat table with model-ready variables | **Critical** |
| **Baselines**          | Random Walk, Random Walk + Drift      | **Critical** |
| **Linear Model**       | Elastic Net (control for H1)          | **Critical** |
| **Nonlinear Model**    | XGBoost with SHAP                     | **Critical** |
| **Walk-Forward**       | Realistic backtesting                 | **Critical** |
| **Evaluation**         | Statistical and economic metrics      | **Critical** |

### Extensions (Post-MVP)

| Capability              | Description                | Priority   |
| ----------------------- | -------------------------- | ---------- |
| **Macro Agent**         | Regime classification      | **High**   |
| **RAG Agent**           | Latent variables from text | **High**   |
| **Model Registry**      | Model versioning           | **Medium** |
| **Prediction Registry** | Prediction traceability    | **Medium** |
| **API**                 | Programmatic access        | **Medium** |
| **Dashboard**           | Interactive visualization  | **Medium** |
| **Multi-Currency**      | Expansion to other pairs   | **Low**    |

---

## 📋 Build Sequence (MVP Approach)

### Phase 0 — Foundation (Weeks 1-2)

| Activity                                    | Deliverable          | Acceptance Criterion     |
| ------------------------------------------- | -------------------- | ------------------------ |
| Set up Python + Docker environment          | `docker-compose.yml` | Reproducible environment |
| Initialize PostgreSQL + TimescaleDB         | Database             | Successful connection    |
| Configure S3 / MinIO                        | Data bucket          | Upload/download works    |
| Define Raw/Normalized/Feature Store schemas | SQL scripts          | Migrations applied       |
| Configure DVC for versioning                | DVC repository       | `dvc pull` works         |

**Minimum Stack:**

* Python 3.10+
* PostgreSQL + TimescaleDB
* S3/MinIO
* DVC
* Docker

---

### Phase 1 — Data Ingestion & Feature Store (Weeks 3-5)

| Activity                       | Deliverable | Acceptance Criterion        |
| ------------------------------ | ----------- | --------------------------- |
| Configure FRED/ALFRED API      | Client      | Successful download         |
| Configure e-Stat / OECD        | Client      | Successful download         |
| Configure Yahoo Finance        | Client      | USD/JPY, VIX, Gold, Oil     |
| Configure CFTC Bulk Exports    | Pipeline    | COT with `release_datetime` |
| Implement Normalized Layer     | Tables      | Complete temporal metadata  |
| Implement Feature Store        | Table       | Leakage tests pass          |
| Create USD/JPY PIT v1 snapshot | Dataset     | Hash verified               |

**Feature Store (MVP):**

```sql
CREATE TABLE feature_store (
    observation_timestamp TIMESTAMPTZ NOT NULL,
    knowledge_timestamp TIMESTAMPTZ NOT NULL, -- When it became available
    -- USD/JPY Features
    usd_jpy_spot NUMERIC(12, 6),
    usd_jpy_return_1d NUMERIC(12, 6),
    usd_jpy_return_5d NUMERIC(12, 6),
    us_jp_rate_spread NUMERIC(12, 6),
    us_jp_inflation_diff NUMERIC(12, 6),
    us_jp_gdp_diff NUMERIC(12, 6),
    us_jp_pmi_diff NUMERIC(12, 6),
    us_jp_productivity_diff NUMERIC(12, 6),
    -- Market Features
    vix_level NUMERIC(12, 6),
    vix_change NUMERIC(12, 6),
    gold_price NUMERIC(12, 6),
    oil_price NUMERIC(12, 6),
    ted_spread NUMERIC(12, 6),
    -- Positioning
    cot_jpy_net_position NUMERIC(18, 6),
    cot_jpy_zscore NUMERIC(12, 6),
    PRIMARY KEY (observation_timestamp, knowledge_timestamp)
);

SELECT create_hypertable('feature_store', 'observation_timestamp');
```

---

### Phase 2 — Target Definition and Baseline Experiments (Weeks 6-8)

| Activity                            | Deliverable          | Acceptance Criterion      |
| ----------------------------------- | -------------------- | ------------------------- |
| **Define target and horizon**       | Frozen specification | See section below         |
| Implement `MeridianModel` interface | Base class           | All models implement it   |
| Random Walk (E0)                    | Benchmark            | Baseline metrics          |
| Random Walk + Drift (E0b)           | Robust benchmark     | Baseline metrics          |
| AR / ARIMA (E1a)                    | Time-series model    | AIC/BIC optimized         |
| Elastic Net (E1b)                   | Linear control       | Cross-validation + SHAP   |
| XGBoost without constraints (E2a)   | Nonlinear model      | Hyperparameters optimized |
| SHAP for explainability             | Explanations         | Functional visualization  |
| Run E0–E2b with walk-forward        | Results matrix       | MLflow logged             |

**Target Definition (FROZEN):**

```text
Target:
5-day forward log return
y_t = log(S_{t+5} / S_t)

Direction:
1 if forward return > 0 else 0

Prediction timestamp:
T (New York close, 17:00 EST)

Information cutoff:
All features with knowledge_timestamp <= T

Evaluation:
Realized return from T to T+5 trading days

Handling:
- Weekends: skip
- Holidays: next trading day
- Overlapping: non-overlapping windows for evaluation
```

---

### Phase 3 — Walk-Forward Protocol (Weeks 9-10)

| Activity                | Deliverable              | Acceptance Criterion                   |
| ----------------------- | ------------------------ | -------------------------------------- |
| Expanding Walk-Forward  | Realistic backtest       | 2015→2021, 2015→2022, ...              |
| Rolling 6M Walk-Forward | Rolling-window backtest  | Consistent results                     |
| Purging & Embargoing    | Boundary cleanup         | Remove nearby overlapping observations |
| Subperiod evaluation    | Robustness analysis      | Consistency in risk-off/on             |
| Diebold-Mariano test    | Statistical significance | Evaluation + interpretation            |

**Walk-Forward Protocol:**

```text
Train: 2015-2021 → Predict: 2022
Train: 2015-2022 → Predict: 2023
Train: 2015-2023 → Predict: 2024
Train: 2015-2024 → Predict: 2025
Train: 2015-2025 → Predict: 2026

Purging: Remove observations within 10 days of train/test boundary
Embargoing: Leave 5-day buffer after training period
```

---

### Phase 4 — Additional Agents (Weeks 11-13)

| Activity                               | Deliverable           | Acceptance Criterion        |
| -------------------------------------- | --------------------- | --------------------------- |
| Macro Agent (rules + Markov Switching) | Regime classification | Accuracy > 80%              |
| Integrate Market Features (E3)         | Extended features     | SHAP + stability            |
| Integrate Regime as feature (E4)       | Regime-aware model    | Improvement vs E3 in crises |
| RAG Agent (Fed + BoJ)                  | Latent variables      | Correlation > 0.3 post-FOMC |
| Integrate RAG (E5)                     | Complete model        | Improvement vs E4           |
| Run E3–E5 with walk-forward            | Results matrix        | MLflow logged               |

**RAG Agent — Event-Driven Design:**

```text
[Document Detection] → [Queue] → [NLP Worker] → [normalized_rag]
                                                    │
                                                    ▼
                                         [Feature Store Override]
                                                    │
                                                    ▼
                                         [Decision Fusion]
```

---

### Phase 5 — Model & Prediction Registry (Weeks 14-15)

| Activity            | Deliverable                 | Acceptance Criterion  |
| ------------------- | --------------------------- | --------------------- |
| Model Registry      | Table + MLflow              | Every model versioned |
| Prediction Registry | Prediction table            | Complete traceability |
| Data Lineage        | Raw→Prediction traceability | Functional query      |

**Model Registry:**

```sql
CREATE TABLE model_registry (
    model_id VARCHAR(64) PRIMARY KEY,
    model_version VARCHAR(32) NOT NULL,
    model_type VARCHAR(32) NOT NULL,
    training_dataset_version VARCHAR(32) NOT NULL,
    feature_version VARCHAR(32) NOT NULL,
    code_commit VARCHAR(64) NOT NULL,
    hyperparameters JSONB,
    training_period_start DATE,
    training_period_end DATE,
    validation_period_start DATE,
    validation_period_end DATE,
    test_period_start DATE,
    test_period_end DATE,
    metrics JSONB, -- includes Sharpe, DA, AUC, etc.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'experimental'
);
```

**Prediction Registry:**

```sql
CREATE TABLE prediction_registry (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(64) NOT NULL REFERENCES model_registry(model_id),
    feature_store_version VARCHAR(32) NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    horizon VARCHAR(10) NOT NULL, -- '5D'
    predicted_return NUMERIC(18, 6),
    predicted_probability NUMERIC(6, 4),
    confidence_interval_lower NUMERIC(18, 6),
    confidence_interval_upper NUMERIC(18, 6),
    shap_values JSONB,
    regime_at_prediction JSONB,
    rag_signal_at_prediction JSONB,
    actual_return NUMERIC(18, 6),
    actual_direction BOOLEAN,
    transaction_cost NUMERIC(18, 6),
    net_return NUMERIC(18, 6),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

### Phase 6 — API & Dashboard (Weeks 16-17)

| Activity                  | Deliverable               | Acceptance Criterion |
| ------------------------- | ------------------------- | -------------------- |
| REST API with FastAPI     | Documented endpoints      | OpenAPI generated    |
| Dashboard with Streamlit  | Interactive visualization | Usability validated  |
| Automated Research Report | HTML/PDF report           | Generation < 5 min   |
| SHAP visualizations       | Graphical explanations    | Interpretable        |

**API Endpoints (MVP):**

```text
GET /health
GET /forecast/usdjpy?horizon=5D
GET /forecast/usdjpy/history?start=2024-01-01&end=2025-01-01
GET /regime/current
GET /rag/signal
GET /shap/explain?timestamp=2026-08-25
GET /performance/matrix?experiment=E5
```

---

### Phase 7 — Multi-Currency (Weeks 18-20)

| Activity         | Deliverable              | Acceptance Criterion     |
| ---------------- | ------------------------ | ------------------------ |
| EUR/USD pipeline | Data + models            | Extended Feature Store   |
| GBP/USD pipeline | Data + models            | Extended Feature Store   |
| Currency Radar   | Multi-currency dashboard | Integrated visualization |

---

## 📊 Evaluation Metrics

### Statistical (Secondary)

| Metric                      | Description                               | Interpretation                    |
| --------------------------- | ----------------------------------------- | --------------------------------- |
| **Directional Accuracy**    | % of correct directions                   | Reference, not an absolute target |
| **AUC**                     | Area under ROC curve                      | Discrimination capability         |
| **Brier Score**             | Probability calibration                   | Probabilistic accuracy            |
| **Log Loss**                | Probabilistic loss                        | Calibration                       |
| **Information Coefficient** | Correlation between prediction and actual | Incremental signal                |

### Economic (Primary)

| Metric                   | Description                | Interpretation       |
| ------------------------ | -------------------------- | -------------------- |
| **Sharpe Ratio**         | Risk-adjusted return       | > 0.5 is interesting |
| **Sortino Ratio**        | Penalizes downside only    | > 0.4 is interesting |
| **Max Drawdown**         | Maximum loss               | < 10% preferable     |
| **Profit Factor**        | Gross profit / gross loss  | > 1.2 is interesting |
| **Cost-Adjusted Return** | After spreads and slippage | Final criterion      |
| **Turnover**             | Trading frequency          | Controls costs       |

### Robustness

| Metric                        | Description                     |
| ----------------------------- | ------------------------------- |
| **Performance by Regime**     | Risk-on vs Risk-off             |
| **Performance by Volatility** | High vs Low volatility          |
| **Performance by Subperiod**  | 2015-2018, 2019-2021, 2022-2026 |
| **Stability**                 | Consistency across walk-forward |
| **SHAP Stability**            | Consistency of drivers          |

---

## 🔐 Governance & Reproducibility

### Model Registry

```text
model_id
model_version
dataset_version
feature_version
code_commit
hyperparameters
training_period
validation_period
test_period
metrics
status
```

### Prediction Registry

```text
prediction_id
model_id
feature_version
timestamp
horizon
predicted_return
predicted_probability
shap_values
regime
rag_signal
actual_return
transaction_cost
net_return
```

### Data Lineage

```text
Prediction
    ↓
Model
    ↓
Feature Store
    ↓
Normalized Data
    ↓
Raw Data
    ↓
Source
```

---

## ✅ MVP Success Criteria

| #  | Criterion                   | Metric                    |
| -- | --------------------------- | ------------------------- |
| 1  | Point-in-time dataset built | 2015–2026, 0% leakage     |
| 2  | Target and horizon defined  | Frozen pre-implementation |
| 3  | Random Walk implemented     | Baseline established      |
| 4  | Elastic Net implemented     | Linear control            |
| 5  | XGBoost implemented         | Nonlinear model           |
| 6  | Walk-Forward implemented    | Realistic backtesting     |
| 7  | SHAP implemented            | Explanations generated    |
| 8  | Economic evaluation         | Sharpe, drawdown, costs   |
| 9  | Results matrix              | E0–E5 comparison          |
| 10 | Functional dashboard        | Interactive visualization |

---

## 🎯 Conclusion

Meridian FX v2.2 is a **quantitative research architecture approved for execution** that:

* ✅ Guarantees point-in-time and anti-leakage through `observation_timestamp` and `knowledge_timestamp`
* ✅ Follows a rigorous experimental methodology (E0 → E7) with walk-forward as the evaluation framework
* ✅ Explicitly defines the target and horizon before implementation
* ✅ Evaluates using economic metrics (Sharpe, costs) as primary metrics
* ✅ Records every prediction with complete traceability
* ✅ Scales from USD/JPY to multi-currency without refactoring
* ✅ Maintains an executable MVP focus within 17 weeks

**The next step is to build:**

> **`USDJPY_PIT_v1` — a reproducible, audited point-in-time dataset with leakage test = 0.**

---

**Version: 2.2 — Approved for Execution** ✅
