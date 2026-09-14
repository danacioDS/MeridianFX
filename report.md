# Meridian FX — Repository Report

**Date:** 2026-09-14 · **Branch:** `main` (in sync with `origin/main`) · **History:** 174 commits (2026-08-25 → 2026-09-14) · **Head commit:** `e301138` "chore(registry): apply promotion gate to registry.json" · **Latest tag:** `v2.5` (2026-09-11; 27 post-tag commits — the v2.6.x line and this v2.7 cycle — remain untagged)

This is an analysis of the repository as it stands today: what it is, what it contains, how it is governed, its verification status, and its known gaps and risks.

---

## 1. What this is

**Meridian FX** is an FX ("foreign exchange") intelligence product whose guiding principle is:

> *"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."*

It answers its product questions through a **9-pair canonical universe** (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) with 30-day decision/risk horizons and 30/60/90-day forecasts:

| Question | Surface |
| --- | --- |
| What is happening in the market? | Global Overview + Market page |
| What does Meridian expect? | Market / Decision pages (canonical forecast) |
| Why? | Decision page (SHAP, economic breakdown) |
| Is it worth acting? | Decision page (economic filter, gates, actionable) |
| What could invalidate the signal? | Decision page (signal validity / hard gates) |
| How risky is it / how good has Meridian been? | Risk page / performance surface |

### What changed since the last report (2026-09-11)

This cycle (**2026-09-11 → 2026-09-14, 7 commits, HEAD `e300e3a` → `e301138`**) tightened the canonical pipeline (partial-data resilience, honest horizon semantics), added a **persistent LLM narrative layer** behind a new router, introduced a **registry promotion gate** that deactivated 9 legacy models, and extended the Decision page. It is effectively the **v2.7** engineering pass, though nothing is tagged.

1. **Partial-macro resilience (v2.7 pipeline, `c31f65b`).** `DecisionPipeline.build` now feeds a neutral `macro=0.0` when `required_data_missing`, the early return that short-circuited the whole pipeline is gone, and `HardGateEngine` keys availability on `model_loaded` only — `required_data_missing` demotes to a **degraded warning** instead of `MODEL_UNAVAILABLE`. Result: **9/9 pairs produce real decisions** (5 actionable, 4 `INSUFFICIENT_EDGE`) and all 7 gates run for every pair. This closes the USD/CNY `MODEL_UNAVAILABLE` false positive caused by `PARTIAL` macro status. ✅
2. **Persistent LLM narratives (v2.7 narrative, `621e5be` + `f0179ee`).** New `backend/layer2/narrative/` (repository · generator · service · prompt_builder) with **`GET /v1/canonical/{pair}/narrative`** (cache-first) and **`POST /v1/canonical/{pair}/narrative/regenerate`** (admin, `X-Admin-Token`). A stable `narrative_key` (who/what/evidence/model/data) invalidates the **no-TTL SQLite cache** only when the logical decision changes; Groq `qwen/qwen3.8-27b` via `LLMFallbackManager` is primary, the deterministic fallback is **never persisted** so the next request retries the LLM. **This partially revives the previously fully-unwired LLM layer** — `LLMFallbackManager` is now reachable through the narrative router (though `EconomicInterpreter` and the `/interpretation` macro block still are not). ✅
3. **Honest horizon semantics (v2.7, `2a53c98`).** `horizon_days` default **30 → 5**, matching the **Logistic_24 training horizon** — now threaded into the economic filter (was hardcoded 30) and the `expected_return` volatility scaling `(2P−1)·σ·√(h/365)`; the `NameError` that previously forced fallback is fixed and a duplicate calculation removed. The API now documents that `horizon_days` is a **volatility-scaling factor, not a per-horizon model**; true 5/30/90d models are deferred to v3.0. ✅
4. **Registry promotion gate (v2.7, `2a53c98` + `e301138`).** `layer2/models/registry.py` now enforces `MIN_AUC=0.52` + `MIN_N_SAMPLES=300` before a model activates; `registry_adapter.py` double-defends the lifecycle; `model_selector.py` serves **DEPLOYED only**; new `scripts/audit_registry.py` + `scripts/apply_gate.py`. Applied retroactively: **9/10 legacy registry models deactivated — only USD/CHF (auc 0.733, n=319) remains active**. The canonical decision pipeline (Logistic_24, untracked) is unaffected, but the **legacy `/v1/fx/ranking` surface collapses to 1 pair** (RankingEngine iterates only registry-active pairs), which also narrows the frontend pair universe (see §7). ⚠️
5. **Honesty renames + deprecated tools (v2.7, `2a53c98`).** `Fake*Registry` → **`Stub*Registry`** (they are placeholders, not fakes), `CentralBankRAGEngine` → **`CentralBankSentimentEngine`** (keyword scorer, not RAG), `train_models.py` marked **DEPRECATED**. README gains a **`## Current Limitations`** section documenting the stub registries, the gate, horizon semantics, LLM scope, sentiment reality, and the absence of CI/CD. ✅
6. **Frontend provenance + narrative blocks (v2.7, `f0179ee`).** New `DecisionProvenance` (WHO/WHAT/EVIDENCE/MODEL/DATA traceability) + `DecisionNarrative` components, new **`useCanonicalNarrative`** hook (via `apiClient`), `useCanonicalDecision`/`useCanonicalRisk` default **5d**, and contract extensions (`artifact`: `prediction_id`, `model_id`, `model_version`, `regime_id`, `rag_signal_ids`, `feature_snapshot_id`, `dataset_id`, `feature_version`, `as_of`, `research_gate_status`; `decision`: `decision_id`, `prediction_id`, `timestamp`, `as_of`, `horizon_days`). ✅
7. **Config & hygiene (`5790e9b`, `5c303de`).** README quickstart rewritten; `.gitignore` adds `backend/venv/`; `requirements.txt` adds `python-dotenv`. ✅

**Balance sheet:** the headline gains are a pipeline that now **decides on all 9 pairs**, a **persistent, retry-able LLM narrative** behind a cache-first endpoint, and an honest, gate-enforced registry. The costs: the legacy **ranking surface (and the frontend universe it drives) shrinks to USD/CHF** with no canonical ranking replacement, `frontend/.env.production` no longer pins the production API URL, the Docker image still lacks root `models/`, the three **stub** L4 registries survive (now honestly named), the ~1.4 MB unminified bundle persists, and none of the new surfaces (pipeline resilience, narrative layer, promotion gate, provenance blocks) have gone through the governance freeze loop.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs + governance + model_selection + MACRO_COVERAGE
│                                + DEUDA_TECNICA_v2.5.md
├── backend/                     Python backend
│   ├── layer1/                  FastAPI delivery API — 12 routers (canonical decision+risk+narrative+regenerate,
│   │                            intelligence, performance, price, forecast-dashboard, model-comparison…; NO /drivers)
│   ├── layer2/                  Live engine — Logistic_24 loader + XGBoost/registry, SHAP, data providers,
│   │                            FRED macro (21 provider files), ranking (60s cache, 1 active pair), status,
│   │                            pipeline_bridge, narrative (NEW — SQLite-persisted LLM layer)
│   ├── layer3/                  Research layer — artifacts, evaluation, experiments, models, regime,
│   │                            sentiment (CentralBankSentimentEngine), gate
│   ├── layer4/                  Data-quality layer — PIT validator, config policies, lineage
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, RiskEngine,
│   │                            RealFeatureStore, Stub* registries, 132 tests)
│   ├── models/                  models/registry.json (10 entries — 1 ACTIVE, 9 below gate; backend/models/*.pkl)
│   ├── tests/                   Backend pytest suite (13 files, 132 tests)
│   ├── pyproject.toml · requirements.txt · docker-compose.yml
├── models/                      Root artifacts: canonical/ (10 Logistic_24 .joblib + metadata),
│                                experimental/ (EUR/USD h10, USD/BOB h20), registry.json (== backend copy)
├── Dockerfile · render.yaml · runtime.txt
├── start.sh · stop.sh           Local run scripts (untracked + gitignored)
├── train_models.py · train_canonical_model{,_extended}.py · train_multi_pairs.py
├── train_experimental_models.py · evaluate_all_pairs.py · final_holdout.py
├── research_gate.py · research_gate_results{,v2}.json · research_validation_*
├── research_walkforward.py + 8 variants + *_results.json
├── shadow_test.py · shadow_test_simple.py · monitor_daily.py · monitor_model.py
├── scripts/audit_consistency.py · scripts/audit_registry.py · scripts/apply_gate.py   REGISTRY GATE (NEW)
├── cache/ · logs/ · venv/                  Runtime state (gitignored; backend/venv/ now ignored too)
├── frontend/                    React + TypeScript + Vite contract-driven dashboard
│   ├── .env.production          Comment-only placeholder for local dev (see §9)
│   ├── src/pages/               Global · Market · Macro · Risk · Decision · About (6 canonical pages)
│   ├── src/hooks/               11 hooks incl. useCanonicalDecision, useCanonicalRisk, useCanonicalNarrative
│   ├── src/components/decision/ DecisionHero, Provenance (NEW), Narrative (NEW), HardGates, …
│   ├── src/types/contracts.ts   Layer 1 §7 mirror (+ canonical contracts inside hooks)
│   └── vercel.json · _headers · _redirects
├── .env                         Runtime secrets + config (keys present, gitignored)
├── README.md                    Product overview + quickstart (updated) + "Current Limitations" section
├── report.md                    This document
└── architecture.md              System architecture (2026-09-14)
```

> **Working-tree hygiene:** `main` in sync with `origin/main`, **clean**. Remaining runtime/ignored noise: `venv/`, `backend/venv/`, `cache/`, `logs/`, `frontend/.trash-v2.5/` (46 archived files on disk).

---

## 3. Backend — the two engines (now three production surfaces)

| Package | Role | Hygiene |
| --- | --- | --- |
| `backend/src/meridian_fx/decision/` | Contract-governed Decision Engine (frozen to L2 spec) + **RiskEngine** | verified ✅ (132 tests) |
| `backend/layer2/` | Live engine the API actually runs (data + ML + status + ranking cache + bridge + **narrative**) | wired into most routers |
| `backend/layer3/` | Research/evaluation layer (models, walk-forward, research gate, sentiment) | wired via `model_comparison`; `run_benchmarks.py` broken |
| `backend/layer4/` | Data-quality/PIT layer | only `PITValidator` is referenced (by tests) |

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Frozen against `docs/Product_specification/Layer_02.md` v3.4.1. **Verification:** 132 passed across 13 files (from `backend/` with repo root + backend on `PYTHONPATH`). This cycle the **pipeline became partial-data tolerant**: `DecisionPipeline.build` neutralizes the macro signal (`macro=0.0`) when `required_data_missing` and `HardGateEngine` reports availability from `model_loaded` only, turning incomplete macro data into a **degradation warning** instead of a `MODEL_UNAVAILABLE` rejection. The `Fake*` quality registries are renamed **`Stub*`** (honest placeholders, still TODO v2.7); `RealFeatureStore` (Yahoo `^VIX`) unchanged.

### 3.2 `layer2/` — the live engine

- **Model resolution:** `DecisionEngine` loads **Logistic_24 canonical models** per pair via `_load_canonical_model` (canonical `.joblib` first), then registry models (`backend/models/*.pkl`) for xgb/logistic (now **only USD/CHF is active** after the gate), then heuristics. PIT `policy_diff` via `MacroService.get_historical_policy_rate`.
- **Horizon semantics (changed):** `horizon_days` default is **5** (Logistic_24's training horizon) across adapters, bridge and routers; the economic filter consumes `horizon_days` (not hardcoded 30); `expected_return = (2P−1)·σ·√(h/365)`.
- **Ranking cache + gate side-effect:** `RankingEngine` caches 60 s, but now iterates **only registry-active pairs → `/v1/fx/ranking` serves USD/CHF only**.
- **Narrative layer (NEW):** `backend/layer2/narrative/{repository,generator,service,prompt_builder}.py` — SQLite-persisted (`backend/cache/narratives.db`), stable `narrative_key`, no TTL, Groq `qwen/qwen3.8-27b` via `LLMFallbackManager`, deterministic fallback never persisted.
- **Pipeline bridge / status / data failover / macros:** unchanged in role; `StatusEngine` still reads CWD-relative `models/registry.json` (works from repo root).

**Key observation:** the canonical-logistic path remains the *primary* model source; registry is secondary and — after the promotion gate — nearly empty (1 active). Both still resolve **CWD-relative**, and the Docker image copies only `backend/`, so `models/canonical/` (and the root `models/registry.json` StatusEngine needs) do not exist inside the container.

---

## 4. Backend — Layer 1 FastAPI delivery API (12 routers, deployed)

`backend/layer1/` is a **real FastAPI app** (v1.0.0). CORS covers localhost/Render/Vercel/Cloudflare/ngrok + `*`. **12 routers** plus `/` and `/health` (the **`drivers` router was removed** earlier in v2.6.3; **`narrative` is new** this cycle). All routes verified 200 via TestClient on 2026-09-11; 132 backend tests green on 2026-09-14.

### 4.1 Endpoints — correctness updated per running service

| Method | Path | Source / notes | Health |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root + health | ✅ |
| GET | `/v1/status` | real `StatusEngine` | ✅ (`HEALTHY`) |
| GET | `/v1/market-intelligence` | deterministic English narrative over `RankingEngine` — **now single-pair** (USD/CHF) | ✅ / ⚠️ |
| GET | `/v1/fx/ranking` | `RankingEngine`, live, **60 s cache** — **1 pair (USD/CHF)** after the gate | ✅ / ⚠️ |
| GET | `/v1/canonical/{pair}/decision` | `DecisionPipeline` via `PipelineBridge` — VIX real, 3 **Stub** registries, `horizon_days` default 5, **9/9 pairs** | ✅ 200 — 5 actionable / 4 INSUFFICIENT_EDGE |
| GET | `/v1/canonical/{pair}/risk` | `RiskEngine` (same bridge) | ✅ 200 — real risk |
| GET | `/v1/canonical/{pair}/narrative` | **NEW** — cache-first persistent LLM narrative (SQLite, no TTL, Groq primary) | ✅ |
| POST | `/v1/canonical/{pair}/narrative/regenerate` | **NEW** — admin regeneration (`X-Admin-Token: $ADMIN_TOKEN`; 503 if unconfigured) | ✅ |
| GET | `/v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` — Logistic_24 → heuristic | ✅ live (lineage block hardcoded) |
| GET | `/v1/fx/performance/{pair}?period=` | `models/registry.json` metrics + hardcoded derivations | ✅ / ⚠️ derived |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (random-synthetic fallback) | ✅ / ⚠️ fallback |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | inline rule-based narrative over live forecast; macro hardcoded | ⚠️ rule-based |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history + XGBoost signal via `_get_model_for_pair` | ✅ live |
| GET | `/v1/fx/{pair}/forecast-dashboard` | **live** — spot, trends, volatility, Logistic_24/XGBoost 30/60/90d, macro | ✅ (network) |
| GET | `/v1/fx/{pair}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding` (in-memory cache) | ✅ 200 (slow) |

> **Changed this cycle:** `canonical` default `horizon_days` **30 → 5**; `narrative` routers added (12 total); `Fake*Registry` → `Stub*Registry`. **Removed earlier:** `/drivers` (`82c9e80`); `FORECAST_DATA` is dead code. **LLM layer:** `LLMFallbackManager` is **now reachable** via the narrative endpoint (Groq `qwen/qwen3.8-27b`); `EconomicInterpreter` is still unimported by any router and `/interpretation`'s `include_macro` still returns a hardcoded `NEUTRAL`/"Contexto macro no disponible" block.

### 4.2 Model resolution now

The canonical Logistic_24 cover all 9 pairs and are the **primary** decision source; registry paths are normalized to `backend/models/*.pkl` but **9/10 are below the promotion gate and deactivated** — only USD/CHF remains servable from the registry (ranking). Remaining path hazards: the Docker image (no root `models/`), `train_models.py` (deprecated, still writes legacy `models/*.pkl` paths), and `StatusEngine`'s CWD-relative `models/registry.json`. `USD/CNY` `MODEL_UNAVAILABLE` on partial macro is **resolved by design** — partial macro now degrades instead of invalidating (9/9 pairs decide).

### 4.3 Supporting modules

- **`adapters/`** — `DecisionEngineAdapter` (legacy engine → `PredictionArtifact`, used by bridge) and `DecisionAdapter` (`to_performance_response` in use; drivers-era methods dead).
- **`routers/canonical.py`** — pipeline = `RealFeatureStore()` + `StubDataQualityRegistry(0.90)` + `StubFreshnessRegistry(3.0)` + `StubDriftRegistry(0.05)`; TODO marker for v2.7 real registries.
- **`routers/narrative.py`** — constructs `SqliteNarrativeRepository` + `NarrativeGenerator` + `NarrativeService` singletons at import time; reuses the canonical `bridge`.
- **`data/forecast_data.py`** — dead; **`llm/`** — now partially reached via narrative (`LLMFallbackManager`); **`decision/`** — dead.

---

## 5. Backend — Layer 3 research layer (`backend/layer3/`)

The **only** live coupler remains `layer1/routers/model_comparison.py` (working). Nothing in `layer2` imports it. State is largely unchanged from the last report:

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | research model registry | Persist research-approved models | ✅ implemented — schema **incompatible** with `backend/models/registry.json` |
| `evaluation/walk_forward.py` | `evaluate`, `evaluate_expanding` | Rolling/expanding backtest | ✅ `evaluate()` fixed and healthy |
| `evaluation/run_benchmarks.py` | CLI runner | Per-window benchmark tables | ❌ **still crashes** — `engine.xgb_model` AttributeError |
| `evaluation/model_evaluator.py` | `ModelEvaluator` | Simple OOS (last 20%) | ⚠️ random-fallback on predict failure |
| `experiments/run.py` | E0–E7 | Sequential experiments | ❌ still **hardcoded** metrics |
| `experiments/real_experiments.py` | `RealExperimentRunner` | Real walk-forward E0–E7 | ⚠️ unblocked but unverified |
| `macro/regime.py` | `MacroRegimeEngine` | Regime classification | ✅ works |
| `models/arima.py` | `ARIMAModel` | ARIMA control | ⚠️ unrunnable — `statsmodels` absent |
| `models/elastic_net.py` / `models/ensemble.py` | control models | ✅ works | |
| `rag/agents.py` | `CentralBankSentimentEngine` (`was CentralBankRAGEngine`) | Fed/BoJ sentiment | ⚠️ keyword scorer, not real RAG |
| `research_gate/*` | gate/real_gate/full_gate | 4-gate approval | ⚠️ `gate.py` works; `full_gate.py` passes `features={}` |

### 5.1 Research Gate pipeline (repo root, unchanged)

`research_validation_test.py / final_holdout.py / evaluate_all_pairs.py` → `research_gate.py` → `research_gate_results_v2.json` → `train_experimental_models.py` → `models/experimental/` (EUR/USD h10 **CANDIDATE**; USD/BOB h20 **CANDIDATE_WITH_WARNINGS**). Caveats unchanged: PR-AUC rule declared but not computed; experimental models unconsumed by the API; v2 results file untracked.

### 5.2 Canonical-model research, walkforward & shadow testing (repo root)

Canonical training (`train_canonical_model*`, `train_multi_pairs`) → `models/canonical/` (10 `.joblib` + 2 metadata); walkforward suite (`research_walkforward.py` + 8 variants → `research_walkforward_*_results.json`); shadow tests (`shadow_test*.py` → `shadow_test_results_*.json`); monitoring (`monitor_daily.py`, `monitor_model.py`, `monitor_history.json`). All research, not wired into the runtime (except the canonical `.joblib` now loaded by `engine._load_canonical_model`).

---

## 6. Backend — Layer 4 data-quality layer (unchanged)

| Area | Purpose | Maturity |
| --- | --- | --- |
| `quality/pit_validator.py` — `PITValidator` (PIT-1…PIT-7) | Point-in-Time compliance | ✅ correct (exercised by `test_pit_adversarial.py`) |
| `config/policies.py` | Versioned config | ✅ implemented, **standalone** |
| `lineage/models.py` | Provenance | ✅ implemented, **standalone** |
| `tests/pit_tests.py` | layer-4 unit tests | ❌ still **syntactically corrupted** (SyntaxError line 90) |

**Live wiring:** only `backend/tests/test_pit_adversarial.py` exercises `PITValidator`. Runtime forecast paths still don't validate PIT; the canonical pipeline's three L4 registries are **stubs**.

---

## 7. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 · TS 5 · Vite 5 (5174) · Tailwind 3 · TanStack Query 5 · axios · date-fns · React Router 6 · Recharts 2**. `src_backup_espanol/` (the Spanish backup) and all legacy pages are gone.

### 7.1 Routes & composition (6 pages, 11 hooks)

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence` |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice` (1y), `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair, 5)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)`, `useCanonicalNarrative` |
| `/about` | AboutPage | (narrative) |

Removed: Forecast/Drivers/Evaluation/Status/Price/Models pages + `TabNav` (v2.4 Sprint 8), HistoricalPage/mockup/`_unused` (v2.5.1), `services/drivers.ts` (v2.6.3). **Hooks (11):** `useCanonicalDecision`, `useCanonicalRisk`, `useCanonicalNarrative` (NEW — `apiClient`, 5 min staleTime), `useForecastDashboard`, `useMarketIntelligence`, `usePrice`, `useRanking`, `useActivePair`, `useForecast`, `usePerformancePeriod` (nav), `usePolling` (**unused**). Canonical decision/risk/narrative contracts are declared inside their hooks; `types/contracts.ts` remains the frozen Layer 1 §7 mirror; `types/gaps.ts` `CONTRACT_GAP_MAP` G1–G5.

**⚠️ Pair universe side-effect:** `pairUniverseFromRanking(ranking)` returns the ranking's pairs when non-empty — and `/v1/fx/ranking` now returns **only USD/CHF**. The frontend universe thereby collapses to USD/CHF on live data (falling back to the 9-pair `FX_PAIRS` only when ranking is empty/errors). The canonical decision/risk/narrative endpoints still serve all 9 pairs; the frontend simply no longer offers the other 8 in the selector while ranking is single-pair.

### 7.2 Presentational surface

`common/*` (11 exported), `decision/*` (**12** — DecisionHero, DecisionMetrics, DecisionShapPanel, DecisionValidity, EconomicBreakdown, HardGates, QualityMetrics, SignalFusion, **DecisionProvenance, DecisionNarrative**), `forecast/*`, `global/*` (ActionableInfo, IntelligenceBrief, LeadingSignals, RankingTable, PriceChartSignalIQ…), `market/*` (MarketHero, HistoricalChart, MarketMeta w/ Volatility), `macro/*` (MacroHero, PolicyDifferentials, MacroMeta), `risk/*` (RiskScoreCard, RiskDriversPanel, RiskDriverBar), `layout/*`. Decision page renders **sizing inline**, the new **Provenance** block (WHO/WHAT/EVIDENCE/MODEL/DATA), and the **Narrative** block. Orphans: `common/MarketConvention.tsx`, `usePolling`, `utils/status.ts` (test-only).

### 7.3 Verification — all green

| Check | Previous report (09-11) | Now (09-14) |
| --- | --- | --- |
| Backend pytest | 132 passed / 13 files | **132 passed** ✅ (13 files) |
| Frontend typecheck | ✅ PASS | ✅ **PASS** |
| Frontend tests | 56 passed / 0 failed (7 files) | **56 passed / 0 failed** ✅ (7 files) |
| Frontend build | ✅ PASS (1,422 kB / 293 kB gzip) | ✅ **PASS** (1,434 kB / 296 kB gzip, minify off) |

**Root cause of the old break (still resolved):** the `9d0b62f` `UniverseSelector`/`useActivePair` refactor was fully migrated — no compile errors remain.

### 7.4 Remaining frontend caveats

Spanish UI strings with `lang="en"`; 4 hooks use raw `fetch` (no retry/backoff) instead of `apiClient` (the new `useCanonicalNarrative` correctly uses `apiClient`, while `useCanonicalDecision`/`useCanonicalRisk` still use raw fetch); bundle 1,434 kB unminified with warning suppressed; `.trash-v2.5/` (46 archived files) still on disk; `usePolling` and `MarketConvention` orphaned; **single-pair universe on live ranking** (see 7.1).

---

## 8. Models & training

- **Production registry** (`models/registry.json`, identical at root/backend): **10 models, `v1.0`** — 9 XGBoost + 1 logistic (USD/JPY), paths normalized to `backend/models/*.pkl`. **After the v2.7 promotion gate (MIN_AUC 0.52, MIN_N_SAMPLES 300): 9/10 deactivated — only USD/CHF xgb (auc 0.733, n=319) is `active: true`**; in-registry AUCs 0.380–0.733.
- **Canonical Logistic_24** (`models/canonical/`, v2.0-era, the runtime's **primary** decision model): 9 per-pair `.joblib` (+ extended, unloaded) with PIT `policy_diff`, loaded by `engine._load_canonical_model`, trained on a **5-day forward target**. Not in the registry.
- **Experimental** (`models/experimental/`): USD/BOB h20 (CANDIDATE_WITH_WARNINGS) + EUR/USD h10 (CANDIDATE) via the v2 gate — **unconsumed** by the API.
- `backend/layer2/models/` — `registry.py` now enforces the promotion gate + lifecycle; `model_selector.py` filters `DEPLOYED` only; `registry_adapter.py` double-defends. `trainer.py` empty; **`train_models.py` deprecated** (still writes the legacy `models/*.pkl` convention).

---

## 9. Deployment & operations

| Target | What | Evidence |
| --- | --- | --- |
| **Render** (backend) | Docker web service, dockerfile, `/health`, `uvicorn layer1.main:app` :10000 | `render.yaml`; `Dockerfile` (python:3.12-slim, `PYTHONPATH=/app/backend`); env FRED/GROQ/ALPHA/TWELVE |
| **Cloudflare Pages** (frontend) | static SPA, `_headers`, `_redirects`, `.cloudflareignore` | `frontend/*` |
| **Vercel** (frontend) | Vite build → `dist`, SPA rewrites | `frontend/vercel.json` |
| **Local** | `docker-compose.yml` (:10000, mounts models+cache); `start.sh` (uvicorn :8000) / `stop.sh` | untracked + gitignored |

Operations caveats (updated):
- **`frontend/.env.production` is now a comment-only placeholder** ("temporalmente vacío para desarrollo local", `d917ca0`) — the prior report's "RESTORED → onrender" note is stale. Fetch-based hooks fall back to `localhost:8000`; `apiClient` uses `VITE_API_URL` with no fallback (relative-URL requests). Deploy pipelines (Cloudflare/Vercel) must inject `VITE_API_URL` at build time; `.env.production.onrender` and `.env.local` are gitignored.
- **Docker image gap (unchanged, top ops risk):** `Dockerfile` copies only `backend/`, so the containered app has no root `models/` — `_load_canonical_model` (`models/canonical/*.joblib`), `StatusEngine` (`models/registry.json`) fail inside the image; the registry xgb path (`backend/models/*.pkl`) does resolve.
- **Ranking exposes a single pair in production after the gate** — USD/CHF only; no canonical ranking backend yet (see §7.1).
- Local smoke (`TestClient`, 2026-09-11 / pytest 2026-09-14): `/v1/status` `HEALTHY`; 132 backend tests green.

---

## 10. Models of verification & governance (unchanged)

The repo remains **prompt-first** (`docs/Prompts/`) with **Contract/** policing fidelity. Frozen specs and freeze artifacts unchanged (L1 v5.1, L2 v3.4.1, L3 v5.0, L4 v3.1.1; traceability 61/12; gaps 16; freeze 0 blocking). `docs/DEUDA_TECNICA_v2.5.md` and `MACRO_COVERAGE.md` unchanged.

> **Not** pushed through the traceability → gaps → freeze loop: the narrative layer (`/narrative`, `narrative_key`, SQLite), the partial-macro pipeline semantics, the registry promotion gate + deactivation of 9 models, horizon-days 5 semantics, `Stub*` renames, the **canonical frontend pages** (Market/Macro/Risk/Decision incl. Provenance/Narrative), plus all surfaces already listed before (canonical decision/risk, RealFeatureStore, RiskEngine, ranking cache, walkforward/shadow research, v2.5.1 cleanup). **No tag beyond `v2.5`**; README top header still claims v2.5.1 (though quickstart + Current Limitations were added this cycle).

---

## 11. Current status & known gaps

**Green**
- Backend pytest **132/132** (13 files); frontend typecheck/build/tests **all pass** (56/56).
- **Canonical pipeline decides for 9/9 pairs** — partial macro now degrades instead of blocking (`USD/CNY` `MODEL_UNAVAILABLE` false positive closed).
- **Persistent LLM narratives live:** cache-first `/v1/canonical/{pair}/narrative` (SQLite, no TTL, Groq `qwen/qwen3.8-27b`, fallback never persisted) with admin regenerate; Decision page renders Provenance + Narrative.
- **Registry promotion gate enforced:** `audit_registry.py`/`apply_gate.py`, `DEPLOYED`-only selection, 9/10 legacy models deactivated.
- **Honest naming + docs:** `Stub*Registry`, `CentralBankSentimentEngine`, `train_models.py` deprecated, README `## Current Limitations`.
- `main` in sync with `origin/main`, working tree clean; `backend/venv/` + `python-dotenv` handled.

**Red / attention**
1. **Legacy ranking collapsed to USD/CHF** after the gate — and the **frontend pair selector inherits it** (universe = ranking pairs). No canonical ranking backend yet; the visible product currently offers a single pair on live data.
2. **Docker model gap:** the image copies only `backend/` → canonical Logistic_24 (`models/canonical/`) and `StatusEngine`'s `models/registry.json` unresolvable inside the container.
3. **Canonical pipeline still runs 3 Stub L4 registries** (DQ/Freshness/Drift; TODO v2.7) — VIX real, quality gating not.
4. **Model-path convention still split/CWD-relative:** `engine` canonical vs registry vs `StatusEngine` paths diverge; `train_models.py` (deprecated) still writes legacy paths.
5. **Layer 3 tail** — `run_benchmarks.py` crashes (`engine.xgb_model`); `run.py` E0–E7 hardcoded; ARIMA unrunnable; L3 registry schema incompatible.
6. **Layer 4** unwired; `layer4/tests/pit_tests.py` still corrupted.
7. **LLM partial:** narrative now uses `LLMFallbackManager` (Groq), but `EconomicInterpreter` is still unimported and `/interpretation` still has a hardcoded macro block.
8. **Hardcoded/simulated remnants** — `/historical` random fallback; `/performance` hardcoded ece/max_dd/regime table; `/status` `database=NOT_CONFIGURED`; FRED simulated without key; dead `FORECAST_DATA`/`layer1/decision/`/drivers adapter methods.
9. **Frontend debt** — 4 hooks raw-fetch (no retry); `usePolling` + `MarketConvention` orphans; `.trash-v2.5/` on disk; Spanish strings / `lang="en"`; 1,434 kB bundle unminified; single-pair universe on live ranking.
10. **Governance/ops lag** — newest surfaces (narrative, pipeline resilience, promotion gate, provenance blocks) not through the freeze loop; **no tag beyond v2.5**; README header stale at v2.5.1; production `VITE_API_URL` not pinned in the repo.

---

## 12. Recommendations

1. **Restore a 9-pair surface before it ships as-is:** either back the ranking/market-intelligence endpoints with the canonical pipeline (9/9 decision/risk/narrative) or keep the frontend universe on canonical/`FX_PAIRS` independent of the legacy registry ranking.
2. **Finish the canonical pipeline (v2.7→v2.8):** replace the three `Stub` L4 registries with real `PITValidator`-backed, freshness/drift-aware providers; then push the canonical logistic path + `/risk` + narrative + RealFeatureStore through the governance loop.
3. **Fix model resolution & Docker (top ops risk):** copy `models/` into the Docker image (or mount it) so `models/canonical/*.joblib` and `models/registry.json` resolve in Render; delete or align `train_models.py`; add a resolution-union smoke test for all 9 pairs across repo-root and container CWDs.
4. **Cut the Layer 3/4 tail:** port `run_benchmarks.py` to `_get_model_for_pair` (or delete), replace hardcoded `run.py`, decide on `statsmodels`, repair `layer4/tests/pit_tests.py`, reconcile L3 registry schema.
5. **Resolve the LLM question fully:** either wire `EconomicInterpreter` into `/interpretation` or delete it; remove the hardcoded `include_macro` block; make the narrative layer's `ADMIN_TOKEN`/SQLite path deployment-aware (Postgres/Neon migration is designed in the Protocol).
6. **Frontend hardening:** unify transport (remaining 4 fetch hooks → `apiClient`), delete `.trash-v2.5/` + orphans (`usePolling`, `MarketConvention`), fix `lang="en"` vs Spanish copy, and consider code-splitting + `minify` for the 1.4 MB bundle.
7. **Close the ops/governance book:** pin `VITE_API_URL` for production builds (un-block the committed `.env.production`), tag the v2.6/v2.7 line (or bump README/versioning to the real HEAD), re-add a post-v2.5 debt ledger, and route the canonical surfaces + research bundle through traceability → gaps → freeze → validation.
8. **Re-run the audit loop** (`scripts/audit_consistency.py`, plus the new `scripts/audit_registry.py`) after the v2.7→v2.8 work; keep the repo-hygiene invariants (no backups, no Spanish backup tree, singleton registry).