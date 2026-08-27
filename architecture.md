# Meridian FX — Architecture

**Date:** 2026-08-27

Overall system architecture for the Meridian FX repo: a contract-driven FX intelligence product with a backend decision engine, a layer-1 delivery contract schema, and a React dashboard, all pinned to a frozen documentation suite.

---

## 1. System context

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCT (MVP — 4 pairs)                           │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY    (single horizon 5D)           │
│                                                                              │
│   ┌───────────────┐    delivery contracts (Layer 1 §7)    ┌──────────────┐  │
│   │   LAYER 1     │ ────────────────────────────────────▶ │  FRONTEND    │  │
│   │ DELIVERY API  │  /v1/fx/{pair}/forecast|drivers       │  Dashboard   │  │
│   │  (FastAPI)*   │  /v1/fx/ranking                       │  (React TS)  │  │
│   └───────┬───────┘  /v1/fx/performance/{pair}?period=    └──────────────┘  │
│           │          /v1/status                                             │
│           │ consumption of the Decision pipeline                           │
│   ┌───────▼────────┐           ┌──────────────────┐      ┌───────────────┐ │
│   │   LAYER 2      │ ◀─────── │   LAYER 3        │      │  LAYER 4      │ │
│   │ DECISION ENGINE│  artifact│ MODEL / SHAP /    │      │ DATA QUALITY  │ │
│   │  (Python, in-  │  + L4   │ RAG / narrative   │      │ FRESHNESS /   │ │
│   │   repo)        │  streams│  (external)       │      │ DRIFT (ext.)  │ │
│   └────────────────┘         └──────────────────┘      └───────────────┘ │
│                                                                           │
│   Deployment blueprint: Render (app) + Neon (PostgreSQL) — see docs/       │
└───────────────────────────────────────────────────────────────────────────┘
```

`*` The Layer 1 FastAPI delivery service is **specified but not yet implemented** in this repo; the frontend already targets its endpoints and the backend validation layer defines the `Decision → ForecastResponse` mapping.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specifications, prompts, and contract governance
├── src/meridian_fx/decision/ Layer 2 Decision Engine (backend logic, Pydantic)
├── tests/                    Backend pytest suite (99 tests)
├── frontend/                 Contract-driven React+TS dashboard
├── pyproject.toml            Backend project metadata (pythonpath=src, pytest config)
├── report.md                 Repository analysis (2026-08-27)
└── architecture.md           This document
```

---

## 3. Backend — Layer 2 Decision Engine

**Root:** `src/meridian_fx/decision/`. **Frozen against:** `docs/Product_specification/Layer_02.md` v3.4.1. **Governance:** *DO NOT INVENT CONTRACTS* (also applies to the frontend).

### 3.1 Decision pipeline (data flow)

```
PredictionArtifact (L3 §11.2) ─┐
L4 streams (policy/GDP/rates,  │  PipelineInputs
  VIX, quality/freshness/drift)└──────────▶ DecisionPipeline.build()
                                                  │
    1. Signals         raw quant/macro/rag ──▶ SignalComponents (bounds-checked)
    2. Regime + fusion determine_regime() ──▶ FusionEngine.fuse() ──▶ Direction
    3. Confidence      ConfidenceCalculator (interval width + signals + reliability)
    4. Costs           CostCalculator (VIX via FeatureStore ONLY — patch P2)
    5. Economic filter EconomicFilter.apply() ──▶ net_return, edge_ratio, actionable
    6. Quality         DecisionQualityEngine (consumes L3?no—L4 registries, patch P5)
    7. Hard gates      HardGateEngine.evaluate() ──▶ GateResult.signal_validity
    8. Sizing          PositionSizingEngine (capacity = secondary, patch P7)
                                                  │
                                                  ▼
                             Decision { action + rejection_reason + signal_validity }
                                                  │
          DecisionRegistry (no L1 delivery fields, P8) · OpportunityScorer (ranking)
          · SafeModeRegistry (for L1) · validation: contract audit (P9) + D/D2 PIT (P10)
```

### 3.2 Package responsibilities

| Package | Responsibility | Key exports |
| --- | --- | --- |
| `decision/contracts/` | Frozen domain contract types + L3/L4 provider interfaces (consumed, never implemented) | `Decision`, `PredictionArtifact`, `SignalComponents`, `FusionEngine`, `ConfidenceCalculator`, `regime` helpers, `FeatureStore`/`DataQualityRegistry`/`FreshnessRegistry`/`DriftRegistry` |
| `decision/filter/` | §7.1 economic filter (net return / edge / minimum edge) + §7.2 dynamic costs | `EconomicFilter`, `CostCalculator`, `CostBreakdown`, `PairCategory`, `VixUnavailableError` |
| `decision/gates/` | Precedence-ordered hard gates (quality, PIT, economic, exposure, correlation, regime alignment) | `HardGateEngine`, `GateResult`, `GateState`, `GATE_PRECEDENCE` |
| `decision/quality/` | Decision quality from L4 registries (data quality / freshness / drift) | `DecisionQualityEngine`, `DecisionQuality`, `QualityLevel` |
| `decision/sizing/` | Position size from edge × quality × VIX-volatility | `PositionSizingEngine`, `PositionSizeResult` |
| `decision/registries/` | Persistence + derived outputs: decisions (P8), opportunities/ranking (§10), safe mode | `DecisionRegistry`, `OpportunityScorer`, `RankedOpportunity`, `SafeModeRegistry` |
| `decision/validation/` | Contract-fidelity audit + end-to-end L1 mapping + PIT synthetic datasets | `validate_contracts`, `validate_integration` |
| `decision/pipeline.py` | Composition root — orchestrates the 8 stages, defines **no** new contracts | `DecisionPipeline`, `PipelineInputs`, `DecisionPipelineResult` |

### 3.3 Key invariants (patches)

- **P1** `Decision.prediction_id` references a complete `PredictionArtifact`.
- **P2** VIX **only** via `FeatureStore.get_feature('vix', T)` — no fallback path.
- **P3** `GateResult.signal_validity` is assigned **directly** to `Decision.signal_validity`.
- **P5** Layer 4 registries are consumed (interfaces), never implemented by Layer 2.
- **P7** Capacity/position-sizing is secondary; it never mutates `GateResult`.
- **P8** Layer 1 delivery fields are never stored by `DecisionRegistry`.
- **P9 / P10** Contract mapping and Synthetic Dataset D/D2 PIT acceptance are validated end-to-end.

---

## 4. Frontend — contract-driven dashboard (React + TypeScript)

**Stack:** React 18, TypeScript, Vite, Tailwind, TanStack Query, React Router, date-fns.

**Contract root:** `frontend/src/types/contracts.ts` mirrors **Layer 1 v5.1 §7** (every field is JSDoc-annotated to its spec line). Gap types in `frontend/src/types/gaps.ts` mirror `docs/Contract/CONTRACT_GAPS.md`.

### 4.1 Layered data flow

```
contracts.ts / gaps.ts / infrastructure.ts        ← frozen type contracts
        │
        ▼
services/  (transport-only: apiClient + endpoints/adapters)
   getForecast · getDrivers · getRanking · getPerformance · getStatus
        │
        ▼
hooks/  (data-fetching + UI/navigation state)
   useForecast · useDrivers · useRanking · usePerformance · useStatus
   usePolling · useActivePair(?pair=) · usePerformancePeriod(?period=)
        │
        ▼
components/*  PRESENTATIONAL — props-only, no hooks, no analysis
   common/ (Header, StatusBadge, RegimeBar, UniverseSelector, TabNav, Panel,
            LoadingSpinner, ApiError, NotAvailable, ErrorBoundary, ThemeProvider)
   global/ (RankingCard, EarlyWarnings)
   forecast/ (ForecastHero, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity)
   drivers/ (ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel)
   evaluation/ (PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator)
   status/ (SystemStatus, InfrastructureStatus)
        ▲
        │ props
        │
pages/  COMPOSITION — hooks → presentational props; NO analysis
   GlobalPage("/") · ForecastPage("/forecast") · DriversPage("/drivers")
   EvaluationPage("/evaluation") · StatusPage("/status")
        │
        ▼
layout/  MainLayout (Sidebar + Header composition wrapper) ── Routes (App.tsx)
```

### 4.2 Layering rules (enforced)

| Rule | Where it lives |
| --- | --- |
| Presentational components receive data via props only (no `use*`) | `components/*` (verified by grep) |
| Pages may call hooks but must not compute/rank/derive | `pages/*` (verified: no `.sort/.reduce/Math.*`) |
| `utils/` re-formats but never infers/calculates business values | `utils/format.ts`, `utils/status.ts` |
| Transport never transforms payloads | `services/api.ts` |
| Unsupported contract elements render `NotAvailable` (no substitution) | `NotAvailable.tsx` + `types/gaps.ts` |
| `position_size` ≠ `position_size_recommendation`; `isActionable()` is forbidden; consume `decision.actionable` / `RankingResponse.opportunities[].actionable` | governance + gap registry |

### 4.3 Composition surface

- **Pair selection** is URL-shared (`?pair=USD%2FJPY`, default `USD/JPY`) via `useActivePair`; universe comes from `RankingResponse.opportunities[].pair` with a documented MVP 4-pair fallback.
- **Evaluation period** is URL-shared (`?period=`, default `6M`) via `usePerformancePeriod`, validated against the `PerformancePeriod` enum.
- **Status header** is a thin composition wrapper (`layout/Header`) that delegates visuals to `components/common/Header`.

### 4.4 Frontend ↔ backend endpoints

| Page | Hook | Endpoint (Layer 1 §3) |
| --- | --- | --- |
| Global | `useRanking` | `GET /v1/fx/ranking` |
| Forecast | `useForecast(pair)` | `GET /v1/fx/{pair}/forecast` |
| Forecast | `useStatus` | `GET /v1/status` (decision validity) |
| Drivers | `useDrivers(pair)` | `GET /v1/fx/{pair}/drivers` |
| Evaluation | `usePerformance(pair, period)` | `GET /v1/fx/performance/{pair}?period=` |
| Status | `useStatus` | `GET /v1/status` |

---

## 5. Documentation & governance layer

The docs are the **authority**; code is verified against them.

```
docs/
├── Domain/                  Why (pitch), economics, data acquisition, production strategy
├── High-Level Design/       Executive summary · product spec/mockup · build strategy ·
│                            implementation roadmap · glossary · MLOps
├── Low-Level Design/        Implementation plan + Layer_01..04 specs
├── Product_specification/   FROZEN Layer_01..04 — contract authority (backend + delivery schema)
├── Prompts/                 The prompt sequence: layer prompts (L1–L4) + prompt_-1/0/X audit & build
└── Contract/                Governance artifacts (below)
```

### Contract governance (docs/Contract/)

| Artifact | Role |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row element→contract matrix (61 verified / 12 gap), with honest tallies |
| `CONTRACT_GAPS.md` (v2.0) | 16 joint gaps: G1–G9 + audit gaps (EC-1..4 economic-filter costs, RA Risk Appetite, CA calibration series, DF-P cumulative series) |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | Freeze status: **FREEZE WITH OPTIONAL GAPS**, 0 blocking |
| `CONTRACT_VALIDATION.md` | Prompt 1 audit (7/7 contracts, PASS, findings F1–F3) |
| `MIGRATION_REPORT.md` | 66 mockup visual elements classified (SUPPORTED / UNSUPPORTED / AMBIGUOUS), 100% enumerated |
| `COMPONENT_MAPPING.md` | Data-bearing field → component → file (100%), + page-wiring table |

**Governance workflow (established):** change request → update `CONTRACT_TRACEABILITY` → update `CONTRACT_GAPS` → re-freeze → re-validate. Frontend constraints: *NO_FALLBACK_ALLOWED*, *NO_DERIVATION_ALLOWED*; unsupported data renders `NotAvailable`.

---

## 6. Runtime & deployment (target)

Per `docs/Domain/04_app_production_strategy.md` and the mockup:

- **Render** (512 MB): FastAPI + Uvicorn (1 worker) — XGBoost loaded demand-driven.
- **Neon (PostgreSQL)**: external database — features, precomputed predictions, SHAP explanations, performance metrics.
- **Inference-only** (no training in prod); precomputed SHAP/predictions; ≤3 DB connections; memory target ~250–300 MB.

The repo currently implements the **decision engine** and **dashboard**; the FastAPI delivery layer, Docker/external services, and deployment configs are not yet present.

---

## 7. Verification matrix

| Layer | Command | Status |
| --- | --- | --- |
| Backend (Layer 2) | `python -m pytest` | **99 passed** (11 files) |
| Frontend typecheck | `cd frontend && npm run typecheck` | clean |
| Frontend tests | `cd frontend && npm run test` | **55 passed** (7 files) |
| Frontend build | `cd frontend && npm run build` | OK (bundle ~310 kB/98 kB gzip) |
| Contract governance | grep-verified: no hooks/analysis in presentational layer; pages free of derivation | OK |