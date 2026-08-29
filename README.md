# Meridian FX

**Financial Intelligence & Decision Support System**

**A Stratus Intelligence Project**

Developed by **Daniel Canedo, MSc in Economics**

---

## Overview

Meridian FX is a quantitative foreign-exchange intelligence platform that transforms market data, macroeconomic indicators, and textual signals into **actionable, traceable, explainable, and measurable financial intelligence**.

It does not merely produce predictions. It produces structured decision outputs with full governance — every forecast is decomposed into economic drivers (SHAP), macro regime context, RAG-based central-bank sentiment, and explicit invalidation conditions.

**MVP scope:** 4 currency pairs (USD/JPY, EUR/USD, GBP/USD, USD/CNY) at a single 5-day horizon.

### What Meridian answers

| Question | Module |
| -------- | ------ |
| What is happening in the market? | Global Overview |
| What does Meridian expect? | Forecast Dashboard |
| Why? | Drivers & Explanation |
| Is it worth acting? | Economic Filter |
| What could invalidate the signal? | Signal Validity |
| How good has Meridian been? | Performance Dashboard |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        PRODUCT (MVP — 4 pairs)                         │
│    USD/JPY · EUR/USD · GBP/USD · USD/CNY    (single horizon 5D)         │
│                                                                        │
│   ┌───────────────┐   delivery contracts (Layer 1 §7)   ┌───────────┐ │
│   │   LAYER 1     │ ──────────────────────────────────▶ │ FRONTEND  │ │
│   │ DELIVERY API  │  /v1/fx/{pair}/forecast|drivers     │ Dashboard │ │
│   │  (FastAPI)*   │  /v1/fx/ranking                     │ (React TS)│ │
│   └───────┬───────┘  /v1/fx/performance/{pair}?period=  └───────────┘ │
│           │         /v1/status                                         │
│           │ consumption of the Decision pipeline                      │
│   ┌───────▼────────┐         ┌────────────────┐    ┌───────────────┐  │
│   │   LAYER 2      │ ◀───── │   LAYER 3      │    │   LAYER 4     │  │
│   │ DECISION       │ arti-  │ MODEL / SHAP / │    │ DATA QUALITY  │  │
│   │ ENGINE         │ fact   │ RAG / narrative │    │ FRESHNESS /   │  │
│   │ (Python)       │ + L4   │ (external)     │    │ DRIFT (ext.)  │  │
│   └────────────────┘ stream └────────────────┘    └───────────────┘  │
│                                                                       │
│   Deployment target: Render (FastAPI) + Neon (PostgreSQL)             │
└───────────────────────────────────────────────────────────────────────┘
```

### Layer responsibilities

| Layer | Role | Technology |
| ----- | ---- | ---------- |
| **Layer 1** — Delivery API | REST endpoints, response contracts | FastAPI, Uvicorn, Pydantic |
| **Layer 2** — Decision Engine | 8-stage deterministic pipeline | Python, XGBoost, scikit-learn, SHAP |
| **Layer 3** — Model / Narrative | Trained models, SHAP explainers, RAG sentiment | MLflow, external NLP |
| **Layer 4** — Data Quality | Freshness, drift, quality registries | External monitoring |
| **Frontend** — Dashboard | Contract-driven presentational UI | React 18, TypeScript, Vite, Tailwind |

---

## Tech Stack

### Backend

| Component | Technology |
| --------- | ---------- |
| Language | Python 3.12 |
| API framework | FastAPI + Uvicorn |
| Data validation | Pydantic 2 |
| ML models | XGBoost 3.4, scikit-learn |
| Explainability | SHAP |
| Data processing | pandas, numpy, pandas_ta |
| Data sources | Alpha Vantage, Twelve Data, Yahoo Finance |
| Testing | pytest (99 tests) |

### Frontend

| Component | Technology |
| --------- | ---------- |
| UI framework | React 18 + TypeScript 5 |
| Build tool | Vite 5 |
| Styling | Tailwind CSS 3 |
| Data fetching | TanStack Query 5 + Axios |
| Routing | react-router-dom 6 |
| Charts | Recharts 2 |
| Dates | date-fns 3 |
| Testing | Vitest + Testing Library (55 tests) |

---

## Project Structure

```
MeridianFX/
├── docs/                          Frozen specifications, prompts, contract governance
│   ├── Domain/                    Why (pitch), economics, data acquisition, production strategy
│   ├── High-Level Design/         Executive summary, product spec, build strategy, roadmap
│   ├── Low-Level Design/          Implementation plan + Layer_01..04 specs
│   ├── Product_specification/     FROZEN Layer_01..04 — contract authority
│   ├── Prompts/                   Prompt sequence: layer prompts + audit & build
│   └── Contract/                  Governance artifacts (traceability, gaps, freeze)
├── src/meridian_fx/decision/      Layer 2 Decision Engine (Python, Pydantic)
│   ├── contracts/                 Frozen domain contract types + provider interfaces
│   ├── filter/                    Economic filter + dynamic costs
│   ├── gates/                     Precedence-ordered hard gates
│   ├── quality/                   Decision quality from L4 registries
│   ├── sizing/                    Position sizing engine
│   ├── registries/                Decision, opportunity, safe-mode registries
│   ├── validation/                Contract audit + end-to-end mapping
│   └── pipeline.py                Composition root — 8-stage orchestration
├── tests/                         Backend pytest suite (99 tests)
├── frontend/                      Contract-driven React + TypeScript dashboard
│   └── src/
│       ├── components/            Presentational components (common, layout, forecast, drivers, ...)
│       ├── services/              API client + domain endpoint adapters
│       ├── hooks/                 Data-fetching hooks (TanStack Query)
│       ├── types/                 Contract types (Layer 1 §7) + gap types
│       ├── utils/                 Presentation-only formatting + status mapping
│       ├── pages/                 Page composition (hooks → presentational props)
│       └── tests/                 Infrastructure test suites (55 tests)
├── models/                        Trained .pkl models + registry
├── data/historical/               Historical market data
├── pyproject.toml                 Backend project metadata
├── architecture.md                System architecture document
└── report.md                      Repository analysis
```

---

## Decision Pipeline

The Layer 2 Decision Engine runs an **8-stage deterministic pipeline**:

```
PredictionArtifact (L3) + L4 streams
        │
        ▼
  1. Signals         raw quant / macro / RAG ──▶ SignalComponents
  2. Regime + fusion determine_regime() ──▶ FusionEngine ──▶ Direction
  3. Confidence      interval width + signals + reliability
  4. Costs           VIX via FeatureStore (no fallback path)
  5. Economic filter net_return, edge_ratio, actionable flag
  6. Quality         L4 registries (data quality / freshness / drift)
  7. Hard gates      quality, PIT, economic, exposure, correlation, regime
  8. Sizing          edge × quality × VIX-volatility
        │
        ▼
  Decision { action + rejection_reason + signal_validity }
```

---

## Frontend Design Principles

The frontend is **contract-driven**. All domain data comes from the Layer 1 v5.1 contract.

- **No derivation:** the frontend MUST NOT calculate, infer, rank, score, or derive analytical values
- **Transport only:** backend responses are consumed verbatim and presented without transformation
- **No fallback:** unsupported contract elements render `NOT_AVAILABLE`; no substitution is permitted
- **Nullability preserved:** `null` is never replaced with defaults

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
python -m pytest          # run 99 backend tests
```

### Frontend

```bash
cd frontend
npm install
npm run dev              # start dev server (http://localhost:5173)
npm run typecheck        # TypeScript no-emit check
npm test                 # run 55 frontend tests
npm run build            # typecheck + production build
```

### Environment Variables (Frontend)

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Layer 1 API base URL |
| `VITE_API_KEY` | `dev_placeholder_key_only` | Development placeholder |
| `VITE_POLLING_INTERVAL` | `60000` | Default polling interval (ms) |
| `VITE_ENVIRONMENT` | `development` | Runtime environment label |

> **Security:** `VITE_API_KEY` must not contain a production secret. Vite env
> variables are embedded in the client bundle. Production authentication must
> use a secure architecture (e.g., short-lived bearer tokens via a trusted
> identity provider).

---

## Testing

| Suite | Command | Coverage |
| ----- | ------- | -------- |
| Backend | `python -m pytest` | 99 tests — pipeline, contracts, gates, filter, sizing, validation |
| Frontend typecheck | `cd frontend && npm run typecheck` | TypeScript clean |
| Frontend tests | `cd frontend && npm test` | 55 tests — format, status, gaps, services, hooks, contracts |
| Frontend build | `cd frontend && npm run build` | Production build (~310 kB / 98 kB gzip) |

---

## Deployment (Target)

| Service | Role |
| ------- | ---- |
| **Render** (512 MB) | FastAPI + Uvicorn, inference-only (no training in prod) |
| **Neon** (PostgreSQL) | Features, precomputed predictions, SHAP explanations, metrics |

Memory target: ~250–300 MB. Max DB connections: ≤3.

---

## Contract Governance

| Artifact | Role |
| -------- | ---- |
| `CONTRACT_TRACEABILITY.md` | 73-row element → contract matrix (61 verified / 12 gap) |
| `CONTRACT_GAPS.md` | 16 joint gaps: G1–G9 + audit gaps |
| `FRONTEND_CONTRACT_FREEZE.md` | Freeze status: FREEZE WITH OPTIONAL GAPS, 0 blocking |
| `CONTRACT_VALIDATION.md` | Prompt 1 audit (7/7 contracts, PASS) |
| `MIGRATION_REPORT.md` | 66 mockup visual elements classified |
| `COMPONENT_MAPPING.md` | Data-bearing field → component → file (100%) |

**Governance workflow:** change request → update `CONTRACT_TRACEABILITY` → update `CONTRACT_GAPS` → re-freeze → re-validate.

---

## License

© 2026 Stratus Intelligence. All rights reserved.

---

<p align="center">
  <strong>MERIDIAN FX</strong><br>
  Financial Intelligence System<br><br>
  <strong>STRATUS INTELLIGENCE</strong>
</p>



## Fornt end 
cd frontend
npm run dev

## Back end 

cd ~/repo_lab/MeridianFX
source venv/bin/activate
uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000