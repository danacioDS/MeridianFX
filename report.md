# Meridian FX — Repository Report

**Date:** 2026-09-05 · **Branch:** `main` (in sync with `origin/main`) · **History:** 85 commits (2026-08-25 → 2026-09-05) · **Head commit:** `9d0b62f` "feat: orden fijo de pares y convención de mercado en UI" · **Latest tag:** `v2.3.5-experimental-20260905` (also `v2.3.1-estable-20260904` … `v2.3.4-estable-20260905`)

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

### What changed since the last report (2026-09-04)

This cycle (2026-09-04 → 2026-09-05, 17 commits, tagged `v2.3.1` → `v2.3.5-experimental`) was dominated by **stabilization and research** work, closing most of the previous report's red route items while opening a new frontend **compile break**:

1. **The `DecisionEngine` refactor disconnect is mostly resolved.** The stale consumers were finally ported to the per-pair API (`_get_model_for_pair`): `drivers.py` (route re-shaped to `/{base}/{quote}/drivers`), `price.py` (signal restored), and `model_comparison.py` (returns 200). Verified live with a TestClient against a running app: `/v1/fx/{pair}/drivers`, `/v1/fx/{pair}/price`, and `/v1/fx/{pair}/model-comparison` now respond 200 instead of 500. **One consequence remains**: `_get_model_for_pair()` resolves models only when the registry's CWD-relative `.pkl` path exists; for USD/JPY, EUR/USD, and GBP/USD the `.pkl` files exist only under `backend/models/`, so `/drivers` 404s for exactly the three core pairs (§4.1, §4.2).
2. **The frontend `format.test.ts` red item is fixed** (commits `81506c6` + `c862f5a` restored the `format.ts` contract): all 18 `format` tests pass now. The equal-but-opposite red item appeared: commit `9d0b62f` ("fixed pair order + market-convention UI") refactored `UniverseSelector`/`useActivePair`/`fxPairs` **without recompiling the app** — the frontend **typecheck and build now fail** and 2 tests in `useActivePair.test.tsx` fail (§7.3).
3. **Layer 3's `walk_forward.evaluate()` NameError is fixed** (`future_returns_test` is now computed in both methods) — the poisoned `real_experiments.py` and `full_gate.py` call paths are unblocked. `run_benchmarks.py` remains the one broken L3 CLI (still reads removed `engine.xgb_model`).
4. **Research Gate became real** (root-level, outside `backend/`): `research_gate.py` classifies candidates with corrected criteria (validation/test AUC > 0.60, stability drop < 0.20, **PR-AUC > 0.50**, calibrated Brier < 0.40), fed by `research_validation_test.py` + `final_holdout.py`. Two candidate models (EUR/USD 10d, USD/BOB 20d — Logistic Regression + sigmoid calibration) were trained under a purged 60/20/20 protocol, gated, and persisted to `models/experimental/` (`train_experimental_models.py`). Results are in `research_gate_results.json` (v1) and `research_gate_results_v2.json` (v2, untracked — the corrected criteria flip EUR/USD from REJECTED → CANDIDATE and USD/BOB → CANDIDATE_WITH_WARNINGS).
5. **New product surface:** `GET /v1/market-intelligence` — a new `intelligence` router producing English narrative synthesis (context, key signals, interpretation, decision view) from the ranking engine.
6. **Frontend/ops plumbing:** CORS expanded (ngrok origins, wildcard `*.ngrok-free.dev`, `*`), `ngrok-skip-browser-warning` header, localhost base-URL fallback, `.env` now sets both `VITE_API_URL` and `VITE_API_BASE_URL`. **However, `frontend/.env.production` was deleted** (`ed4758c`) leaving no repo-configured production API URL for frontend builds (§9).
7. **Git hygiene improved then regressed:** `main` is now in sync with `origin/main` and the stale root `requirements.txt` is gone — but the cycle committed junk: a 13.9 MB `ngrok-stable-linux-amd64.zip`, `commandos.md`, `start_backend.sh`, `VERSION*.txt`, and several `.bak`/`.backup` files (re-introduced in `c06e357`, §2).
8. **Verification footprint:** backend pytest stays **103 passed**; the new failures are exclusively frontend (`typecheck`, `build`, 2 tests).

The balance sheet moved: three previously-red routes are green, the format-test red item is green, but the **trunk now fails to compile** — the last commit (`9d0b62f`) shipped types against un-migrated callers, so the production build is currently broken at source.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs, prompts, and contract governance (Domain / HLD / LLD / Product_specification / Contract / Prompts)
├── backend/                     Python backend
│   ├── layer1/                  FastAPI delivery API — implemented (11 routers, models, adapters, LLM, decision, INTELLIGENCE)
│   ├── layer2/                  Live engine — XGBoost/SHAP/data providers/FRED macro/status/ranking
│   ├── layer3/                  Research layer — artifacts, evaluation, experiments, models, macro regime, RAG, research gate
│   ├── layer4/                  Data-quality layer — PIT validator, config policies, lineage
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, tests)
│   ├── models/                  Trained XGBoost/logistic .pkl + models/registry.json (10 models) + models/experimental/
│   ├── tests/                   Backend pytest suite (12 files)
│   ├── pyproject.toml           Backend project config (pythonpath=src, pytest)
│   └── requirements.txt         Backend dependency manifest
├── Dockerfile                   Render container (python:3.12-slim, uvicorn layer1.main:app, port 10000)
├── render.yaml                  Render blueprint (docker web service, free plan, /health)
├── runtime.txt                  Python 3.12.0 pin for Render
├── backend/docker-compose.yml   Local docker-compose (port 10000)
├── train_models.py              XGBoost training script (registers into ModelRegistry)
├── train_experimental_models.py NEW — trains + gates logistic candidate models (models/experimental/)
├── evaluate_all_pairs.py        NEW — systematic per-pair/per-horizon evaluation (pairs × horizons)
├── final_holdout.py             NEW — final holdout validation script
├── research_validation_test.py  NEW — runs validation + summarizer → research_validation_*.{json,csv}
├── research_gate.py             NEW — Research Gate v2 classifier (AUC / PR-AUC / calibrated Brier)
├── research_gate_results.json   NEW — gate output v1 (committed)   [EUR/USD REJECTED]
├── research_gate_results_v2.json  NEW — gate output v2 (UNTRACKED) [corrected criteria]
├── research_validation_results.json · research_validation_summary.csv · final_holdout_results.csv   NEW outputs
├── models/experimental/         Experimental candidates: EUR/USD h10 · USD/BOB h20 (model + calibrator + metadata.json)
├── models/                      Root-level model artifacts (only 6 of 9 XGBoost .pkl — see §4.2)
├── test_macro.py                MacroService tests
├── frontend/                    React + TypeScript + Vite contract-driven dashboard (+ Recharts)
│   ├── .env                     VITE_API_URL=VITE_API_BASE_URL=http://localhost:8000 — NO .env.production (deleted)
│   ├── vercel.json · _headers · _redirects   SPA routing for Cloudflare Pages / Vercel
│   └── src/                     pages, hooks (16), components, utils, tests
├── .env                         Runtime secrets + config (keys: FRED, GROQ, ALPHA_VANTAGE, TWELVE_DATA, OPENAI, CLOUDFLARE, …)
├── vite.config.ts               Frontend Vite config (port 5174, minify off, chunk limit 1000)
├── README.md                    Product overview + quickstart
├── ngrok-stable-linux-amd64.zip (13.9 MB — accidentally committed in c06e357)
├── commandos.md · start_backend.sh · VERSION*.txt · *.bak / *.backup files   (committed clutter)
├── report.md                    This document
└── architecture.md              System architecture
```

> **Working-tree hygiene:** `main` is in sync with `origin/main` (0 ahead / 0 behind). The only dirty entries are `cache/forecast_cache.json` (runtime cache churn) and the **untracked `research_gate_results_v2.json`** — the output of the latest `research_gate.py` run on the corrected criteria; it should be committed alongside `train_experimental_models.py` or gitignored. The `ngrok-stable-linux-amd64.zip` (13.9 MB) and `*.bak`/`*.backup` files that were purged in `11bcd1e` were **re-introduced** by `c06e357` and are still there.

---

## 3. Backend — the two engines (unchanged roles, new neighbors)

The backend has **two cooperating Python engines** plus two new layers:

| Package | Role | Hygiene |
| --- | --- | --- |
| `backend/src/meridian_fx/decision/` | Contract-governed Decision Engine (frozen to L2 spec, 103 tests) | verified ✅ |
| `backend/layer2/` | Live engine the API actually runs (data + ML + status) | wired into most routers |
| `backend/layer3/` | Research/evaluation layer (models, walk-forward, research gate) | wired via `model_comparison`; `run_benchmarks.py` broken |
| `backend/layer4/` | Data-quality/PIT layer | only `PITValidator` is referenced (by tests) |

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Unchanged this cycle. Package root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1. **Verification:** `python -m pytest` (from `backend/`) → **103 passed** across 12 files (~0.2s), including `test_pit_adversarial.py` (Layer 4 `PITValidator` on adversarial datasets A–D).

### 3.2 `layer2/` — the live engine (data + ML, now + status)

- **Data layer** (`data/`): `DataProvider` ordered failover **Yahoo → Alpha Vantage → Twelve Data** (+ `fred.py` simulated fallback); `data/macro/` = `MacroService` + disk `MacroCache` (24 h TTL) + `MacroTransformer`.
- **Status engine** (`status/engine.py`): real `/v1/status` — model states, live data-source probes, LLM-provider availability, cache/memory, aggregate `HEALTHY/DEGRADED`. Verified live: returns `HEALTHY`.
- **Models** (`models/`): `XGBoostModel`, `LogisticModel`, `ModelRegistry`; `model_selector.py` and `registry_adapter.py` remain **unreferenced dead code**; `trainer.py` still **empty**.
- **`engine.py`**: `DecisionEngine` with per-pair model dicts + `_get_model_for_pair()` and a 5-min TTL disk cache. **Model resolution is CWD-sensitive** (`os.path.exists` on the registry's relative `models/*.pkl` path): from the repo root only 6 of 9 XGBoost pairs resolve (§4.2).

**Key observation:** the practical gap highlighted last cycle — the refactor was shipped without porting its consumers — is now closed for the routers. What remains is the **CWD/path side of that refactor**: registry paths assume a `models/` folder at the process CWD, so which pairs get a live signal depends on *where the process runs*.

---

## 4. Backend — Layer 1 FastAPI delivery API (11 routers, deployed)

`backend/layer1/` is a **real FastAPI app** (`main.py`, "Meridian FX API" v1.0.0). CORS now covers localhost, Render, Vercel, Cloudflare Pages, ngrok (`*.ngrok-free.dev`) and `*`. **11 routers** plus `/` and `/health`.

### 4.1 Endpoints — correctness updated per running service (verified with TestClient)

| Method | Path | Source / notes | Health |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root + health | ✅ |
| GET | `/v1/status` | real `StatusEngine` | ✅ (`HEALTHY`) |
| GET | `/v1/market-intelligence` | **NEW** — `intelligence` router, English synthesis over `RankingEngine` | ✅ |
| GET | `/v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) | ✅ (network) |
| GET | `/v1/fx/{base}/{quote}/drivers` | SHAP + macro via `_get_model_for_pair` (was 500) | ✅ / ⚠️ — **200 for 6 pairs; 404 for USD/JPY, EUR/USD, GBP/USD** (`.pkl` missing at repo-root `models/`) |
| GET | `/v1/fx/{base}/{quote}/forecast` | hardcoded `FORECAST_DATA` (`layer1/data/forecast_data.py`) + random fallback | ⚠️ hardcoded |
| GET | `/v1/fx/performance/{pair}?period=` | real — `models/registry.json` metrics | ✅ |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (stochastic fallback) | ✅ (network) |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | `EconomicInterpreter` + `FORECAST_DATA`; macro import (`layer1.services.macro_service`) still **missing** → macro branch warns | ⚠️ partial |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history; XGBoost signal **restored** via `_get_model_for_pair` (was always-skipped) | ✅ / ⚠️ — 200, but signal only when the pair's model resolves |
| GET | `/v1/fx/{pair}/forecast-dashboard` | **live** — spot, trends, volatility, XGBoost 30/60/90d, macro | ✅ (network) |
| GET | `/v1/fx/{pair}/model-comparison` | Layer 3 walk-forward + ensemble (was 500) | ✅ — 200 (still a slow 3-year walk-forward per pair) |

> The `/v1/fx/macro/status` and `/v1/fx/macro/refresh` endpoints remain removed (interpretation router exposes only `/interpretation`).

### 4.2 DecisionEngine refactor — consumers now ported; path resolution is the new fault line

All four stale consumers from last cycle were updated to the per-pair API:

- `routers/drivers.py` → route changed to `/{base}/{quote}/drivers`, calls `engine._get_model_for_pair(pair, "xgboost")` → **200 with SHAP** when the model loads. If the model does **not** load it returns the new 404 path ("Model not found for …") — i.e. the 500 is gone, and the 404 is now a *live symptom* of the path issue below.
- `routers/model_comparison.py` → uses `engine._get_model_for_pair(...)` for xgboost/logistic → **200** (verified; ensemble now reported as `"available": false` / `evaluation: not_implemented`, `best_model` chosen by Sharpe).
- `routers/price.py` → guards on `xgb_model.model` from `_get_model_for_pair` → **200 with real prediction** when the model resolves.
- `layer3/evaluation/run_benchmarks.py` → **still broken**: it reads `engine.xgb_model` (removed attribute) and crashes at call time.

**Path-resolution fault line (NEW, live):** the registry stores CWD-relative paths like `models/xgboost_USD_JPY_v1.0.pkl`. From the repo root, `backend/models/registry.json` lists 10 models but only 6 of the 9 XGBoost `.pkl` files exist in the repo-root `models/` folder — USD/JPY, EUR/USD, and GBP/USD artifacts live only under `backend/models/`. Consequently `_get_model_for_pair` returns `None` for exactly those three (verified: `/drivers` → 404), i.e. **the three non-USD-quoted core pairs have no live signal**. In the Render container (WORKDIR `/app`, registry path `models/…` → `/app/models` which doesn't exist) this would disable model resolution for *all* pairs unless the deploy copies `backend/models` to `/app/models`.

### 4.3 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter`; **`adapters/decision_engine_adapter.py`** NEW (engine → response shaping).
- **`decision/`** — `decision_context.py`, `economic_filter.py`, `signal_validity.py`.
- **`llm/`** — providers/manager/interpreter; `EconomicInterpreter` still resolves via the rule-based fallback; the LLM chain is still not actively invoked.
- **`routers/intelligence.py`** NEW — `/v1/market-intelligence` (English narrative; purely deterministic over `RankingEngine.get_ranking()`).

---

## 5. Backend — Layer 3 research layer (`backend/layer3/`)

The **only** live coupler remains `layer1/routers/model_comparison.py` (now working, §4.2). Nothing in `layer2` imports it.

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | `ModelArtifact`, `PredictionArtifact`, `ModelRegistry` | Persist research-approved models | ✅ implemented — JSON schema still **incompatible** with `backend/models/registry.json` |
| `evaluation/walk_forward.py` | `evaluate`, `evaluate_expanding` | Rolling/expanding backtest (purging, DA/AUC/Brier/ECE/Sharpe/MaxDD/PF) | ✅ **`evaluate()` NameError FIXED** (`future_returns_test` now computed in both methods) |
| `evaluation/benchmarks.py` | `BenchmarkEvaluator` | Reference strategies | ✅ works |
| `evaluation/run_benchmarks.py` | CLI runner | Per-window benchmark tables | ❌ **still crashes** — `engine.xgb_model` access (not ported) |
| `evaluation/model_evaluator.py` | `ModelEvaluator.evaluate_xgboost` | Simple OOS (last 20%) | ⚠️ random-fallback on predict failure; backward-looking target |
| `evaluation/decision_policy.py` | `DecisionPolicyEvaluator` | Threshold LONG/FLAT/SHORT | ✅ works |
| `experiments/run.py` | `ExperimentRunner` E0–E7 | Sequential experiments | ❌ still **hardcoded** metrics (`DA: 0.60–0.62`, `Sharpe: 0.45–0.50`) |
| `experiments/real_experiments.py` | `RealExperimentRunner` | Real walk-forward E0–E7 | ⚠️ unblocked by the walk-forward fix, but not verified |
| `macro/regime.py` | `MacroRegimeEngine` | Regime classification | ✅ works, deterministic |
| `models/arima.py` | `ARIMAModel` | ARIMA control model | ⚠️ still unrunnable — `statsmodels` absent from `requirements.txt`/venv |
| `models/elastic_net.py` | `ElasticNetModel` | Elastic-net control model | ✅ works |
| `models/ensemble.py` | `EnsembleModel` | Weighted XGB+ElasticNet+ARIMA | ✅ works |
| `rag/agents.py` | `CentralBankRAGEngine` | Fed/BoJ sentiment | ⚠️ keyword-dictionary scorer, not real RAG |
| `research_gate/gate.py` | `ResearchGate` | 4-gate approval | ✅ works (robustness branch still keys on absent `sharpe_net`) |
| `research_gate/real_gate.py` | `RealResearchGate` | Gate over `ModelEvaluator` | ⚠️ works, inherits evaluator caveats |
| `research_gate/full_gate.py` | `FullResearchGate` | Full approve/reject pipeline | ⚠️ **unblocked** (broken `evaluate()` fixed) but still passes `features={}` placeholder for leakage |

**Bottom line:** Layer 3's two confirmed NameError bugs are fixed and the live `model_comparison` route works end-to-end. Remaining red: `run_benchmarks.py` (stale attribute), hardcoded `run.py` experiments, and the ARIMA dependency gap.

### 5.1 Research Gate (root-level, NEW — outside `backend/`)

A standalone, script-driven research loop now exists at the repo root (not under `backend/`):

| Piece | File(s) | Role | Status |
| --- | --- | --- | --- |
| Validation engine | `research_validation_test.py`, `final_holdout.py`, `evaluate_all_pairs.py` | Purging 60/20/20 splits (train/val/test), LR+sigmoid, holdout summary | ✅ ran · outputs committed |
| Gate classifier | `research_gate.py` | RULES: val AUC>0.60, test AUC>0.60, drop<0.20, PR-AUC>0.50, calibrated Brier<0.40 | ✅ ran (criteria corrected in `fd87a17`) |
| Outputs | `research_gate_results.json` (v1) / `research_gate_results_v2.json` (v2, untracked) | Classify CANDIDATES = USD/BOB 20d, EUR/USD 10d | **v1:** BOB=CANDIDATE, EUR=REJECTED · **v2 (corrected):** BOB=CANDIDATE_WITH_WARNINGS (cal Brier 0.636>0.40), EUR=CANDIDATE (no warnings) |
| Candidates | `train_experimental_models.py` → `models/experimental/{EUR_USD/h10, USD_BOB/h20}/` | Logistic + sigmoid-calibrator, purged protocol, 23 features, 300–309 samples | ✅ persisted with `metadata.json` (status EXPERIMENTAL) |

Caveats: PR-AUC is a documented rule but is *not actually computed* (the code notes "no está en el CSV, lo calculamos aparte"), and no experimental model is registered in the API registry (`backend/models/registry.json`) — `models/experimental/` is entirely unconsumed by the running app.

---

## 6. Backend — Layer 4 data-quality layer (NEW, `backend/layer4/`)

Unchanged this cycle.

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `quality/pit_validator.py` | `PITValidator` (PIT-1…PIT-7) | Feature-snapshot Point-in-Time compliance | ✅ implemented and correct (verified vs datasets A–D, exercised by `test_pit_adversarial.py`) |
| `config/policies.py` | policies + `ConfigRegistry` | Versioned data-source/feature/target config | ✅ implemented, **standalone** — referenced nowhere |
| `lineage/models.py` | lineage classes | Provenance/audit records | ✅ implemented, **standalone** — referenced nowhere |
| `tests/pit_tests.py` | layer-4 unit tests | PITValidator tests | ❌ still **syntactically corrupted** (won't parse) |

**Live wiring:** only `backend/tests/test_pit_adversarial.py` exercises `PITValidator`. Runtime forecast paths still don't validate PIT.

---

## 7. Frontend — contract-driven dashboard (React + TypeScript)

Stack unchanged (**React 18 + TS + Vite 5174 + Tailwind + TanStack Query + axios + date-fns + React Router + Recharts**).

### 7.1 Routes & composition (16 hook modules)

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/models` | ModelComparisonPage | `useModelComparison` → `GET /v1/fx/{pair}/model-comparison` |
| `/about` | AboutPage | (narrative) |

New this cycle: `common/MarketConvention.tsx`, `constants/fxPairs.ts` (fixed pair order + market-convention labels), `UniverseSelector` refactor, `useActivePair` simplified to a fixed universe (`pairUniverseFromRanking()` now ignores its argument). Still-dead: `useFanChartData.ts`, orphaned `HistoricalPage.tsx`, duplicate `common/Header.tsx` vs `layout/Header.tsx`, `mockup/*`, `useHistorical`/`useIntegrity`-adjacent orphans.

### 7.2 Presentational surface

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, **MarketConvention** (NEW), *duplicate* `Header`), `global/*`, `forecast/*`, `drivers/*`, `evaluation/*`, `status/*`, `layout/*`, `macro/*`, `mockup/*`.

### 7.3 Verification — the red moved, and broke the compile

| Check | Previous report (09-04) | Now (09-05) |
| --- | --- | --- |
| Backend pytest | 103 passed | **103 passed** ✅ (12 files) |
| Frontend typecheck | clean | ❌ **FAILS** — `UniverseSelector`/`useActivePair` refactor left ~20 errors across 6 pages, `MarketConvention`, `useActivePair.test.tsx` |
| Frontend tests | 45 passed / 10 FAILED | **53 passed / 2 FAILED** — `format.test.ts` fixed (18 pass ✅); `useActivePair.test.tsx` now red (references removed `DEFAULT_PAIR_UNIVERSE`, calls `pairUniverseFromRanking(arg)` with 0-arg function) |
| Frontend build | OK | ❌ **FAILS** (same type errors) |

**Root cause of the compile break:** commit `9d0b62f` changed `UniverseSelector` to drop the `currencies` prop and made `pairUniverseFromRanking()` take no arguments, but never updated the six pages that pass `currencies={...}` (Global, Forecast, Drivers, Evaluation, Price, ModelComparison), the `useActivePair` test, or the `React`/`FX_PAIR_LABELS` unused-import lint in the two new files. The trunk no longer compiles; the production build is broken at source.

---

## 8. Models & training

- **Production registry** (`backend/models/registry.json`): **10 registered, all `active: true`**, all `v1.0` — 9 XGBoost (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) + 1 logistic (USD/JPY). Current metrics (in-registry): AUC range **0.380–0.733** — best USD/CHF **0.733**; worst USD/CNY **0.380**; USD/JPY xgboost 0.408 vs logistic 0.448 (logistic still better); EUR/USD 0.45, GBP/USD 0.43, USD/MXN 0.437, USD/BRL 0.520, USD/ARS 0.513, USD/BOB 0.437. `train_models.py` remains the XGBoost trainer.
- **Experimental candidates** (`models/experimental/`, NOT in the production registry): **USD/BOB 20d** → CANDIDATE_WITH_WARNINGS (val AUC 0.674, test AUC 0.917, calibrated Brier 0.636 > 0.40 threshold) and **EUR/USD 10d** → CANDIDATE (val AUC 0.780, test AUC 0.869, calibrated Brier 0.237) under the v2 corrected gate criteria. Trained via `train_experimental_models.py` (logistic + sigmoid calibration, 60/20/20 purged protocol) — still **experimental**: not wired into `engine.py`, the registry, or any router.
- `backend/layer2/models/` — `model_selector.py` + `registry_adapter.py` remain unwired; `trainer.py` still empty.

---

## 9. Deployment & operations

| Target | What | Evidence |
| --- | --- | --- |
| **Render** (backend) | Docker web service, `dockerfilePath: ./Dockerfile`, `/health`, `uvicorn layer1.main:app` :10000 | `render.yaml`; `Dockerfile` (python:3.12-slim, `PYTHONPATH=/app/backend`); env FRED/GROQ/ALPHA/TWELVE (`sync:false`) |
| **Cloudflare Pages** (frontend) | Static-site mode, `_headers` (X-Robots-Tag, ACAO), `_redirects` (`/* → /index.html 200`), `.cloudflareignore` | `frontend/_headers`, `_redirects` |
| **Vercel** (frontend) | Vite build → `dist`, SPA rewrites | `frontend/vercel.json` |
| **Local** | `backend/docker-compose.yml` — port 10000, mounts `./models` + `./cache` | — |

Operations caveats (updated):
- **`frontend/.env.production` was deleted in `ed4758c`.** The production API URL (`https://meridianfx.onrender.com`) is no longer referenced anywhere in the repo; `frontend/.env` now pins `VITE_API_URL`/`VITE_API_BASE_URL` to `http://localhost:8000`. A frontend build from this tree would call localhost. (`frontend/.env.local` also points at localhost:8000.)
- **Model resolution is CWD-relative and currently inconsistent** across local / docker: registry paths `models/*.pkl` resolve only if a `models/` dir exists at the process CWD. At the repo root, 3 of 9 XGBoost pairs 404 (§4.2); in the Render image (WORKDIR `/app`), the artifacts live at `/app/backend/models` and would need to be copied to `/app/models` (or the paths normalized) — unverified against the deployed image.
- `/v1/status` returned `HEALTHY` on a live smoke test; data fetches fell back Yahoo → Alpha Vantage successfully over the network during route tests.

---

## 10. Models of verification & governance (unchanged)

The repo is **prompt-first** (`docs/Prompts/`) and **Contract/** polices fidelity. Freeze artifacts unchanged: `CONTRACT_TRACEABILITY.md` (73-row, 61 verified / 12 gap), `CONTRACT_GAPS.md` (16 gaps), `FRONTEND_CONTRACT_FREEZE.md`, `CONTRACT_VALIDATION.md`, `MIGRATION_REPORT.md`, `COMPONENT_MAPPING.md`. Frozen specs: L1 v5.1 (frontend authority), L2 v3.4.1 (backend authority).

> **Not** pushed through the traceability → gaps → freeze loop: the Layer 3/4 code, the Model Comparison surface, the **new `/v1/market-intelligence` endpoint**, the **Research Gate/experimental-model pipeline**, and the frontend **fixed-universe/market-convention** changes.

---

## 11. Current status & known gaps

**Green**
- Backend pytest **103/103**; `/v1/status` live and `HEALTHY`.
- The three previously-500 routes are ported to the per-pair API and return 200 (drivers/price/model-comparison) — though two of them only for pairs whose model resolves.
- `walk_forward.evaluate()` NameError fixed.
- Frontend `format.test.ts` regression fixed (18/18 pass).
- Real Research Gate + purged candidate pipeline (USD/BOB 20d, EUR/USD 10d) with corrected v2 criteria; `models/experimental/` populated.
- `main` in sync with `origin/main`.

**Red / attention**
1. **Frontend does not compile** — `9d0b62f` shipped a `UniverseSelector`/`useActivePair`/`fxPairs` refactor without migrating 6 pages + a test: **`npm run typecheck` and `npm run build` fail**; 2 tests fail in `useActivePair.test.tsx`. This is the single most important issue (production build broken at source).
2. **Core-pair model resolution broken by CWD**: USD/JPY, EUR/USD, GBP/USD `.pkl` files only exist under `backend/models/`, so registry-relative paths miss from the repo root → `/drivers` 404s and `/price` loses the signal for exactly the 3 non-USD-quoted core pairs; the Render image has the same latent mismatch (WORKDIR `/app` vs `/app/backend/models`).
3. **`frontend/.env.production` deleted** — no repo-configured production API URL; default builds point at `localhost:8000`.
4. **`layer3/evaluation/run_benchmarks.py` still crashes** (`engine.xgb_model`); `experiments/run.py` E0–E7 still hardcoded; ARIMA unrunnable (`statsmodels` absent).
5. **Layer 4** still unwired (PIT only exercised in tests); `layer4/tests/pit_tests.py` won't parse.
6. **Hardcoded/simulated live endpoints persist**: `/forecast` (`FORECAST_DATA`), `/interpretation` (missing `layer1.services.macro_service` import → macro section fails), drivers `macro_drivers` (VIX 16.8 / Risk Appetite 72 / RISK_ON), FRED simulated without key.
7. **Research Gate caveats**: PR-AUC rule is declared but not computed; `models/experimental/` is unconsumed by the API; `research_gate_results_v2.json` is untracked.
8. **`src` decision engine still not wired to `layer2`/`layer1`** — 103 verified tests, zero runtime footprint.
9. **L3 registry schema** still incompatible with `backend/models/registry.json`.
10. **Contract-shape drift persists** in newer pages (`direction === 'UP'` derivations, VIX/riskAppetite/regime hardcodes, locally derived returns).
11. **Dead/stale artifacts persist** (HistoricalPage, FanChart/useFanChartData, WhyNow/DataTimestamps/ForecastHero, mockup/*, duplicate common/Header, empty trainer.py, dead layer2 adapters) **plus new** committed clutter: `ngrok-stable-linux-amd64.zip` (13.9 MB), `commandos.md`, `start_backend.sh`, `VERSION*.txt`, `*.bak`/`*.backup` (re-introduced in `c06e357`).
12. **`EconomicInterpreter` never invokes the LLM chain** (rule-based primary).
13. **Bundle size** 1,397 kB minified; warning threshold raised instead of code-splitting.

---

## 12. Recommendations

1. **Fix the frontend compile immediately (top priority).** Either restore the `currencies` prop / `DEFAULT_PAIR_UNIVERSE` and old `pairUniverseFromRanking(ranking)` signature, or migrate the six pages (Global, Forecast, Drivers, Evaluation, Price, ModelComparison) + `useActivePair.test.tsx` and remove the unused-`React`/`FX_PAIR_LABELS` imports. Then re-run `npm run typecheck` and `npm run build` before the next commit.
2. **Decide the model-path convention.** Normalize registry paths to be repo-root-relative (`backend/models/…`) or make `_get_model_for_pair` resolve against both `models/` and `backend/models/`; copy `backend/models` → `/app/models` (or fix paths) in the Docker image; add a union test asserting all 9 pairs resolve. This unblocks the 404s on USD/JPY, EUR/USD, GBP/USD.
3. **Restore a production API URL for the frontend** — re-add `frontend/.env.production` with `VITE_API_URL=https://meridianfx.onrender.com` (or wire env at the deploy platform) so production builds don't silently target localhost.
4. **Close the Layer 3 tail**: port `run_benchmarks.py` to `_get_model_for_pair`, delete/harden the hardcoded `run.py` experiments, add `statsmodels` if ARIMA is wanted, and either repair `layer4/tests/pit_tests.py` or fold PIT tests into `backend/tests/`.
5. **Finish real-data migration** (§6 of last report): replace `FORECAST_DATA` in `/forecast`/`/interpretation`, fix the `macro_service` import, wire `FRED_API_KEY` in Render, and replace the hardcoded drivers `macro_drivers`.
6. **Wire the intended integrations**: `layer2.engine.py` → PIT adapter before caching; `model_comparison` as the L3 showcase; reconcile L3 artifact registry schema with `backend/models/registry.json`; decide whether `models/experimental/` candidates graduate into the production registry (with real thresholds) or stay gated.
7. **Repair git hygiene**: commit or gitignore `research_gate_results_v2.json`; delete the 13.9 MB `ngrok-*.zip`, `commandos.md`, `start_backend.sh`, `VERSION*.txt`, and `*.bak`/`*.backup` litter.
8. **Push the new surfaces through governance** (Model Comparison, Layer 3/4, `/v1/market-intelligence`, Research Gate pipeline, fixed-universe UI) — traceability → gaps → freeze → validation.
9. **Re-run the audit loop** after the compile fix, and consider code-splitting the 1.4 MB bundle.