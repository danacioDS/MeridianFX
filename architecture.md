# Meridian FX — Architecture

**Date:** 2026-08-30

System architecture for the Meridian FX repo: a contract-driven FX intelligence product with a FastAPI delivery API (Layer 1), a live ML/decision engine (Layer 2), a contract-verified decision engine (`src`), and a React dashboard with a FRED macro panel and SignalIQ-style Global Intelligence — all pinned to a frozen documentation suite.

---

## 1. System context

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCT (MVP — 4 core pairs, 9-pair ranking)            │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY   (single horizon 5D)                  │
│                                                                                   │
│   ┌────────────────┐  delivery contracts (Layer 1 §7)   ┌──────────────────────┐  │
│   │   LAYER 1      │ ──────────────────────────────────▶ │  FRONTEND            │  │
│   │ DELIVERY API   │  /v1/fx/{pair}/forecast|drivers     │  Dashboard            │  │
│   │  (FastAPI)     │  /v1/fx/ranking · historical        │  (React + TS)         │  │
│   │  layer1/       │  /v1/fx/interpretation · macro      │  incl. Macro (FRED)   │  │
│   └───────┬────────┘  /v1/fx/performance/{pair} · /v1/status   SignalIQ Global   │  │
│           │  /v1/fx/{pair}/price · /v1/fx/{pair}/forecast-dashboard │ PriceChart │
│           │  imports / uses layer2 engine + src decision                           │
│   ┌───────▼──────────────┐         ┌────────────────────┐      ┌───────────────┐  │
│   │ LAYER 2  LIVE ENGINE │         │  LAYER 3           │      │  LAYER 4      │  │
│   │ layer2/: XGBoost ·    │ ◀───── │ MODEL / SHAP /     │      │ DATA QUALITY  │  │
│   │ SHAP · data providers │ artifact│ RAG / narrative    │      │ FRESHNESS /   │  │
│   │ Yahoo→Alpha→Twelve ·  │ + L4   │ (external)         │      │ DRIFT (ext.)  │  │
│   │ FRED macro · ranking  │ streams│                    │      │               │  │
│   └──────────┬────────────┘        └────────────────────┘      └───────────────┘  │
│              │  + src/meridian_fx/decision/ (contract-governed engine, 99 tests)   │
│                                                                                   │
│   Deployment target: Render (FastAPI + Uvicorn) + Neon (PostgreSQL) — docs/        │
└───────────────────────────────────────────────────────────────────────────────────┘
```

> **Two Python engines coexist:** `layer2/` is the *live* engine the API actually runs (data sources, XGBoost, SHAP, ranking, macro). `src/meridian_fx/decision/` is the *contract-governed* decision pipeline (verified with 99 tests) frozen to the Layer 2 spec. They are currently **not wired to each other**; Layer 1 consumes `layer2/` directly.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specifications, prompts, contract governance
├── layer1/                   FastAPI delivery API (routers, models, adapters, LLM, decision)
├── layer2/                   Live engine (data, features, models, explainers, macro, ranking, engine)
├── src/meridian_fx/decision/ Contract-governed Decision Engine (8-stage pipeline, 99 tests)
├── tests/                    Backend pytest suite (11 files)
├── frontend/                 Contract-driven React+TS dashboard (Macro FRED + SignalIQ Global)
├── models/                   Trained XGBoost/logistic .pkl + models/registry.json
├── cache/                    Runtime forecast + macro caches
├── train_models.py           XGBoost training script
├── requirements.txt          Backend dependency manifest (populated)
├── pyproject.toml            Backend project metadata (pythonpath=src, pytest)
├── vite.config.ts            Frontend Vite config
├── README.md                 Product overview + quickstart
├── report.md                 Repository analysis (2026-08-30)
└── architecture.md           This document
```

---

## 3. Backend — Layer 1 FastAPI delivery API (`layer1/`)

**Entry:** `layer1/main.py` — `FastAPI(title="Meridian FX API", version="1.0.0")`, CORS limited to `localhost:5174` / `127.0.0.1:5174`. Includes **9 routers** plus `/` and `/health`.

### 3.1 Routers

| Router | Endpoints | Data source |
| --- | --- | --- |
| `ranking` | `GET /v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) |
| `drivers` | `GET /v1/fx/{pair}/drivers` | `layer2.DecisionEngine` + `SHAPExplainer` (macro/RAG placeholder) |
| `forecast` | `GET /v1/fx/{base}/{quote}/forecast` | hardcoded `FORECAST_DATA` + random fallback |
| `forecast_dashboard` | `GET /v1/fx/{pair}/forecast-dashboard` | **live** — `DataProvider` + trends/volatility + `DecisionEngine` XGBoost 30/60/90d + `MacroService` (FRED) |
| `price` | `GET /v1/fx/{pair}/price?period=` | **live** — spot + 100-pt history + XGBoost signal |
| `performance` | `GET /v1/fx/performance/{pair}?period=` | mock data |
| `historical` | `GET /v1/fx/{pair}/historical?period=` | `layer2.DataProvider` + `TechnicalFeatures` (+ stochastic fallback) |
| `status` | `GET /v1/status` | hardcoded HEALTHY |
| `interpretation` | `GET /v1/fx/interpretation?pair=` · `GET /v1/fx/macro/status` · `POST /v1/fx/macro/refresh` | Layer 1 `DecisionContext` + `EconomicInterpreter` + `layer2.MacroService` (FRED) |

> `price` and `forecast_dashboard` (both introduced around `v2.3.0`) are the first forecast/quote routes backed by real market + ML data; the legacy `/forecast` remains hardcoded.

### 3.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter` (dict → response models; currently used by `performance` only).
- **`decision/`** — `decision_context.py` (`DecisionContext`, `MacroContext`, `DecisionEngine.build_context`), `economic_filter.py` (cost-aware), `signal_validity.py` (thesis/invalidation).
- **`llm/`** — `base.py` (ABC), `providers.py` (Groq live; GLM/Gemini stubs; rule-based `FallbackLLM`), `manager.py` (fallback chain), `interpreter.py` (bilingual economic bullets; currently always uses rule-based fallback).

---

## 4. Backend — Layer 2 live engine (`layer2/`)

### 4.1 Data flow

```
DataProvider (Yahoo → Alpha Vantage → Twelve Data)
        │  get_historical(pair)
        ▼
TechnicalFeatures.generate(df) ── 23 features ── get_feature_names() (shared contract)
        │  latest row
        ▼
XGBoostModel.predict (via ModelRegistry.get_active(pair,'xgboost'))
        │
        ├─▶ SHAPExplainer.explain ──▶ top-10 contributions
        └─▶ EconomicFilter.apply ──▶ edge_ratio / confidence / position_size
        ▼
DecisionEngine.get_forecast(pair)  ── tools on-disk cache (5-min TTL)
        │
        ├─▶ RankingEngine.get_ranking()  (score = 0.6·prob + 0.4·edge)
        └─▶ [layer1/price, layer1/forecast_dashboard]  (live quotes + 30/60/90d forecasts)
```

### 4.2 Module responsibilities

| Area | Files | Role |
| --- | --- | --- |
| `config.py` | — | Env config: keys, trading thresholds (`MIN_EDGE_RATIO`, `MIN_CONFIDENCE`, `MAX_POSITION_SIZE`), paths |
| `data/` | `provider.py`, `fetcher.py` | Multi-source FX data with failover priority Yahoo → Alpha → Twelve; freshness/fallback metadata |
| `data/sources/` | `yahoo.py`, `alpha_vantage.py`, `twelve.py`, `fred.py` | Per-source fetchers; FRED catalog of 14 macro series + simulated fallback |
| `data/macro/` | `service.py`, `cache.py`, `transformer.py` | `MacroService` (FRED orchestration), disk cache (24 h TTL), `MacroTransformer` (summaries/indicators/FX relevance) |
| `features/` | `technical.py` | 23 technical indicators + `create_target()` (derived/macro stubs empty) |
| `models/` | `xgboost_model.py`, `logistic_model.py`, `registry.py` | Model training/prediction + versioned `ModelRegistry` (`models/registry.json`) |
| `explainers/` | `shap_explainer.py` | SHAP `TreeExplainer`, log-odds→probability, top-10 contributions |
| `decision/` | `filter.py` | Simplified `EconomicFilter` (edge/confidence/signal-strength/position size) |
| `ranking/` | `engine.py` | `RankingEngine` over active-model pairs |
| `macro/` | `intelligence.py` (empty) | (macro intelligence stub) |
| `engine.py` | — | `DecisionEngine` orchestrator + persistent cache + heuristic fallback |

### 4.3 Models & registry

`models/registry.json` holds **10 models** (9 XGBoost + 1 logistic). Each entry: `model_id`, `pair`, `model_type`, `version`, `path`, `metrics`, `created_at`, `active`. `ModelRegistry.register()` auto-activates on a better AUC; `get_active(pair, type)` locates the active artifact. Training is done offline via `train_models.py`.

---

## 5. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Root: `src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1. Governance: *DO NOT INVENT CONTRACTS*.

```
PredictionArtifact (L3 §11.2) ─┐
L4 streams (policy/GDP/rates,  │  PipelineInputs
  VIX, quality/freshness/drift)└──────────▶ DecisionPipeline.build()
                                                    │
     1. Signals        raw quant/macro/rag ──▶ SignalComponents   [OOB → INVALID]
     2. Regime+fusion  determine_regime() ──▶ FusionEngine ──▶ Direction
     3. Confidence     ConfidenceCalculator (interval + signals + reliability)
     4. Costs          CostCalculator (VIX via FeatureStore ONLY — patch P2)
     5. Economic filter EconomicFilter.apply() ──▶ net_return, edge_ratio, actionable
     6. Quality        DecisionQualityEngine (L4 registries — patch P5/P6)
     7. Hard gates     HardGateEngine.evaluate() ──▶ GateResult.signal_validity (P3)
     8. Sizing         PositionSizingEngine (capacity secondary — patch P7)
                                                    │
                                                    ▼
                          Decision { action + rejection_reason + signal_validity }
                                                    │
    DecisionRegistry (no L1 fields, P8) · OpportunityRegistry (ranking §10)
    · SafeModeRegistry · validation: contract audit (P9) + D/D2 PIT (P10)
```

### Key invariants (patches)

- **P1** `Decision.prediction_id` references a complete `PredictionArtifact`.
- **P2** VIX **only** via `FeatureStore.get_feature('vix')` — no fallback.
- **P3** `GateResult.signal_validity` assigned directly to `Decision.signal_validity`.
- **P5/P6** L4 registries consumed (never implemented); quality status mapping.
- **P7** Capacity/sizing secondary; never mutates `GateResult`.
- **P8** DecisionRegistry never stores Layer 1 delivery fields.
- **P9/P10** Contract mapping + Synthetic Dataset D/D2 PIT acceptance validated end-to-end.

---

## 6. Frontend — contract-driven dashboard (`frontend/`)

**Stack:** React 18, TypeScript 5, Vite 5 (port 5174), Tailwind 3, TanStack Query 5, axios, date-fns, React Router 6, **Recharts** 2 (`v2.3.0`). **Contract root:** `types/contracts.ts` mirrors Layer 1 v5.1 §7.

### 6.1 Layered data flow

```
types/ (contracts · gaps · infrastructure)          ← frozen type contracts
        ▼
services/  (transport-only axios adapters: getForecast/getDrivers/getRanking/getPerformance/getStatus)
        +  direct-fetch hooks (usePrice/useForecastDashboard/useRanking/useInterpretation/useMacro/…)
        ▼
hooks/  (useActivePair?pair= · usePerformancePeriod?period= · usePolling · useHistorical)
        ▼
components/*  PRESENTATIONAL — props-only
        ▲ props
        ▼
pages/  COMPOSITION — hooks → presentational props
        ▼
layout/MainLayout (Header/Footer) ── Routes (App.tsx)
```

### 6.2 Routes

| Path | Page | Data hooks |
| --- | --- | --- |
| `/` | GlobalPage (SignalIQ) | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/about` | AboutPage | (narrative accumulation) |

> `/historical` is no longer routed (orphaned `HistoricalPage.tsx`). GlobalPage and ForecastPage both consume the **live** `/v1/fx/{pair}/forecast-dashboard` endpoint via `useForecastDashboard` (polling 30 s, stale 15 s). The old contract-driven `useForecast`/`useInterpretation` data hooks are superseded on those pages.

### 6.3 SignalIQ Global Intelligence + Forecast Dashboard (v2.3.0)

- `components/global/PriceChartSignalIQ.tsx` + `PriceChartWithHover.tsx` — area chart with gradient, hover tooltip, 30d/90d/6m/1y range selector.
- `components/forecast/ForecastCard.tsx`, `SpotCard.tsx`, `TrendCard.tsx` — 30/60/90-day forecast cards, live spot, multi-horizon trend returns.
- `hooks/useForecastDashboard.ts` — direct-fetch of `/v1/fx/{pair}/forecast-dashboard`.
- Global `price`/`forecast-dashboard` router data flows into GlobalPage, ForecastPage, and PricePage.

### 6.4 Macro dashboard (FRED) — FASE 5.4

`components/macro/MacroPanel.tsx` + `hooks/useMacro.ts` (tag `v2.3.0-macro-panel`): renders an 8-indicator macro grid (Fed Funds, CPI, unemployment, GDP, 10Y/2Y, 10-2 spread, confidence), policy/growth/inflation badges, FX relevance; consumes `GET /v1/fx/interpretation?pair=USD/JPY&include_macro=true` and `GET /v1/fx/macro/status`. Wired into `ForecastPage` (5-min refetch, 4-min staleTime).

### 6.5 Presentational components (~34)

- `common/` — Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, Header
- `global/` — RankingTable, RankingCard, EarlyWarnings, PriceChartSignalIQ, PriceChartWithHover
- `forecast/` — ForecastHero, ForecastCard, SpotCard, TrendCard, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity (+ unexported mockup WhyNow/DataTimestamps)
- `drivers/` — ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel
- `evaluation/` — PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator
- `status/` — SystemStatus, InfrastructureStatus
- `layout/` — Header (includes Price nav), Footer, MainLayout
- `macro/` — MacroPanel
- `mockup/` — Gauge, PipelineStepper, RegimeStrip, SHAPBar

### 6.6 Layering rules

| Rule | Location |
| --- | --- |
| Presentational components receive props only (no `use*`) | `components/*` |
| Pages call hooks but don't compute/rank/derive | `pages/*` |
| `utils/` re-formats but never infers/calculates | `format.ts`, `status.ts`, `gaps.ts` |
| Transport never transforms payloads | `services/api.ts` |
| Unsupported contract elements render `NotAvailable` | `types/gaps.ts` + `NotAvailable.tsx` |
| No derivation: `isActionable()` forbidden; consume `decision.actionable` | governance + gap registry |

> **Note:** several newer pages (Global/Forecast) and `RankingTable` do locally derive/assume values (e.g. `direction === 'UP'`, computed returns, **hardcoded `vix={16.8}`/`regime="UNKNOWN"`/`riskAppetite={0.72}`** in `RegimeStrip`) that drift from the strict contract — a documented tension between the visual generation and the contract-driven discipline. The FRED macro data is real; the `RegimeStrip` is mock.

---

## 7. Documentation & governance layer

The docs are the **authority**; code is verified against them.

```
docs/
├── Domain/                  Why (pitch), economics, data acquisition, production strategy
├── High-Level Design/       Executive summary · product spec/mockup · build strategy · roadmap · glossary · MLOps
├── Low-Level Design/        Implementation plan + Layer_01..04 specs
├── Product_specification/   FROZEN Layer_01 (v5.1) · Layer_02 (v3.4.1) · Layer_03 (v5.0) · Layer_04 (v3.1.1)
├── Prompts/                 Prompt sequence: layer prompts + prompt_-1/0/X audit & build
└── Contract/                Governance artifacts (traceability, gaps, freeze, validation, migration, mapping)
```

### Contract governance (`docs/Contract/`)

| Artifact | Role |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row element→contract matrix (61 verified / 12 gap) |
| `CONTRACT_GAPS.md` (v2.0) | 16 unified gaps: G1–G9 + EC-1..4, RA, CA, DF-P |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | FREEZE WITH OPTIONAL GAPS, 0 blocking |
| `CONTRACT_VALIDATION.md` | Prompt 1 audit (7/7 contracts, PASS) |
| `MIGRATION_REPORT.md` | 66 mockup visual elements classified (100%) |
| `COMPONENT_MAPPING.md` | Data-bearing field → component → file (100%) |

**Governance workflow:** change request → update `CONTRACT_TRACEABILITY` → update `CONTRACT_GAPS` → re-freeze → re-validate. Frontend constraints: *NO_FALLBACK_ALLOWED*, *NO_DERIVATION_ALLOWED*.

---

## 8. Runtime & deployment (target)

Per `docs/Domain/04_app_production_strategy.md`:

- **Render** (512 MB): FastAPI + Uvicorn (1 worker), inference-only — XGBoost loaded demand-driven.
- **Neon (PostgreSQL)**: external DB for features, precomputed predictions, SHAP explanations, performance metrics.
- Memory target ~250–300 MB; ≤3 DB connections; no training in prod.

The repo implements the delivery API, live engine, decision engine, and dashboard; Docker/external services/deployment configs are not yet present.

---

## 9. Verification matrix

| Layer | Command | Status (2026-08-30) |
| --- | --- | --- |
| Backend `src` decision engine | `python -m pytest` | **99 passed** (11 files) ✅ |
| Layer 1 / Layer 2 imports | `python -c "import layer1.main"` | pass ✅ |
| Frontend typecheck | `cd frontend && npm run typecheck` | **clean** ✅ |
| Frontend tests | `cd frontend && npm test` | **55 passed** ✅ |
| Frontend build | `cd frontend && npm run build` | **OK** ✅ (bundle > 500 kB warning) |

The previous (2026-08-29) frontend failures are resolved: `SystemStatus` renders the string-enum health values verbatim (no `.status` access), `DEFAULT_STATUS_COLOR` is exported, and `getSignalStrengthLabel` accepts `number | string`.

---

## 10. Known gaps & risks

1. **Live endpoints hardcoded/mock/simulated** — `/forecast` (hardcoded `FORECAST_DATA`), `/performance` (mock), `/status` (hardcoded), drivers macro/RAG (placeholders), and FRED (no `FRED_API_KEY` → **simulated** data). Real-data routes: `ranking`, `historical`, `drivers` (SHAP), and the new `price`/`forecast-dashboard`.
2. **`src` decision engine not wired to `layer2`/`layer1`** — the contract-governed pipeline (99 tests) and the live engine coexist unconnected.
3. **Dual `DecisionEngine` naming** (Layer 1 `decision_context` vs Layer 2 `engine`) — confusing.
4. **`EconomicInterpreter` bypasses the LLM chain** (always rule-based).
5. **Contract-shape drift** in newer frontend pages (Global/Forecast) vs `contracts.ts` — hardcoded `VIX`/`riskAppetite`/`regime`, `direction === 'UP'` derivations, locally computed returns.
6. **Env-key mismatch** (`VITE_API_BASE_URL` vs `VITE_API_URL`).
7. **Dead/stale artifacts** (`*.bak` ×5, orphaned `HistoricalPage.tsx`, unused mockup/forecast components, empty `data/historical/`).
8. **Git hygiene** — stray root file from a copy-pasted commit message; modified `cache/forecast_cache.json`.
9. **Frontend bundle size** — main chunk 722 kB minified (build warning; consider code-splitting).
10. **Single-horizon / partial multi-pair MVP** — multi-horizon, RAG/NLP, MLflow deferred to V2/V3 (though 30/60/90d forecasts now exist via `forecast-dashboard`).