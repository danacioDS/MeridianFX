# Meridian FX — Architecture

**Date:** 2026-09-14

System architecture for the Meridian FX repo: a contract-driven FX intelligence product with a FastAPI delivery API (Layer 1, **12 routers incl. canonical decision + risk + narrative/regenerate**), a live ML/decision engine (Layer 2, Logistic_24 + XGBoost, real-VIX canonical pipeline that now **decides on all 9 pairs** at a **5-day default horizon**), a persistent **LLM narrative layer** (Layer 2 `narrative/`, SQLite, Groq via `LLMFallbackManager`), research (Layer 3) and data-quality (Layer 4) codebases, a contract-verified decision engine (`src`, **132 tests**, incl. Risk Assessment Engine), a **registry promotion gate** (9/10 legacy models deactivated — only USD/CHF remains; legacy ranking collapses to 1 pair while the canonical pipeline keeps 9/9), a script-driven Research Gate + walkforward research suite (repo root), and a React dashboard (6 canonical pages: Global · Market · Macro · Risk · Decision · About, incl. Provenance + Narrative blocks), deployed in production (Render backend, Cloudflare Pages + Vercel frontend).

---

## 1. System context

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCT (9-pair universe · 5d model horizon · 30/60/90d forecasts)    │
│      USD/JPY · EUR/USD · GBP/USD · USD/CNY · USD/MXN · USD/BRL · USD/ARS · USD/BOB · USD/CHF │
│                                                                                              │
│   ┌────────────────┐  delivery contracts (Layer 1 §7)   ┌───────────────────────┐            │
│   │   LAYER 1      │ ──────────────────────────────────▶ │  FRONTEND (React+TS) │            │
│   │ DELIVERY API   │  /v1/fx/ranking · price · forecast  │  Global · Market ·    │            │
│   │  (FastAPI, 12  │  /v1/fx/{pair}/forecast-dashboard   │  Macro · Risk ·       │            │
│   │   routers)     │  /v1/canonical/{pair}/decision|risk │  Decision · About     │            │
│   │  backend/layer1 │ /v1/canonical/{pair}/narrative      │  (Provenance +        │            │
│   └───────┬────────┘  /v1/fx/{pair}/model-comparison     │   Narrative blocks)   │            │
│           │  /v1/market-intelligence · /v1/status        └───────────────────────┘            │
│           │  /v1/fx/interpretation · historical · performance                                 │
│           │  uses layer2 engine (+ layer3 via model-comparison, + src decision via pipeline_bridge) │
│   ┌───────▼──────────────────┐         ┌────────────────────────┐ ┌───────────────┐          │
│   │ LAYER 2  LIVE ENGINE     │         │ LAYER 3  RESEARCH       │ │ LAYER 4 DATA  │          │
│   │ backend/layer2:          │◀───────▶│ backend/layer3:        │ │  QUALITY      │          │
│   │ Logistic_24 canonical    │  + docs │ eval/walk_forward (fix) │ │ backend/layer4│          │
│   │ (_load_canonical_model)  │         │ benchmarks · arima/    │ │ PITValidator  │          │
│   │ XGBoost via registry     │         │ elastic_net/ensemble · │ │ (PIT-1..7) ·  │          │
│   │   (1 active after gate)  │         │ macro regime ·         │ │ config ·      │          │
│   │ SHAP · Yahoo→Alpha→Twelve│         │ sentiment ·           │ │ lineage       │          │
│   │ FRED macro · ranking     │         │ research_gate          │ │               │          │
│   │   (60s cache, 1 pair) ·  │         │ run_benchmarks BROKEN  │ │               │          │
│   │ StatusEngine · narrative │         │                        │ │               │          │
│   │   (SQLite LLM cache)     │         │                        │ │               │          │
│   └──────────┬──────────────┘  (wired via model_comparison only) │               │          │
│              │  + src/meridian_fx/decision/ (contract-governed engine: 8-stage pipeline,     │
│              │    RiskEngine, RealFeatureStore VIX, Stub* L4 registries, 132 tests)          │
│              │                                                                                │
│   RESEARCH (repo root): research_validation_test.py · final_holdout.py · research_gate.py     │
│              (AUC/PR-AUC/Brier v2) → models/experimental/ (EUR/USD h10 + USD/BOB h20)         │
│              research_walkforward_{models,macro,pit,xgb_macro_pit,inflation,lag,nonoverlap,   │
│              head_to_head}.py · shadow_test*.py · monitor_*.py  — NOT wired into Layer 1/2    │
│                                                                                                │
│   GOVERNANCE (scripts/): audit_consistency.py · audit_registry.py · apply_gate.py (MIN_AUC=0.52,│
│              MIN_N_SAMPLES=300 → 9/10 legacy models deactivated, USD/CHF only)                │
│                                                                                                │
│   DEPLOY:  Render (Docker FastAPI+Uvicorn :10000, /health) · Cloudflare Pages + Vercel (SPA) │
│            FRED/GROQ/ALPHA/TWELVE keys via render.yaml; frontend/.env.production = placeholder │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Key relationships:** Layer 1 consumes `layer2/` directly: per-pair models (canonical **Logistic_24** `.joblib` via `engine._load_canonical_model` + XGBoost via `registry.json`, **1 active** after the gate), the real `StatusEngine`, a **60 s-cached RankingEngine** (now **single-pair**), the **canonical pipeline** wired via `pipeline_bridge.py` (Layer 2 → `DecisionPipeline`), and the **narrative router** (`layer2/narrative/` → `LLMFallbackManager`). The canonical `/v1/canonical/{pair}/decision`, `/risk` and `/narrative` routes run on **real VIX** (`RealFeatureStore`, Yahoo `^VIX`), real macro (FRED, simulated without key) and real Logistic_24 forecasts; **9/9 pairs produce decisions** (partial macro data now degrades via a neutral `macro=0.0` and a degraded warning instead of `MODEL_UNAVAILABLE`). The three **quality/freshness/drift registries are `Stub*` placeholders** (renamed from `Fake*`, TODO v2.7). Layer 3 is wired into the API **only** via `model_comparison` (working); `run_benchmarks.py` remains broken. Layer 4 runs **only** through tests. The `src` engine also contains the **Risk Assessment Engine** (`/risk`). A `/drivers` router existed historically and was **removed** in v2.6.3. The root-level Research Gate + walkforward bundle produces `models/canonical/` **and** `models/experimental/` candidates; the API loads the canonical Logistic_24 but never loads `models/experimental/`.

---

## 2. Repo map (top-level)

```
MeridianFX/
├── docs/                     Frozen specs, prompts, contract governance, model_selection,
│                             MACRO_COVERAGE.md, DEUDA_TECNICA_v2.5.md
├── backend/                  Python backend
│   ├── layer1/               FastAPI delivery API (12 routers incl. canonical decision+risk+narrative,
│   │                         intelligence, performance, price, forecast-dashboard, model-comparison; NO /drivers)
│   │                         + adapters/, llm/ (PARTIAL — via narrative only), decision/ (DEAD subsystem)
│   ├── layer2/               Live engine (engine.py: Logistic_24 loader + registry; data, features, models,
│   │                         explainers, macro, ranking w/ 60s cache, status, pipeline_bridge, narrative/NEW)
│   ├── layer3/               Research/evaluation layer (walk-forward, benchmarks, models, regime,
│   │                         sentiment (was rag), gate)
│   ├── layer4/               Data-quality layer (PIT validator, config policies, lineage; pit_tests.py corrupt)
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, RiskEngine,
│   │                         RealFeatureStore, Stub* L4 registries, 132 tests)
│   ├── models/               models/registry.json (10 entries — 1 ACTIVE, 9 below gate) + 10 .pkl
│   ├── tests/                Backend pytest suite (13 files, 132 tests)
│   ├── pyproject.toml        Backend project metadata (pythonpath=src, pytest)
│   ├── requirements.txt      Backend dependency manifest (+ python-dotenv)
│   └── docker-compose.yml    Local compose (port 10000, mounts models/ + cache/)
│   └── cache/                Runtime state incl. narratives.db (SQLite narrative store)
├── models/                   Root-level artifacts: canonical/ (10 Logistic_24 .joblib + metadata),
│                             experimental/ (EUR/USD, USD/BOB), registry.json (== backend copy)
├── Dockerfile                Render container (python:3.12-slim, uvicorn layer1.main:app :10000)
├── render.yaml               Render blueprint (docker free web service, /health, env keys)
├── runtime.txt               Python 3.12.0 pin (repo root)
├── start.sh · stop.sh        Local runs (untracked + gitignored)
├── train_models.py · train_canonical_model{,_extended}.py · train_multi_pairs.py
├── train_experimental_models.py · evaluate_all_pairs.py · final_holdout.py
├── research_gate.py · research_gate_results{,v2}.json · research_validation_*
├── research_walkforward.py + 8 specialized variants + *_results.json
├── shadow_test.py · shadow_test_simple.py · monitor_daily.py · monitor_model.py
├── scripts/audit_consistency.py · scripts/audit_registry.py · scripts/apply_gate.py   NEW — registry gate
├── cache/ · logs/            Runtime state (gitignored; backend/venv/ ignored too)
├── frontend/                 Contract-driven React+TS dashboard (Cloudflare Pages + Vercel)
│   ├── .env.production       Comment-only placeholder for local dev (d917ca0); .env.production.onrender ignored
│   ├── src/pages/            Global · Market · Macro · Risk · Decision · About (6 canonical pages)
│   ├── src/hooks/            11 hooks (useCanonicalDecision, useCanonicalRisk, useCanonicalNarrative, …)
│   ├── src/components/decision/  … incl. DecisionProvenance + DecisionNarrative (NEW)
│   ├── src/types/contracts.ts Layer 1 §7 mirror (+ canonical contracts in hooks)
│   └── .trash-v2.5/          Local archive (46 files, gitignored)
├── .env                      Runtime env (FRED/GROQ/ALPHA/TWELVE/OPENAI/CLOUDFLARE keys + config)
├── README.md                 Quickstart updated + "## Current Limitations" section (header still v2.5.1)
├── report.md                 Repository analysis (2026-09-14)
└── architecture.md           This document
```

> **Hygiene:** working tree clean, `main` in sync with `origin/main`. Root/backend `models/registry.json` byte-identical (10 entries, `backend/models/*.pkl` paths). 9 models now `active:false` (promotion gate), 1 active (USD/CHF). Gitignored: `start.sh`/`stop.sh`, `venv/`, `backend/venv/`, `cache/`, `logs/`, `frontend/.trash-v2.5/`.

---

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

**Entry:** `backend/layer1/main.py` — `FastAPI(title="Meridian FX API", version="1.0.0")`, CORS covering localhost/Render/Vercel/Cloudflare/ngrok/`*`. **12 routers** (ranking, forecast, performance, status, intelligence, canonical, narrative, historical, interpretation, price, model_comparison, forecast_dashboard) plus `/` and `/health`. 132 backend tests green on 2026-09-14; TestClient smoke previously verified 200 on all endpoints (2026-09-11).

### 3.1 Routers

| Router | Endpoint | Data source | Status |
| --- | --- | --- | --- |
| `ranking` | `GET /v1/fx/ranking` | `layer2.RankingEngine` (60 s in-memory cache) — after the gate iterates only **registry-active pairs → USD/CHF only** | ✅ / ⚠️ 1 pair |
| `forecast` | `GET /v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` — **Logistic_24** → heuristic fallback (was `FORECAST_DATA`); horizon default 5 | ✅ live (lineage block hardcoded `{type: logistic, version: v1.0}`) |
| `performance` | `GET /v1/fx/performance/{pair}?period=` | `models/registry.json` metrics + hardcoded derivations (`ece=0.05`, `max_drawdown=-0.06`, static `regime_performance`) | ✅ / ⚠️ derived |
| `status` | `GET /v1/status` | **real** — `layer2.status.engine.StatusEngine` (registry, live probes, LLM key checks) | ✅ `HEALTHY` |
| `intelligence` | `GET /v1/market-intelligence` | English narrative synthesis over `RankingEngine` (deterministic) — **single-pair now** | ✅ / ⚠️ |
| `canonical` | `GET /v1/canonical/{pair}/decision` | `DecisionPipeline` via `pipeline_bridge.py` — **RealFeatureStore (VIX)** + 3 **Stub** quality registries (TODO v2.7); `horizon_days` default **5**; **9/9 pairs** | ✅ 200 — 5 actionable / 4 INSUFFICIENT_EDGE |
| `canonical` | `GET /v1/canonical/{pair}/risk` | **same bridge → `RiskEngine.compute`** (`src/.../risk/engine.py`) | ✅ 200 — real risk scores |
| `narrative` | `GET /v1/canonical/{pair}/narrative` | **NEW** — cache-first persistent LLM narrative (`layer2/narrative/`, SQLite `backend/cache/narratives.db`, stable `narrative_key`, no TTL) | ✅ |
| `narrative` | `POST /v1/canonical/{pair}/narrative/regenerate` | **NEW** — admin regeneration (`X-Admin-Token`; `503` if `ADMIN_TOKEN` unset) | ✅ |
| `historical` | `GET /v1/fx/{pair}/historical?period=` | `layer2.DataProvider` + `TechnicalFeatures` (random-synthetic **fallback** on failure) | ✅ / ⚠️ fallback |
| `interpretation` | `GET /v1/fx/interpretation?pair=&include_macro=` | **inline rule-based narrative** over `get_forecast`; `include_macro=true` returns hardcoded `{"regime":"NEUTRAL","summary":"Contexto macro no disponible"}` | ⚠️ rule-based + hardcoded macro |
| `price` | `GET /v1/fx/{pair}/price?period=` | **live** spot/history; XGBoost signal via `_get_model_for_pair` (try/except → `UNKNOWN`) | ✅ live |
| `model_comparison` | `GET /v1/fx/{pair}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding`; in-memory `_comparison_cache`; ensemble `not_implemented`, best by Sharpe | ✅ 200 (slow 3y walk-forward) |
| `forecast_dashboard` | `GET /v1/fx/{pair}/forecast-dashboard` | **live** — provider + trends/volatility + Logistic_24/XGBoost via `DecisionEngine` 30/60/90d + FRED macro | ✅ network |

> **Removed earlier:** `/drivers` (`GET /v1/fx/{base}/{quote}/drivers`) was **deleted in v2.6.3** (`82c9e80`) along with `services/drivers.ts` and its hardcoded `macro_drivers`. `FORECAST_DATA` in `layer1/data/forecast_data.py` is **dead code**. `/v1/fx/macro/status` and `/v1/fx/macro/refresh` remain removed.

### 3.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7.
- **`adapters/decision_to_response.py`** — `DecisionAdapter` (`to_performance_response` used; `to_drivers_response` dead after `/drivers` removal).
- **`adapters/decision_engine_adapter.py`** — `DecisionEngineAdapter` (legacy `DecisionEngine.get_forecast` → canonical `PredictionArtifact`, braided with `MacroService`); used by `PipelineBridge`; `get_drivers()` dead.
- **`decision/`** — `decision_context.py`, `economic_filter.py`, `signal_validity.py`: **standalone dead subsystem** (no router imports them).
- **`llm/`** — `GroqProvider` (real HTTP, model now `qwen/qwen3.8-27b`), `GLM/GeminiProvider` (NotImplementedError), `FallbackLLM`, `LLMFallbackManager`, `EconomicInterpreter`. **Now partially reached:** `LLMFallbackManager` is imported by `layer2/narrative/generator.py` and driven by the narrative router. `EconomicInterpreter` remains imported by no router.
- **`routers/canonical.py`** — constructs `DecisionPipeline(feature_store=RealFeatureStore(), data_quality_registry=StubDataQualityRegistry(0.90), freshness_registry=StubFreshnessRegistry(3.0), drift_registry=StubDriftRegistry(0.05))`. VIX is real (Yahoo `^VIX`, 60 s TTL, failure → `UNAVAILABLE`); the 3 L4 registries are **stubs** (renamed from `Fake*` in v2.7 for honesty).
- **`routers/narrative.py`** — `SqliteNarrativeRepository` + `NarrativeGenerator` + `NarrativeService` singletons built at import time; reuse the canonical `bridge` to derive the decision, then cache-first LLM narrative.
- **`routers/__init__.py`** imports only `canonical` (side-effect: constructs the canonical pipeline at import time).
- **`data/forecast_data.py`** — dead (`FORECAST_DATA` referenced by no code).

> **Live outputs (2026-09-11 smoke, semantics updated 09-14):** with partial-macro resilience, all 9 pairs now return real decisions — 5 actionable, 4 `INSUFFICIENT_EDGE`; earlier smoke had EUR/USD `actionable SHORT conf 0.66`, GBP/USD `SHORT conf 0.55`, USD/JPY `INSUFFICIENT_EDGE`, USD/CNY `MODEL_UNAVAILABLE` (the USD/CNY false positive on `PARTIAL` macro is resolved by design). `/v1/canonical/EUR/USD/risk` → `risk_level MODERATE (30.5)`, real VIX 15.8. The narrative endpoint served cache-first LLM narratives.

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
DecisionEngine.get_forecast(pair, horizon_days=5)      ← default now 5 (Logistic_24 target), was 30
   ├─ _get_model_for_pair(pair,'logistic')  → Logistic_24 canonical (engine._load_canonical_model,
   │    hardcoded 9-pair map → models/canonical/*.joblib)  ⚠️ CWD-sensitive
   ├─ else _get_model_for_pair(pair,'xgboost') → registry (backend/models/*.pkl; only USD/CHF active after gate)
   └─ else _heuristic_forecast
        │  on-disk forecast cache (5-min TTL)
        ▼
├─▶ RankingEngine.get_ranking()  (score = 0.6·prob + 0.4·edge, 60s TTL cache — iterates ACTIVE pairs only → 1 pair) │
├─▶ StatusEngine.get_full_status()  (registry + live probes + LLM checks → HEALTHY/DEGRADED)
├─▶ PipelineBridge.build_inputs() ──▶ DecisionPipeline (RealFeatureStore VIX + MacroDifferentialProvider
│        + DecisionEngineAdapter → Live PredictionArtifact) ──▶ /decision + /risk (+ RiskEngine)  → 9/9 pairs
├─▶ NarrativeService (layer2/narrative/) ──▶ LLMFallbackManager (Groq) → SQLite cache ──▶ /narrative
└─▶ [layer1 forecast · price · forecast-dashboard · model-comparison · market-intelligence]
```

### 4.2 Module responsibilities

| Area | Files | Role |
| --- | --- | --- |
| `config.py` | — | Env config: keys, trading thresholds, paths |
| `engine.py` | — | `DecisionEngine` — `_load_canonical_model` (Logistic_24, 9 pairs), `_get_model_for_pair` (registry xgb/logistic), PIT `_get_policy_diff`, `horizon_days`-aware economic filter + `expected_return=(2P−1)·σ·√(h/365)`, 5-min disk cache, heuristic fallback |
| `data/` | `provider.py`, `fetcher.py` (legacy dup), `sources/{yahoo,alpha_vantage,twelve,fred}.py` | Multi-source failover data; FRED **simulated without key**; country providers `allow_simulation=False` |
| `data/macro/` | `service.py`, `cache.py`, `transformer.py`, `canonical_adapter.py`, `differential_provider.py`, `differential_status.py`, `registry.py` | `MacroService` (+ PIT `get_historical_policy_rate`), `MacroTransformer`, `MacroDifferentialProvider` (normalized ±1, `calculate_historical` PIT merge_asof), `MacroDataStatus` FULL/PARTIAL |
| `data/macro/providers/` | 10 registered (USD FRED, EUR, CHF, GBP, JPY, MXN, BRL, ARS, BOB, CNY chain) + unregistered building blocks (ECB, PBoC, SNB, SOFR, Banxico, CNBS, World Bank, Investing.com, Trading Economics…) | Country macro contexts |
| `status/` | `engine.py` | `StatusEngine` — model states (age/active/stale), live data-source probes, LLM key presence, cache stats, HEALTHY/DEGRADED |
| `ranking/` | `engine.py` | `RankingEngine` — `opportunity_score = 0.6·prob + 0.4·min(edge/3,1)`, 60 s TTL cache; **only registry-active pairs (USD/CHF)** |
| `features/` | `technical.py` (23), `derived.py`, `macro.py` | Indicators + `create_target()`, derived/macro features |
| `models/` | `xgboost_model.py`, `logistic_model.py` (supports sklearn Pipeline artifacts), `registry.py`, `registry_adapter.py`, `model_selector.py` | Per-pair models + `ModelRegistry` with **promotion gate** (`MIN_AUC=0.52`, `MIN_N_SAMPLES=300`); adapter double-defends lifecycle; selector serves `DEPLOYED` only; `trainer.py` empty |
| `explainers/` | `shap_explainer.py` | SHAP `TreeExplainer`, top-10 contributions |
| `decision/` | `filter.py` | Simplified `EconomicFilter` |
| `pipeline_bridge.py` | — | `PipelineBridge` — layer-2 data → `PipelineInputs` (macro regime, differential status, traceability, `required_data_missing`) |
| `narrative/` | `repository.py`, `generator.py`, `service.py`, `prompt_builder.py`, `__init__.py` | **NEW** — persistent LLM narratives: SQLite (`backend/cache/narratives.db`, Protocol → Postgres/Neon), stable `narrative_key` (who/what/evidence/model/data), no TTL, Groq primary via `LLMFallbackManager`, deterministic fallback **never persisted** |
| `quality/` | `pit_adapter.py` | Adapter over `PITValidator` — **dead code** |

### 4.3 Models & registry

- **`models/registry.json`** (root **and** `backend/models/` — byte-identical): **10 models, `v1.0`** (9 XGBoost + 1 logistic USD/JPY), paths normalized to `backend/models/*.pkl`. **After the v2.7 promotion gate: 9/10 `active:false` (CANDIDATE) — only USD/CHF xgb (auc 0.733, n=319) is active and `current`.** In-registry AUCs 0.380–0.733.
- **Promotion gate** (`layer2/models/registry.py`): a model activates only if `auc ≥ 0.52 AND n_samples ≥ 300` and it beats the current active model; `registry_adapter.py` refuses activation below gate (unless `force`), `model_selector.py` filters `DEPLOYED`. Tooling: `scripts/audit_registry.py`, `scripts/apply_gate.py` (applied in `e301138`).
- **Canonical Logistic_24** (`models/canonical/`): **10 `.joblib` + 2 metadata** (`logistic_24_{PAIR}_{20260908/09}_*.joblib` + `logistic_24_extended_20260908_180112.joblib`, not loaded). `engine._load_canonical_model` maps **9 pairs** via a hardcoded CWD-relative `models/canonical/*.joblib` path. Trained 2026-09-08/09 with PIT `policy_diff` on a **5-day forward target**; **not in registry.json**.
- **Experimental** (`models/experimental/`): EUR/USD h10 + USD/BOB h20 (research gate candidates) — never loaded by the API.
- **Horizon semantics (v2.7):** the API's `horizon_days` is **not** a per-horizon model — it is a volatility-scaling factor (`expected_return = (2P−1)·σ·√(h/365)`); default is **5** to match training. Multi-horizon models (5d/30d/90d) are planned for v3.0.
- **Path caveat (unchanged):** registry paths resolve from the repo root; **but** `engine._load_canonical_model` (`models/canonical/`), `train_models.py` (deprecated, still writes old `models/xgboost_*` paths), and `StatusEngine` (`models/registry.json`) are **CWD-relative** — behavior differs by process CWD and in the Dockerfile (which copies `backend/` only, so canonical Logistic_24 won't load there).

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
| `rag/agents.py` | `CentralBankSentimentEngine` | Fed/BoJ sentiment + expectation gap | ⚠️ keyword scorer, **not** RAG (renamed in v2.7 to say so) |
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
                                            · scripts/audit_registry.py · scripts/apply_gate.py (NEW)
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

**Wiring:** `PITValidator` is executed via `backend/tests/test_pit_adversarial.py` (part of the 132 passing suite). Runtime forecast paths do not validate PIT; the canonical pipeline's three L4 registries are **`Stub*` placeholders** (`StubDataQualityRegistry`, `StubFreshnessRegistry`, `StubDriftRegistry`).

---

## 7. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Root: `backend/src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consumes Layer 3 §11.2 / Layer 4 §7 contracts. Packages: `contracts/`, `filter/`, `gates/`, `quality/` (+ `real_providers.py`), `registries/`, `risk/`, `sizing/`, `validation/`, `pipeline.py`.

```
PredictionArtifact (live via DecisionEngineAdapter) ─┐
RealFeatureStore (VIX, Yahoo) · MacroService +        │  PipelineInputs
  MacroDifferentialProvider · Stub DQ/Freshness/Drift └──────────▶ DecisionPipeline.build()
                                                                          │
     1. Signals        OOB → INVALID · 2. Regime+fusion → Direction
     3. Confidence · 4. Costs (VIX via FeatureStore P2) · 5. Economic filter (horizon-aware)
     6. Quality · 7. Hard gates (signal_validity P3, model_loaded-only availability)
     8. Sizing → Decision {...}
                                                                          │
     RiskEngine.compute (vol .30 · macro .25 · model .20 · regime .15 · edge .10) → RiskAssessment
```

**Verification:** `python -m pytest` from `backend/` (repo root + backend on `PYTHONPATH`) → **132 passed** across **13 files** (includes `test_risk_engine.py` 26, `test_signals_fusion.py` 17, `test_gates.py` 18, `test_quality.py` 10, `test_registries.py` 10, `test_pit_adversarial.py`, `test_canonical_macro_adapter.py`).

> **Runtime wiring (updated v2.7):** partial macro data no longer blocks decisions — `pipeline.py` feeds neutral `macro=0.0` when `required_data_missing`, and `gates/engine.py` keys Gate #1 availability on `model_loaded` only, demoting incomplete data to a **degraded warning**; **9/9 pairs** decide (5 actionable / 4 INSUFFICIENT_EDGE). VIX real via `RealFeatureStore` (Yahoo `^VIX`, 60 s TTL, failure → `UNAVAILABLE`). Remaining placeholders: `StubDataQualityRegistry`, `StubFreshnessRegistry`, `StubDriftRegistry` — **TODO v2.7**. `FakeFeatureStore` survives only in `validation/validate_integration.py` (test-only).

---

## 8. Frontend — contract-driven dashboard (`frontend/`)

**Stack:** React 18, TS 5, Vite 5 (5174, `minify off`), Tailwind 3, TanStack Query 5 (5-min staleTime), axios + raw fetch, date-fns, React Router 6 (v7 future flags on), Recharts 2. **Deploys:** Cloudflare Pages + Vercel. **Contract root:** `types/contracts.ts` mirrors Layer 1 v5.1 §7; canonical decision/risk/narrative/forecast-dashboard contracts declared in their hooks.

### 8.1 Routes (6 canonical pages, 11 hook modules)

| Path | Page | Data hooks |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence` |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice` (1y), `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair, 5)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)`, `useCanonicalNarrative(pair, 5)` |
| `/about` | AboutPage | (narrative) |

**Legacy pages removed** (v2.4 Sprint 8 `5bd324e`: Forecast, ForecastPageCanonical, Drivers, Evaluation, Status, Price, ModelComparison, TabNav; v2.5.1: HistoricalPage, mockup/, `_unused/`). **Hooks (11):** `useActivePair`, `useCanonicalDecision`, `useCanonicalRisk` (60 s refresh), `useCanonicalNarrative` (**NEW** — `apiClient`, 5 min staleTime), `useForecast`, `useForecastDashboard`, `useMarketIntelligence`, `usePerformancePeriod` (nav-only), `usePolling` (unused), `usePrice`, `useRanking`. Removed earlier: `useDrivers`, `useMacroContext`, `useFanChartData`, `useStatus`, `usePerformance`, `useModelComparison`, `useInterpretation`, `useHistorical`, `useMacro` (archived in `.trash-v2.5/`).

> **⚠️ Universe side-effect (v2.7):** `pairUniverseFromRanking()` uses the ranking's pairs when non-empty, and `/v1/fx/ranking` now returns only **USD/CHF**. On live data the frontend pair selector collapses to USD/CHF (9-pair `FX_PAIRS` fallback only when ranking is empty/errors). Canonical endpoints still serve all 9 pairs.

### 8.2 Presentational components

`common/*` (11 in barrel: Panel, EmptyState, ApiError, LoadingSpinner, UniverseSelector, ThemeProvider, StatusBadge, RegimeBar, NotAvailable, MetricsHelp, ErrorBoundary; **MarketConvention orphaned** — not imported), `decision/*` (**12** — DecisionHero, DecisionMetrics, DecisionShapPanel, DecisionValidity, EconomicBreakdown, HardGates, QualityMetrics, SignalFusion, **DecisionProvenance — WHO/WHAT/EVIDENCE/MODEL/DATA traceability, NEW**, **DecisionNarrative — LLM explanation block, NEW**), `forecast/*` (SpotCard, TrendCard, ForecastCard 30/60/90d), `global/*` (ActionableInfo w/ dynamic thresholds, IntelligenceBrief, LeadingSignals, RankingTable — enriched with Confidence/Quality/Position, MarketIntelligenceHero, ModelExplanation, PriceChartSignalIQ), `market/*` (MarketHero, HistoricalChart, **MarketMeta** — 5-column grid incl. **Volatility** block), `macro/*` (MacroHero, PolicyDifferentials, MacroMeta), `risk/*` (RiskScoreCard, RiskDriversPanel, RiskDriverBar), `layout/*`. **Sizing is rendered inline in DecisionPage** (no `SizingPanel` component).

### 8.3 Transport & contracts

- `services/api.ts` — axios `apiClient` (baseURL `import.meta.env.VITE_API_URL`, 30 s timeout, retry max 3 exp. backoff); `services/{forecast,ranking,performance,status}.ts` zero-transform adapters.
- ⚠️ 4 hooks (`usePrice`, `useRanking`, `useMarketIntelligence`, `useForecastDashboard`) use **raw `fetch`** with `VITE_API_URL || localhost:8000` — bypassing `apiClient`'s retry/backoff. `useCanonicalDecision`/`useCanonicalRisk` also raw-fetch; only the new `useCanonicalNarrative` uses `apiClient`.
- `types/contracts.ts` — frozen Layer 1 §7.1–7.7 mirror; `types/gaps.ts` `CONTRACT_GAP_MAP` (G1–G5). Canonical types (decision/risk/narrative/market-intelligence/dashboard) live in hook files; the decision contract gained `artifact.{prediction_id,model_id,model_version,regime_id,rag_signal_ids,feature_snapshot_id,dataset_id,feature_version,as_of,research_gate_status}` and `decision.{decision_id,prediction_id,timestamp,as_of,horizon_days}`.
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

> ✅ **Compile state (green):** `npm run typecheck` PASS, `npm run build` PASS (1,434 kB JS / 296 kB gzip — minify off), `npm test` **56 passed** (7 files). The `9d0b62f` break flagged in prior reports is **resolved**.

---

## 9. Deployment & runtime

| Target | Mechanism | Notes |
| --- | --- | --- |
| **Render** (backend) | Docker web service (`render.yaml`, plan free, `/health`) | python:3.12-slim, `PYTHONPATH=/app/backend`, `uvicorn layer1.main:app` :10000; env FRED/GROQ/ALPHA/TWELVE (`sync:false`). **Dockerfile copies only `backend/`** — containered app has no root `models/` (canonical `.joblib` + StatusEngine `models/registry.json` absent). |
| **Cloudflare Pages** (frontend) | Static-site mode; `_headers`, `_redirects` (`/* → /index.html 200`), `.cloudflareignore` | VITE_API_URL must be injected at build |
| **Vercel** (frontend) | `vercel.json` — Vite build → `dist`, SPA rewrites | VITE_API_URL must be injected at build |
| **Local** | `backend/docker-compose.yml` — port 10000, mounts `./models` + `./cache`; `start.sh`/`stop.sh` — uvicorn backend :8000 + vite preview :5173 | start/stop untracked + gitignored |

**Ops caveats (updated):**
- **`frontend/.env.production` is a comment-only placeholder for local dev** (`d917ca0`, 09-12) — it no longer pins `https://meridianfx.onrender.com`. Fetch-based hooks fall back to `localhost:8000`; the axios `apiClient` uses `VITE_API_URL` with no fallback (relative-URL requests). Deploy pipelines must inject `VITE_API_URL`; `.env.production.onrender` and `.env.local` are gitignored. The prior report's "RESTORED → onrender" note is stale.
- **Model paths still CWD-relative but improved:** registry paths are `backend/models/*.pkl` — resolve from repo root (and in Docker via `/app/backend/models`). Remaining mismatches: `engine._load_canonical_model` reads `models/canonical/*.joblib` (repo root only; absent in the `backend/`-only Docker image), `StatusEngine` reads `models/registry.json` (root), `train_models.py` (deprecated) still writes legacy paths.
- **Ranking is single-pair after the gate** — `/v1/fx/ranking` and `/v1/market-intelligence` reflect only USD/CHF; canonical decision/risk/narrative still cover 9/9.
- FRED real data requires `FRED_API_KEY`; without it the macro path serves simulated data (country providers refuse simulation and report `available=False`). Partial macro is now a **degradation**, not a decision blocker.
- `ADMIN_TOKEN` must be set for the narrative regenerate endpoint (else `503`).

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
└── DEUDA_TECNICA_v2.5.md    Engineering-debt baseline v2.5
```

| Artifact | Role |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row element→contract matrix (61 verified / 12 gap) |
| `CONTRACT_GAPS.md` (v2.0) | 16 unified gaps: G1–G9 + EC-1..4, RA, CA, DF-P |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | FREEZE WITH OPTIONAL GAPS, 0 blocking |
| `CONTRACT_VALIDATION.md` / `MIGRATION_REPORT.md` / `COMPONENT_MAPPING.md` | Prompt-1 audit PASS / 66 mockups / 100% mapping |
| `MACRO_COVERAGE.md` | Macro provider coverage & traceability baseline (v2.5) |
| `DEUDA_TECNICA_v2.5.md` | Debt ledger: resolved-in-v2.5 (frontend + backend), deferred (v2.5.1/v2.6/v3.0) |

**README (repo root):** quickstart updated (`5790e9b`) and a **`## Current Limitations`** section added (`2a53c98`) documenting the clamp: Stub* quality registries, registry gate status, horizon semantics (5d model + volatility scaling), LLM chain scope, sentiment analysis reality, no CI/CD. **Top header still claims v2.5.1** (HEAD `c878c53`).

**Governance workflow:** change request → traceability → gaps → freeze → validate. **Not** pushed through the loop (v2.7): the narrative layer (`/narrative`, `narrative_key`, SQLite, regenerate), partial-macro pipeline semantics, the registry promotion gate + 9-model deactivation, horizon-semantics change, `Stub*`/`CentralBankSentimentEngine` renames, the frontend Provenance/Narrative blocks — plus surfaces listed earlier (canonical decision/risk, RealFeatureStore, RiskEngine, ranking cache, walkforward/shadow research). **Latest tag is still `v2.5`** — no v2.6 or v2.7 tag despite 27 post-tag commits.

---

## 11. Verification matrix

| Layer | Command | Status (2026-09-14) |
| --- | --- | --- |
| Backend `src` decision engine (+ L4 PIT, RiskEngine) | `cd backend && PYTHONPATH=<repo>:<repo/backend> python -m pytest` | **132 passed** (13 files) ✅ |
| Layer 1 import | `python -c "import backend.layer1.main"` | pass ✅ |
| Layer 1 endpoints (smoke) | TestClient against running app | `/status` `HEALTHY`; `/market-intelligence` 200; `/ranking` 200 (1 pair after gate); `/forecast` 200 (live); `/performance` 200; `/canonical/{pair}/decision` 200 (9/9 pairs); `/canonical/{pair}/risk` 200 (real risk, VIX real); `/canonical/{pair}/narrative` 200 (cache-first LLM); `/price` 200 ✅ |
| Frontend typecheck | `cd frontend && npm run typecheck` | ✅ PASS |
| Frontend tests | `cd frontend && npm test` | **56 passed / 0 failed** (7 files) |
| Frontend build | `cd frontend && npm run build` | ✅ PASS (1,434 kB / 296 kB gzip — minify off) |

---

## 12. Known gaps & risks

1. **Legacy ranking collapsed to USD/CHF after the promotion gate** — `RankingEngine` iterates only registry-active models; `/v1/fx/ranking` and `/v1/market-intelligence` now surface 1 pair, and the **frontend pair selector inherits it** (`pairUniverseFromRanking`). The canonical pipeline still covers 9/9; there is no canonical ranking replacement yet.
2. **Canonical pipeline still runs 3 `Stub` L4 registries** — VIX is real (`RealFeatureStore`), but `StubDataQuality/Freshness/DriftRegistry` remain in `canonical.py` (renamed from `Fake*` for honesty; explicit TODO v2.7); quality gating is not yet real.
3. **Model path resolution is still CWD-relative and inconsistent** — registry `backend/models/*.pkl` resolves from repo root; `engine._load_canonical_model` (`models/canonical/`), `StatusEngine` (`models/registry.json`) and `train_models.py` (deprecated) are not aligned; the Render Dockerfile copies only `backend/`, so canonical Logistic_24 (and the root registry view) are absent in the container.
4. **Registry gate vs canonical runtime tension** — 9/10 legacy registry models are deactivated; only USD/CHF is servable from the registry, but the canonical Logistic_24 (the real decision engine) is **not tracked/measured in the same gate methodology**.
5. **Layer 3 tail** — `run_benchmarks.py` still crashes (`engine.xgb_model` AttributeError); `experiments/run.py` E0–E7 hardcoded; `arima.py` needs absent `statsmodels`; `artifacts/registry.py` schema incompatible with `backend/models/registry.json`.
6. **Layer 4 mostly unwired** — PIT runs only in tests; `pit_adapter.py`/`config`/`lineage` dead; `pit_tests.py` still corrupted (SyntaxError line 90).
7. **LLM chain partially wired** — narrative now drives `LLMFallbackManager` (Groq `qwen/qwen3.8-27b`, fallback never persisted); **but** `EconomicInterpreter` is still imported by no router and `/interpretation`'s `include_macro` block remains hardcoded (`NEUTRAL`/"Contexto macro no disponible"). `ADMIN_TOKEN` must be configured for regenerate.
8. **Hardcoded/simulated remnants** — `/interpretation` macro block; `/historical` random-synthetic fallback; `/performance` hardcoded `ece`/`max_drawdown`/`regime_performance`; `/price` hardcoded display labels; `/status` `database=NOT_CONFIGURED`; FRED simulated without key. `FORECAST_DATA` is dead code.
9. **Frontend dead/stale** — `usePolling` unused; `MarketConvention.tsx` orphaned; `utils/status.ts` only covered by tests; `.trash-v2.5/` (46 archived files) on disk; empty `src/pages/historical/` dir; 4+ hooks bypass `apiClient` (raw fetch, no retry — only `useCanonicalNarrative` uses `apiClient`); Spanish UI strings vs `lang="en"`; single-pair universe on live ranking.
10. **Deployment/governance debt** — Docker model-dir mismatch (canonical/StatusEngine paths absent in image); `frontend/.env.production` is an empty placeholder (production `VITE_API_URL` must be injected by pipelines); README header stale at v2.5.1; **no tag beyond `v2.5`** despite 27 post-tag commits; v2.7 surfaces not through the governance loop.
11. **Layer 1 dead subsystems** — `decision/` (own `DecisionEngine`), `data/forecast_data.py`, drivers-era adapter remnants (`get_drivers`, `to_drivers_response`), `routers/__init__` subtle import side-effect.
12. **Bundle size** — 1,434 kB JS chunk (296 kB gzip), `minify: false`, warning silenced by raised `chunkSizeWarningLimit`.
13. **Live-model caveats** — `/model-comparison` slow (3y walk-forward per pair); `/price`/`/forecast-dashboard` signals depend on model resolution + network (macros empty on failure).