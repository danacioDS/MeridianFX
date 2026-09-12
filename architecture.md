# Meridian FX — Architecture

**Date:** 2026-09-11

System architecture for the Meridian FX repo: a contract-driven FX intelligence product with a FastAPI delivery API (Layer 1, **11 routers incl. canonical decision + risk**), a live ML/decision engine (Layer 2, Logistic_24 + XGBoost, real-VIX canonical pipeline), research (Layer 3) and data-quality (Layer 4) codebases, a contract-verified decision engine (`src`, **132 tests, incl. Risk Assessment Engine**), a canonical DecisionPipeline wired via bridge (feature store now **real VIX**, quality registries still fake via TODO v2.7), a script-driven Research Gate + walkforward research suite (repo root), and a React dashboard (6 canonical pages: Global · Market · Macro · Risk · Decision), deployed in production (Render backend, Cloudflare Pages + Vercel frontend).

---

## 1. System context

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCT (9-pair universe · 30d horizon decisions/risk · 30/60/90d)    │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY · USD/MXN · USD/BRL · USD/ARS · USD/BOB · USD/CHF │
│                                                                                              │
│   ┌────────────────┐  delivery contracts (Layer 1 §7)   ┌───────────────────────┐            │
│   │   LAYER 1      │ ──────────────────────────────────▶ │  FRONTEND (React+TS) │            │
│   │ DELIVERY API   │  /v1/fx/ranking · price · forecast  │  Global · Market ·    │            │
│   │  (FastAPI, 11  │  /v1/fx/{pair}/forecast-dashboard   │  Macro · Risk ·       │            │
│   │   routers)     │  /v1/canonical/{pair}/decision|risk │  Decision · About     │            │
│   │  backend/layer1 │ /v1/fx/{pair}/model-comparison     │                       │            │
│   └───────┬────────┘  /v1/market-intelligence · /v1/status├───────────────────────┘            │
│           │  /v1/fx/interpretation · historical · performance                                 │
│           │  uses layer2 engine (+ layer3 via model-comparison, + src decision via pipeline_bridge) │
│   ┌───────▼──────────────────┐         ┌────────────────────────┐ ┌───────────────┐          │
│   │ LAYER 2  LIVE ENGINE     │         │ LAYER 3  RESEARCH       │ │ LAYER 4 DATA  │          │
│   │ backend/layer2:          │◀───────▶│ backend/layer3:        │ │  QUALITY      │          │
│   │ Logistic_24 canonical    │  + docs │ eval/walk_forward (fix) │ │ backend/layer4│          │
│   │ (_load_canonical_model)  │         │ benchmarks · arima/    │ │ PITValidator  │          │
│   │ XGBoost via registry     │         │ elastic_net/ensemble · │ │ (PIT-1..7) ·  │          │
│   │ SHAP · Yahoo→Alpha→Twelve│         │ macro regime · rag ·   │ │ config ·      │          │
│   │ FRED macro · ranking     │         │ research_gate          │ │ lineage       │          │
│   │   (60s cache) ·          │         │ run_benchmarks BROKEN  │ │               │          │
│   │ StatusEngine (/v1/status)│         │                        │ │               │          │
│   └──────────┬──────────────┘  (wired via model_comparison only) │               │          │
│              │  + src/meridian_fx/decision/ (contract-governed engine: 8-stage pipeline,     │
│              │    RiskEngine, RealFeatureStore VIX, 132 tests)                                │
│              │                                                                                │
│   RESEARCH (repo root): research_validation_test.py · final_holdout.py · research_gate.py     │
│              (AUC/PR-AUC/Brier v2) → models/experimental/ (EUR/USD h10 + USD/BOB h20)         │
│              research_walkforward_{models,macro,pit,xgb_macro_pit,inflation,lag,nonoverlap,   │
│              head_to_head}.py · shadow_test*.py · monitor_*.py  — NOT wired into Layer 1/2    │
│                                                                                                │
│   DEPLOY:  Render (Docker FastAPI+Uvicorn :10000, /health) · Cloudflare Pages + Vercel (SPA) │
│            FRED/GROQ/ALPHA/TWELVE keys via render.yaml; frontend/.env.production → onrender   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Key relationships:** Layer 1 consumes `layer2/` directly: per-pair models (canonical **Logistic_24** `.joblib` via `engine._load_canonical_model` + XGBoost via `registry.json`), the real `StatusEngine`, a **60s-cached RankingEngine**, and the **canonical pipeline** wired via `pipeline_bridge.py` (Layer 2 → `DecisionPipeline`). The canonical `/v1/canonical/{pair}/decision` and `/v1/canonical/{pair}/risk` routes run on **real VIX** (`RealFeatureStore`, Yahoo `^VIX`), real macro (FRED, simulated without key) and real Logistic_24 forecasts; the three **quality/freshness/drift registries are still fakes** (TODO v2.7). Every core endpoint was **live-verified 200** on 2026-09-11. Layer 3 is wired into the API **only** via `model_comparison` (working); `run_benchmarks.py` remains broken. Layer 4 runs **only** through tests. The `src` engine now also contains the **Risk Assessment Engine** (`/risk`). A `/drivers` router existed historically and was **removed** in v2.6.3 (hardcoded macro_drivers). The root-level Research Gate + walkforward bundle produces `models/canonical/` **and** `models/experimental/` candidates; the API loads the canonical Logistic_24 but never loads `models/experimental/`.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specs, prompts, contract governance, model_selection,
│                             MACRO_COVERAGE.md, DEUDA_TECNICA_v2.5.md (NEW)
├── backend/                  Python backend
│   ├── layer1/               FastAPI delivery API (11 routers incl. canonical decision+risk, intelligence,
│   │                         performance, price, forecast-dashboard, model-comparison; NO /drivers)
│   │                         + adapters/, llm/ (UNWIRED), decision/ (DEAD subsystem)
│   ├── layer2/               Live engine (engine.py: Logistic_24 loader + registry; data, features, models,
│   │                         explainers, macro, ranking w/ 60s cache, status, pipeline_bridge)
│   ├── layer3/               Research/evaluation layer (walk-forward, benchmarks, models, regime, RAG, gate)
│   ├── layer4/               Data-quality layer (PIT validator, config policies, lineage; pit_tests.py corrupt)
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, RiskEngine,
│   │                         RealFeatureStore, 132 tests)
│   ├── models/               models/registry.json + 10 .pkl (9 xgboost + 1 logistic) — normalized paths
│   ├── tests/                Backend pytest suite (13 files, 132 tests)
│   ├── pyproject.toml        Backend project metadata (pythonpath=src, pytest)
│   ├── requirements.txt      Backend dependency manifest
│   └── docker-compose.yml    Local compose (port 10000, mounts models/ + cache/)
├── models/                   Root-level artifacts: canonical/ (10 Logistic_24 .joblib + metadata),
│                             experimental/ (EUR/USD, USD/BOB), registry.json (== backend copy)
├── Dockerfile                Render container (python:3.12-slim, uvicorn layer1.main:app :10000)
├── render.yaml               Render blueprint (docker free web service, /health, env keys)
├── runtime.txt               Python 3.12.0 pin (repo root)
├── start.sh · stop.sh        Local runs (untracked + gitignored since a017cd7)
├── train_models.py · train_canonical_model{,_extended}.py · train_multi_pairs.py
├── train_experimental_models.py · evaluate_all_pairs.py · final_holdout.py
├── research_gate.py · research_gate_results{,v2}.json · research_validation_*  (NEW — unchanged)
├── research_walkforward.py + 8 specialized variants + *_results.json
├── shadow_test.py · shadow_test_simple.py · monitor_daily.py · monitor_model.py
├── scripts/audit_consistency.py    NEW — repo audit script
├── cache/ · logs/            Runtime state (gitignored)
├── frontend/                 Contract-driven React+TS dashboard (Cloudflare Pages + Vercel)
│   ├── .env.production       VITE_API_URL = https://meridianfx.onrender.com  (RESTORED, 2c0cbb9)
│   ├── src/pages/            Global · Market · Macro · Risk · Decision · About (6 canonical pages)
│   ├── src/hooks/            10 hooks (useCanonicalDecision, useCanonicalRisk, …)
│   ├── src/types/contracts.ts Layer 1 §7 mirror (+ canonical contracts in hooks)
│   └── .trash-v2.5/          Local archive (46 files, gitignored)
├── .env                      Runtime env (FRED/GROQ/ALPHA/TWELVE/OPENAI/CLOUDFLARE keys + config)
├── README.md                 Product overview + quickstart (stale: still claims v2.5.1)
├── report.md                 Repository analysis (2026-09-11)
└── architecture.md           This document
```

> **Hygiene (improved):** the v2.5.1 cleanup removed the committed clutter flagged in prior reports — `src_backup_espanol/`, `ngrok-*.zip` (13.9 MB), `commandos.md`, `start_backend.sh`, `VERSION*.txt`, all `*.bak`/`*.backup` files. Root/backend `models/registry.json` are byte-identical (10 entries, `backend/models/*.pkl` paths). Gitignored: `start.sh`/`stop.sh`, `venv/`, `cache/`, `logs/`, `frontend/.trash-v2.5/`.

---

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

**Entry:** `backend/layer1/main.py` — `FastAPI(title="Meridian FX API", version="1.0.0")`, CORS covering localhost/Render/Vercel/Cloudflare/ngrok/`*`. **11 routers** (12 − drivers) plus `/` and `/health`. Verified live via `TestClient` on 2026-09-11: all endpoints return 200.

### 3.1 Routers

| Router | Endpoint | Data source | Status |
| --- | --- | --- | --- |
| `ranking` | `GET /v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs, **60s in-memory cache** — v2.6) | ✅ live |
| `forecast` | `GET /v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` — **Logistic_24** → heuristic fallback (was `FORECAST_DATA`) | ✅ live (lineage block hardcoded `{type: logistic, version: v1.0}`) |
| `performance` | `GET /v1/fx/performance/{pair}?period=` | `models/registry.json` metrics + hardcoded derivations (`ece=0.05`, `max_drawdown=-0.06`, static `regime_performance`) | ✅ / ⚠️ derived |
| `status` | `GET /v1/status` | **real** — `layer2.status.engine.StatusEngine` (registry, live probes, LLM key checks) | ✅ `HEALTHY` |
| `intelligence` | `GET /v1/market-intelligence` | English narrative synthesis over `RankingEngine` (deterministic) | ✅ |
| `canonical` | `GET /v1/canonical/{pair}/decision` | `DecisionPipeline` via `pipeline_bridge.py` — **RealFeatureStore (VIX)** + 3 fake quality registries (TODO v2.7) | ✅ 200 — real per-pair decisions |
| `canonical` | `GET /v1/canonical/{pair}/risk` | **same bridge → `RiskEngine.compute`** (`src/.../risk/engine.py`) | ✅ 200 — real risk scores |
| `historical` | `GET /v1/fx/{pair}/historical?period=` | `layer2.DataProvider` + `TechnicalFeatures` (random-synthetic **fallback** on failure) | ✅ / ⚠️ fallback |
| `interpretation` | `GET /v1/fx/interpretation?pair=&include_macro=` | **inline rule-based narrative** over `get_forecast`; `include_macro=true` returns hardcoded `{"regime":"NEUTRAL","summary":"Contexto macro no disponible"}` | ⚠️ rule-based + hardcoded macro |
| `price` | `GET /v1/fx/{pair}/price?period=` | **live** spot/history; XGBoost signal via `_get_model_for_pair` (try/except → `UNKNOWN`) | ✅ live |
| `model_comparison` | `GET /v1/fx/{pair}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding`; in-memory `_comparison_cache`; ensemble `not_implemented`, best by Sharpe | ✅ 200 (slow 3y walk-forward) |
| `forecast_dashboard` | `GET /v1/fx/{pair}/forecast-dashboard` | **live** — provider + trends/volatility + Logistic_24/XGBoost via `DecisionEngine` 30/60/90d + FRED macro | ✅ network |

> **Removed:** `/drivers` (`GET /v1/fx/{base}/{quote}/drivers`) was **deleted in v2.6.3** (`82c9e80`) — router, frontend `services/drivers.ts`, and its hardcoded `macro_drivers` (VIX 16.8 / RA 72 / RISK_ON). `FORECAST_DATA` in `layer1/data/forecast_data.py` is now **dead code** (no imports). `/v1/fx/macro/status` and `/v1/fx/macro/refresh` remain removed.

### 3.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter` (`to_performance_response` used; `to_drivers_response` dead after `/drivers` removal).
- **`adapters/decision_engine_adapter.py`** — `DecisionEngineAdapter` (legacy `DecisionEngine.get_forecast` → canonical `PredictionArtifact`, braided with `MacroService`); used by `PipelineBridge`; `get_drivers()` dead.
- **`decision/`** — `decision_context.py` (incl. its own `DecisionEngine`), `economic_filter.py`, `signal_validity.py`: **standalone dead subsystem** (no router imports them).
- **`llm/`** — `GroqProvider` (real HTTP), `GLM/GeminiProvider` (NotImplementedError), `FallbackLLM`, `LLMFallbackManager`, `EconomicInterpreter`: the **entire LLM chain is unreachable** (no router imports it; `/interpretation` does its own inline narrative).
- **`routers/canonical.py`** — constructs `DecisionPipeline(feature_store=RealFeatureStore(), data_quality_registry=FakeDataQualityRegistry(0.90), freshness_registry=FakeFreshnessRegistry(3.0), drift_registry=FakeDriftRegistry(0.05))`. **VIX is real** (Yahoo `^VIX`, 60 s TTL, failure → `UNAVAILABLE`); the 3 L4 registries remain fakes.
- **`routers/__init__.py`** imports only `canonical` (side-effect: constructs the pipeline at import time).
- **`data/forecast_data.py`** — dead (`FORECAST_DATA` referenced by no code).

> **Live smoke (2026-09-11):** `/v1/canonical/EUR/USD/decision` → `actionable:True, SHORT, conf 0.66`; `GBP/USD` → `actionable:True, SHORT, conf 0.55`; `USD/JPY` → `INSUFFICIENT_EDGE`; `USD/CNY` → `MODEL_UNAVAILABLE` (data-dependent). `/v1/canonical/EUR/USD/risk` → `risk_level: MODERATE (30.5)`, drivers vol 8.76 / macro 0 / model 6.7 / regime 15 / edge, **real VIX 15.8**. These are genuine live pipeline outputs, not fixtures.

---

## 4. Layer 2 — live engine (`backend/layer2/`)

### 4.1 Data flow

```
DataProvider (Yahoo → Alpha Vantage → Twelve Data)
        │  get_historical(pair)
        ▼
TechnicalFeatures.generate(df) ── 23 features (+ policy_diff appended at runtime, PIT) ── get_feature_names()
        │  latest row
        ▼
DecisionEngine.get_forecast(pair)
   ├─ _get_model_for_pair(pair,'logistic')  → Logistic_24 canonical (engine._load_canonical_model,
   │    hardcoded 9-pair map → models/canonical/*.joblib)  ⚠️ CWD-sensitive
   ├─ else _get_model_for_pair(pair,'xgboost') → registry (backend/models/*.pkl, 10 entries)
   └─ else _heuristic_forecast
        │  on-disk forecast cache (5-min TTL)
        ▼
├─▶ RankingEngine.get_ranking()  (score = 0.6·prob + 0.4·edge, 60s TTL cache — v2.6)
├─▶ StatusEngine.get_full_status()  (registry + live probes + LLM checks → HEALTHY/DEGRADED)
├─▶ PipelineBridge.build_inputs() ──▶ DecisionPipeline (RealFeatureStore VIX + MacroDifferentialProvider
│        + DecisionEngineAdapter → Live PredictionArtifact)  ──▶ /decision + /risk (+ RiskEngine)
└─▶ [layer1 forecast · price · forecast-dashboard · model-comparison · market-intelligence]
```

### 4.2 Module responsibilities

| Area | Files | Role |
| --- | --- | --- |
| `config.py` | — | Env config: keys, trading thresholds, paths |
| `engine.py` | — | `DecisionEngine` — `_load_canonical_model` (Logistic_24, 9 pairs), `_get_model_for_pair` (registry xgb/logistic), PIT `_get_policy_diff`, 5-min disk cache, heuristic fallback |
| `data/` | `provider.py`, `fetcher.py` (legacy dup), `sources/{yahoo,alpha_vantage,twelve,fred}.py` | Multi-source failover data; FRED **simulated without key**; country providers `allow_simulation=False` |
| `data/macro/` | `service.py`, `cache.py`, `transformer.py`, `canonical_adapter.py`, `differential_provider.py`, `differential_status.py`, `registry.py` | `MacroService` (+ PIT `get_historical_policy_rate`), `MacroTransformer`, `MacroDifferentialProvider` (normalized ±1, `calculate_historical` PIT merge_asof), `MacroDataStatus` FULL/PARTIAL |
| `data/macro/providers/` | 10 registered (USD FRED, EUR, CHF, GBP, JPY, MXN, BRL, ARS, BOB, CNY chain) + unregistered building blocks (ECB, PBoC, SNB, SOFR, Banxico, CNBS, World Bank, Investing.com, Trading Economics…) | Country macro contexts |
| `status/` | `engine.py` | `StatusEngine` — model states (age/active/stale), live data-source probes, LLM key presence, cache stats, HEALTHY/DEGRADED |
| `ranking/` | `engine.py` | `RankingEngine` — `opportunity_score = 0.6·prob + 0.4·min(edge/3,1)`, **60 s TTL cache** |
| `features/` | `technical.py` (23), `derived.py`, `macro.py` | Indicators + `create_target()`, derived/macro features |
| `models/` | `xgboost_model.py`, `logistic_model.py` (supports sklearn Pipeline artifacts), `registry.py`, `registry_adapter.py`, `model_selector.py` | Per-pair models + `ModelRegistry`; selector/adapter unwired; `trainer.py` empty |
| `explainers/` | `shap_explainer.py` | SHAP `TreeExplainer`, top-10 contributions |
| `decision/` | `filter.py` | Simplified `EconomicFilter` |
| `pipeline_bridge.py` | — | `PipelineBridge` — layer-2 data → `PipelineInputs` (macro regime, differential status, traceability, truthful `required_data_missing`) |
| `quality/` | `pit_adapter.py` | Adapter over `PITValidator` — **dead code** |

### 4.3 Models & registry

- **`models/registry.json`** (root **and** `backend/models/` — byte-identical): **10 models, all `active: true`, `v1.0`** (9 XGBoost + 1 logistic USD/JPY), paths normalized to **`backend/models/*.pkl`** by v2.5.1 (`e31ed31`); all 10 `.pkl` files exist. In-registry AUCs **0.38–0.733** (USD/CHF 0.733 best, USD/CNY 0.380 worst; USD/JPY xgb 0.408 / logistic 0.448).
- **Canonical Logistic_24** (`models/canonical/`): **10 `.joblib` + 2 metadata** (`logistic_24_{PAIR}_{20260908/09}_*.joblib` + `logistic_24_extended_20260908_180112.joblib`, not loaded). `engine._load_canonical_model` maps **9 pairs** to these via a hardcoded CWD-relative `models/canonical/*.joblib` path. Trained 2026-09-08/09 with PIT `policy_diff`; **not in registry.json**.
- **Experimental** (`models/experimental/`): EUR/USD h10 + USD/BOB h20 (research gate candidates) — never loaded by the API.
- **Path caveat (updated):** registry paths now resolve from the repo root for all 10 artifacts; **but** `engine._load_canonical_model` (`models/canonical/`), `train_models.py` (still writes old `models/xgboost_*` paths), and `StatusEngine` (`models/registry.json`) are **CWD-relative** — behavior differs by process CWD and in the Dockerfile (which copies `backend/` only, so the containered app has no root `models/` → canonical Logistic_24 won't load there).

---

## 5. Layer 3 — research layer (`backend/layer3/`)

Standalone research/evaluation package. **Only coupling to the API:** `layer1/routers/model_comparison.py` (working). Nothing in `layer2` imports it.

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | `ModelArtifact`, `PredictionArtifact`, `ModelRegistry` | Persistence of research-approved models | ✅ implemented — schema **incompatible** with layer-2 `registry.json` |
| `evaluation/` | `walk_forward.py`, `benchmarks.py`, `run_benchmarks.py`, `model_evaluator.py`, `decision_policy.py` | Backtests, reference strategies, OOS split, policy search | ✅ `evaluate()` **FIXED**; ❌ `run_benchmarks.py` still crashes (`engine.xgb_model`); `model_evaluator` random fallback |
| `experiments/` | `run.py`, `real_experiments.py` | E0–E7 experiment suite | ❌ `run.py` still **hardcoded** stubs; `real_experiments.py` unblocked but unverified |
| `macro/regime.py` | `MacroRegimeEngine` | Risk/Policy/Growth/Inflation → regime classification | ✅ works |
| `models/` | `arima.py`, `elastic_net.py`, `ensemble.py` | Control models | ⚠️ ARIMA needs absent `statsmodels`; elastic-net/ensemble work |
| `rag/agents.py` | `CentralBankRAGEngine` | Fed/BoJ sentiment + expectation gap | ⚠️ keyword scorer, not real RAG |
| `research_gate/` | `gate.py`, `real_gate.py`, `full_gate.py` | 4-gate model approval | ⚠️ `gate.py` works; `full_gate.py` passes `features={}`; `real_gate.py` inherits evaluator caveats |

### 5.1 Research Gate pipeline (repo root, unchanged)

```
research_validation_test.py / final_holdout.py / evaluate_all_pairs.py
        ▼  purged 60/20/20 split · logistic + sigmoid calibration
research_validation_summary.csv
        ▼
research_gate.py  (RULES: val AUC>0.60 · test AUC>0.60 · drop<0.20 · PR-AUC>0.50 · cal-Brier<0.40)
        ▼
research_gate_results_v2.json   →   USD/BOB 20d  CANDIDATE_WITH_WARNINGS (cal Brier 0.636)
                                    EUR/USD 10d  CANDIDATE (cal Brier 0.237)
        ▼
train_experimental_models.py → models/experimental/{EUR_USD/h10, USD_BOB/h20}  (model + calibrator + metadata.json)
```

Caveats: PR-AUC is a declared rule but **not actually computed**; the experimental candidates are **not registered** in `backend/models/registry.json` and are never loaded by the API; `research_gate_results_v2.json` is untracked.

### 5.2 Canonical-model research, walkforward & shadow testing (repo root)

```
train_canonical_model.py · train_canonical_model_extended.py · train_multi_pairs.py
        ▼   Logistic_24 for all 9 pairs (PIT policy_diff)
models/canonical/logistic_24_*_2026090{8,9}_*.joblib  (10 models + metadata)
        ▼
research_walkforward.py · research_walkforward_{models,macro,pit,xgb_macro_pit,inflation,lag,nonoverlap,head_to_head}.py
        ▼  walkforward A/B/head-to-head studies → research_walkforward_{*}_results.json
        ▼
shadow_test.py · shadow_test_simple.py → shadow_test_results_*.json (PIT + non-PIT)
        ▼
monitor_daily.py · monitor_model.py  (daily/monitoring hooks) · scripts/audit_consistency.py
```

Docs: `docs/model_selection/2026-09-08_model_selection_logistic_vs_xgboost.md`. `requirements-stable-v2.0.txt` pins the stable dependency set.

---

## 6. Layer 4 — data-quality layer (`backend/layer4/`)

| Area | Files | Role | Maturity |
| --- | --- | --- | --- |
| `quality/pit_validator.py` | `PITValidator` (PIT-1…PIT-7) | Point-in-Time compliance | ✅ correct (verified vs datasets A–D) |
| `config/policies.py` | `SourcePolicy`, `FeatureConfig`, `TargetConfig`, `ConfigRegistry` | Versioned configuration | ✅ implemented, **unused** |
| `lineage/models.py` | LineageReference/Record/Registry | Provenance | ✅ implemented, **unused** |
| `tests/pit_tests.py` | layer-4 unit tests | PITValidator tests | ❌ **syntactically corrupted** — won't parse (line 90 SyntaxError; duplicated `run_all`) |

**Wiring:** `PITValidator` is executed via `backend/tests/test_pit_adversarial.py` (part of the 132 passing suite). Runtime forecast paths do not validate PIT.

---

## 7. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consumes Layer 3 §11.2 / Layer 4 §7 contracts. Packages: `contracts/`, `filter/`, `gates/`, `quality/` (+ `real_providers.py`), `registries/`, `risk/`, `sizing/`, `validation/`, `pipeline.py`.

```
PredictionArtifact (live via DecisionEngineAdapter) ─┐
RealFeatureStore (VIX, Yahoo) · MacroService +        │  PipelineInputs
  MacroDifferentialProvider · fake DQ/Freshness/Drift └──────────▶ DecisionPipeline.build()
                                                                          │
     1. Signals        OOB → INVALID · 2. Regime+fusion → Direction
     3. Confidence · 4. Costs (VIX via FeatureStore P2) · 5. Economic filter
     6. Quality · 7. Hard gates (signal_validity P3) · 8. Sizing → Decision {...}
                                                                          │
     RiskEngine.compute (vol .30 · macro .25 · model .20 · regime .15 · edge .10) → RiskAssessment
```

**Verification:** `python -m pytest` from `backend/` → **132 passed** across **13 files** (includes `test_risk_engine.py` 26, `test_signals_fusion.py` 17, `test_gates.py` 18, `test_quality.py` 10, `test_registries.py` 10, `test_pit_adversarial.py`, `test_canonical_macro_adapter.py`). Needs repo-root + backend on `PYTHONPATH`.

> **Runtime wiring (updated):** `/v1/canonical/{pair}/decision` **and** `/v1/canonical/{pair}/risk` are served from the real pipeline: **VIX real** via `RealFeatureStore` (Yahoo `^VIX`, 60 s TTL, failure → `UNAVAILABLE`), forecasts real (Logistic_24/XGBoost), macro real-or-simulated. Remaining fakes: `FakeDataQualityRegistry`, `FakeFreshnessRegistry`, `FakeDriftRegistry` — **TODO v2.7**. `FakeFeatureStore` survives only in `validation/validate_integration.py` (test-only).

---

## 8. Frontend — contract-driven dashboard (`frontend/`)

**Stack:** React 18, TS 5, Vite 5 (5174, `minify off`), Tailwind 3, TanStack Query 5 (5-min staleTime), axios + raw fetch, date-fns, React Router 6 (v7 future flags on), Recharts 2. **Deploys:** Cloudflare Pages + Vercel. **Contract root:** `types/contracts.ts` mirrors Layer 1 v5.1 §7; canonical decision/risk/market-intelligence/forecast-dashboard contracts declared in their hooks.

### 8.1 Routes (6 canonical pages, 10 hook modules)

| Path | Page | Data hooks |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence` |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice` (1y), `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 30)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair, 30)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 30)` |
| `/about` | AboutPage | (narrative) |

**Legacy pages removed** (v2.4 Sprint 8 `5bd324e`: Forecast, ForecastPageCanonical, Drivers, Evaluation, Status, Price, ModelComparison, TabNav; v2.5.1: HistoricalPage, mockup/, `_unused/`). **Hooks:** `useActivePair`, `useCanonicalDecision`, `useCanonicalRisk` (60 s refresh), `useForecast`, `useForecastDashboard`, `useMarketIntelligence`, `usePerformancePeriod` (nav-only), `usePolling` (unused), `usePrice`, `useRanking`. Removed: `useDrivers`, `useMacroContext`, `useFanChartData`, `useStatus`, `usePerformance`, `useModelComparison`, `useInterpretation`, `useHistorical`, `useMacro` (archived in `.trash-v2.5/`).

### 8.2 Presentational components

`common/*` (11 in barrel: Panel, EmptyState, ApiError, LoadingSpinner, UniverseSelector, ThemeProvider, StatusBadge, RegimeBar, NotAvailable, MetricsHelp, ErrorBoundary; **MarketConvention orphaned** — not imported), `decision/*` (DecisionHero, DecisionMetrics, DecisionShapPanel, DecisionValidity, EconomicBreakdown, HardGates, QualityMetrics, SignalFusion), `forecast/*` (SpotCard, TrendCard, ForecastCard 30/60/90d), `global/*` (ActionableInfo w/ dynamic thresholds, IntelligenceBrief, LeadingSignals, RankingTable — v2.6.4 enriched with Confidence/Quality/Position, MarketIntelligenceHero, ModelExplanation, PriceChartSignalIQ), `market/*` (MarketHero, HistoricalChart, **MarketMeta** — 5-column grid incl. **Volatility** block, v2.6.6), `macro/*` (MacroHero, PolicyDifferentials, MacroMeta), `risk/*` (RiskScoreCard, RiskDriversPanel, RiskDriverBar), `layout/*`. **Sizing is rendered inline in DecisionPage** (no `SizingPanel` component).

### 8.3 Transport & contracts

- `services/api.ts` — axios `apiClient` (baseURL `VITE_API_URL`, 30 s timeout, retry max 3 exp. backoff); `services/{forecast,ranking,performance,status}.ts` zero-transform adapters.
- ⚠️ 4 hooks (`usePrice`, `useRanking`, `useMarketIntelligence`, `useForecastDashboard`) use **raw `fetch`** with `VITE_API_URL || localhost:8000` — bypassing `apiClient`'s retry/backoff.
- `types/contracts.ts` — frozen Layer 1 §7.1–7.7 mirror; `types/gaps.ts` `CONTRACT_GAP_MAP` (G1–G5). Canonical types (decision/risk/market-intelligence/dashboard) live in hook files.
- **UI strings are Spanish** though `index.html` is `lang="en"` — localization inconsistency.

### 8.4 Layering rules

| Rule | Location |
| --- | --- |
| Presentational components receive props only | `components/*` |
| Pages call hooks but don't compute/rank/derive | `pages/*` |
| `utils/` re-formats but never infers/calculates | `format.ts`, `status.ts`, `gaps.ts`, `safeFormat.ts` |
| Transport never transforms payloads | `services/api.ts` |
| Unsupported contract elements render `NotAvailable` | `types/gaps.ts` + `NotAvailable.tsx` |
| No derivation: consume `decision.actionable` | governance + gap registry |

> ✅ **Compile state (green):** `npm run typecheck` PASS, `npm run build` PASS (1,422 kB JS / 293 kB gzip — minify off), `npm test` **56 passed** (7 files). The `9d0b62f` break flagged in prior reports is **resolved**.

---

## 9. Deployment & runtime

| Target | Mechanism | Notes |
| --- | --- | --- |
| **Render** (backend) | Docker web service (`render.yaml`, plan free, `/health`) | python:3.12-slim, `PYTHONPATH=/app/backend`, `uvicorn layer1.main:app` :10000; env FRED/GROQ/ALPHA/TWELVE (`sync:false`). **Dockerfile copies only `backend/`** — containered app has no root `models/` (canonical `.joblib` + StatusEngine `models/registry.json` absent). |
| **Cloudflare Pages** (frontend) | Static-site mode; `_headers`, `_redirects` (`/* → /index.html 200`), `.cloudflareignore` | — |
| **Vercel** (frontend) | `vercel.json` — Vite build → `dist`, SPA rewrites | — |
| **Local** | `backend/docker-compose.yml` — port 10000, mounts `./models` + `./cache`; `start.sh`/`stop.sh` — uvicorn backend :8000 + vite preview :5173 | start/stop untracked + gitignored |

**Ops caveats (updated):**
- **`frontend/.env.production` RESTORED** (`2c0cbb9`, 2026-09-09) → `VITE_API_URL=https://meridianfx.onrender.com`. The prior "deleted" flag is resolved; local `.env` still targets localhost:8000.
- **Model paths still CWD-relative but improved:** registry paths are `backend/models/*.pkl` — resolve from repo root (and in Docker via `/app/backend/models`). Remaining mismatches: `engine._load_canonical_model` reads `models/canonical/*.joblib` (repo root only; absent in the `backend/`-only Docker image), `StatusEngine` reads `models/registry.json` (root), `train_models.py` still writes legacy `models/*.pkl` paths.
- FRED real data requires `FRED_API_KEY`; without it the macro path serves simulated data (country providers refuse simulation and report `available=False`).

---

## 10. Documentation & governance layer

The docs are the **authority**; code is verified against them.

```
docs/
├── Domain/ · High-Level Design/ · Low-Level Design/
├── Product_specification/   FROZEN L1 v5.1 · L2 v3.4.1 · L3 v5.0 · L4 v3.1.1
├── Prompts/                 Layer prompts + prompt_-1/0/X audit & build
├── model_selection/         2026-09-08 Logistic vs XGBoost selection report
├── MACRO_COVERAGE.md        Macro provider coverage & traceability baseline
└── DEUDA_TECNICA_v2.5.md    NEW — engineering-debt baseline v2.5 (only doc added since 09-09)
```

| Artifact | Role |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row element→contract matrix (61 verified / 12 gap) |
| `CONTRACT_GAPS.md` (v2.0) | 16 unified gaps: G1–G9 + EC-1..4, RA, CA, DF-P |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | FREEZE WITH OPTIONAL GAPS, 0 blocking |
| `CONTRACT_VALIDATION.md` / `MIGRATION_REPORT.md` / `COMPONENT_MAPPING.md` | Prompt-1 audit PASS / 66 mockups / 100% mapping |
| `MACRO_COVERAGE.md` | Macro provider coverage & traceability baseline (v2.5) |
| `DEUDA_TECNICA_v2.5.md` | Debt ledger: resolved-in-v2.5 (frontend + backend), deferred (v2.5.1/v2.6/v3.0) |

**Governance workflow:** change request → traceability → gaps → freeze → validate. **Not** pushed through the loop: the canonical decision/risk endpoints + `pipeline_bridge`, RealFeatureStore/real-VIX wiring, the RiskEngine, ranking cache, `/v1/market-intelligence`, the canonical frontend pages (Market/Macro/Risk/Decision), the walkforward/shadow research bundle, and the ROI cleanup. **README lags:** says v2.5.1; HEAD is v2.6.6-fix (no v2.6 tag yet — latest tag is `v2.5`).

---

## 11. Verification matrix

| Layer | Command | Status (2026-09-11) |
| --- | --- | --- |
| Backend `src` decision engine (+ L4 PIT, RiskEngine) | `cd backend && python -m pytest` | **132 passed** (13 files) ✅ |
| Layer 1 import | `python -c "import backend.layer1.main"` | pass ✅ |
| Layer 1 endpoints (smoke) | TestClient against running app | `/status` `HEALTHY`; `/market-intelligence` 200; `/ranking` 200; `/forecast` 200 (live); `/performance` 200; `/canonical/{pair}/decision` 200 (real per-pair output); `/canonical/{pair}/risk` 200 (real risk, VIX real); `/price` 200 ✅ |
| Frontend typecheck | `cd frontend && npm run typecheck` | ✅ PASS |
| Frontend tests | `cd frontend && npm test` | **56 passed / 0 failed** (7 files) |
| Frontend build | `cd frontend && npm run build` | ✅ PASS (1,422 kB / 293 kB gzip — minify off) |

---

## 12. Known gaps & risks

1. **Canonical pipeline still runs 3 fake L4 registries** — VIX is now real (`RealFeatureStore`), but `FakeDataQualityRegistry/FakeFreshnessRegistry/FakeDriftRegistry` remain in `canonical.py` (explicit TODO v2.7); data-quality gating is not yet real.
2. **Model path resolution is still CWD-relative and inconsistent** — registry `backend/models/*.pkl` resolves from repo root; `engine._load_canonical_model` (`models/canonical/`), `StatusEngine` (`models/registry.json`) and `train_models.py` (legacy `models/*.pkl` paths) are not aligned; the Render Dockerfile copies only `backend/`, so canonical Logistic_24 (and the root registry view) are absent in the container.
3. **`USD/CNY` canonical decision returned `MODEL_UNAVAILABLE`** in the live smoke run (others: EUR/USD/GBP/USD actionable SHORT, USD/JPY INSUFFICIENT_EDGE) — genuine dependency on live macro/model data; monitor per-pair.
4. **Layer 3 tail** — `run_benchmarks.py` still crashes (`engine.xgb_model` AttributeError); `experiments/run.py` E0–E7 hardcoded; `arima.py` needs absent `statsmodels`; `artifacts/registry.py` schema incompatible with `backend/models/registry.json`.
5. **Layer 4 mostly unwired** — PIT runs only in tests; `pit_adapter.py`/`config`/`lineage` dead; `pit_tests.py` still corrupted (SyntaxError line 90).
6. **LLM chain entirely unwired** — `layer1/llm/*` (Groq real, GLM/Gemini stubs, FallbackLLM, `EconomicInterpreter`) is imported by no router; `/interpretation` uses inline rule-based narrative.
7. **Hardcoded/simulated remnants** — `/interpretation` `include_macro` block hardcoded (`NEUTRAL`/"Contexto macro no disponible"); `/historical` random-synthetic fallback; `/performance` hardcoded `ece`/`max_drawdown`/`regime_performance`; `/price` hardcoded display labels; `/status` `database=NOT_CONFIGURED`; FRED simulated without key. `FORECAST_DATA` is dead code.
8. **Frontend dead/stale** — `usePolling` unused; `MarketConvention.tsx` orphaned; `utils/status.ts` only covered by tests; `.trash-v2.5/` (46 archived files) on disk; empty `src/pages/historical/` dir; 4 hooks bypass `apiClient` (raw fetch, no retry); Spanish UI strings vs `lang="en"`.
9. **Deployment/governance debt** — Docker model-dir mismatch (canonical/StatusEngine paths absent in image); README stale at v2.5.1; **no v2.6 tag** despite 9 v2.6.x commits; post-freeze surfaces (canonical risk, RealFeatureStore, RiskEngine, ranking cache, new pages, research bundle) not through the governance loop.
10. **Layer 1 dead subsystems** — `decision/` (own `DecisionEngine`), `data/forecast_data.py`, drivers-era adapter remnants (`get_drivers`, `to_drivers_response`), `routers/__init__` subtle import side-effect.
11. **Bundle size** — 1,422 kB JS chunk (293 kB gzip), `minify: false`, warning silenced by raised `chunkSizeWarningLimit`.
12. **Live-model caveats** — `/model-comparison` slow (3y walk-forward per pair); `/price`/`/forecast-dashboard` signals depend on model resolution + network (macros empty on failure).