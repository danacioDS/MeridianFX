# Meridian FX — Architecture

**Date:** 2026-09-04

System architecture for the Meridian FX repo: a contract-driven FX intelligence product with a FastAPI delivery API (Layer 1), a live ML/decision engine (Layer 2), research (Layer 3) and data-quality (Layer 4) codebases, a contract-verified decision engine (`src`), and a React dashboard — deployed in production (Render backend, Cloudflare Pages + Vercel frontend) and pinned to a frozen documentation suite.

---

## 1. System context

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                              PRODUCT (MVP — 4 core pairs, 9-pair ranking)                    │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY   (single horizon 5D; +30/60/90d forecasts)        │
│                                                                                              │
│   ┌────────────────┐  delivery contracts (Layer 1 §7)   ┌───────────────────────┐            │
│   │   LAYER 1      │ ──────────────────────────────────▶ │  FRONTEND (React+TS) │            │
│   │ DELIVERY API   │  /v1/fx/{pair}/forecast|drivers     │  Global · Price ·     │            │
│   │  (FastAPI)     │  /v1/fx/ranking · historical        │  Forecast · Drivers · │            │
│   │  backend/layer1 │ /v1/fx/interpretation · performance │  Evaluation · Status ·│            │
│   └───────┬────────┘  /v1/status · price · forecast-dashboard · model-comparison │ Models      │
│           │  uses layer2 engine (+ layer3 via model-comparison, + src decision)  │             │
│   ┌───────▼──────────────────┐         ┌────────────────────────┐ ┌───────────────┐          │
│   │ LAYER 2  LIVE ENGINE     │         │ LAYER 3  RESEARCH (NEW)│ │ LAYER 4 DATA  │          │
│   │ backend/layer2:          │◀───────▶│ backend/layer3:        │ │  QUALITY (NEW)│          │
│   │ XGBoost (per-pair dict)  │         │ eval/walk_forward ·    │ │ backend/layer4│          │
│   │ SHAP · Yahoo→Alpha→Twelve│ + docs  │ benchmarks · arima/    │ │ PITValidator  │          │
│   │ FRED macro · ranking ·   │         │ elastic_net/ensemble · │ │ (PIT-1..7) ·  │          │
│   │ StatusEngine (real /status)        │ macro regime · rag ·   │ │ config ·      │          │
│   │                      SUB                research_gate       │ │ lineage       │          │
│   └──────────┬──────────────┘ (partial wiring, uneven maturity)  └──────┬────────┘          │
│              │  + src/meridian_fx/decision/ (contract-governed engine, 103 tests)            │
│              │                                                                                │
│   DEPLOY:  Render (Docker FastAPI+Uvicorn :10000, /health) · Cloudflare Pages + Vercel (SPA) │
│            FRED/GROQ/ALPHA/TWELVE keys injected via render.yaml; Neon DB deferred                           │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Key relationships:** Layer 1 consumes `layer2/` directly (now including the real `StatusEngine`). Layer 3 is wired into the API **only** via the `model_comparison` router (broken — see §4/§5). Layer 4 is wired into runtime **only** through tests (`test_pit_adversarial.py`); `layer2/quality/pit_adapter.py` delegates to `PITValidator` but is dead code. The contract-governed `src/meridian_fx/decision/` engine remains unconnected to the live API.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specifications, prompts, contract governance
├── backend/                  Python backend (moved from root during the deploy cycle)
│   ├── layer1/               FastAPI delivery API (10 routers, models, adapters, LLM, decision)
│   ├── layer2/               Live engine (data, features, models, explainers, macro, ranking, status, engine)
│   ├── layer3/               Research/evaluation layer (walk-forward, benchmarks, models, regime, RAG, gate)
│   ├── layer4/               Data-quality layer (PIT validator, config policies, lineage)
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, 103 tests)
│   ├── models/               Trained XGBoost/logistic .pkl + models/registry.json (10 models)
│   ├── tests/                Backend pytest suite (12 files)
│   ├── pyproject.toml        Backend project metadata (pythonpath=src, pytest)
│   ├── requirements.txt      Backend dependency manifest
│   └── docker-compose.yml    Local compose (port 10000, mounts models/ + cache/)
├── Dockerfile                Render container (python:3.12-slim, uvicorn layer1.main:app :10000)
├── render.yaml               Render blueprint (docker free web service, /health, env keys)
├── runtime.txt               Python 3.12.0 pin (repo root)
├── train_models.py           XGBoost training script (repo root)
├── backend/models/           Model artifacts (registry.json + .pkl)
├── cache/                    Runtime forecast + macro caches (CWD-relative in prod)
├── frontend/                 Contract-driven React+TS dashboard (Cloudflare Pages + Vercel)
│   ├── .env.production       VITE_API_URL=https://meridianfx.onrender.com
│   ├── vercel.json · _headers · _redirects · dist/
├── .env                      Runtime env (FRED/GROQ/ALPHA/TWELVE/OPENAI/CLOUDFLARE keys + config)
├── README.md                 Product overview + quickstart
├── report.md                 Repository analysis (2026-09-04)
└── architecture.md           This document
```

---

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

**Entry:** `backend/layer1/main.py` — `FastAPI(title="Meridian FX API", version="1.0.0")`, CORS extended to Render/Vercel/Cloudflare origins. Includes **10 routers** plus `/` and `/health`.

### 3.1 Routers

| Router | Endpoint | Data source | Status |
| --- | --- | --- | --- |
| `ranking` | `GET /v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) | ✅ network |
| `drivers` | `GET /v1/fx/{pair}/drivers` | `layer2.DecisionEngine` SHAP + macro/RAG | ❌ **500** — `engine.get_drivers()` removed |
| `forecast` | `GET /v1/fx/{base}/{quote}/forecast` | hardcoded `FORECAST_DATA` (`layer1/data/forecast_data.py`) + random fallback | ⚠️ hardcoded |
| `forecast_dashboard` | `GET /v1/fx/{pair}/forecast-dashboard` | **live** — provider + trends/volatility + XGBoost 30/60/90d (`_get_model_for_pair`) + FRED macro | ✅ network |
| `price` | `GET /v1/fx/{pair}/price?period=` | **live** spot/history; ML block guarded by removed `engine.xgb_model` → always skipped | ⚠️ degraded (direction always UNKNOWN) |
| `performance` | `GET /v1/fx/performance/{pair}?period=` | **real** — `models/registry.json` metrics + `DecisionAdapter` (was mock) | ✅ |
| `historical` | `GET /v1/fx/{pair}/historical?period=` | `layer2.DataProvider` + `TechnicalFeatures` (+ stochastic fallback) | ✅ network |
| `status` | `GET /v1/status` | **real** — `layer2.status.engine.StatusEngine` (was hardcoded) | ✅ |
| `interpretation` | `GET /v1/fx/interpretation?pair=&include_macro=` | `EconomicInterpreter` + `FORECAST_DATA`; macro via missing `layer1.services.macro_service` | ⚠️ partial |
| `model_comparison` | `GET /v1/fx/{pair:path}/model-comparison` | **NEW** — Layer 3 `WalkForwardEvaluator.evaluate_expanding` + `EnsembleModel` | ❌ **500** — reads removed `engine.xgb_model`/`logistic_model` |

> **Removed in this cycle:** `/v1/fx/macro/status` and `/v1/fx/macro/refresh` (interpretation router now exposes only `/interpretation`; frontend `useMacro` updated). `FORECAST_DATA` consolidated into `layer1/data/forecast_data.py`.

### 3.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7 (exercised by `status`, `ranking`, `performance`).
- **`adapters/decision_to_response.py`** — `DecisionAdapter` (dict → response models).
- **`decision/`** — `decision_context.py` (`DecisionContext`, `MacroContext`, `build_context`), `economic_filter.py` (cost-aware), `signal_validity.py`.
- **`llm/`** — `base.py` (ABC), `providers.py` (Groq live; GLM/Gemini stubs; rule-based `FallbackLLM`), `manager.py` (fallback chain), `interpreter.py` (bilingual bullets; resolves via rule-based fallback).
- **`data/forecast_data.py`** — consolidated hardcoded `FORECAST_DATA` (9 pairs).

> **Regression driver:** `layer2.engine.DecisionEngine` moved to per-pair dynamic models (`xgb_models`/`logistic_models` dicts + `_get_model_for_pair()`) and dropped `xgb_model`/`logistic_model`/`get_drivers()`. `drivers.py`, `model_comparison.py`, `price.py`, and `layer3/evaluation/run_benchmarks.py` still target the old API.

---

## 4. Layer 2 — live engine (`backend/layer2/`)

### 4.1 Data flow

```
DataProvider (Yahoo → Alpha Vantage → Twelve Data)
        │  get_historical(pair)
        ▼
TechnicalFeatures.generate(df) ── 23 features ── get_feature_names() (shared contract)
        │  latest row
        ▼
XGBoostModel.predict (via DecisionEngine._get_model_for_pair(pair,'xgboost'))
        │
        ├─▶ SHAPExplainer.explain ──▶ top-10 contributions
        └─▶ EconomicFilter.apply ──▶ edge_ratio / confidence / position_size
        ▼
DecisionEngine.get_forecast(pair)  ── on-disk cache (5-min TTL) + heuristic fallback
        │
        ├─▶ RankingEngine.get_ranking()  (score = 0.6·prob + 0.4·edge)
        ├─▶ StatusEngine.get_full_status()  (registry + live data-source probes + LLM/API-key checks)
        └─▶ [layer1 price · forecast-dashboard · drivers · model-comparison]
```

### 4.2 Module responsibilities

| Area | Files | Role |
| --- | --- | --- |
| `config.py` | — | Env config: keys, trading thresholds, paths |
| `data/` | `provider.py`, `fetcher.py` | Multi-source FX data with failover Yahoo → Alpha → Twelve |
| `data/sources/` | `yahoo.py`, `alpha_vantage.py`, `twelve.py`, `fred.py` | Per-source fetchers; FRED catalog + simulated fallback |
| `data/macro/` | `service.py`, `cache.py`, `transformer.py` | `MacroService`, disk cache (24 h TTL), `MacroTransformer` |
| `status/` | `engine.py` (NEW) | `StatusEngine` — model states, live source probes, LLM availability, cache/memory, HEALTHY/DEGRADED |
| `features/` | `technical.py` | 23 technical indicators + `create_target()` |
| `models/` | `xgboost_model.py`, `logistic_model.py`, `registry.py` | Training/prediction + versioned `ModelRegistry`; **NEW (unwired):** `model_selector.py`, `registry_adapter.py`; `trainer.py` (empty) |
| `explainers/` | `shap_explainer.py` | SHAP `TreeExplainer`, log-odds→probability, top-10 |
| `decision/` | `filter.py` | Simplified `EconomicFilter` |
| `ranking/` | `engine.py` | `RankingEngine` over active-model pairs |
| `quality/` | `pit_adapter.py` (NEW) | Adapter over `layer4.quality.pit_validator.PITValidator` — **dead code** |
| `engine.py` | — | `DecisionEngine` — per-pair model dicts, cache, heuristic fallback |

### 4.3 Models & registry

`backend/models/registry.json` holds **10 models** (9 XGBoost + 1 logistic), all `active: true`, all `v1.0`. AUCs 0.38–0.73 (best USD/CHF 0.733; worst USD/CNY 0.380; USD/JPY < 0.45). `ModelRegistry.register()` auto-activates on better AUC; `get_active(pair, type)` locates artifacts. Training offline via root `train_models.py`.

---

## 5. Layer 3 — research layer (`backend/layer3/`, NEW)

Standalone research/evaluation package. **Only coupling to the API:** `layer1/routers/model_comparison.py` (currently broken). Nothing in `layer2` imports it.

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | `ModelArtifact`, `PredictionArtifact`, `ModelRegistry` | Persistence of research-approved models | ✅ implemented — schema **incompatible** with layer-2 `registry.json` |
| `evaluation/` | `walk_forward.py`, `benchmarks.py`, `run_benchmarks.py`, `model_evaluator.py`, `decision_policy.py` | Backtests, reference strategies, OOS split, policy search | ⚠️ `walk_forward.evaluate()` NameError; `run_benchmarks.py` crashes; `model_evaluator` random fallback |
| `experiments/` | `run.py`, `real_experiments.py` | E0–E7 experiment suite | ❌ `run.py` hardcoded stubs; `real_experiments.py` broken via `evaluate()` |
| `macro/regime.py` | `MacroRegimeEngine` | Risk/Policy/Growth/Inflation → regime classification | ✅ works |
| `models/` | `arima.py`, `elastic_net.py`, `ensemble.py` | Control models (ARIMA, elastic-net, weighted ensemble) | ⚠️ ARIMA needs `statsmodels` (absent); elastic-net/ensemble work |
| `rag/agents.py` | `CentralBankRAGEngine` | Fed/BoJ sentiment + expectation gap | ⚠️ keyword scorer, not real RAG |
| `research_gate/` | `gate.py`, `real_gate.py`, `full_gate.py` | 4-gate model approval | ✅ gate.py works; `full_gate.py` broken (calls `evaluate()` + `features={}`); `real_gate.py` inherits evaluator caveats |

---

## 6. Layer 4 — data-quality layer (`backend/layer4/`, NEW)

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `quality/pit_validator.py` | `PITValidator` (PIT-1…PIT-7) | Point-in-Time compliance for feature snapshots | ✅ correct (verified vs datasets A–D) |
| `config/policies.py` | `SourcePolicy`, `FeatureConfig`, `TargetConfig`, `ConfigRegistry` | Versioned configuration | ✅ implemented, **unused** |
| `lineage/models.py` | LineageReference/Record/Registry | Provenance for audit/explainability | ✅ implemented, **unused** |
| `tests/pit_tests.py` | layer-4 unit tests | PITValidator tests | ❌ syntactically corrupted — won't parse |

**Wiring:** `PITValidator` is executed via `backend/tests/test_pit_adversarial.py` (part of the 103 passing suite). `layer2/quality/pit_adapter.py` delegates to it but is dead code; runtime forecast paths do not validate PIT.

---

## 7. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consumes Layer 3 §11.2 / Layer 4 §7 contracts. Governance: *DO NOT INVENT CONTRACTS*.

```
PredictionArtifact (L3 §11.2) ─┐
L4 streams (policy/GDP/rates,  │  PipelineInputs
  VIX, quality/freshness/drift)└──────────▶ DecisionPipeline.build()
                                                    │
     1. Signals        OOB → INVALID · 2. Regime+fusion → Direction
     3. Confidence · 4. Costs (VIX via FeatureStore P2) · 5. Economic filter
     6. Quality · 7. Hard gates (signal_validity P3) · 8. Sizing
                                                    ▼
                          Decision { action + rejection_reason + signal_validity }
     Registries (P8) · validation: contract audit (P9) + Synthetic D/D2 PIT (P10)
```

**Verification:** `python -m pytest` (from `backend/`) → **103 passed** across 12 files; +4 tests this cycle from `test_pit_adversarial.py` (drives the Layer 4 `PITValidator`).

---

## 8. Frontend — contract-driven dashboard (`frontend/`)

**Stack:** React 18, TS 5, Vite 5 (port 5174, minify off), Tailwind 3, TanStack Query 5, axios, date-fns, React Router 6, Recharts 2. **Contract root:** `types/contracts.ts` mirrors Layer 1 v5.1 §7. **Deploys:** Cloudflare Pages (root-index + `_redirects` SPA fallback) and Vercel (`vercel.json` rewrites); prod API in `.env.production`.

### 8.1 Routes (17 hooks)

| Path | Page | Data hooks |
| --- | --- | --- |
| `/` | GlobalPage (SignalIQ) | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/models` | ModelComparisonPage (NEW) | `useModelComparison` → `/v1/fx/{pair}/model-comparison` |
| `/about` | AboutPage | (narrative) |

New components this cycle: `global/ActionableInfo.tsx`, `global/ModelExplanation.tsx`, `forecast/FanChart.tsx` + `hooks/useFanChartData.ts` (**unmounted/dead**), `hooks/useModelComparison.ts`, `hooks/useMacroContext.ts`.

### 8.2 SignalIQ Global + Forecast + Model Comparison

- `global/PriceChartSignalIQ.tsx` + `PriceChartWithHover.tsx` — area chart, gradient, hover tooltip, 30d/90d/6m/1y ranges.
- `forecast/` ForecastCard/SpotCard/TrendCard — 30/60/90-day XGBoost forecasts, live spot, trend returns.
- `hooks/useForecastDashboard.ts` — direct-fetch of `/v1/fx/{pair}/forecast-dashboard`.
- `ModelComparisonPage` — walk-forward comparison of XGBoost / Logistic / Ensemble (Sharpe, PF, DA, AUC, NetReturn; `best_model` badge) from `GET /v1/fx/{pair}/model-comparison`.

### 8.3 Macro dashboard (FRED)

`components/macro/MacroPanel.tsx` + `hooks/useMacro.ts` — 8-indicator macro grid, policy/growth/inflation badges, FX relevance from `GET /v1/fx/interpretation?pair=…&include_macro=true` (the `/v1/fx/macro/status` + `/refresh` endpoints are gone). Wired into `ForecastPage`.

### 8.4 Presentational components

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, **Header** — duplicate of the live `layout/Header.tsx`), `global/*` (RankingTable, RankingCard, EarlyWarnings, PriceChartSignalIQ, PriceChartWithHover, ActionableInfo, ModelExplanation), `forecast/*` (ForecastHero, ForecastCard, SpotCard, TrendCard, FanChart, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity, WhyNow, DataTimestamps), `drivers/*` (ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel), `evaluation/*` (PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator), `status/*` (SystemStatus, InfrastructureStatus), `layout/*` (Header, Footer, MainLayout), `macro/*` (MacroPanel), `mockup/*` (Gauge, PipelineStepper, RegimeStrip, SHAPBar). `pages/HistoricalPage.tsx` remains orphaned.

### 8.5 Layering rules

| Rule | Location |
| --- | --- |
| Presentational components receive props only (no `use*`) | `components/*` |
| Pages call hooks but don't compute/rank/derive | `pages/*` |
| `utils/` re-formats but never infers/calculates | `format.ts`, `status.ts`, `gaps.ts`, `safeFormat.ts` |
| Transport never transforms payloads | `services/api.ts` |
| Unsupported contract elements render `NotAvailable` | `types/gaps.ts` + `NotAvailable.tsx` |
| No derivation: consume `decision.actionable` | governance + gap registry |

---

## 9. Deployment & runtime

| Target | Mechanism | Notes |
| --- | --- | --- |
| **Render** (backend) | Docker web service (`render.yaml`, plan free, `/health`) | python:3.12-slim, `PYTHONPATH=/app/backend`, `uvicorn layer1.main:app` :10000; env FRED/GROQ/ALPHA/TWELVE (`sync:false`). `runtime.txt` (3.12.0) at repo root. |
| **Cloudflare Pages** (frontend) | Static-site mode; `_headers` (noindex, ACAO `*`), `_redirects` (`/* → /index.html 200`); `.cloudflareignore` | `dist/` committed; polyfills removed for Pages build |
| **Vercel** (frontend) | `vercel.json` — Vite build → `dist`, SPA rewrites | `.vercel/` present |
| **Local** | `backend/docker-compose.yml` — port 10000, mounts `./models` + `./cache` | — |

**Ops caveats:**
- Backend reads `models/registry.json` and `cache/` CWD-relative; the Docker image sets `/app` as WORKDIR while those live under `/app/backend/` — path assumptions must be validated against the deployed image.
- FRED real data still requires `FRED_API_KEY` at runtime; without it the macro path serves simulated data.

---

## 10. Documentation & governance layer

The docs are the **authority**; code is verified against them.

```
docs/
├── Domain/                  Why, economics, data acquisition, production strategy
├── High-Level Design/       Executive summary · product spec/mockup · build strategy · roadmap · glossary · MLOps
├── Low-Level Design/        Implementation plan + Layer_01..04 specs
├── Product_specification/   FROZEN L1 v5.1 · L2 v3.4.1 · L3 v5.0 · L4 v3.1.1
├── Prompts/                 Layer prompts + prompt_-1/0/X audit & build
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

**Governance workflow:** change request → update `CONTRACT_TRACEABILITY` → update `CONTRACT_GAPS` → re-freeze → re-validate. Frontend constraints: *NO_FALLBACK_ALLOWED*, *NO_DERIVATION_ALLOWED*. The Layer 3/4 code and the Model Comparison surface introduced this cycle have **not** gone through this loop.

---

## 11. Verification matrix

| Layer | Command | Status (2026-09-04) |
| --- | --- | --- |
| Backend `src` decision engine (+ L4 PIT) | `cd backend && python -m pytest` | **103 passed** (12 files) ✅ |
| Layer 1 import | `python -c "import layer1.main"` | pass ✅ |
| Layer 1 endpoints | live smoke (Render `https://meridianfx.onrender.com/health`) | ✅ health; ❌ `/drivers`, `/model-comparison` 500; ⚠️ `/price` signal disabled |
| Frontend typecheck | `cd frontend && npm run typecheck` | **clean** ✅ |
| Frontend tests | `cd frontend && npm test` | **45 passed / 10 FAILED** ❌ (`format.test.ts`) |
| Frontend build | `cd frontend && npm run build` | **OK** ✅ (1,397 kB main bundle, minify off) |

---

## 12. Known gaps & risks

1. **`DecisionEngine` refactor broke live routes** — `/drivers` and `/model-comparison` return 500 (`get_drivers`/`xgb_model` removed); `/price` ML silently disabled; `run_benchmarks.py` crashes.
2. **Frontend test regression** — 10 failures in `format.test.ts` after the `format.ts` rewrite (contract vs implementation mismatch).
3. **Layer 3 uneven** — `walk_forward.evaluate()` NameError poisons `real_experiments.py` + `full_gate.py`; `run.py` experiments hardcoded; `arima.py` needs `statsmodels`; `run_benchmarks.py` broken; artifact registry schema incompatible with `backend/models/registry.json`.
4. **Layer 4 mostly unwired** — `PITValidator` runs only in tests; `pit_adapter.py`/`config`/`lineage` dead; `pit_tests.py` corrupted.
5. **Live endpoints still hardcoded/simulated** — `/forecast` & `/interpretation` use `FORECAST_DATA`; interpretation's macro import (`layer1.services.macro_service`) is missing; FRED simulated without key; drivers macro/RAG placeholders.
6. **`EconomicInterpreter` bypasses the LLM chain** (rule-based primary).
7. **`src` decision engine not wired to `layer2`/`layer1`** — 103 verified tests, zero runtime footprint.
8. **Contract-shape drift in frontend** — `direction === 'UP'` derivations, hardcoded VIX/riskAppetite/regime in `RegimeStrip`, locally computed returns.
9. **Dead/stale artifacts** — orphaned `HistoricalPage.tsx`; unused `FanChart`/`useFanChartData`/`WhyNow`/`DataTimestamps`/`ForecastHero`/`mockup/*`/duplicate `common/Header.tsx`; empty `trainer.py`; dead `layer2` adapters.
10. **Git hygiene** — `main` ahead of `origin/main` by 1 unpushed commit; stale **untracked `requirements.txt`** at repo root (name-collides with `backend/requirements.txt`).
11. **Env keys** — `VITE_API_BASE_URL` vs `VITE_API_URL` mismatch persists (works by defaults).
12. **Bundle size** — 1,397 kB main chunk; warning silenced by raising `chunkSizeWarningLimit` rather than splitting.