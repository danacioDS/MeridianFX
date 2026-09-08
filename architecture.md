# Meridian FX — Architecture

**Date:** 2026-09-05

System architecture for the Meridian FX repo: a contract-driven FX intelligence product with a FastAPI delivery API (Layer 1), a live ML/decision engine (Layer 2), research (Layer 3) and data-quality (Layer 4) codebases, a contract-verified decision engine (`src`), a script-driven Research Gate + experimental-model pipeline (repo root), and a React dashboard — deployed in production (Render backend, Cloudflare Pages + Vercel frontend) and pinned to a frozen documentation suite.

---

## 1. System context

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                              PRODUCT (MVP — 4 core pairs, 9-pair ranking)                    │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY   (single horizon 5D; +30/60/90d forecasts)        │
│                                                                                              │
│   ┌────────────────┐  delivery contracts (Layer 1 §7)   ┌───────────────────────┐            │
│   │   LAYER 1      │ ──────────────────────────────────▶ │  FRONTEND (React+TS) │            │
│   │ DELIVERY API   │  /v1/fx/{base}/{quote}/drivers     │  Global · Price ·     │            │
│   │  (FastAPI, 11  │  /v1/fx/{pair}/price|forecast|h... │  Forecast · Drivers · │            │
│   │   routers)     │  /v1/fx/ranking · performance      │  Evaluation · Status ·│            │
│   │  backend/layer1 │ /v1/market-intelligence (NEW)     │  Models               │            │
│   └───────┬────────┘  /v1/status · forecast-dashboard · model-comparison         │             │
│           │  uses layer2 engine (+ layer3 via model-comparison, + src decision)  │             │
│   ┌───────▼──────────────────┐         ┌────────────────────────┐ ┌───────────────┐          │
│   │ LAYER 2  LIVE ENGINE     │         │ LAYER 3  RESEARCH       │ │ LAYER 4 DATA  │          │
│   │ backend/layer2:          │◀───────▶│ backend/layer3:        │ │  QUALITY      │          │
│   │ XGBoost per-pair dict    │  + docs │ eval/walk_forward (fix) │ │ backend/layer4│          │
│   │ (_get_model_for_pair)    │         │ benchmarks · arima/    │ │ PITValidator  │          │
│   │ SHAP · Yahoo→Alpha→Twelve│         │ elastic_net/ensemble · │ │ (PIT-1..7) ·  │          │
│   │ FRED macro · ranking ·   │         │ macro regime · rag ·   │ │ config ·      │          │
│   │ StatusEngine (real /status)        │ research_gate          │ │ lineage       │          │
│   └──────────┬──────────────┘  (wired via model_comparison; run_benchmarks broken) │          │
│              │  + src/meridian_fx/decision/ (contract-governed engine, 103 tests)             │
│              │                                                                                │
│   RESEARCH (repo root, NEW): research_validation_test.py · final_holdout.py ·                 │
│   evaluate_all_pairs.py → research_gate.py (AUC/PR-AUC/Brier, v2) → models/experimental/      │
│   candidates EUR/USD h10 + USD/BOB h20 (logistic + sigmoid) — NOT wired into Layer 1/2        │
│                                                                                                │
│   DEPLOY:  Render (Docker FastAPI+Uvicorn :10000, /health) · Cloudflare Pages + Vercel (SPA) │
│            FRED/GROQ/ALPHA/TWELVE keys injected via render.yaml; Neon DB deferred              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Key relationships:** Layer 1 consumes `layer2/` directly, now including `_get_model_for_pair` for per-pair models and the real `StatusEngine`. Layer 3 is wired into the API **only** via the `model_comparison` router (now working); `run_benchmarks.py` remains broken. Layer 4 is wired into runtime **only** through tests (`test_pit_adversarial.py`). The contract-governed `src/meridian_fx/decision/` engine remains unconnected to the live API. The root-level Research Gate pipeline (**`research_gate.py` + `research_validation_test.py` + `train_experimental_models.py`)** produces `models/experimental/` candidates that the API never loads.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specifications, prompts, contract governance
├── backend/                  Python backend
│   ├── layer1/               FastAPI delivery API (11 routers incl. NEW intelligence, models, adapters, LLM, decision)
│   ├── layer2/               Live engine (data, features, models, explainers, macro, ranking, status, engine)
│   ├── layer3/               Research/evaluation layer (walk-forward FIXED, benchmarks, models, regime, RAG, gate)
│   ├── layer4/               Data-quality layer (PIT validator, config policies, lineage)
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, 103 tests)
│   ├── models/               Trained XGBoost/logistic .pkl + models/registry.json (10 models) + models/experimental/
│   ├── tests/                Backend pytest suite (12 files)
│   ├── pyproject.toml        Backend project metadata (pythonpath=src, pytest)
│   ├── requirements.txt      Backend dependency manifest
│   └── docker-compose.yml    Local compose (port 10000, mounts models/ + cache/)
├── Dockerfile                Render container (python:3.12-slim, uvicorn layer1.main:app :10000)
├── render.yaml               Render blueprint (docker free web service, /health, env keys)
├── runtime.txt               Python 3.12.0 pin (repo root)
├── train_models.py           XGBoost training script (production registry)
├── train_experimental_models.py  NEW — logistic + sigmoid candidates with purged protocol
├── evaluate_all_pairs.py · final_holdout.py · research_validation_test.py   NEW validation scripts
├── research_gate.py · research_gate_results{,v2}.json   NEW Research Gate + outputs
├── research_validation_results.json · research_validation_summary.csv · final_holdout_results.csv  NEW
├── models/                   Root-level artifacts (ONLY 6 of 9 XGBoost .pkl — see §4.2/§9)
├── cache/                    Runtime forecast + macro caches (CWD-relative in prod)
├── frontend/                 Contract-driven React+TS dashboard (Cloudflare Pages + Vercel)
│   ├── .env                  VITE_API_URL = VITE_API_BASE_URL = http://localhost:8000  (NO .env.production)
│   ├── vercel.json · _headers · _redirects
│   └── src/constants/fxPairs.ts  NEW fixed pair order + market convention (UI refactor)
├── .env                      Runtime env (FRED/GROQ/ALPHA/TWELVE/OPENAI/CLOUDFLARE keys + config)
├── ngrok-stable-linux-amd64.zip · commandos.md · start_backend.sh · VERSION*.txt · *.bak  (committed clutter)
├── README.md                 Product overview + quickstart
├── report.md                 Repository analysis (2026-09-05)
└── architecture.md           This document
```

---

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

**Entry:** `backend/layer1/main.py` — `FastAPI(title="Meridian FX API", version="1.0.0")`, CORS covering localhost/Render/Vercel/Cloudflare/**ngrok**/`*`. **11 routers** plus `/` and `/health`.

### 3.1 Routers

| Router | Endpoint | Data source | Status |
| --- | --- | --- | --- |
| `ranking` | `GET /v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) | ✅ network |
| `drivers` | `GET /v1/fx/{base}/{quote}/drivers` | SHAP + macro via `_get_model_for_pair` | ✅ / ⚠️ — **200 for 6 pairs; 404 for USD/JPY/EUR/USD/GBP/USD** (`.pkl` missing at repo-root `models/`) |
| `forecast` | `GET /v1/fx/{base}/{quote}/forecast` | hardcoded `FORECAST_DATA` (`layer1/data/forecast_data.py`) | ⚠️ hardcoded |
| `forecast_dashboard` | `GET /v1/fx/{pair}/forecast-dashboard` | **live** — provider + trends/volatility + XGBoost 30/60/90d (`_get_model_for_pair`) + FRED macro | ✅ network |
| `price` | `GET /v1/fx/{pair}/price?period=` | **live** spot/history; XGBoost via `_get_model_for_pair` (was always-skipped) | ✅ / ⚠️ signal only for pairs whose model resolves |
| `performance` | `GET /v1/fx/performance/{pair}?period=` | **real** — `models/registry.json` metrics | ✅ |
| `historical` | `GET /v1/fx/{pair}/historical?period=` | `layer2.DataProvider` + `TechnicalFeatures` | ✅ network |
| `status` | `GET /v1/status` | **real** — `layer2.status.engine.StatusEngine` | ✅ `HEALTHY` (verified) |
| `intelligence` | `GET /v1/market-intelligence` | **NEW** — English narrative synthesis over `RankingEngine` | ✅ |
| `interpretation` | `GET /v1/fx/interpretation?pair=&include_macro=` | `EconomicInterpreter` + `FORECAST_DATA`; macro via missing `layer1.services.macro_service` | ⚠️ partial |
| `model_comparison` | `GET /v1/fx/{pair:path}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding` (was 500) | ✅ — 200 (slow 3y walk-forward per pair) |

> `/v1/fx/macro/status` and `/v1/fx/macro/refresh` remain removed (interpretation router exposes only `/interpretation`).

### 3.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter`; **`adapters/decision_engine_adapter.py`** NEW.
- **`decision/`** — `decision_context.py`, `economic_filter.py`, `signal_validity.py`.
- **`llm/`** — provider chain + rule-based `FallbackLLM`; `EconomicInterpreter` resolves via fallback (LLM chain not invoked).
- **`routers/intelligence.py`** NEW — deterministic market-intelligence endpoint.
- **`data/forecast_data.py`** — consolidated hardcoded `FORECAST_DATA`.

> **Regression driver (closed for routers, open for models):** the layer-2 `DecisionEngine` per-pair refactor is now reflected in `drivers.py`, `price.py`, and `model_comparison.py` (all use `_get_model_for_pair`). The remaining fault line is **path resolution**: registry paths (`models/*.pkl`) are CWD-relative, and at the repo root the USD/JPY, EUR/USD, GBP/USD artifacts don't exist → those 3 pairs 404 in `drivers` and lose the `price` signal. `run_benchmarks.py` also still reads the removed `engine.xgb_model`.

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
XGBoostModel.predict (via DecisionEngine._get_model_for_pair(pair,'xgboost'))   ⚠️ CWD-sensitive
        │
        ├─▶ SHAPExplainer.explain ──▶ top-10 contributions   (drivers 200 when model resolves)
        └─▶ EconomicFilter.apply ──▶ edge_ratio / confidence / position_size
        ▼
DecisionEngine.get_forecast(pair)  ── on-disk cache (5-min TTL) + heuristic fallback
        │
        ├─▶ RankingEngine.get_ranking()  (score = 0.6·prob + 0.4·edge)
        ├─▶ StatusEngine.get_full_status()  (registry + live probes + LLM checks → HEALTHY/DEGRADED)
        └─▶ [layer1 price · forecast-dashboard · drivers · model-comparison · market-intelligence]
```

### 4.2 Module responsibilities

| Area | Files | Role |
| --- | --- | --- |
| `config.py` | — | Env config: keys, trading thresholds, paths |
| `data/` | `provider.py`, `fetcher.py`, `sources/{yahoo,alpha_vantage,twelve,fred}.py` | Multi-source failover data; FRED + simulated fallback |
| `data/macro/` | `service.py`, `cache.py`, `transformer.py` | `MacroService`, disk cache (24 h TTL), `MacroTransformer` |
| `status/` | `engine.py` | `StatusEngine` — model states, live probes, LLM availability, HEALTHY/DEGRADED |
| `features/` | `technical.py` | 23 technical indicators + `create_target()` |
| `models/` | `xgboost_model.py`, `logistic_model.py`, `registry.py` | Per-pair models + `ModelRegistry`; `model_selector.py`/`registry_adapter.py` unwired; `trainer.py` empty |
| `explainers/` | `shap_explainer.py` | SHAP `TreeExplainer`, top-10 contributions |
| `decision/` | `filter.py` | Simplified `EconomicFilter` |
| `ranking/` | `engine.py` | `RankingEngine` over active-model pairs |
| `quality/` | `pit_adapter.py` | Adapter over `PITValidator` — **dead code** |
| `engine.py` | — | `DecisionEngine` — per-pair model dicts, cache, heuristic fallback |

### 4.3 Models & registry

`backend/models/registry.json`: **10 models, all `active: true`**, all `v1.0` (9 XGBoost + 1 logistic). In-registry AUCs **0.380–0.733** (USD/CHF 0.733 best; USD/CNY 0.380 worst; USD/JPY xgb 0.408 / logistic 0.448). **Path caveat:** registry `path` is CWD-relative `models/*.pkl`; from the repo root only 6 of 9 XGBoost artifacts exist there (USD/JPY, EUR/USD, GBP/USD live only under `backend/models/`). `train_models.py` trains XGBoost into the registry; the new `train_experimental_models.py` trains logistic+sigmoid candidates into `models/experimental/`.

---

## 5. Layer 3 — research layer (`backend/layer3/`)

Standalone research/evaluation package. **Only coupling to the API:** `layer1/routers/model_comparison.py` (working). Nothing in `layer2` imports it.

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | `ModelArtifact`, `PredictionArtifact`, `ModelRegistry` | Persistence of research-approved models | ✅ implemented — schema **incompatible** with layer-2 `registry.json` |
| `evaluation/` | `walk_forward.py`, `benchmarks.py`, `run_benchmarks.py`, `model_evaluator.py`, `decision_policy.py` | Backtests, reference strategies, OOS split, policy search | ⚠️ `evaluate()` **FIXED**; `run_benchmarks.py` still crashes (`engine.xgb_model`); `model_evaluator` random fallback |
| `experiments/` | `run.py`, `real_experiments.py` | E0–E7 experiment suite | ❌ `run.py` still **hardcoded** stubs; `real_experiments.py` unblocked but unverified |
| `macro/regime.py` | `MacroRegimeEngine` | Risk/Policy/Growth/Inflation → regime classification | ✅ works |
| `models/` | `arima.py`, `elastic_net.py`, `ensemble.py` | Control models | ⚠️ ARIMA needs absent `statsmodels`; elastic-net/ensemble work |
| `rag/agents.py` | `CentralBankRAGEngine` | Fed/BoJ sentiment + expectation gap | ⚠️ keyword scorer, not real RAG |
| `research_gate/` | `gate.py`, `real_gate.py`, `full_gate.py` | 4-gate model approval | ⚠️ `gate.py` works; `full_gate.py` unblocked but passes `features={}`; `real_gate.py` inherits evaluator caveats |

### 5.1 Research Gate pipeline (repo root, NEW)

```
research_validation_test.py / final_holdout.py / evaluate_all_pairs.py
        ▼  purged 60/20/20 split · logistic + sigmoid calibration
research_validation_summary.csv
        ▼
research_gate.py  (RULES: val AUC>0.60 · test AUC>0.60 · drop<0.20 · PR-AUC>0.50 · cal-Brier<0.40)
        ▼
research_gate_results_v2.json        →   USD/BOB 20d  CANDIDATE_WITH_WARNINGS (cal Brier 0.636)
                                          EUR/USD 10d  CANDIDATE (cal Brier 0.237)
        ▼
train_experimental_models.py → models/experimental/{EUR_USD/h10, USD_BOB/h20}  (model + calibrator + metadata.json)
```

Caveats: PR-AUC is a declared rule but **not actually computed**; the experimental candidates are **not registered** in `backend/models/registry.json` and are never loaded by the API; `research_gate_results_v2.json` is currently untracked.

---

## 6. Layer 4 — data-quality layer (`backend/layer4/`)

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `quality/pit_validator.py` | `PITValidator` (PIT-1…PIT-7) | Point-in-Time compliance | ✅ correct (verified vs datasets A–D) |
| `config/policies.py` | `SourcePolicy`, `FeatureConfig`, `TargetConfig`, `ConfigRegistry` | Versioned configuration | ✅ implemented, **unused** |
| `lineage/models.py` | LineageReference/Record/Registry | Provenance | ✅ implemented, **unused** |
| `tests/pit_tests.py` | layer-4 unit tests | PITValidator tests | ❌ syntactically corrupted — won't parse |

**Wiring:** `PITValidator` is executed via `backend/tests/test_pit_adversarial.py` (part of the 103 passing suite). Runtime forecast paths do not validate PIT.

---

## 7. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consumes Layer 3 §11.2 / Layer 4 §7 contracts.

```
PredictionArtifact (L3 §11.2) ─┐
L4 streams (policy/GDP/rates,  │  PipelineInputs
  VIX, quality/freshness/drift)└──────────▶ DecisionPipeline.build()
                                                    │
     1. Signals        OOB → INVALID · 2. Regime+fusion → Direction
     3. Confidence · 4. Costs (VIX via FeatureStore P2) · 5. Economic filter
     6. Quality · 7. Hard gates (signal_validity P3) · 8. Sizing → Decision {...}
```

**Verification:** `python -m pytest` (from `backend/`) → **103 passed** across 12 files, incl. `test_pit_adversarial.py`.

---

## 8. Frontend — contract-driven dashboard (`frontend/`)

**Stack:** React 18, TS 5, Vite 5 (5174, minify off), Tailwind 3, TanStack Query 5, axios, date-fns, React Router 6, Recharts 2. **Contract root:** `types/contracts.ts` mirrors Layer 1 v5.1 §7. **Deploys:** Cloudflare Pages + Vercel.

### 8.1 Routes (16 hook modules)

| Path | Page | Data hooks |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/models` | ModelComparisonPage | `useModelComparison` → `/v1/fx/{pair}/model-comparison` |
| `/about` | AboutPage | (narrative) |

New this cycle: `constants/fxPairs.ts` (fixed pair order), `common/MarketConvention.tsx`, `UniverseSelector` refactor (drops `currencies` prop), `useActivePair` fixed-universe simplification. Dead/stale: `useFanChartData.ts`, orphaned `HistoricalPage.tsx`, duplicate `common/Header.tsx`, `mockup/*`.

### 8.2 SignalIQ Global + Forecast + Model Comparison

- `global/PriceChartSignalIQ.tsx` + `PriceChartWithHover.tsx`; `forecast/` ForecastCard/SpotCard/TrendCard — 30/60/90d XGBoost, live spot.
- `ModelComparisonPage` — walk-forward XGBoost / Logistic / Ensemble comparison from `/v1/fx/{pair}/model-comparison`.
- **New UI convention:** UniverseSelector is pair-driven (no `currencies` prop) with `MarketConvention` hint.

### 8.3 Macro dashboard (FRED)

`components/macro/MacroPanel.tsx` + `hooks/useMacro.ts` — 8-indicator grid from `/v1/fx/interpretation?pair=…&include_macro=true` (macro-side still warns: import `layer1.services.macro_service` missing).

### 8.4 Presentational components

`common/*` (incl. **MarketConvention**, duplicate `Header`), `global/*`, `forecast/*`, `drivers/*`, `evaluation/*`, `status/*`, `layout/*`, `macro/*`, `mockup/*`. `pages/HistoricalPage.tsx` remains orphaned.

### 8.5 Layering rules

| Rule | Location |
| --- | --- |
| Presentational components receive props only | `components/*` |
| Pages call hooks but don't compute/rank/derive | `pages/*` |
| `utils/` re-formats but never infers/calculates | `format.ts`, `status.ts`, `gaps.ts`, `safeFormat.ts` |
| Transport never transforms payloads | `services/api.ts` |
| Unsupported contract elements render `NotAvailable` | `types/gaps.ts` + `NotAvailable.tsx` |
| No derivation: consume `decision.actionable` | governance + gap registry |

> ⚠️ **Compile state:** `9d0b62f` refactored `UniverseSelector`/`useActivePair`/`fxPairs` but did not migrate the 6 page callers or `useActivePair.test.tsx` — **`npm run typecheck` and `npm run build` currently fail** and 2 tests are red.

---

## 9. Deployment & runtime

| Target | Mechanism | Notes |
| --- | --- | --- |
| **Render** (backend) | Docker web service (`render.yaml`, plan free, `/health`) | python:3.12-slim, `PYTHONPATH=/app/backend`, `uvicorn layer1.main:app` :10000; env FRED/GROQ/ALPHA/TWELVE (`sync:false`). `runtime.txt` (3.12.0) at repo root. |
| **Cloudflare Pages** (frontend) | Static-site mode; `_headers`, `_redirects` (`/* → /index.html 200`), `.cloudflareignore` | — |
| **Vercel** (frontend) | `vercel.json` — Vite build → `dist`, SPA rewrites | — |
| **Local** | `backend/docker-compose.yml` — port 10000, mounts `./models` + `./cache` | — |

**Ops caveats (updated):**
- **`frontend/.env.production` deleted (ed4758c)** — no production API URL in the repo; `frontend/.env`/`.env.local` point at `http://localhost:8000`. Production builds from source would target localhost.
- **Model paths are CWD-relative and inconsistent:** registry `path = models/*.pkl` resolves only when a `models/` dir exists at the process CWD. At repo root 3 core pairs (USD/JPY, EUR/USD, GBP/USD) 404; in Docker (WORKDIR `/app`) artifacts live at `/app/backend/models` and need `backend/models` → `/app/models` (or normalized paths) — unverified against the deployed image.
- FRED real data still requires `FRED_API_KEY`; without it the macro path serves simulated data.

---

## 10. Documentation & governance layer

The docs are the **authority**; code is verified against them.

```
docs/
├── Domain/ · High-Level Design/ · Low-Level Design/
├── Product_specification/   FROZEN L1 v5.1 · L2 v3.4.1 · L3 v5.0 · L4 v3.1.1
├── Prompts/                 Layer prompts + prompt_-1/0/X audit & build
└── Contract/                Governance artifacts (traceability, gaps, freeze, validation, migration, mapping)
```

| Artifact | Role |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row element→contract matrix (61 verified / 12 gap) |
| `CONTRACT_GAPS.md` (v2.0) | 16 unified gaps: G1–G9 + EC-1..4, RA, CA, DF-P |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | FREEZE WITH OPTIONAL GAPS, 0 blocking |
| `CONTRACT_VALIDATION.md` / `MIGRATION_REPORT.md` / `COMPONENT_MAPPING.md` | Prompt-1 audit PASS / 66 mockups / 100% mapping |

**Governance workflow:** change request → traceability → gaps → freeze → validate. The Layer 3/4 code, the Model Comparison surface, the new `/v1/market-intelligence` endpoint, the root Research Gate/experimental pipeline, and the fixed-universe UI changes have **not** gone through this loop.

---

## 11. Verification matrix

| Layer | Command | Status (2026-09-05) |
| --- | --- | --- |
| Backend `src` decision engine (+ L4 PIT) | `cd backend && python -m pytest` | **103 passed** (12 files) ✅ |
| Layer 1 import | `python -c "import backend.layer1.main"` | pass ✅ |
| Layer 1 endpoints (smoke) | TestClient against running app | `/status` `HEALTHY`; `/market-intelligence` 200; `/drivers` 200 (6 pairs) / 404 (3 core pairs); `/price` 200; `/model-comparison` 200 ✅ |
| Frontend typecheck | `cd frontend && npm run typecheck` | ❌ **FAILS** (~20 TS errors from `9d0b62f`) |
| Frontend tests | `cd frontend && npm test` | **53 passed / 2 FAILED** (`useActivePair.test.tsx`; `format.test.ts` green) |
| Frontend build | `cd frontend && npm run build` | ❌ **FAILS** (same TS errors) |

---

## 12. Known gaps & risks

1. **Frontend does not compile** — `UniverseSelector`/`useActivePair`/`fxPairs` refactor (`9d0b62f`): 6 pages still pass removed `currencies` prop; `useActivePair.test.tsx` references removed `DEFAULT_PAIR_UNIVERSE` and a 0-arg function's old 1-arg signature; unused `React`/`FX_PAIR_LABELS` imports. Typecheck, build, and 2 tests are red.
2. **Core-pair model resolution broken by CWD**: USD/JPY, EUR/USD, GBP/USD `.pkl` exist only under `backend/models/`, so registry-relative paths 404 from the repo root (`/drivers`) and suppress the `price` signal; the Docker image has the same latent mismatch.
3. **`frontend/.env.production` deleted** — no repo-configured production API URL; default builds target `localhost:8000`.
4. **Layer 3 tail** — `run_benchmarks.py` crashes (`engine.xgb_model`); `run.py` E0–E7 hardcoded; `arima.py` needs absent `statsmodels`; `artifacts/registry.py` schema incompatible with `backend/models/registry.json`.
5. **Layer 4 mostly unwired** — PIT runs only in tests; `pit_adapter.py`/`config`/`lineage` dead; `pit_tests.py` corrupted.
6. **Hardcoded/simulated endpoints** — `/forecast` & `/interpretation` use `FORECAST_DATA`; interpretation macro import (`layer1.services.macro_service`) missing; drivers `macro_drivers` hardcoded (VIX 16.8 / 72 / RISK_ON); FRED simulated without key.
7. **Research Gate caveats** — PR-AUC rule declared but not computed; `models/experimental/` unconsumed by the API; v2 results file untracked.
8. **`EconomicInterpreter` bypasses the LLM chain** (rule-based primary).
9. **`src` decision engine not wired to `layer2`/`layer1`** — 103 verified tests, zero runtime footprint.
10. **Contract-shape drift in frontend** — `direction === 'UP'` derivations, hardcoded VIX/riskAppetite/regime in `RegimeStrip`, locally computed returns.
11. **Dead/stale artifacts** — orphaned `HistoricalPage.tsx`; unused `FanChart`/`useFanChartData`/`WhyNow`/`DataTimestamps`/`ForecastHero`/`mockup/*`/duplicate `common/Header.tsx`; empty `trainer.py`; dead `layer2` adapters; **plus committed clutter** (13.9 MB ngrok zip, `commandos.md`, `start_backend.sh`, `VERSION*.txt`, `*.bak`/`*.backup`).
12. **Bundle size** — 1,397 kB main chunk; warning silenced by raising `chunkSizeWarningLimit`.