# 🏗️ MERIDIAN FX — BUILD STRATEGY AND ARCHITECTURE
---

## 📌 GUIDING PRINCIPLE

> **"First prove that Meridian generates incremental out-of-sample information. Then build the platform around that evidence."**

**The center of gravity of the project is not a model. It is a reproducible, point-in-time, leakage-free dataset.**

---

## 📐 MAPPING TO SOFTWARE ENGINEERING

| Petroleum Engineering     | Software Engineering                       | Meridian FX                          | Question Answered              |
| ------------------------- | ------------------------------------------ | ------------------------------------ | ------------------------------ |
| **Conceptual**            | **Product / System Concept**               | Problem Statement + Product Vision   | What are we building and why?  |
| **Basic Engineering**     | **Architecture / High-Level Design**       | 4-Layer Architecture + C4 Diagrams   | How will it be structured?     |
| **Detailed Engineering**  | **Detailed Design / Low-Level Design**     | Schemas + Interfaces + API Contracts | How will each component work?  |
| **Construction Drawings** | **Implementation Specs / Code + IaC**      | Repo Structure + Docker              | How exactly will it be built?  |
| **Construction**          | **Implementation + Integration + Testing** | Code + CI/CD + Tests                 | Is it built and working?       |
| **Commissioning**         | **Validation + Performance Testing**       | Backtesting + Leakage Tests + SHAP   | Does it meet the requirements? |
| **As-Built**              | **System Documentation + ADRs**            | C4 Diagrams + ADRs + API Docs        | What was actually built?       |
| **Operations**            | **Production + Monitoring**                | Serving + Alerts + Drift Detection   | Is it still working correctly? |

---

# 🏛️ 4-LAYER ARCHITECTURE + CROSS-CUTTING GOVERNANCE

```text
┌─────────────────────────────────────────────────────────────┐
│                   1. INTELLIGENCE LAYER                     │
│       API · Dashboard · Morning Brief · Registry            │
├─────────────────────────────────────────────────────────────┤
│                   2. DECISION ENGINE                        │
│       Dynamic Signal Fusion · Ranking · Economic Filter     │
├─────────────────────────────────────────────────────────────┤
│                   3. RESEARCH LAYER                         │
│   Quant Models · Macro Models · RAG · Backtesting           │
├─────────────────────────────────────────────────────────────┤
│                    4. DATA LAYER                            │
│      Raw Data · Normalization · Feature Engineering         │
├─────────────────────────────────────────────────────────────┤
│              CROSS-CUTTING: GOVERNANCE / MLOps              │
│ Versioning · Lineage · Experiment Tracking · Monitoring     │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Principle

```text
DATA CONTRACT → FEATURE CONTRACT → MODEL CONTRACT →
EVALUATION CONTRACT → DEPLOYMENT CONTRACT → OBSERVABILITY CONTRACT
```

**Each layer has a clearly defined contract with the layer before and after it.**

---

# 📋 LAYER 1 — DATA LAYER (Data Engineering)

**Role:** Single source of truth for the ML pipeline.

| Component            | Technical Role         | Technology    |
| -------------------- | ---------------------- | ------------- |
| **Raw Storage**      | Immutable source data  | S3 / MinIO    |
| **Normalized DB**    | Clean and unified data | PostgreSQL    |
| **Feature Store**    | Temporal features      | TimescaleDB   |
| **Feature Pipeline** | Feature computation    | Python / DVC  |
| **PIT Dataset**      | Leakage-free data      | Parquet + DVC |

### Timestamp Semantics (CRITICAL)

```text
┌────────────────────────────────────────────────────────────────┐
│                    TIMESTAMP SEMANTICS                        │
├────────────────────────────────────────────────────────────────┤
│  observation_timestamp  → When the economic event occurred    │
│  release_timestamp      → When it was officially published   │
│  knowledge_timestamp    → When it became available to the     │
│                           model (release + ingestion delay)   │
│  prediction_timestamp   → When the prediction is generated   │
│  revision_timestamp     → When the data was revised          │
└────────────────────────────────────────────────────────────────┘
```

### Fundamental Rule (Inviolable)

```text
knowledge_timestamp <= prediction_timestamp
```

**No future information may enter the feature matrix.**

### Primary Artifact

```text
USDJPY_PIT_v1
```

**Characteristics:**

* 0% leakage (automatically validated)
* 100% reproducible (DVC + hashes)
* Coverage: 2015–2026
* Versioned with DVC

---

# 📋 LAYER 2 — RESEARCH LAYER (ML Engineering)

**Role:** Research and modeling pipeline.

### Research Pipeline

```text
                RESEARCH PIPELINE

                    Dataset (USDJPY_PIT_v1)
                       ↓
               Feature Pipeline
                       ↓
                Train / Validation Split
                       ↓
                 Model Training
                       ↓
                  Backtesting
                       ↓
                 Explainability (SHAP)
                       ↓
                  Experiment Log (MLflow)
```

### Components

**Quant Engine:** Predictive models (XGBoost, Elastic Net, ARIMA)

**Macro Engine:** Economic regime classification (Inflation, Growth, Risk, Policy)

**RAG Engine:** Extraction of latent variables from central bank documents (Fed, BoJ) with 12-month z-score normalization

**Walk-Forward Backtester:** Realistic backtesting with purging and embargoing

---

# 📋 LAYER 3 — DECISION ENGINE (Dynamic Signal Fusion)

**Role:** Combine signals into a final forecast using regime-dependent weights.

### Signal Flow

```text
             ┌──────────────┐
             │ Quant Signal │ (XGBoost prediction + probability)
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │  Macro Regime │ (Inflation, Growth, Risk, Policy)
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │  RAG Signal  │ (Hawkish/Dovish z-score, Divergence)
             └──────┬───────┘
                    │
                    ▼
         Dynamic Signal Fusion
         (Regime-Dependent Weights)
                    │
                    ▼
             Decision Score
                    │
                    ▼
          Economic Filter (Costs)
                    │
                    ▼
          Final Forecast
```

### Regime-Based Weights

| Regime       | Quant | Macro | RAG  | Rationale                                  |
| ------------ | ----- | ----- | ---- | ------------------------------------------ |
| **Risk-On**  | 0.50  | 0.30  | 0.20 | Market functions normally, quant dominates |
| **Risk-Off** | 0.30  | 0.40  | 0.30 | Macro and central banks matter more        |
| **Neutral**  | 0.45  | 0.35  | 0.20 | Balanced                                   |

**Note:** The weights are experimental hypotheses, not definitive rules. They will be calibrated out-of-sample through walk-forward testing.

### Architectural Principle

> **SHAP is an explainability layer, not a decision layer.**

```text
                 MODEL
                   │
              prediction
                   │
        ┌──────────┴──────────┐
        │                     │
   Decision Engine          SHAP
        │                     │
   WHAT to predict       WHY the model
        │                made the prediction
        │                     │
        └──────────┬──────────┘
                   ↓
              INTELLIGENCE
```

### Target Definition (FROZEN)

```text
Target: 5-day forward log return
y_t = log(S_{t+5} / S_t)

Direction: 1 if y_t > 0 else 0

Prediction timestamp: T (New York close, 17:00 EST)

Information cutoff: knowledge_timestamp <= T

Evaluation: realized return from T to T+5 trading days

Handling:
- Weekends: skip
- Holidays: next trading day
- Non-overlapping windows for evaluation
```

### Economic Filter

```text
Forecast Distribution
        ↓
Expected Return
        ↓
Subtract: Spread + Slippage + Transaction Costs
        ↓
Net Expected Return
        ↓
IF Net Expected Return > Minimum Economic Edge
        ↓
    Actionable Signal
ELSE
        ↓
    No Trade
```

---

# 📋 LAYER 4 — INTELLIGENCE LAYER (Application)

**Role:** Convert ML infrastructure into a product.

### API Layer

```text
GET /v1/fx/{pair}/forecast
GET /v1/fx/{pair}/forecast/history
GET /v1/regime/current
GET /v1/rag/signal
GET /v1/shap/explain
GET /v1/performance/matrix
```

### Dashboard Structure

```text
┌─────────────────────────────────────────────────────────────┐
│  MERIDIAN FX — USD/JPY FORECAST                            │
├─────────────────────────────────────────────────────────────┤
│  Forecast: Bullish │ Probability: 74% │ Horizon: 5D       │
│  Model: XGBoost v2.3 │ Feature Store: FS-v1.2              │
├─────────────────────────────────────────────────────────────┤
│  KEY DRIVERS                                               │
│  ├── Rate Spread     ▲ +0.31                              │
│  ├── VIX            ▼ -0.18                              │
│  └── COT            ▼ -0.12                              │
├─────────────────────────────────────────────────────────────┤
│  MACRO REGIME: Restrictive US / Normalizing JP             │
│  POLICY DIVERGENCE: High (Fed Hawkish / BoJ Dovish)        │
│  RISK REGIME: Risk-On                                      │
├─────────────────────────────────────────────────────────────┤
│  RAG SIGNAL                                                │
│  ├── FOMC Sentiment: Hawkish (z-score: +1.2)              │
│  ├── BoJ Sentiment: Dovish (z-score: -0.8)                │
│  └── Policy Divergence: High (0.44)                       │
├─────────────────────────────────────────────────────────────┤
│  HISTORICAL PERFORMANCE                                    │
│  Accuracy: TBD │ Sharpe: TBD │ Max DD: TBD                │
│  Calibration: TBD                                          │
└─────────────────────────────────────────────────────────────┘
```

---

# 🔬 EXPERIMENTATION (Ablation Study)

**Principle:** Every new component must earn its place through an experiment.

### Experiment Sequence

```text
E0   → Random Walk (Baseline benchmark)
E0b  → Random Walk + Drift (Robust benchmark)
E1a  → ARIMA (Time-series model)
E1b  → Elastic Net (Linear control)
E2a  → XGBoost (Non-linear model)
E2b  → XGBoost + Monotonic Constraints (Economically informed)
E3   → + Market Features (VIX, COT, Gold, Oil)
E4   → + Macro Regime (Macro context)
E5   → + Central Bank RAG (Central bank texts)
E6   → Walk-Forward Retraining (Temporal adaptation)
E7   → Ensemble (XGBoost + LSTM)
```

### Evaluation Framework

**Primary Metrics (Economic):**

* Sharpe Ratio
* Sortino Ratio
* Maximum Drawdown
* Net Return (after costs)
* Profit Factor
* Turnover

**Secondary Metrics (Statistical):**

* Directional Accuracy
* AUC
* Brier Score
* Log Loss
* Information Coefficient
* Calibration Error

**Robustness Analysis:**

* Performance by regime (Risk-On / Risk-Off)
* Performance by volatility (High / Low)
* Performance by subperiod (2015–2018, 2019–2021, 2022–2026)
* Walk-forward stability

---

# 🔐 GOVERNANCE / MLOps (Cross-Cutting Layer)

**Role:** Answer the question: *"Which model generated this prediction, using which data, code, and features?"*

### Lineage Model

```text
Prediction
    │
    ├── Model Registry
    │       ├── model_version
    │       ├── feature_version
    │       ├── dataset_version
    │       ├── hyperparameters
    │       ├── git_commit
    │       └── training_run
    │
    ├── Prediction Registry
    │       ├── prediction_id
    │       ├── timestamp
    │       ├── predicted_value
    │       ├── probability
    │       ├── shap_values
    │       └── actual_value
    │
    ├── Fusion Registry
    │       ├── fusion_version
    │       ├── weights
    │       ├── calibration_window
    │       └── regime_weights
    │
    └── Data Lineage
            ├── Feature Store
            ├── Normalized Data
            ├── Raw Data
            └── Original Source
```

### Registries

**Model Registry:**

```text
model_id
model_version
model_type
dataset_version
feature_version
code_commit
hyperparameters
training_period_start
training_period_end
validation_period_start
validation_period_end
test_period_start
test_period_end
metrics (Sharpe, DA, AUC, etc.)
status (experimental, staging, production)
created_at
deployed_at
```

**Prediction Registry:**

```text
prediction_id
model_id
fusion_version
feature_store_version
timestamp_utc
horizon
predicted_return
predicted_probability
calibrated_probability
confidence_interval_lower
confidence_interval_upper
shap_values (JSON)
regime_at_prediction (JSON)
rag_signal_at_prediction (JSON)
decision_score
actual_return
transaction_cost
net_return
created_at
```

**Fusion Registry:**

```text
fusion_id
fusion_version
weights (JSON)
regime_weights (JSON)
calibration_window_start
calibration_window_end
calibration_method
metrics
status
created_at
```

---

# 🧪 TESTING STRATEGY

```text
                    TESTING PYRAMID
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
           DATA        MODEL     SYSTEM
              │          │          │
       Schema       Metrics      API
       Range        Stability    Integration
       PIT          Calibration  Deployment
       Duplicates   Drift        Contracts
       Quality      Reproducibility
```

### Test Categories

| Category           | Tests                                                   | When              |
| ------------------ | ------------------------------------------------------- | ----------------- |
| **Data Tests**     | Schema, Range, PIT, Duplicates, Quality                 | Post-ingestion    |
| **Model Tests**    | Metrics, Stability, Calibration, Drift, Reproducibility | Post-training     |
| **System Tests**   | API, Integration, Deployment, Contracts                 | Pre-deployment    |
| **Backtest Tests** | Leakage, Overfitting, Stability, Costs                  | During evaluation |
| **Economic Tests** | Sharpe, Drawdown, Turnover, Net Return                  | Post-backtest     |

### Critical Test (Invariant)

```text
knowledge_timestamp <= prediction_timestamp
```

**If violated, the pipeline fails immediately.**

---

# 📋 BUILD STRATEGY — 8 WEEKS (MVP)

## Week 1 — Infrastructure

| Activity                 | Deliverable              |
| ------------------------ | ------------------------ |
| Docker + Python          | Reproducible environment |
| PostgreSQL + TimescaleDB | Database                 |
| S3 / MinIO               | Raw storage              |
| DVC                      | Data versioning          |
| MLflow                   | Experiment tracking      |

**Criterion:** `docker compose up` starts all services.

---

## Week 2 — Data Pipeline

| Activity    | Source            |
| ----------- | ----------------- |
| US Macro    | FRED / ALFRED     |
| Japan Macro | e-Stat / OECD     |
| Market Data | Yahoo Finance     |
| Positioning | CFTC Bulk Exports |

**Criterion:** Complete ingestion of raw data.

---

## Week 3 — PIT Dataset

| Activity            | Deliverable                |
| ------------------- | -------------------------- |
| Normalization Layer | Unified data               |
| Point-in-Time Join  | `knowledge_timestamp <= t` |
| Feature Engineering | Ready-to-use features      |
| Leakage Tests       | Automated validation       |
| DVC Snapshot        | `USDJPY_PIT_v1`            |

**Criterion:** 0% leakage, versioned dataset.

---

## Week 4 — Baseline Models

| Activity                  | Deliverable      |
| ------------------------- | ---------------- |
| Random Walk (E0)          | Benchmark        |
| Random Walk + Drift (E0b) | Robust benchmark |
| Elastic Net (E1b)         | Linear control   |
| XGBoost (E2a)             | Non-linear model |
| SHAP                      | Explanations     |

**Criterion:** All experiments logged in MLflow.

---

## Week 5 — Walk-Forward Backtesting

| Activity               | Deliverable              |
| ---------------------- | ------------------------ |
| Expanding Walk-Forward | Realistic backtest       |
| Rolling Walk-Forward   | Moving-window evaluation |
| Purging & Embargoing   | Boundary cleanup         |
| Transaction Costs      | Spread + slippage        |

**Criterion:** E0–E2 results matrix.

---

## Week 6 — Macro Regime & Advanced Features

| Activity             | Deliverable               |
| -------------------- | ------------------------- |
| Macro Agent          | Regime classification     |
| E3 + Market Features | VIX, COT, Gold, Oil       |
| E4 + Regime          | Model with regime context |

**Criterion:** Ablation study demonstrates incremental improvement.

---

## Week 7 — Decision Engine & API

| Activity            | Deliverable              |
| ------------------- | ------------------------ |
| Dynamic Fusion      | Regime-dependent weights |
| Economic Filter     | Costs and tradability    |
| REST API            | FastAPI endpoints        |
| Prediction Registry | Prediction traceability  |

**Criterion:** API returns forecast + explanation.

---

## Week 8 — Dashboard & Documentation

| Activity            | Deliverable                |
| ------------------- | -------------------------- |
| Dashboard           | Streamlit                  |
| Morning Brief       | Executive report           |
| SHAP Visualizations | Graphical explanations     |
| Documentation       | ADRs + API Docs + Runbooks |

**Criterion:** Dashboard displays forecast + drivers + performance.

---

# 🚀 THE FIRST ENGINEERING MILESTONE

**Not:** *"Build an XGBoost model."*

**Yes:**

> **Build a reproducible, point-in-time, leakage-free dataset for USD/JPY.**

```text
                 USDJPY_PIT_v1

Raw Sources (FRED, e-Stat, Yahoo, CFTC)
     ↓
Ingestion (API calls, downloads)
     ↓
Validation (schema, ranges, duplicates)
     ↓
Normalization (unified schema, UTC timestamps)
     ↓
Point-in-Time Join (knowledge_timestamp <= t)
     ↓
Feature Engineering (differentials, spreads, z-scores)
     ↓
Leakage Tests (automatic validation)
     ↓
Versioning (DVC, hash, snapshot)
     ↓
USDJPY_PIT_v1
```

**Once this artifact exists, the rest of Meridian can be built on a reliable foundation.**

---

# 📋 EXECUTIVE SUMMARY

| Aspect                | Meridian FX                                           |
| --------------------- | ----------------------------------------------------- |
| **Architecture**      | 4 layers + cross-cutting MLOps                        |
| **Development Model** | Incremental / hypothesis-driven                       |
| **Data Strategy**     | PIT, anti-leakage, versioned                          |
| **ML Strategy**       | Ablation study E0→E7                                  |
| **Fusion**            | Dynamic regime-dependent weights                      |
| **Evaluation**        | Statistical + economic metrics                        |
| **Governance**        | Model, Prediction & Fusion Registries                 |
| **Testing**           | Data + Model + System + Backtest + Economic           |
| **Delivery**          | API + Dashboard + Morning Brief                       |
| **Stack**             | Python, PostgreSQL, XGBoost, FastAPI, Docker          |
| **MVP**               | 8 weeks (USD/JPY, PIT, XGBoost, SHAP, API, Dashboard) |

---

# 🎯 GUIDING PRINCIPLES

| Principle             | Implementation                                             |
| --------------------- | ---------------------------------------------------------- |
| **Data First**        | `Data → Features → Models`                                 |
| **Leakage-Free**      | `knowledge_timestamp <= prediction_timestamp`              |
| **Hypothesis Driven** | Every component must justify its value                     |
| **Reproducible**      | `same code + same dataset + same config = same experiment` |
| **Modular**           | Layers with clear interfaces                               |
| **Traceable**         | `Prediction → Model → Features → Data → Source`            |
| **Observable**        | Metrics, logs, alerts, drift detection                     |

---

**Meridian FX — From Market Noise to Actionable FX Intelligence** ✅

**Version 2.4 — Approved for Execution**
