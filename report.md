# Meridian FX — Repository Report

**Date:** 2026-09-11 · **Branch:** `main` (in sync with `origin/main`) · **History:** 163 commits (2026-08-25 → 2026-09-11) · **Head commit:** `e300e3a` "v2.6.6-fix: integrar bloque Volatility en MarketMeta" · **Latest tag:** `v2.5` (2026-09-11; the 9 v2.6.x commits are post-tag, untagged)

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

### What changed since the last report (2026-09-09)

This cycle (**2026-09-09 → 2026-09-11, 68 commits, tag `v2.0` → HEAD `e300e3a`**) was a **full product re-platform**: the backend gained dynamic macro semantics, expected-return/volatility/thresholds, and a Risk Assessment Engine; the frontend was rebuilt around the **canonical pipeline**; the repo was cleaned; and the frontend finally compiles again.

1. **Backend v2.1–v2.3 — dynamic decisions + risk.** `v2.1` (`591af11`) added `inflation_differential` + resilient FRED fallback; `v2.2`/`v2.2.1` made **expected return, volatility, and thresholds configurable** and added sizing config (`BASE_SIZE`, `MAX_EXPOSURE`, `HISTORICAL_RELIABILITY`); `v2.3` (`27c90ec`) shipped the **Risk Assessment Engine** (`src/.../risk/engine.py`: vol .30 / macro .25 / model .20 / regime .15 / edge .10, LOW/MODERATE/HIGH/EXTREME) plus **`GET /v1/canonical/{pair}/risk`**. ✅
2. **Frontend v2.4 — canonical re-platform (the headline).** Sprints 1–8 replaced the old 8-page dashboard with **6 canonical pages — Global · Market · Macro · Risk · Decision · About** — each E2E (hook → component → page): `useCanonicalDecision`, `useCanonicalRisk`, `useMarketIntelligence`, `useForecastDashboard`, `usePrice`, `useRanking`; Decision page renders sizing inline; Risk page renders 5-driver risk; 7 legacy pages + `TabNav` removed (`5bd324e`); self-hosted fonts (Google Fonts dropped), `EmptyState`, mobile responsive, query `staleTime` 5 min. **The v2.4/ex-Sprint work also closed the long-standing compile break: `npm run typecheck`, `build`, and all tests are green.** ✅
3. **Frontend canonical contracts (v2.5 Fase 3).** `ActionableInfo` uses dynamic thresholds; Decision page renders **Economic Breakdown + Hard Gates (Fase 3.1), Quality Metrics + Signal Fusion (Fase 3.2)**; Global page drives on canonical data (3.8); MacroRegime deduped (MacroPanel deleted); hooks/contracts consolidated and typed (F6); Market page consumes `PriceResponse` (F7). ✅
4. **Backend polish (v2.5.2→v2.6).** Header version + expected-return fixes; ranking cache **TTL 60 s** (`9639ef4`; cold ~5.4 s → warm 0.001 s); favicon; **VIX real in the canonical pipeline** via `RealFeatureStore` (`de05ec6` — Yahoo `^VIX`, replacing `FakeFeatureStore`); **`/drivers` endpoint removed** (`82c9e80`, deleting the hardcoded `macro_drivers` VIX 16.8 / RA 72 / RISK_ON); `RankingTable` enriched (Confidence/Quality/Position); `IntelligenceBrief` on Global; Volatility block in `MarketMeta` (`e300e3a`). ✅
5. **Repo hygiene + model normalization (v2.5.1).** `e31ed31` deleted `src_backup_espanol/` (~130 files), `mockup/`, `_unused/`, the 13.9 MB `ngrok-*.zip`, `commandos.md`, `start_backend.sh`, `VERSION*.txt`, all `*.bak`/`*.backup` litter; normalized both `models/registry.json` copies to **`backend/models/*.pkl`** paths; added gitignore rules for `*.bak*`, `*.backup*`, `.trash*/`, `src_backup_*/`; `start.sh`/`stop.sh` made local-only (`a017cd7`). `docs/DEUDA_TECNICA_v2.5.md` supersedes the v2.4 debt ledger. ✅
6. **Canonical pipeline now on real data (mostly).** `/v1/canonical/{pair}/decision` and `/risk` run on **real VIX**, real Logistic_24 forecasts, and real macro — live-smoke on 2026-09-11 returned actionable SHORT for EUR/USD and GBP/USD, `INSUFFICIENT_EDGE` for USD/JPY, and `MODEL_UNAVAILABLE` for USD/CNY (dataset-dependent). Remaining fakes: the **3 quality/freshness/drift registries** (explicit TODO v2.7). 🟡
7. **Untouched red items from last cycle:** `run_benchmarks.py` still crashes (`engine.xgb_model`), `layer4/tests/pit_tests.py` still won't parse, `experiments/run.py` E0–E7 still hardcoded, ARIMA still needs absent `statsmodels`, and the LLM chain is **still entirely unwired** (no router imports `llm/*` at all — stronger than before).

**Balance sheet:** the headline gain is a coherent **canonical product loop** — real-VIX decision + risk endpoints, a green frontend that consumes them, and a cleaned repo. The costs: three fake L4 registries and a live-data-dependent `MODEL_UNAVAILABLE` for one pair remain, the Docker image still can't resolve the canonical models, the frontend ships 1.4 MB unminified with Spanish UI strings under `lang="en"`, and the quarter's newest surfaces (canonical risk, RealFeatureStore, RiskEngine, ranking cache, the 6 pages) have not passed the governance freeze loop.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs + governance + model_selection + MACRO_COVERAGE
│                                + DEUDA_TECNICA_v2.5.md (NEW — debt ledger)
├── backend/                     Python backend
│   ├── layer1/                  FastAPI delivery API — 11 routers (canonical decision+risk, intelligence,
│   │                            performance, price, forecast-dashboard, model-comparison…; NO /drivers)
│   ├── layer2/                  Live engine — Logistic_24 loader + XGBoost/registry, SHAP, data providers,
│   │                            FRED macro (21 provider files), ranking (60s cache), status, pipeline_bridge
│   ├── layer3/                  Research layer — artifacts, evaluation, experiments, models, regime, RAG, gate
│   ├── layer4/                  Data-quality layer — PIT validator, config policies, lineage
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (8-stage pipeline, RiskEngine,
│   │                            RealFeatureStore, 132 tests)
│   ├── models/                  models/registry.json (10 entries, backend/models/*.pkl) + 10 .pkl
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
├── scripts/audit_consistency.py             NEW — repo audit script
├── cache/ · logs/ · venv/                  Runtime state (gitignored)
├── frontend/                    React + TypeScript + Vite contract-driven dashboard
│   ├── .env.production          VITE_API_URL=https://meridianfx.onrender.com  (RESTORED)
│   ├── src/pages/               Global · Market · Macro · Risk · Decision · About (6 canonical pages)
│   ├── src/hooks/               10 hooks incl. useCanonicalDecision, useCanonicalRisk
│   ├── src/types/contracts.ts   Layer 1 §7 mirror (+ canonical contracts inside hooks)
│   └── vercel.json · _headers · _redirects
├── .env                         Runtime secrets + config (keys present, gitignored)
├── README.md                    Product overview + quickstart (v2.5.1 — stale)
├── report.md                    This document
└── architecture.md              System architecture (2026-09-11)
```

> **Working-tree hygiene:** `main` in sync with `origin/main`, **clean** — the clutter inventory from the last report is gone (Spanish backup, ngrok zip, backups, VERSION files, commandos.md). Remaining runtime/ignored noise: `venv/`, `cache/`, `logs/`, `frontend/.trash-v2.5/` (46 archived files on disk), and `train_models.py.backup_target_alignment` (untracked, gitignored).

---

## 3. Backend — the two engines (roles stable, wiring advanced)

| Package | Role | Hygiene |
| --- | --- | --- |
| `backend/src/meridian_fx/decision/` | Contract-governed Decision Engine (frozen to L2 spec) + **RiskEngine** | verified ✅ (132 tests) |
| `backend/layer2/` | Live engine the API actually runs (data + ML + status + ranking cache + bridge) | wired into most routers |
| `backend/layer3/` | Research/evaluation layer (models, walk-forward, research gate) | wired via `model_comparison`; `run_benchmarks.py` broken |
| `backend/layer4/` | Data-quality/PIT layer | only `PITValidator` is referenced (by tests) |

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Frozen against `docs/Product_specification/Layer_02.md` v3.4.1. **Verification:** 132 passed across 13 files (from `backend/` with repo root + backend on `PYTHONPATH`). This cycle added the **Risk Engine** (`risk/engine.py`, methodology v2.3.0, 26 tests) and **`real_providers.py`** (`RealFeatureStore` — Yahoo `^VIX`, 60 s TTL, failure → `UNAVAILABLE`).

### 3.2 `layer2/` — the live engine

- **Model resolution (rewired):** `DecisionEngine` now loads **Logistic_24 canonical models** per pair via `_load_canonical_model` (hardcoded 9-pair map → repo-root `models/canonical/*.joblib`) and falls back to **registry** models (`backend/models/*.pkl`, 10 entries) for xgb/logistic, then heuristics. PIT `policy_diff` computed via `MacroService.get_historical_policy_rate`.
- **Ranking cache:** `RankingEngine` caches for 60 s (`9639ef4`), fixing transient "0 pares" and cutting warm latency to ~0.001 s.
- **Pipeline bridge:** `PipelineBridge` assembles real macro (FRED or simulated), differentials (`MacroDifferentialProvider.calculate`/`calculate_historical`, PIT `merge_asof`), forecast → `PredictionArtifact` via `DecisionEngineAdapter`; the **router** injects `RealFeatureStore` for VIX.
- **Status engine, data failover, macros:** unchanged in role; `StatusEngine` still reads CWD-relative `models/registry.json` (works from repo root).

**Key observation:** the canonical-logistic path is now the *primary* model source and registry is secondary, but both still resolve **CWD-relative** — and the Docker image copies only `backend/`, so `models/canonical/` (and the root `models/registry.json` StatusEngine needs) do not exist inside the container.

---

## 4. Backend — Layer 1 FastAPI delivery API (11 routers, deployed)

`backend/layer1/` is a **real FastAPI app** (v1.0.0). CORS covers localhost/Render/Vercel/Cloudflare/ngrok + `*`. **11 routers** plus `/` and `/health` (the **`drivers` router was removed** in v2.6.3). All routes verified 200 via TestClient on 2026-09-11.

### 4.1 Endpoints — correctness updated per running service

| Method | Path | Source / notes | Health |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root + health | ✅ |
| GET | `/v1/status` | real `StatusEngine` | ✅ (`HEALTHY`) |
| GET | `/v1/market-intelligence` | deterministic English narrative over `RankingEngine` | ✅ |
| GET | `/v1/fx/ranking` | `RankingEngine`, live, 9 pairs, **60 s cache** | ✅ (network) |
| GET | `/v1/canonical/{pair}/decision` | **`DecisionPipeline`** via `PipelineBridge` — VIX **real**, 3 L4 registries fake | ✅ 200 — real decisions (EUR/USD/GBP/USD actionable; USD/JPY INSUFFICIENT_EDGE; USD/CNY MODEL_UNAVAILABLE in smoke) |
| GET | `/v1/canonical/{pair}/risk` | **`RiskEngine`** (same bridge) | ✅ 200 — real risk (e.g. EUR/USD MODERATE 30.5, VIX 15.8) |
| GET | `/v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` — Logistic_24 → heuristic (was `FORECAST_DATA`) | ✅ live (lineage block hardcoded) |
| GET | `/v1/fx/performance/{pair}?period=` | `models/registry.json` metrics + hardcoded derivations | ✅ / ⚠️ derived |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (random-synthetic fallback) | ✅ / ⚠️ fallback |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | inline rule-based narrative over live forecast; macro hardcoded | ⚠️ rule-based |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history + XGBoost signal via `_get_model_for_pair` | ✅ live |
| GET | `/v1/fx/{pair}/forecast-dashboard` | **live** — spot, trends, volatility, Logistic_24/XGBoost 30/60/90d, macro | ✅ (network) |
| GET | `/v1/fx/{pair}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding` (in-memory cache) | ✅ 200 (slow) |

> **Removed/changed this cycle:** `/drivers` deleted (`82c9e80`) with its hardcoded `macro_drivers`; `FORECAST_DATA` is dead code (no imports); **LLM layer (`llm/`) is entirely unreachable** — no router imports `EconomicInterpreter`/`LLMFallbackManager`; `layer1/decision/` is a standalone dead subsystem; `interpretation`'s `include_macro` returns a hardcoded `NEUTRAL`/"Contexto macro no disponible" block.

### 4.2 Model resolution now

The old "6-of-9 pairs 404" fault line is **largely resolved at the repo root**: registry paths were normalized to `backend/models/*.pkl` (v2.5.1), all 10 artifacts exist, and the canonical Logistic_24 cover all 9 pairs. Remaining path hazards are the Docker image (no root `models/`), `train_models.py` (still writes legacy `models/*.pkl` paths), and `StatusEngine`'s CWD-relative `models/registry.json`. Canonical `/decision` still depends on live macro/model data per pair (USD/CNY returned `MODEL_UNAVAILABLE` in the smoke run).

### 4.3 Supporting modules

- **`adapters/`** — `DecisionEngineAdapter` (legacy engine → `PredictionArtifact`, used by bridge) and `DecisionAdapter` (`to_performance_response` in use; drivers-era methods dead).
- **`routers/canonical.py`** — pipeline = `RealFeatureStore()` + `FakeDataQualityRegistry(0.90)` + `FakeFreshnessRegistry(3.0)` + `FakeDriftRegistry(0.05)`; TODO marker for v2.7 real registries.
- **`data/forecast_data.py`** — dead; **`llm/`** — dead; **`decision/`** — dead.

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
| `rag/agents.py` | `CentralBankRAGEngine` | Fed/BoJ sentiment | ⚠️ keyword scorer, not real RAG |
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

**Live wiring:** only `backend/tests/test_pit_adversarial.py` exercises `PITValidator`. Runtime forecast paths still don't validate PIT.

---

## 7. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 · TS 5 · Vite 5 (5174) · Tailwind 3 · TanStack Query 5 · axios · date-fns · React Router 6 · Recharts 2**. `src_backup_espanol/` (the Spanish backup) and all legacy pages are gone.

### 7.1 Routes & composition (6 pages, 10 hooks)

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence` |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice` (1y), `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 30)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair, 30)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 30)` |
| `/about` | AboutPage | (narrative) |

Removed: Forecast/Drivers/Evaluation/Status/Price/Models pages + `TabNav` (v2.4 Sprint 8), HistoricalPage/mockup/`_unused` (v2.5.1), `services/drivers.ts` (v2.6.3). **Hooks (10):** `useCanonicalDecision`, `useCanonicalRisk` (60 s refresh), `useForecastDashboard`, `useMarketIntelligence`, `usePrice`, `useRanking`, `useActivePair`, `useForecast`, `usePerformancePeriod` (nav), `usePolling` (**unused**). Canonical decision/risk contracts are declared inside their hooks; `types/contracts.ts` remains the frozen Layer 1 §7 mirror; `types/gaps.ts` `CONTRACT_GAP_MAP` G1–G5.

### 7.2 Presentational surface

`common/*` (11 exported), `decision/*`, `forecast/*`, `global/*` (ActionableInfo, IntelligenceBrief, LeadingSignals, RankingTable, PriceChartSignalIQ…), `market/*` (MarketHero, HistoricalChart, MarketMeta w/ Volatility), `macro/*` (MacroHero, PolicyDifferentials, MacroMeta), `risk/*` (RiskScoreCard, RiskDriversPanel, RiskDriverBar), `layout/*`. Sizing inline in DecisionPage. Orphans: `common/MarketConvention.tsx`, `usePolling`, `utils/status.ts` (test-only).

### 7.3 Verification — all green

| Check | Previous report (09-09) | Now (09-11) |
| --- | --- | --- |
| Backend pytest | 103 passed / 13 files | **132 passed** ✅ (RiskEngine +26, signals_fusion +17, gates +18…) |
| Frontend typecheck | ❌ FAILS (~20 errors) | ✅ **PASS** |
| Frontend tests | 53 passed / 2 FAILED | **56 passed / 0 failed** (7 files) |
| Frontend build | ❌ FAILS | ✅ **PASS** (1,422 kB / 293 kB gzip, minify off) |

**Root cause of the old break (resolved):** the `9d0b62f` `UniverseSelector`/`useActivePair` refactor was fully migrated — legacy pages that passed the removed `currencies` prop were deleted in v2.4 Sprint 8, and `useActivePair.test.tsx` was rewritten. No compile errors remain.

### 7.4 Remaining frontend caveats

Spanish UI strings with `lang="en"`; 4 hooks use raw `fetch` (no retry/backoff) instead of `apiClient`; bundle 1,422 kB unminified with warning suppressed; `.trash-v2.5/` (46 archived files) still on disk; `usePolling` and `MarketConvention` orphaned.

---

## 8. Models & training

- **Production registry** (`models/registry.json`, identical at root/backend): **10 models, all `active: true`, `v1.0`** — 9 XGBoost + 1 logistic (USD/JPY), paths normalized to **`backend/models/*.pkl`** (v2.5.1; all on disk). In-registry AUCs **0.380–0.733** (USD/CHF best 0.733; USD/CNY worst 0.380; USD/JPY xgb 0.408 vs logistic 0.448).
- **Canonical Logistic_24** (`models/canonical/`, v2.0-era, now the **primary runtime model**): 9 per-pair `.joblib` (+ extended, unloaded) with PIT `policy_diff`, loaded by `engine._load_canonical_model`. Not in the registry.
- **Experimental** (`models/experimental/`): USD/BOB h20 (CANDIDATE_WITH_WARNINGS) + EUR/USD h10 (CANDIDATE) via the v2 gate — **unconsumed** by the API.
- `backend/layer2/models/` — `model_selector.py`/`registry_adapter.py` unwired; `trainer.py` empty. `train_models.py` writes the **legacy** `models/*.pkl` convention (inconsistent with the normalized registry).

---

## 9. Deployment & operations

| Target | What | Evidence |
| --- | --- | --- |
| **Render** (backend) | Docker web service, dockerfile, `/health`, `uvicorn layer1.main:app` :10000 | `render.yaml`; `Dockerfile` (python:3.12-slim, `PYTHONPATH=/app/backend`); env FRED/GROQ/ALPHA/TWELVE |
| **Cloudflare Pages** (frontend) | static SPA, `_headers`, `_redirects`, `.cloudflareignore` | `frontend/*` |
| **Vercel** (frontend) | Vite build → `dist`, SPA rewrites | `frontend/vercel.json` |
| **Local** | `docker-compose.yml` (:10000, mounts models+cache); `start.sh` (uvicorn :8000) / `stop.sh` | untracked + gitignored |

Operations caveats (updated):
- **`frontend/.env.production` RESTORED** (`2c0cbb9`) → `VITE_API_URL=https://meridianfx.onrender.com`; local `.env` still localhost:8000. The prior "production builds target localhost" flag is **resolved**.
- **Docker image gap (new):** `Dockerfile` copies only `backend/`, so the containered app has **no root `models/`** — `_load_canonical_model` (`models/canonical/*.joblib`), `StatusEngine` (`models/registry.json`) and any root-script registry read fail inside the image; the registry-based xgb path (`backend/models/*.pkl`) does resolve. Unverified against the deployed image; a fix (copy `models/` or mount it pre-deploy) is pending.
- Local smoke (`TestClient`, 2026-09-11): `/v1/status` `HEALTHY`; data failover Yahoo→Alpha live.

---

## 10. Models of verification & governance (unchanged)

The repo remains **prompt-first** (`docs/Prompts/`) with **Contract/** policing fidelity. Frozen specs and freeze artifacts unchanged (L1 v5.1, L2 v3.4.1, L3 v5.0, L4 v3.1.1; traceability 61/12; gaps 16; freeze 0 blocking). **NEW this cycle:** `docs/DEUDA_TECNICA_v2.5.md` (debt ledger superseding the v2.4 file); pre-existing `MACRO_COVERAGE.md` and the model-selection report unchanged.

> **Not** pushed through the traceability → gaps → freeze loop: canonical decision **+ risk** endpoints & `pipeline_bridge`, **RealFeatureStore/real-VIX**, **RiskEngine**, **ranking cache**, `/v1/market-intelligence`, canonical Logistic_24 as the runtime model, the **canonical frontend pages** (Market/Macro/Risk/Decision), walkforward/shadow research, and the v2.5.1 cleanup. README lags at v2.5.1 vs HEAD v2.6.6 (and there is no v2.6 tag).

---

## 11. Current status & known gaps

**Green**
- Backend pytest **132/132** (13 files); frontend typecheck/build/tests **all pass** (56/56). The long-standing compile break is **closed**.
- **Canonical product loop live:** `/v1/canonical/{pair}/decision` + `/risk` return real per-pair output (real VIX, Logistic_24, macro) — e.g. EUR/USD `actionable SHORT`, GBP/USD `SHORT`, USD/JPY `INSUFFICIENT_EDGE`.
- **Risk Assessment Engine** (v2.3): 5 weighted drivers, LOW→EXTREME, 26 tests, `/risk` endpoint.
- **Frontend v2.4 re-platform:** 6 canonical pages, 10 hooks, dynamic thresholds/hard-gates/quality metrics/signal fusion, empty states, mobile responsive, self-hosted fonts, 5-minute staleTime, backend ranking cache (60 s).
- **Repo hygiene + model normalization:** all flagged clutter removed; registries identical with `backend/models/*.pkl`; `.env.production` restored.
- `main` in sync with `origin/main`, working tree clean.

**Red / attention**
1. **Canonical pipeline still runs 3 fake L4 registries** (DQ/Freshness/Drift; TODO v2.7) — VIX real, quality gating not.
2. **Docker model gap:** the image copies only `backend/` → canonical Logistic_24 (`models/canonical/`) and `StatusEngine`'s `models/registry.json` unresolvable inside the container.
3. **USD/CNY canonical decision flipped `MODEL_UNAVAILABLE`** in live smoke while EUR/USD/GBP/USD were actionable — live-data dependency; needs monitoring.
4. **Model-path convention still split/CWD-relative**: `train_models.py` writes legacy `models/*.pkl`; `engine` canonical vs registry vs `StatusEngine` paths diverge.
5. **Layer 3 tail** — `run_benchmarks.py` crashes (`engine.xgb_model`); `run.py` E0–E7 hardcoded; ARIMA unrunnable; L3 registry schema incompatible.
6. **Layer 4** unwired; `layer4/tests/pit_tests.py` still corrupted.
7. **LLM chain entirely unwired** — `layer1/llm/*` unreachable; `/interpretation` rule-based with hardcoded macro block.
8. **Hardcoded/simulated remnants** — `/historical` random fallback; `/performance` hardcoded ece/max_dd/regime table; `/status` `database=NOT_CONFIGURED`; FRED simulated without key; dead `FORECAST_DATA`/`layer1/decision/`/drivers adapter methods.
9. **Frontend debt** — 4 hooks raw-fetch (no retry); `usePolling` + `MarketConvention` orphans; `.trash-v2.5/` on disk; Spanish strings / `lang="en"`; 1,422 kB bundle unminified.
10. **Governance lag** — newest surfaces (canonical risk, RealFeatureStore, RiskEngine, ranking cache, 6 pages, research bundle) not through the freeze loop; **no v2.6 tag**; README stale at v2.5.1.

---

## 12. Recommendations

1. **Finish the canonical pipeline (v2.7):** replace the three fake L4 registries with real `PITValidator`-backed, freshness/drift-aware providers; then push the canonical logistic path + `/risk` + RealFeatureStore through the governance loop.
2. **Fix model resolution & Docker (top ops risk):** copy `models/` into the Docker image (or mount it) so `models/canonical/*.joblib` and `models/registry.json` resolve in Render; align `train_models.py` with the `backend/models/*.pkl` convention; add a resolution-union test for all 9 pairs across repo-root and container CWDs.
3. **Investigate the USD/CNY `MODEL_UNAVAILABLE`** canonical decision (live-data route vs regression) and add per-pair canonical health to `/v1/status`.
4. **Cut the Layer 3/4 tail:** port `run_benchmarks.py` to `_get_model_for_pair` (or delete), replace hardcoded `run.py`, decide on `statsmodels`, repair `layer4/tests/pit_tests.py`, reconcile L3 registry schema.
5. **Resolve the LLM question:** wire `EconomicInterpreter`/`LLMFallbackManager` into `/interpretation` (or delete `llm/`); remove the hardcoded `include_macro` block and remaining FORECAST/performance/status hardcodes.
6. **Frontend hardening:** unify transport (4 fetch hooks → `apiClient`), delete `.trash-v2.5/` + orphans (`usePolling`, `MarketConvention`), fix `lang="en"` vs Spanish copy, and consider code-splitting + `minify` for the 1.4 MB bundle (as the deploy stage, not the dev default).
7. **Close the ops/governance book:** tag the v2.6.x line (or bump README/versioning to the real HEAD), re-add a v2.6 debt ledger, and route the canonical surfaces + research bundle through traceability → gaps → freeze → validation.
8. **Re-run the audit loop** (`scripts/audit_consistency.py`) after the v2.7 work; keep the repo-hygiene invariants (no backups, no Spanish backup tree, singleton registry).