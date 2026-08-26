# 📋 DOC 3 — OUTPUT SPECIFICATION — Analysis Summary

> *"Is this document necessary?"*

---

## ✅ SHORT ANSWER

**Yes, it is necessary and valuable.** Document 3 (Output Specification) is the **missing link** between the previous two documents. It is not redundant — it **completes the specification cycle**.

---

## 📊 THE THREE DOCUMENTS AS A CYCLE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE THREE DOCUMENTS AS A CYCLE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DOC 1 — BUILD STRATEGY                                            │    │
│  │  "HOW is it built?"                                                │    │
│  │                                                                     │    │
│  │  • Architecture (4 layers)                                         │    │
│  │  • Technologies (XGBoost, PostgreSQL, Docker)                      │    │
│  │  • Processes (PIT, leakage tests, walk-forward)                    │    │
│  │  • Timeline (8 weeks)                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DOC 2 — PRODUCT MOCKUP                                           │    │
│  │  "WHAT do users see?"                                             │    │
│  │                                                                     │    │
│  │  • UI/UX (screens, layouts)                                       │    │
│  │  • Views (Forecast, Drivers, Performance)                         │    │
│  │  • Deferred features (what goes to V2/V3)                         │    │
│  │  • Deployment (Neon, Render, 512 MB)                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DOC 3 — OUTPUT SPECIFICATION                                     │    │
│  │  "WHAT DATA is produced?"                                         │    │
│  │                                                                     │    │
│  │  • Output data structures (schemas)                                │    │
│  │  • Formal mathematical definitions                                 │    │
│  │  • Output levels (1-4)                                             │    │
│  │  • Metrics and quality criteria                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 WHAT DOC 3 PROVIDES THAT OTHERS DON'T

### 1. Data Schemas (Not UI, Not Architecture)

| Aspect | Doc 1 (Build) | Doc 2 (Mockup) | Doc 3 (Output) |
|--------|---------------|----------------|----------------|
| Data structure | ❌ Not specified | ❌ Visual only | ✅ **Complete** |
| Data types | ❌ | ❌ | ✅ **Defined** |
| Required fields | ❌ | ❌ | ✅ **Listed** |

**Doc 3 Example:**
```text
FORECAST
├── pair: "USD/JPY"          ← NEW
├── timestamp: UTC           ← NEW
├── raw_probability: 0.74    ← NEW
├── calibrated_probability: 0.68 ← NEW
├── expected_return: 0.0082  ← NEW
├── prediction_interval_95   ← NEW
│   ├── lower: -0.0031       ← NEW
│   └── upper: 0.0195        ← NEW
└── economic_filter          ← NEW
    ├── net_return: 0.0062   ← NEW
    ├── edge_ratio: 3.1      ← NEW
    └── actionable: true     ← NEW
```

---

### 2. Formal Mathematical Definitions

Doc 3 is the **only** document that provides equations:

| Concept | Doc 1 | Doc 2 | Doc 3 |
|---------|-------|-------|-------|
| Probability Calibration | ❌ | ❌ | ✅ `P_cal = f(P_raw)` |
| Expected Return | ✅ Conceptual | ❌ | ✅ `E[R] = E[log(S/t+h/S/t)]` |
| Sharpe Ratio | ❌ | ❌ | ✅ `Sharpe = (E[R_p] - R_f) / σ_p` |
| Brier Score | ❌ | ❌ | ✅ `Brier = (1/N) * Σ (P_pred - y_real)²` |
| Edge Ratio | ✅ Conceptual | ✅ Visual | ✅ **Formal** |

---

### 3. Four Output Levels

Doc 3 introduces a **new organization** not present in the others:

```
LEVEL 1 — FORECAST          ← Not in Doc 1/2 (structured)
LEVEL 2 — DRIVERS           ← Not in Doc 1/2 (structured)
LEVEL 3 — GLOBAL            ← Not in Doc 1/2 (structured)
LEVEL 4 — EVALUATION        ← Not in Doc 1/2 (structured)
```

Doc 2 has separate screens, but Doc 3 **conceptually unifies** all 4 levels as a coherent data model.

---

### 4. Model vs Strategy Distinction

Doc 3 is the **only** document that clearly distinguishes:

```
┌─────────────────────────────┐     ┌─────────────────────────────────┐
│  MODEL EVALUATION           │     │  STRATEGY EVALUATION            │
│  (Statistical)              │     │  (Economic)                     │
├─────────────────────────────┤     ├─────────────────────────────────┤
│  • Directional Accuracy     │     │  • Net Return                   │
│  • AUC                      │     │  • Sharpe Ratio                 │
│  • Brier Score              │     │  • Sortino Ratio                │
│  • Log Loss                 │     │  • Maximum Drawdown             │
│  • ECE (Calibration)        │     │  • Profit Factor                │
└─────────────────────────────┘     └─────────────────────────────────┘
```

**Why this is critical:**
- A model can have good DA but poor profitability
- A strategy can be profitable but poorly calibrated
- The distinction guides improvement decisions

---

### 5. Data Provenance (Traceability)

Doc 3 specifies **data origin metadata** that the others lack:

```
DATA PROVENANCE
├── source: Original data source
├── source_timestamp: When data was published
├── ingestion_timestamp: When Meridian ingested it
├── knowledge_timestamp: When data became available
├── revision_timestamp: When data was revised
└── data_quality_status: high / medium / low
```

This is essential for enforcing: **`knowledge_timestamp <= prediction_timestamp`**

---

## 📋 DETAILED COMPARISON

| Aspect | Doc 1 | Doc 2 | Doc 3 | Unique? |
|--------|-------|-------|-------|---------|
| **Architecture** | ✅ Complete | ⚠️ Simplified | ❌ | Doc 1 |
| **UI/UX** | ❌ | ✅ Complete | ❌ | Doc 2 |
| **Timeline** | ✅ 8 weeks | ❌ | ❌ | Doc 1 |
| **Technologies** | ✅ Stack | ✅ Neon/Render | ❌ | Doc 1+2 |
| **Data Schemas** | ❌ | ❌ | ✅ **Complete** | **Doc 3** |
| **Formal Math** | ⚠️ Conceptual | ❌ | ✅ **Formal** | **Doc 3** |
| **Output Levels** | ❌ | ⚠️ Separate screens | ✅ **Structured** | **Doc 3** |
| **Model vs Strategy** | ❌ | ❌ | ✅ **Distinction** | **Doc 3** |
| **Data Provenance** | ⚠️ Timestamp semantics | ❌ | ✅ **Complete** | **Doc 3** |
| **Target Audience** | Engineers | Stakeholders/UX | **Backend/Data** | **Doc 3** |

---

## 🎯 TARGET AUDIENCE FOR EACH DOCUMENT

| Document | Primary Audience | Purpose |
|----------|------------------|---------|
| **Doc 1 (Build Strategy)** | Software Architects, ML Engineers | Build the system |
| **Doc 2 (Product Mockup)** | Product Managers, Designers, Stakeholders | Visualize the product |
| **Doc 3 (Output Specification)** | **Data Engineers, Backend, Data Scientists** | **Implement the outputs** |

---

## ✅ IS IT NECESSARY?

### Arguments FOR keeping it:

1. **Completes the specification cycle** — "How" (Doc 1) → "What users see" (Doc 2) → "What data is produced" (Doc 3)

2. **Bridges ML and UI** — Backend engineers need to know exactly what data to serve

3. **Formalizes concepts** — Mathematical definitions are essential for correct implementation

4. **Specifies data contracts** — Critical for APIs and databases

5. **Distinguishes model from strategy** — Prevents conceptual confusion

### Arguments AGAINST keeping it:

1. **Somewhat redundant** — Some concepts appear in Doc 1 and 2
2. **More documentation** — Increases maintenance burden
3. **Could be merged** — Could be integrated into Doc 1 as "Output Contracts"

---

## 📝 RECOMMENDATION

**Keep Doc 3 but with a clearly defined role:**

### Proposed Renaming

```
Doc 1: 📐 MERIDIAN FX — System Architecture & Build Strategy
Doc 2: 📊 MERIDIAN FX — Product Mockup & UX Specification
Doc 3: 📋 MERIDIAN FX — Output Contracts & Data Specification  ← NEW NAME
```

### Doc 3 as "Contracts"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOC 3 AS "CONTRACTS"                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONTRACT 1 — Forecast Output                                      │    │
│  │  • JSON Schemas                                                    │    │
│  │  • Data types                                                      │    │
│  │  • Validations                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONTRACT 2 — Drivers Output                                       │    │
│  │  • SHAP structure                                                  │    │
│  │  • Macro regime format                                             │    │
│  │  • RAG output format                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONTRACT 3 — Global Intelligence Output                           │    │
│  │  • Rankings format                                                 │    │
│  │  • Divergences structure                                           │    │
│  │  • Early warnings schema                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONTRACT 4 — Evaluation Output                                    │    │
│  │  • Metrics schema                                                  │    │
│  │  • Calibration data format                                         │    │
│  │  • Drift detection output                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏁 FINAL CONCLUSION

| Question | Answer |
|----------|--------|
| **Is it necessary?** | ✅ **Yes** |
| **Is it redundant?** | ⚠️ **Partially**, but provides unique value |
| **What's unique?** | Schemas, formal definitions, output levels, model/strategy distinction |
| **Who is it for?** | Data engineers, backend engineers, data scientists |
| **Can it be merged?** | Yes, with Doc 1 (as "Output Contracts") |
| **Recommendation** | **Keep as a separate document** but rename to clarify its role |

---

## ONE-SENTENCE SUMMARY

> **Doc 3 is the "data contract" that ensures what Doc 1 builds and Doc 2 displays are aligned in terms of structure, types, and metrics — without it, backend engineers and UI developers work with undocumented implicit assumptions.**