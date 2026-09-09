# Meridian FX — Repository Report

**Date:** 2026-09-09 · **Branch:** `main` (in sync with `origin/main`) · **History:** 95 commits (2026-08-25 → 2026-09-09) · **Head commit:** `cac4721` "feat: MeridianFX v2.0 estable — Logistic_24 para 9 pares" · **Latest tag:** `v2.0-estable` (Logistic_24, 2026-09-09)

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

### What changed since the last report (2026-09-05)

This cycle (2026-09-05 → 2026-09-09, 21 commits, tagged `v2.3.5-experimental-20260905` → `cac4721` "v2.0 estable") was dominated by **canonical-model productionization, macro-provider expansion, and a big research/walkforward push**:

1. **Logistic_24 canonical models shipped (the headline).** `cac4721`/`7b972dd`/`2f6a3a4` train and persist **Logistic_24 models in `models/canonical/`** — **10 `.joblib` artifacts + 2 metadata files** (per-pair Logistic_24 across the USD-pair universe plus extended variants), with **PIT `policy_diff` integration** and training metadata. This is the self-declared "v2.0 estable" deliverable. Training scripts: `train_canonical_model.py`, `train_canonical_model_extended.py`, `train_multi_pairs.py`. A model-selection report was added at `docs/model_selection/2026-09-08_model_selection_logistic_vs_xgboost.md` (`76664b5`). The canonical models live at the repo root (`models/canonical/`), **not** in `backend/models/registry.json` — distinct from the 6/9 XGBoost production registry. ✅
2. **Canonical DecisionPipeline wired (partially).** `6c11bc8` + `c529efe` add **`backend/layer1/routers/canonical.py`** (`GET /v1/canonical/{pair}/decision`) and **`backend/layer2/pipeline_bridge.py`**, connecting the contract-governed `src/meridian_fx/decision/` pipeline to Layer 2 data via `CanonicalMacroAdapter`, `MacroDifferentialProvider`, and `MacroDifferentialStatus` (traceability). **Caveat:** the pipeline currently runs against **fake providers** (`FakeFeatureStore`, `FakeDataQualityRegistry`) — the routing/plumbing is real, the live-data feed is not. 🟡
3. **Country Macro Providers v2.5.** `500b093` + `ab593e9` + `9462590` expand `backend/layer2/data/macro/providers/` to **21 country/indicator providers (~2065 lines)** — ECB, PBoC, BoJ, SNB, World Bank, Investing.com, Trading Economics, policy-rate chain, SOFR, CNBS, etc. — plus `differential_provider.py` and `required_data_missing` enum reflecting FULL/PARTIAL macro state. `docs/MACRO_COVERAGE.md` added as a coverage/traceability baseline. `test_canonical_macro_adapter.py` extends the suite to 13 files. ✅
4. **Research/walkforward bundle (repo root).** A deep study suite: `research_walkforward.py` + **8 specialized scripts** (`_models`, `_macro`, `_pit`, `_xgb_macro_pit`, `_inflation`, `_lag`, `_nonoverlap`, `_head_to_head`) each generating `research_walkforward_{...}_results.json`; **shadow testing** (`shadow_test.py`, `shadow_test_simple.py` → `shadow_test_results_*.json`, PIT + non-PIT); **monitoring** (`monitor_daily.py`, `monitor_model.py`). These are research artifacts, not wired into the API. ✅
5. **Frontend Spanish backup committed.** `cac4721` commits `frontend/src_backup_espanol/` (~130 files) — a full Spanish-language copy of the frontend tree, adding to the committed-clutter inventory. ⚠️
6. **Untouched red items from last cycle:** the frontend compile break from `9d0b62f` **is still present** (typecheck/build/2 tests red) — none of this cycle's commits touched the six un-migrated pages. `run_benchmarks.py` still crashes, `layer4/tests/pit_tests.py` still won't parse, `/forecast` + `/interpretation` still use `FORECAST_DATA`, `frontend/.env.production` still deleted, and the repo-root `models/` still only has 6 of 9 XGBoost `.pkl` files (CWD-relative registry paths → `/drivers` 404 for USD/JPY, EUR/USD, GBP/USD).
7. **Version bookkeeping is noisy.** VERSION tags jumped `v2.3.5-experimental-20260905` → `v2.0-estable`, while `VERSION_STABLE.txt` still reads `v2.3.2-estable-20260905`; multiple `*_backup_espanol`, `.bak`, `.backup`, `.bak_intelligence`, `.bak_before_path_fix`, `.backup_pair` files accumulate.

**Balance sheet:** the headline gain is the canonical Logistic_24 productionization (10 `.joblib` models, PIT-aware) and the first real plumbing of the contract-governed decision engine into the API. The costs: an even larger pile of ungoverned research scripts/artifacts, a committed Spanish-backup frontend tree, and the continued frontend compile break at source.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs, prompts, and contract governance (Domain / HLD / LLD / Product_specification / Contract / Prompts / model_selection)
├── backend/                     Python backend
│   ├── layer1/                  FastAPI delivery API — implemented (12 routers incl. canonical, models, adapters, LLM, decision, INTELLIGENCE)
│   ├── layer2/                  Live engine — XGBoost/Logistic/SHAP/data providers/FRED macro/status/ranking/pipeline_bridge
│   ├── layer3/                  Research layer — artifacts, evaluation, experiments, models, macro regime, RAG, research gate
│   ├── layer4/                  Data-quality layer — PIT validator, config policies, lineage
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, tests)
│   ├── models/                  Trained XGBoost/logistic .pkl + models/registry.json (10 models) + models/experimental/
│   ├── tests/                   Backend pytest suite (13 files)
│   ├── pyproject.toml           Backend project config (pythonpath=src, pytest)
│   └── requirements.txt         Backend dependency manifest
├── models/canonical/            NEW — Logistic_24 canonical models (10 .joblib + metadata) (v2.0 estable)
├── Dockerfile                   Render container (python:3.12-slim, uvicorn layer1.main:app, port 10000)
├── render.yaml                  Render blueprint (docker web service, free plan, /health)
├── runtime.txt                  Python 3.12.0 pin for Render
├── backend/docker-compose.yml   Local docker-compose (port 10000)
├── train_models.py              XGBoost training script (registers into ModelRegistry)
├── train_experimental_models.py Logistic + sigmoid candidates (models/experimental/)
├── train_canonical_model.py     NEW — canonical Logistic_24 training
├── train_canonical_model_extended.py  NEW — extended canonical training
├── train_multi_pairs.py         NEW — multi-pair canonical training (9 pairs)
├── evaluate_all_pairs.py · final_holdout.py · research_validation_test.py  Validation scripts
├── research_gate.py             Research Gate v2 classifier (AUC / PR-AUC / calibrated Brier)
├── research_gate_results.json · research_gate_results_v2.json  Gate outputs
├── research_walkforward.py      NEW — walkforward research (base)
├── research_walkforward_*.py    NEW — 8 specialized walkforward studies (models/macro/pit/xgb_macro_pit/inflation/lag/nonoverlap/head_to_head)
├── research_walkforward_*_results.json  NEW — walkforward outputs
├── shadow_test.py · shadow_test_simple.py  NEW — shadow testing (PIT + non-PIT)
├── monitor_daily.py · monitor_model.py  NEW — monitoring scripts
├── research_validation_results.json · research_validation_summary.csv · final_holdout_results.csv  Outputs
├── models/experimental/         Experimental candidates: EUR/USD h10 · USD/BOB h20
├── models/                      Root-level model artifacts (6 of 9 XGBoost .pkl + canonical/ + experimental/)
├── test_macro.py                MacroService tests
├── frontend/                    React + TypeScript + Vite contract-driven dashboard (+ Recharts)
│   ├── .env                     VITE_API_URL=VITE_API_BASE_URL=http://localhost:8000 — NO .env.production (deleted)
│   ├── vercel.json · _headers · _redirects   SPA routing for Cloudflare Pages / Vercel
│   ├── src/                     pages, hooks (19), components, utils, tests
│   └── src_backup_espanol/      NEW — full Spanish-language frontend backup (~130 files)
├── .env                         Runtime secrets + config (keys: FRED, GROQ, ALPHA_VANTAGE, TWELVE_DATA, OPENAI, CLOUDFLARE, …)
├── vite.config.ts               Frontend Vite config (port 5174, minify off, chunk limit 1000)
├── README.md                    Product overview + quickstart
├── ngrok-stable-linux-amd64.zip (13.9 MB — accidentally committed in c06e357)
├── commandos.md · start_backend.sh · VERSION*.txt · *.bak / *.backup files   (committed clutter)
├── report.md                    This document
└── architecture.md              System architecture
```

> **Working-tree hygiene:** `main` is in sync with `origin/main` (0 ahead / 0 behind). The dirty entries remain runtime cache churn (`cache/forecast_cache.json`, `cache/macro/`), `research_gate_results_v2.json` (untracked) — plus this cycle added **`frontend/src_backup_espanol/`** (committed), `requirements-stable-v2.0.txt`, `monitor_history.json`, multiple `.bak`/`.backup` files (`main.py.bak_intelligence`, `canonical.py.backup_before_path_fix`, `drivers.py.backup_pair`, `useActivePair.ts.backup`, `walk_forward.py.backup`, `index.html.backup`), and the 13.9 MB `ngrok-*.zip` persists.

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

`backend/layer1/` is a **real FastAPI app** (`main.py`, "Meridian FX API" v1.0.0). CORS covers localhost, Render, Vercel, Cloudflare Pages, ngrok (`*.ngrok-free.dev`) and `*`. **12 routers** plus `/` and `/health`.

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
| GET | `/v1/canonical/{pair}/decision` | **NEW** — contract-governed `DecisionPipeline` via `PipelineBridge` (fake providers) | ✅ — 200 |

> The `/v1/fx/macro/status` and `/v1/fx/macro/refresh` endpoints remain removed (interpretation router exposes only `/interpretation`).

### 4.2 DecisionEngine refactor — consumers now ported; path resolution is the new fault line

All four stale consumers from last cycle were updated to the per-pair API:

- `routers/drivers.py` → route changed to `/{base}/{quote}/drivers`, calls `engine._get_model_for_pair(pair, "xgboost")` → **200 with SHAP** when the model loads. If the model does **not** load it returns the new 404 path ("Model not found for …") — i.e. the 500 is gone, and the 404 is now a *live symptom* of the path issue below.
- `routers/model_comparison.py` → uses `engine._get_model_for_pair(...)` for xgboost/logistic → **200** (verified; ensemble now reported as `"available": false` / `evaluation: not_implemented`, `best_model` chosen by Sharpe).
- `routers/price.py` → guards on `xgb_model.model` from `_get_model_for_pair` → **200 with real prediction** when the model resolves.
- `layer3/evaluation/run_benchmarks.py` → **still broken**: it reads `engine.xgb_model` (removed attribute) and crashes at call time.

**Path-resolution fault line (NEW, live):** the registry stores CWD-relative paths like `models/xgboost_USD_JPY_v1.0.pkl`. From the repo root, `backend/models/registry.json` lists 10 models but only 6 of the 9 XGBoost `.pkl` files exist in the repo-root `models/` folder — USD/JPY, EUR/USD, and GBP/USD artifacts live only under `backend/models/`. Consequently `_get_model_for_pair` returns `None` for exactly those three (verified: `/drivers` → 404), i.e. **the three non-USD-quoted core pairs have no live signal**. In the Render container (WORKDIR `/app`, registry path `models/…` → `/app/models` which doesn't exist) this would disable model resolution for *all* pairs unless the deploy copies `backend/models` to `/app/models`.

### 4.3 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–§7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter`; **`adapters/decision_engine_adapter.py`** (engine → response shaping).
- **`decision/`** — `decision_context.py`, `economic_filter.py`, `signal_validity.py`.
- **`llm/`** — providers/manager/interpreter; `EconomicInterpreter` still resolves via the rule-based fallback; the LLM chain is still not actively invoked.
- **`routers/intelligence.py`** — `/v1/market-intelligence` (English narrative; purely deterministic over `RankingEngine.get_ranking()`).
- **`routers/canonical.py`** **NEW** — `/v1/canonical/{pair}/decision`; instantiates the contract-governed `DecisionPipeline` and serves decisions through `PipelineBridge` (layer2 → `src` decision engine). **Currently the pipeline is constructed with `FakeFeatureStore`/`FakeDataQualityRegistry`/`FakeFreshnessRegistry`/`FakeDriftRegistry`, so the feed is not live.**
- **`layer2/pipeline_bridge.py`** **NEW** — builds `PipelineInputs` (prediction artifact, macro regime, differential status via `CanonicalMacroAdapter` + `MacroDifferentialProvider`) and exposes traceability for `required_data_missing` (FULL/PARTIAL).

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

### 5.2 Canonical-model research, walkforward & shadow testing (repo root, NEW this cycle)

| Piece | File(s) | Role | Status |
| --- | --- | --- | --- |
| Canonical training | `train_canonical_model.py`, `train_canonical_model_extended.py`, `train_multi_pairs.py` | Train Logistic_24 per-pair models with PIT `policy_diff` | ✅ `models/canonical/` (10 `.joblib` + metadata, 2026-09-08/09) |
| Model selection doc | `docs/model_selection/2026-09-08_model_selection_logistic_vs_xgboost.md` | Logistic vs XGBoost selection rationale | ✅ committed (`76664b5`) |
| Walkforward studies | `research_walkforward.py` + 8 variants (`_models`, `_macro`, `_pit`, `_xgb_macro_pit`, `_inflation`, `_lag`, `_nonoverlap`, `_head_to_head`) | A/B and head-to-head walkforward experiments | ✅ ran · `research_walkforward_*_results.json` outputs |
| Shadow testing | `shadow_test.py`, `shadow_test_simple.py` | Live-shadow evaluation (PIT + non-PIT) | ✅ `shadow_test_results_*.json` (2026-09-08) |
| Monitoring | `monitor_daily.py`, `monitor_model.py` | Per-model/daily monitoring hooks | ✅ scripts only |
| Deps pin | `requirements-stable-v2.0.txt` | Stable dependency manifest | ⚠️ duplicate of `backend/requirements.txt` |

> These are **research artifacts** — none are wired into the API or layer2 runtime.

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

### 7.1 Routes & composition (19 hook modules)

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

New this cycle (09-05): `common/MarketConvention.tsx`, `constants/fxPairs.ts` (fixed pair order + market-convention labels), `UniverseSelector` refactor, `useActivePair` simplified to a fixed universe. New this cycle (09-05→09-09): `ForecastPageCanonical.tsx` + `useCanonicalDecision` (canonical fan-chart page) from `6c11bc8`, `ForecastCard`/`RankingCard`/`RankingTable`/`ActionableInfo`/`MacroPanel`/`PricePage`/`GlobalPage` touched by `cac4721`, and the full **Spanish-language backup tree `frontend/src_backup_espanol/`** (~130 files) committed. Still-dead: `useFanChartData.ts`, orphaned `HistoricalPage.tsx`, duplicate `common/Header.tsx` vs `layout/Header.tsx`, `mockup/*`, `useHistorical`-adjacent orphans.

### 7.2 Presentational surface

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, **MarketConvention** (NEW), *duplicate* `Header`), `global/*`, `forecast/*`, `drivers/*`, `evaluation/*`, `status/*`, `layout/*`, `macro/*`, `mockup/*`.

### 7.3 Verification — frontend still red at source

| Check | Previous report (09-05) | Now (09-09) |
| --- | --- | --- |
| Backend pytest | 103 passed | **103 passed** ✅ (13 files — added `test_canonical_macro_adapter.py`) |
| Frontend typecheck | ❌ FAILS | ❌ **FAILS (unchanged)** — `UniverseSelector`/`useActivePair` refactor left ~20 errors across 6 pages, `MarketConvention`, `useActivePair.test.tsx` |
| Frontend tests | 53 passed / 2 FAILED | **53 passed / 2 FAILED (unchanged)** |
| Frontend build | ❌ FAILS | ❌ **FAILS (unchanged)** |

**Root cause (unchanged):** commit `9d0b62f` changed `UniverseSelector` to drop the `currencies` prop and made `pairUniverseFromRanking()` take no arguments, but never updated the six pages that pass `currencies={...}` (Global, Forecast, Drivers, Evaluation, Price, ModelComparison), the `useActivePair` test, or the `React`/`FX_PAIR_LABELS` unused-import lint in the two new files. **No commit since `9d0b62f` has touched the six callers — the trunk still fails to compile at source.**

---

## 8. Models & training

- **Production registry** (`backend/models/registry.json`): **10 registered, all `active: true`**, all `v1.0` — 9 XGBoost (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) + 1 logistic (USD/JPY). Current metrics (in-registry): AUC range **0.380–0.733** — best USD/CHF **0.733**; worst USD/CNY **0.380**; USD/JPY xgboost 0.408 vs logistic 0.448 (logistic still better); EUR/USD 0.45, GBP/USD 0.43, USD/MXN 0.437, USD/BRL 0.520, USD/ARS 0.513, USD/BOB 0.437. `train_models.py` remains the XGBoost trainer.
- **Canonical Logistic_24 models (NEW, v2.0 estable):** `models/canonical/` holds **10 `.joblib` models + metadata** (`logistic_24_*_20260908/09_*.joblib`), per-pair Logistic_24 for the USD-pair universe plus aggregate/extended variants, trained with **PIT `policy_diff`** via `train_canonical_model.py` / `train_canonical_model_extended.py` / `train_multi_pairs.py`. Analysis documented in `docs/model_selection/2026-09-08_model_selection_logistic_vs_xgboost.md`. **These are NOT in `backend/models/registry.json`** and are not loaded by `_get_model_for_pair` — they are artifacts of the canonical-research track.
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

The repo is **prompt-first** (`docs/Prompts/`) and **Contract/** polices fidelity. Freeze artifacts unchanged: `CONTRACT_TRACEABILITY.md` (73-row, 61 verified / 12 gap), `CONTRACT_GAPS.md` (16 gaps), `FRONTEND_CONTRACT_FREEZE.md`, `CONTRACT_VALIDATION.md`, `MIGRATION_REPORT.md`, `COMPONENT_MAPPING.md`. Frozen specs: L1 v5.1 (frontend authority), L2 v3.4.1 (backend authority). **NEW this cycle:** `docs/MACRO_COVERAGE.md` (macro provider coverage + traceability baseline) and `docs/model_selection/2026-09-08_model_selection_logistic_vs_xgboost.md`.

> **Not** pushed through the traceability → gaps → freeze loop: the Layer 3/4 code, the Model Comparison surface, the `/v1/market-intelligence` endpoint, the **canonical router + `pipeline_bridge`**, the **Country Macro Providers v2.5**, the **canonical Logistic_24 models** (`models/canonical/`), the **walkforward research bundle + shadow tests**, the Research Gate/experimental-model pipeline, and the frontend fixed-universe/market-convention changes.

---

## 11. Current status & known gaps

**Green**
- Backend pytest **103/103** (13 files); `/v1/status` live and `HEALTHY`.
- **Canonical Logistic_24 productionization**: 10 `.joblib` models across the USD-pair universe with PIT `policy_diff` (`models/canonical/`, v2.0 estable) + model-selection doc.
- **Canonical DecisionPipeline wired into the API** (`/v1/canonical/{pair}/decision`) via `pipeline_bridge.py` — routing + traceability real (feed still fake-provider).
- **Country Macro Providers v2.5**: 21 providers (~2065 lines), `required_data_missing` FULL/PARTIAL, `docs/MACRO_COVERAGE.md`.
- Walkforward research bundle (9 scripts + results), shadow testing (`shadow_test*.py`), and monitoring hooks added.
- Real Research Gate + purged candidate pipeline (USD/BOB 20d, EUR/USD 10d) with corrected v2 criteria; `models/experimental/` populated.
- The three previously-500 routes return 200 (drivers/price/model-comparison); `walk_forward.evaluate()` NameError fixed; `format.test.ts` green.
- `main` in sync with `origin/main`.

**Red / attention**
1. **Frontend does not compile (unchanged, top priority)** — `9d0b62f` shipped a `UniverseSelector`/`useActivePair`/`fxPairs` refactor without migrating 6 pages + a test: **`npm run typecheck` and `npm run build` fail**; 2 tests in `useActivePair.test.tsx`. No commit since has touched the callers — the production build is still broken at source.
2. **Core-pair model resolution broken by CWD**: USD/JPY, EUR/USD, GBP/USD `.pkl` files only exist under `backend/models/`, so registry-relative paths miss from the repo root → `/drivers` 404s and `/price` loses the signal for exactly the 3 non-USD-quoted core pairs; the Render image has the same latent mismatch (WORKDIR `/app` vs `/app/backend/models`).
3. **`frontend/.env.production` deleted** — no repo-configured production API URL; default builds point at `localhost:8000`.
4. **`layer3/evaluation/run_benchmarks.py` still crashes** (`engine.xgb_model`); `experiments/run.py` E0–E7 still hardcoded; ARIMA unrunnable (`statsmodels` absent).
5. **Layer 4** still unwired (PIT only exercised in tests); `layer4/tests/pit_tests.py` won't parse.
6. **Hardcoded/simulated live endpoints persist**: `/forecast` (`FORECAST_DATA`), `/interpretation` (missing `layer1.services.macro_service` import → macro section fails), drivers `macro_drivers` (VIX 16.8 / Risk Appetite 72 / RISK_ON), FRED simulated without key.
7. **Research Gate caveats**: PR-AUC rule is declared but not computed; `models/experimental/` unconsumed by the API; `research_gate_results_v2.json` untracked.
8. **Canonical pipeline runs on fake providers** — `/v1/canonical/{pair}/decision` works but feeds `FakeFeatureStore`/`FakeDataQualityRegistry`; the `src` decision engine still has zero live-data footprint.
9. **L3 registry schema** still incompatible with `backend/models/registry.json`.
10. **Contract-shape drift persists** in newer pages (`direction === 'UP'` derivations, VIX/riskAppetite/regime hardcodes, locally derived returns).
11. **Dead/stale artifacts + clutter accumulate**: `frontend/src_backup_espanol/` (~130 committed backup files), `*.bak`/`*.backup`/`.bak_*`/`.backup_*` litter, orphaned `HistoricalPage.tsx`, unused `FanChart`/`useFanChartData`/`WhyNow`/`DataTimestamps`/`ForecastHero`/`mockup/*`/duplicate `common/Header.tsx`, empty `trainer.py`, dead `layer2` adapters, `ngrok-stable-linux-amd64.zip` (13.9 MB), `commandos.md`, `start_backend.sh`, `VERSION*.txt`.
12. **`EconomicInterpreter` never invokes the LLM chain** (rule-based primary).
13. **Bundle size** 1,397 kB minified; warning threshold raised instead of code-splitting.
14. **Research sprawl** — 9 walkforward scripts + shadow tests + 20+ result JSON/CSV outputs committed at repo root with no single orchestrator or governance entry; `requirements-stable-v2.0.txt` duplicates `backend/requirements.txt`.

---

## 12. Recommendations

1. **Fix the frontend compile immediately (top priority, unchanged).** Either restore the `currencies` prop / `DEFAULT_PAIR_UNIVERSE` and old `pairUniverseFromRanking(ranking)` signature, or migrate the six pages (Global, Forecast, Drivers, Evaluation, Price, ModelComparison) + `useActivePair.test.tsx` and remove the unused-`React`/`FX_PAIR_LABELS` imports. Then re-run `npm run typecheck` and `npm run build` before the next commit.
2. **Decide the model-path convention (unchanged).** Normalize registry paths to be repo-root-relative or make `_get_model_for_pair` resolve against both `models/` and `backend/models/`; copy `backend/models` → `/app/models` in the Docker image; add a union test asserting all 9 pairs resolve. This unblocks the 404s on USD/JPY, EUR/USD, GBP/USD.
3. **Restore a production API URL for the frontend (unchanged)** — re-add `frontend/.env.production` with `VITE_API_URL=https://meridianfx.onrender.com` so production builds don't silently target localhost.
4. **Give the canonical pipeline real providers.** Replace `FakeFeatureStore`/`FakeDataQualityRegistry` in `canonical.py`/`pipeline_bridge.py` with the real `MacroDifferentialProvider` + PIT-backed registries, then decide whether the canonical Logistic_24 models (`models/canonical/`) graduate into `backend/models/registry.json` (with live thresholds) or stay as a research track. Wire them into `_get_model_for_pair` for the `/v1/canonical` and `forecast-dashboard` surfaces.
5. **Consolidate the research sprawl.** Add a single orchestrator (or a `Makefile`/script) that runs the walkforward suite + shadow tests and writes to a `research/outputs/` dir; commit or gitignore the individual `research_walkforward_*_results.json` / `shadow_test_*.json` outputs; reconcile `requirements-stable-v2.0.txt` with `backend/requirements.txt`.
6. **Close the Layer 3 tail (unchanged):** port `run_benchmarks.py` to `_get_model_for_pair`, delete/harden the hardcoded `run.py` experiments, add `statsmodels` if ARIMA is wanted, and repair `layer4/tests/pit_tests.py`.
7. **Finish real-data migration (unchanged):** replace `FORECAST_DATA` in `/forecast`/`/interpretation`, fix the `macro_service` import (or delete the macro branch), wire `FRED_API_KEY` in Render, and replace the hardcoded drivers `macro_drivers` — the v2.5 macro providers make most of this feasible now.
8. **Wire the intended integrations:** `layer2.engine.py` → PIT adapter before caching; reconcile L3 artifact registry schema with `backend/models/registry.json`; PIT + `pipeline_bridge` traceability for the canonical route.
9. **Repair git hygiene (bigger list now):** commit or gitignore `research_gate_results_v2.json`/`requirements-stable-v2.0.txt`/`monitor_history.json`; delete `frontend/src_backup_espanol/`, the 13.9 MB `ngrok-*.zip`, `commandos.md`, `start_backend.sh`, `VERSION*.txt`, and all `*.bak`/`*.backup`/`.bak_*`/`.backup_*` litter.
10. **Push the new surfaces through governance:** Model Comparison, Layer 3/4, `/v1/market-intelligence`, **canonical router + `pipeline_bridge`**, **Country Macro Providers v2.5**, **canonical Logistic_24 models**, **walkforward/shadow research**, Research Gate pipeline, fixed-universe UI — traceability → gaps → freeze → validation.
11. **Re-run the audit loop** after the compile fix, and consider code-splitting the 1.4 MB bundle.