# Meridian FX — Repository Report

**Date:** 2026-09-04 · **Branch:** `main` (ahead of `origin/main` by 1 local commit) · **History:** 68 commits (2026-08-25 → 2026-09-02) · **Head commit:** `1734463` "Deploy to production" · **Latest tag:** `v2.3.0-estable-20260830`

This is an analysis of the repository as it stands today: what it is, what it contains, how it is governed, its verification status, and its known gaps and risks.

---

## 1. What this is

**Meridian FX** is an FX ("foreign exchange") intelligence product whose guiding principle is:

> *"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."*

It answers six product questions in its MVP (4 core pairs — USD/JPY, EUR/USD, GBP/USD, USD/CNY — with a 9-pair ranking universe):

| # | Question | Module |
| --- | --- | --- |
| 1 | What is happening in the market? | Global Overview |
| 2 | What does Meridian expect? | Forecast Dashboard |
| 3 | Why? | Drivers & Explanation |
| 4 | Is it worth acting? | Economic Filter |
| 5 | What could invalidate the signal? | Signal Validity |
| 6 | How good has Meridian been? | Performance Dashboard |

### What changed since the last report (2026-08-30)

This reporting cycle was dominated by **structural and operational** work rather than new product surfaces:

1. **Production deployment.** The app is now actually deployed: the FastAPI backend runs on **Render** (Docker, `uvicorn layer1.main:app`, port 10000, Python 3.12, health-check `/health`) and the frontend is published to **Cloudflare Pages** and **Vercel**, with the production API at `https://meridianfx.onrender.com` (`frontend/.env.production`). This required a long tail of fixes (CORS for the new origins, Docker/Cloudflare build wrangling, Python pinning for numba/shap).
2. **Backend restructure.** The Python code moved under a `backend/` folder (`backend/{layer1,layer2,layer3,layer4,src,models,tests}`); the dependency manifest became `backend/requirements.txt` and deploys via a root `Dockerfile` + `render.yaml`.
3. **Layer 3 and Layer 4 are now implemented as code** (previously described as "external"/docs-only): a Layer 3 research/evaluation stack (model artifacts, walk-forward evaluation, benchmark strategies, ARIMA/ElasticNet/Ensemble models, macro regime, central-bank "RAG", Research Gate) and a Layer 4 data-quality stack (PIT validation, config policies, lineage registry). Maturity is uneven — several pieces are functional, several are broken stubs (detailed in §5–§6).
4. **The `/v1/status` and `/v1/performance` endpoints became real** — a new `layer2/status/engine.py` `StatusEngine` probes models, data sources, and LLM providers live; performance now reads real registry metrics.
5. **A Model Comparison feature** was added end-to-end: router `/v1/fx/{pair}/model-comparison` (walk-forward vs. XGBoost/Logistic/Ensemble) + frontend `/models` page.
6. **A backend test regression appeared elsewhere**: the `src/` decision-engine suite grew to **103 passed**, and the new `test_pit_adversarial.py` wires the Layer 4 `PITValidator` into verification.
7. **A frontend regression appeared**: the rewritten `utils/format.ts` broke its own test suite — **45 passed / 10 failed** (`format.test.ts`). This is the current red item on the trunk.

The repo remains a working multi-layer application, now in production, but the production-hardened endpoints coexist with a set of **newly-red live routes caused by the `DecisionEngine` refactor** (§4.2): `/v1/fx/{pair}/drivers` and `/v1/fx/{pair}/model-comparison` now 500, and the `/price` endpoint silently loses its XGBoost signal.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs, prompts, and contract governance (Domain / HLD / LLD / Product_specification / Contract / Prompts)
├── backend/                     Python backend (moved from repo root in the deploy cycle)
│   ├── layer1/                  FastAPI delivery API — implemented (routers, models, adapters, LLM, decision)
│   ├── layer2/                  Live engine — XGBoost/SHAP/data providers/FRED macro/status/ranking
│   ├── layer3/                  NEW research layer — artifacts, evaluation, experiments, models, macro regime, RAG, research gate
│   ├── layer4/                  NEW data-quality layer — PIT validator, config policies, lineage
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, tests)
│   ├── models/                  Trained XGBoost/logistic .pkl + models/registry.json
│   ├── tests/                   Backend pytest suite (12 files)
│   ├── pyproject.toml           Backend project config (pythonpath=src, pytest)
│   └── requirements.txt         Backend dependency manifest (populated)
├── Dockerfile                   Render container (python:3.12-slim, uvicorn layer1.main:app, port 10000)
├── render.yaml                  Render blueprint (docker web service, free plan, /health)
├── runtime.txt                  Python 3.12.0 pin for Render
├── backend/docker-compose.yml   Local docker-compose (port 10000)
├── train_models.py              XGBoost training script (registers into ModelRegistry)
├── test_macro.py                MacroService tests (in backend/tests in practice)
├── frontend/                    React + TypeScript + Vite contract-driven dashboard (+ Recharts)
│   ├── .env.production          API → https://meridianfx.onrender.com
│   ├── vercel.json · _headers · _redirects   SPA routing for Cloudflare Pages / Vercel
│   └── dist/                    Committed production build
├── .env                         Runtime secrets + config (keys: FRED, GROQ, ALPHA_VANTAGE, TWELVE_DATA, OPENAI, CLOUDFLARE, …)
├── vite.config.ts               Frontend Vite config (port 5174, minify off, chunk limit 1000)
├── README.md                    Product overview + quickstart
├── report.md                    This document
└── architecture.md              System architecture
```

> **Working-tree hygiene:** `main` is ahead of `origin/main` by one **unpushed** local commit `11bcd1e` ("chore: limpieza de archivos basura y actualización README", 2026-09-04) that purged all `*.bak` / `*.backup_20260830` files (−1,403 lines) and updated `.gitignore`. A **stale untracked `requirements.txt`** (old pinned manifest: `fastapi==0.104.1`, `xgboost==2.0.3`, …) sits at the repo root with a friendly name collision against `backend/requirements.txt`; it should be deleted. The stray "ión estable 2.3.0 …" root file from the previous report is gone (removed in `11bcd1e`).

---

## 3. Backend — the two engines (unchanged roles, new neighbors)

The backend has **two cooperating Python engines** plus two new layers:

| Package | Role | Hygien |
| --- | --- | --- |
| `backend/src/meridian_fx/decision/` | Contract-governed Decision Engine (frozen to L2 spec, 103 tests) | verified ✅ |
| `backend/layer2/` | Live engine the API actually runs (data + ML + status) | wired into most routers |
| `backend/layer3/` | Research/evaluation layer (models, walk-forward, research gate) | NEW — partially wired (via `model_comparison`), several broken pieces |
| `backend/layer4/` | Data-quality/PIT layer | NEW — only `PITValidator` is referenced (by tests) |

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Unchanged in this cycle. Package root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consuming Layer 3 v5.0 (§11.2) and Layer 4 v3.1.1 (§7) inputs. Rule on every module docstring: **IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.**

`DecisionPipeline.build(PipelineInputs) → DecisionPipelineResult` runs 8 stages — Signals → Regime+Fusion → Confidence → Costs → Economic filter → Quality → Hard gates → Sizing — plus short-circuit paths yielding `NEUTRAL/INVALID`. Invariants encoded as patches P1–P10 (P2: VIX only via `FeatureStore`; P3: `GateResult.signal_validity` direct; P8: DecisionRegistry never stores L1 fields; P9/P10: delivery mapping + Synthetic D/D2 PIT acceptance validated).

**Verification:** `python -m pytest` (from `backend/`) → **103 passed** across 12 files (~0.2s). +4 tests this cycle come from `test_pit_adversarial.py`, which exercises the **Layer 4 `PITValidator`** against adversarial PIT datasets A–D (leakage / revision / derived-leakage).

### 3.2 `layer2/` — the live engine (data + ML, now + status)

Package root: `backend/layer2/`. The *wired* engine that fetches data, runs ML, explains it, and now reports its own health.

- **Data layer** (`data/`): `DataProvider` with ordered failover **Yahoo → Alpha Vantage → Twelve Data** (+ `fred.py` macro with simulated fallback when `FRED_API_KEY` is absent); `data/macro/` = `MacroService` + `MacroCache` (disk, 24 h TTL) + `MacroTransformer`.
- **Status engine** (`status/engine.py`, NEW): `StatusEngine` computes a real `/v1/status` — model states (active/stale/inactive from `models/registry.json`), live HTTP probes of the 4 data sources, LLM-provider availability (Groq/GLM/Gemini by `*_API_KEY` presence), cache size, memory, and an aggregate `HEALTHY/DEGRADED`. Wired into the `status` router.
- **Features** (`features/technical.py`): 23 technical indicators; `get_feature_names()` is the shared column contract.
- **Models** (`models/`): `XGBoostModel`, `LogisticModel`, `ModelRegistry` (versioned `.pkl`, auto-activation on better AUC). **NEW:** `model_selector.py` (per-pair best-approved model) and `registry_adapter.py` (L2 registry → L3 `ModelArtifact`-shaped dicts) are implemented but **not referenced anywhere** (dead code); `trainer.py` is still **empty**.
- **Explainers** (`explainers/shap_explainer.py`): SHAP `TreeExplainer`, log-odds→probability, top-10 contributions.
- **Ranking** (`ranking/engine.py`): score = 60% probability + 40% normalized edge ratio over the 9 pairs with active models.
- **Quality/PIT** (`quality/pit_adapter.py`, NEW): adapter over `layer4.quality.pit_validator.PITValidator` — implemented but **never imported** (dead code). `engine.py` does **not** reference it.
- **`engine.py`**: `DecisionEngine` with an on-disk forecast cache (5-min TTL) and a heuristic fallback. **Refactored this cycle**: it now holds *per-pair* model dicts (`xgb_models`, `logistic_models`) loaded dynamically via `_get_model_for_pair()`. It **no longer has** `xgb_model` / `logistic_model` attributes and **no `get_drivers()` method** — breaking several stale consumers (§4.2).

**Key observation (unchanged but now consequential):** the frozen `src/meridian_fx/decision/` and the live `layer2/` still both implement an "economic filter / decision" step and are **not wired to each other**. The refactor of `layer2.DecisionEngine` made the disconnect *painful*: routers written against the old single-model API (`drivers`, `model_comparison`, `price`) were not updated and now misbehave.

---

## 4. Backend — Layer 1 FastAPI delivery API (10 routers, deployed)

`backend/layer1/` is a **real FastAPI app** (`main.py`, "Meridian FX API" v1.0.0) with CORS extended to Render/Vercel/Cloudflare origins, **10 routers**, `/` and `/health`.

### 4.1 Endpoints — correctness updated per running service

| Method | Path | Source / notes | Health |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root + health | ✅ |
| GET | `/v1/status` | **real** `layer2.status.engine.StatusEngine` (was hardcoded) | ✅ |
| GET | `/v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) | ✅ (network) |
| GET | `/v1/fx/{pair}/drivers` | `layer2.DecisionEngine` SHAP + macro/RAG | ❌ **500** — calls `engine.get_drivers()`, which no longer exists |
| GET | `/v1/fx/{base}/{quote}/forecast` | hardcoded `FORECAST_DATA` (`layer1/data/forecast_data.py`) + random fallback | ⚠️ hardcoded |
| GET | `/v1/fx/performance/{pair}?period=` | **real** — `models/registry.json` metrics (was mock) | ✅ |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (stochastic fallback) | ✅ (network) |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | `EconomicInterpreter` + `FORECAST_DATA`; macro import (`layer1.services.macro_service`) **missing** → macro branch warns | ⚠️ partial |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history; XGBoost signal guarded by `engine.xgb_model` → **always skipped** | ⚠️ degraded |
| GET | `/v1/fx/{pair}/forecast-dashboard` | **live** — spot, trends, volatility, XGBoost 30/60/90d (`_get_model_for_pair`), macro | ✅ (network) |
| GET | `/v1/fx/{pair:path}/model-comparison` | **NEW** — Layer 3 walk-forward + ensemble | ❌ **500** — reads `engine.xgb_model`/`engine.logistic_model` (do not exist) |

> The `/v1/fx/macro/status` and `/v1/fx/macro/refresh` endpoints from the previous report are **gone** (interpretation router now exposes only `/interpretation`; the frontend `useMacro` hook was adjusted accordingly). `FORECAST_DATA` now lives in `layer1/data/forecast_data.py`.

### 4.2 DecisionEngine refactor — the source of the new red routes

`layer2.engine.DecisionEngine` moved from single-model (`self.xgb_model`) to per-pair dynamic loading (`self.xgb_models` dict + `_get_model_for_pair()`), but the following consumers were **not** ported:

- `routers/drivers.py` → still calls `engine.get_drivers(pair)` (a method that was proposed in `engine.py.bak` but never merged) → **HTTP 500**.
- `routers/model_comparison.py` → still reads `engine.xgb_model` / `engine.logistic_model` → **HTTP 500** (also triggers a slow 3-year walk-forward).
- `routers/price.py` → guards the ML block on `if engine.xgb_model:` → the guard is always false → **prediction silently disabled** (direction stays `UNKNOWN`).
- `layer3/evaluation/run_benchmarks.py` → same stale `engine.xgb_model` access → crashes at startup.

This is the single most important regression of the cycle: a working concept (multi-pair model loading) was shipped without updating its callers or re-running the affected routes.

### 4.3 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7 (now actually exercised by `status`, `ranking`, `performance`).
- **`adapters/decision_to_response.py`** — `DecisionAdapter` (dict → response models).
- **`decision/`** — `decision_context.py` (`DecisionContext`, `MacroContext`, `DecisionEngine.build_context`), `economic_filter.py`, `signal_validity.py`.
- **`llm/`** — `base.py`, `providers.py` (Groq live; GLM/Gemini stubs; rule-based `FallbackLLM`), `manager.py`, `interpreter.py`. The `EconomicInterpreter` still resolves via the rule-based fallback; the LLM chain is not actively invoked. (The `v2.3.0-estable-20260830` tag message claims "estable con LLM" — the plumbing exists, the router path does not exercise it.)

---

## 5. Backend — Layer 3 research layer (NEW, `backend/layer3/`)

Previously documented as an external/Layer-3 service, Layer 3 is now a Python package. It is **almost entirely standalone**: the *only* live coupler is `layer1/routers/model_comparison.py` (broken, §4.2). Nothing in `layer2` imports it.

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | `ModelArtifact`, `PredictionArtifact`, `ModelRegistry` | Persist research-approved models | ✅ implemented — but its JSON schema is **incompatible** with the layer-2 `models/registry.json` it defaults to (loading raises `TypeError`) |
| `evaluation/walk_forward.py` | `WalkForwardEvaluator.evaluate`, `evaluate_expanding` | Rolling/expanding backtest with purging + DA/AUC/Brier/ECE/Sharpe/MaxDD/PF | ⚠️ **`evaluate()` is broken** (`NameError: future_returns_test` — the var is only defined in `evaluate_expanding`); `evaluate_expanding()` works |
| `evaluation/benchmarks.py` | `BenchmarkEvaluator` (always long/short, buy&hold, random) | Reference strategies | ✅ works (numpy only) |
| `evaluation/run_benchmarks.py` | CLI runner | Print per-window benchmark tables | ❌ **crashes** — early `engine.xgb_model` access |
| `evaluation/model_evaluator.py` | `ModelEvaluator.evaluate_xgboost` | Simple OOS (last 20%) split | ⚠️ works but falls back to `random.random()` on predict failure; target uses a backward-looking rolling window |
| `evaluation/decision_policy.py` | `DecisionPolicyEvaluator` (threshold LONG/FLAT/SHORT) | Policy testing | ✅ works |
| `experiments/run.py` | `ExperimentRunner` E0–E7 | Sequential experiments | ❌ **stub** — every experiment returns **hardcoded** metrics |
| `experiments/real_experiments.py` | `RealExperimentRunner` | Run E0–E7 with real walk-forward | ❌ **broken** — routes through the broken `evaluate()` |
| `macro/regime.py` | `MacroRegimeEngine` (Risk/Policy/Growth/Inflation → Expansion/Late/Stagflation/…) | Regime classification | ✅ works, deterministic rules |
| `models/arima.py` | `ARIMAModel` (fit/predict, ADF, AIC search) | ARIMA control model | ⚠️ implemented but **unrunnable**: needs `statsmodels` (not in `requirements.txt`/venv) |
| `models/elastic_net.py` | `ElasticNetModel` (saga, purged walk-forward CV) | Elastic-net control model | ✅ works (sklearn only) |
| `models/ensemble.py` | `EnsembleModel` (weighted XGB+ElasticNet+ARIMA) | Ensemble | ✅ works (weighted average) — the only L3 piece actually used by a router |
| `rag/agents.py` | `CentralBankRAGEngine` (Fed/BoJ sentiment, expectation gap, features) | Central-bank "RAG" | ⚠️ implemented as a **keyword-dictionary scorer**, not real RAG/embeddings |
| `research_gate/gate.py` | `ResearchGate` (leakage/statistical/economic/robustness) | 4-gate model approval | ✅ works (robustness loop reads `sharpe_net` but walk-forward reports `Sharpe` → the failure branch is effectively inert) |
| `research_gate/real_gate.py` | `RealResearchGate.evaluate_and_validate` | Gate over `ModelEvaluator` | ⚠️ works, inherits evaluator caveats |
| `research_gate/full_gate.py` | `FullResearchGate` | Full approve/reject pipeline | ❌ **broken** — calls broken `evaluate()`; passes `features={}` |

**Bottom line:** Layer 3 is scaffolding with a working core (benchmarks, elastic-net, ensemble, macro regime, gate) surrounded by stubs and two confirmed NameError bugs. Despite the "research gate" framing, nothing gates anything at runtime yet.

---

## 6. Backend — Layer 4 data-quality layer (NEW, `backend/layer4/`)

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `quality/pit_validator.py` | `PITValidator` (PIT-1…PIT-7) | Feature-snapshot Point-in-Time compliance | ✅ **implemented and correct** — verified manually against datasets A (pass), B/C/D (fail as intended) |
| `config/policies.py` | `SourcePolicy`, `FeatureConfig`, `TargetConfig`, `ConfigRegistry`, `create_default_config()` | Versioned data-source/feature/target configuration | ✅ implemented, **standalone** — referenced nowhere |
| `lineage/models.py` | `SourceReference`, `LineageReference`, `LineageRecord`, `LineageRegistry` | Provenance/audit records | ✅ implemented, **standalone** — referenced nowhere (the `"lineage"` literal in `forecast.py` is unrelated) |
| `tests/pit_tests.py` | layer-4 unit tests | Test suite for PITValidator | ❌ **syntactically corrupted** (missing params, mangled lines) — does not even parse |

**Live wiring of Layer 4 → rest of repo:**
- `backend/tests/test_pit_adversarial.py` (the suite that pushed backend tests to 103) imports `PITValidator` directly — this is the only *actually executed* integration.
- `backend/layer2/quality/pit_adapter.py` delegates to `PITValidator` but is dead code.
- `PITValidator` is **not** called from `engine.py` or any router, so PIT compliance is validated in tests but not enforced at runtime.

---

## 7. Frontend — contract-driven dashboard (React + TypeScript)

Stack unchanged: **React 18 + TS + Vite (5174) + Tailwind + TanStack Query + axios + date-fns + React Router + Recharts**. Now deployed: **Cloudflare Pages** (root-index mode, `_headers`/`_redirects` SPA fallback) and **Vercel** (`vercel.json` rewrites), prod API `https://meridianfx.onrender.com`.

### 7.1 Routes & composition (17 hooks)

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/models` | **ModelComparisonPage** (NEW) | `useModelComparison` → `GET /v1/fx/{pair}/model-comparison` |
| `/about` | AboutPage | (narrative) |

New components this cycle: `global/ActionableInfo.tsx`, `global/ModelExplanation.tsx`, `forecast/FanChart.tsx` (+ `hooks/useFanChartData.ts` — **dead code**, not mounted), `hooks/useModelComparison.ts`, `hooks/useMacroContext.ts`.

### 7.2 Presentational surface

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, **Header** — a *duplicate* `common/Header.tsx` exists next to the live `layout/Header.tsx` that `MainLayout` actually imports), `global/*` (+ ActionableInfo, ModelExplanation), `forecast/*` (+ FanChart; unexported WhyNow/DataTimestamps/ForecastHero remain), `drivers/*`, `evaluation/*`, `status/*`, `layout/*`, `macro/*`, `mockup/*` (Gauge, PipelineStepper, RegimeStrip, SHAPBar). `pages/HistoricalPage.tsx` is still orphaned (no route).

### 7.3 Verification — one red item returned

| Check | Previous report | Now |
| --- | --- | --- |
| Backend pytest | 99 passed | **103 passed** ✅ (12 files) |
| Frontend typecheck (`npm run typecheck`) | clean | **clean** ✅ |
| Frontend tests (`npm test`) | 55 passed | **45 passed / 10 FAILED** ❌ |
| Frontend build (`npm run build`) | OK | **OK** ✅ |

The 10 failures are all in `src/tests/utils/format.test.ts`: `formatPercent`, `formatProbability`, `formatDateTime`, `formatDate`, `formatNumber`, `formatDirection`, `formatEdgeRatio`, `formatDrawdown`, `formatStatus`, `formatCurrency`-adjacent cases. Root cause: `utils/format.ts` was rewritten in commit `683e28e` ("add formatDate and complete format utilities") — decimal counts changed (`12.34%` → `12.3%`), `formatEdgeRatio` lost its `×` suffix, date/time use `es-ES` locale, status mapping became partial — but the tests (which encode the intended contract) were not updated. Either the tests or the implementation must give.

Build note: the main bundle is now **1,397 kB** (minify disabled). The previous >500 kB warning was silenced by raising `chunkSizeWarningLimit: 1000` in `vite.config.ts` rather than by code-splitting.

---

## 8. Models & training

- `backend/models/registry.json` — **10 registered models**, all `active`, all `v1.0`: 9 XGBoost (USD/CHF, GBP/USD, USD/BRL, USD/ARS, USD/MXN, USD/JPY, USD/CNY, EUR/USD, USD/BOB) + 1 logistic (USD/JPY). Metrics are weak-to-modest: AUCs 0.38–0.73 (best USD/CHF 0.733; worst USD/CNY 0.380); USD/JPY models sit below 0.45 AUC with ~0.31 accuracy. The `v2.3.0` tag noted "Logistic como mejor modelo" for USD/JPY — consistent with the registry (logistic AUC 0.448 vs xgboost 0.408).
- `train_models.py` (root) — trains XGBoost per pair (`DataProvider` + `TechnicalFeatures` + `XGBoostModel` + `ModelRegistry`).
- `backend/layer2/models/` — `model_selector.py` + `registry_adapter.py` (implemented, unwired), `trainer.py` (empty, still a stub).

---

## 9. Deployment & operations (NEW — now real)

| Target | What | Evidence |
| --- | --- | --- |
| **Render** (backend) | Docker web service, plan free, `dockerfilePath: ./Dockerfile`, health path `/health` | `render.yaml`; `Dockerfile` (python:3.12-slim, `PYTHONPATH=/app/backend`, `uvicorn layer1.main:app`, port 10000); env vars FRED/GROQ/ALPHA_VANTAGE/TWELVE_DATA (sync:false) |
| **Cloudflare Pages** (frontend) | Static-site mode (no wrangler config), root-index, `_headers` (X-Robots-Tag, ACAO `*`), `_redirects` (`/* → /index.html 200`) | `frontend/_headers`, `_redirects`, `.cloudflareignore`; `.wrangler/` dir |
| **Vercel** (frontend) | Vite build → `dist`, SPA rewrites | `frontend/vercel.json`; `.vercel/` dir |
| **Local** | `docker-compose.yml` in `backend/`, port 10000, volumes `./models`+`./cache` | — |

Operations caveats:
- `runtime.txt` pins **3.12.0** at the repo root (the "moved to backend/" commit was later reverted in the Docker fix stack, so it lives at root).
- The backend reads `models/registry.json` and `cache/` **relative to the CWD**; in the Docker image the working dir is `/app` while models/cache live under `/app/backend/` — paths must be checked against the deployed image.
- Only the FRED/GROQ/ALPHA/TWELVE keys can be injected at deploy; `OPENAI_API_KEY`/`CLOUDFLARE_API_TOKEN` are in local `.env` only.

---

## 10. Models of verification & governance (unchanged)

The repo is **prompt-first** (`docs/Prompts/` drives each layer) and **Contract/ polices** fidelity. Freeze artifacts unchanged: `CONTRACT_TRACEABILITY.md` (73-row, 61 verified / 12 gap), `CONTRACT_GAPS.md` (16 gaps), `FRONTEND_CONTRACT_FREEZE.md`, `CONTRACT_VALIDATION.md`, `MIGRATION_REPORT.md`, `COMPONENT_MAPPING.md`. Frozen specs: L1 v5.1 (frontend authority), L2 v3.4.1 (backend authority).

> The new Layer 3/Layer 4 code and the shipped Model Comparison surface have **not** been pushed through the traceability→gaps→freeze loop.

---

## 11. Current status & known gaps

**Green**
- Production deploys: backend on Render, frontend on Cloudflare Pages + Vercel.
- Backend pytest: **103/103** (contract fidelity + PIT/D2 validation enforced; `src/` suite grew +4 via `test_pit_adversarial`).
- Frontend typecheck clean; production build OK.
- `/v1/status` and `/v1/performance` are now **real** (StatusEngine + registry metrics).
- Layer 3/4 scaffolding exists with several functional pieces (benchmarks, elastic-net/ensemble, macro regime, research gate, PITValidator).

**Red / attention**
1. **`DecisionEngine` refactor broke three live routes** — `drivers` (500, `get_drivers` gone) and `model_comparison` (500, `xgb_model` gone), `price` (ML silently disabled, always `UNKNOWN`); `run_benchmarks.py` crashes too.
2. **Frontend tests: 10 failures** in `format.test.ts` from the `format.ts` rewrite (contract vs. implementation mismatch) — the previous green 55/55 regressed.
3. **Layer 3 has two confirmed NameError bugs** (`walk_forward.evaluate()`, poisoned `real_experiments.py` + `full_gate.py`), hardcoded experiment stubs (E0–E7), an unrunnable ARIMA model (missing `statsmodels`), and a broken `run_benchmarks.py`.
4. **Layer 4 test suite is corrupted** (`tests/pit_tests.py` won't parse) even though the PITValidator itself is correct; Layer 4 is otherwise unwired (config/lineage/quality adapters are dead code).
5. **Live endpoints still hardcoded/simulated**: `/forecast` (hardcoded `FORECAST_DATA`), `/interpretation` (FORECAST_DATA + a macro import that no longer exists → macro section fails), FRED simulated without `FRED_API_KEY`, drivers macro/RAG placeholders.
6. **Layer 3 registry schema mismatch** — `layer3.artifacts.registry.ModelRegistry` cannot read `backend/models/registry.json`.
7. **`EconomicInterpreter` never invokes the LLM chain** (always rule-based fallback as the primary path).
8. **`src` decision engine still not wired to `layer2`/`layer1`** — the contract-governed pipeline (103 tests) and the live engine remain unconnected.
9. **Contract-shape drift** persists in newer pages (Global/Forecast `direction === 'UP'` derivations, hardcoded `vix={16.8}`/`riskAppetite`/`regime="UNKNOWN"` in `RegimeStrip`, locally derived returns).
10. **Env-key mismatch persists** (`VITE_API_BASE_URL` vs `VITE_API_URL`); `.env` sets only the latter (works by coincidence of defaults + `frontend/.env.production`).
11. **Dead/stale artifacts persist**: orphaned `HistoricalPage.tsx`, unused `FanChart`/`useFanChartData`/`WhyNow`/`DataTimestamps`/`ForecastHero`/`mockup/*`/`common/Header.tsx` (duplicate), empty `data/historical/`, empty `layer2/models/trainer.py`, dead `layer2` adapters (pit/model_selector/registry_adapter).
12. **Git hygiene**: `main` is ahead of `origin/main` by 1 unpushed commit (`11bcd1e`); a stale **untracked `requirements.txt`** at the repo root collides by name with `backend/requirements.txt`.
13. **Bundle size grew** to 1,397 kB minified; the warning threshold was raised to 1000 kB instead of code-splitting.

---

## 12. Recommendations

1. **Fix the `DecisionEngine` API drift immediately** — restore a `get_drivers()` method (or rewrite `drivers.py` against `_get_model_for_pair`), port `model_comparison.py`/`price.py`/`run_benchmarks.py` to the per-pair API, and re-verify `/v1/fx/{pair}/drivers`, `/price`, `/model-comparison` end-to-end.
2. **Reconcile `format.ts` with `format.test.ts`** — it's the only red frontend item; either update the tests to the new contract or restore the previous behavior.
3. **Fix the Layer 3 `walk_forward.evaluate()` NameError** (`future_returns_test` → `returns_test`), delete/harden `run.py`'s hardcoded experiments, add `statsmodels` to `requirements.txt` if ARIMA is wanted, and repair `layer4/tests/pit_tests.py` (or fold PIT tests into `backend/tests/`).
4. **Wire the intended integrations**: make `layer2.engine.py` call the PIT adapter before caching forecasts, make the `model_comparison` router the showcase path for Layer 3, and reconcile the Layer 3 artifact registry schema with `backend/models/registry.json`.
5. **Finish real-data migration**: replace `FORECAST_DATA` in `/forecast` and `/interpretation` with the `forecast-dashboard` real payload, fix the `layer1.services.macro_service` import, and set `FRED_API_KEY` in Render.
6. **Button up ops**: harden the CWD-relative `models/registry.json`/`cache` paths in the Docker image, push the pending local commit, and delete the stale root `requirements.txt`.
7. **Push the new surfaces through governance** (Model Comparison, Layer 3/4 code) — traceability → gaps → freeze → validation, per the established model.
8. **Re-run the audit loop** after the format/route fixes, and consider code-splitting the 1.4 MB bundle instead of raising the warning limit.