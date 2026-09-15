# Meridian FX — Repository Report

**Date:** 2026-09-15 · **Branch:** `main` (in sync with `origin/main`) · **History:** 220 commits (2026-08-25 → 2026-09-15) · **Head commit:** `5c75999` "feat(frontend): regime divergence UI (banner, projection, panel, Risk, English)" · **Latest tag:** `v2.7.5` (2026-09-15; `STABLE.md` registers v2.7.5 as current stable) · **Since last report (2026-09-14, `e301138`):** 46 commits.

This is an analysis of the repository as it stands today: what it is, what it contains, how it is governed, its verification status, and its known gaps and risks.

---

## 1. What this is

**Meridian FX** is an FX ("foreign exchange") intelligence product whose guiding principle is:

> *"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."*

It answers its product questions through a **9-pair canonical universe** (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) with 5-day decision/risk horizons and 30/60/90-day forecasts:

| Question | Surface |
| --- | --- |
| What is happening in the market? | Global Overview + Market page |
| What does Meridian expect? | Market / Decision pages (canonical forecast) |
| Why? | Decision page (SHAP, economic breakdown) |
| Is it worth acting? | Decision page (economic filter, gates, actionable) |
| What could invalidate the signal? | Decision page (signal validity / hard gates) |
| Is the pair's regime trustworthy? | Global page (regime-divergence banner + panel) |
| How risky is it / how good has Meridian been? | Risk page / performance surface |

### What changed since the last report (2026-09-14)

This cycle (**2026-09-14 → 2026-09-15, 46 commits, `e301138` → `5c75999`**) matured the v2.7 line into **tagged releases v2.7 → v2.7.5**, added a **pre-model forecast-eligibility gate** (exchange-regime classification, KI-009), shipped a **regime-divergence analysis** (rolling ARIMA(1,0,1)) with a **new endpoint + frontend UI**, made progress on the **temporal-provenance audit** (KI-002), and closed the two headline ops gaps from the last report (Docker model copying, frontend pair-universe collapse).

1. **Exchange-regime classification + forecast-eligibility gate (KI-009, `9edd92e` + `3accd20`).** New `backend/src/meridian_fx/decision/contracts/exchange_regime.py` (provisional, primary-source verification pending): `USD/CNY` → `MANAGED_FLOAT`, `USD/BOB`/`USD/ARS` → `UNKNOWN` (not yet `ADMINISTERED`), the 6 G10/EM pairs → `FREE_FLOAT`. `DecisionPipeline.build()` now short-circuits into a **RESTRICTED decision** (no scoring) when `forecast_eligibility != ELIGIBLE`; the value is propagated onto `Decision.forecast_eligibility`. `USD/BOB` no longer emits a technically-meaningless "LONG · ACTIONABLE · edge 36×" from a non-market price series. ✅ (10 tests, `test_exchange_regime.py`).
2. **Regime divergence (KI-009 supplementary, `caa3af6` + `b1bada7` + `050b42d`).** New `backend/src/meridian_fx/decision/divergence/` (scipy-based rolling ARIMA(1,0,1) `arima.py`, `metrics.py`, `report.py` — *no* `statsmodels`) + **`GET /v1/fx/{pair}/regime-divergence?window_days=90&period=1y`** (13th router). `docs/divergence/README.md` documents the method; empirical evidence (2026-09-15, same window/source): USD/CHF `free_float` **+0.55 `normal`**, USD/BOB `unknown` **−2.43 `extreme`** — discriminates a clean float from an intervened pair without fundamental data. Divergence measures the anomaly; it does **not** upgrade the classification. ✅ (10 tests, `test_divergence.py`).
3. **Risk computed for RESTRICTED decisions (Opción B, `7bcf3f9`).** `_restricted_decision()` now invokes `RiskEngine` with worst-case inputs (`confidence=0`, `edge=0`, `regime=UNKNOWN`, real VIX), so `/v1/canonical/{pair}/risk` produces a real assessment for **all 9 pairs** — including USD/BOB, USD/ARS, USD/CNY. ✅
4. **Temporal-provenance audit progress (KI-002, steps 1–4).** `contracts/temporal.py` `TemporalProvenance` + `TemporalConfidence` (KI-002-D design; PIT-7 ordering enforced at model level, `8b428fe`/`72d3baa`); `engine.get_forecast` now exposes **`last_date`** (tz-aware UTC after `bc056c5`) in the `data_provider` block (step 1, `7a681e6`); `DecisionEngineAdapter` **derives `as_of` from the market data cutoff** with an explicit wall-clock fallback (step 2 + test, `ec74ccf`/`5a4396d`); `FeatureValue` migrated to `TemporalProvenance` (step 4, `4488464` + correction `ac3c9fa`). Residual: full provenance chain still not end-to-end; KI-002-A/B/C remain open (see §11). ⚠️→🟡
5. **Existing KI hygiene.** KI-006 (`4ee61d5` — bare `except:` → explicit types) and KI-007 (`a3b3a1d` — `/status` emits contract-valid `InfrastructureLevel`, `database="degraded"`, 5 contract tests) resolved; KI-008 (`df7f5f8` — CNBS/ECB providers documented as incomplete). Backend suite grew **132 → 180** tests. ✅
6. **Frontend universe collapse fixed (`7fa9eda`).** `pairUniverseFromRanking()` now returns `CANONICAL_FX_PAIRS` (9 pairs) unconditionally — the selector no longer inherits the 1-pair legacy ranking. Regression test updated. ✅ (Backend ranking still serves USD/CHF; see §11.)
7. **Docker model gap fixed (`503872b`).** Dockerfile now `COPY models/ ./models/`, `PYTHONPATH=/app/backend:/app`, `ENV MERIDIAN_MODEL_DIR=/app/models` — the containered app resolves `models/canonical/*.joblib` and the root `models/registry.json` (engine/StatusEngine still read CWD-relative paths from `/app`). The top ops risk from the last report is closed. ✅
8. **Frontend regime-divergence UI (English, `6a1f85c` + `5c75999`).** New `useRegimeDivergence` hook (`apiClient`), `RegimeWarningBanner`, `DivergencePanel`, and the ARIMA projection overlaid on `PriceChartSignalIQ` (Global page). Market-intelligence router rewritten in **English with non-expert context** (actionable/selective semantics, `selected_pair_view`).
9. **Tooling & release machinery.** Root `pytest.ini` (`958ea5c`, `testpaths=backend/tests`), **GitHub Actions CI** (`b4b92d1`), **pre-commit** pytest+hygiene hooks (`7c59697`), `STABLE.md` (release registry, current stable **v2.7.5** `f45b097`), `KNOWN_ISSUES.md` (authoritative debt ledger KI-001…KI-009/A3/A4/P1/B/Stub). README header updated to **v2.7**.
10. **v2.7.x polish.** v2.7.1 hygiene (dead code after early-return in `pit_tests.py` removed, `MarketConvention` orphan deleted, `.trash-v2.5` gone); v2.7.2 UI contract coherence (`ModelDivergenceNotice` once, `ActionableInfo` edge-ratio = net/required-min, `⚠ STUB SCORE` labels); v2.7.3/4 dead `_unavailable_decision()` removal (with post-condition verification process change); v2.7.5 `Decision.timestamp` captured once per `build()` (KI-002 sub-1). ✅

**Balance sheet:** the headline gains are a functioning **pre-model regime gate** that stops economically-meaningless forecasts for administered/unknown regimes, a working **statistical divergence probe** (endpoint + UI + docs) that needs no fundamental data, **PIT temporal provenance now partially real** (data-cutoff `as_of`), a **9-pair frontend universe**, and a **Docker image that can actually serve the canonical models** — plus the release line finally tagged (v2.7.5 stable) with CI/pre-commit in place. The costs: the **legacy ranking backend still serves USD/CHF only** (deferred to v3.0), the three **Stub L4 registries** remain, **KI-002-A/B/C and KI-003/004 stay open**, the LLM layer is still partially wired (`EconomicInterpreter` unimported; `/interpretation` macro hardcoded), the **CI backend job collects zero tests** (`pytest backend/layer4/tests/` → `pit_tests.py` matches no discovery pattern), the unminified bundle grew to **1,495 kB**, and none of the new surfaces (regime gate, divergence, temporal contract) have gone through the governance freeze loop.

---

## 2. Repository layout

```
MeridianFX/
├── .github/workflows/ci.yml         NEW — GitHub Actions (backend compile, layer4 pytest, frontend build+test)
├── .pre-commit-config.yaml          NEW — pre-commit: hygiene hooks + backend pytest gate
├── docs/                            Frozen specs + governance + model_selection + MACRO_COVERAGE
│                                    + DEUDA_TECNICA_v2.5.md + divergence/README.md (NEW)
├── backend/                         Python backend
│   ├── layer1/                      FastAPI delivery API — 13 routers (now incl. divergence;
│   │                                canonical decision+risk+narrative+regenerate, intelligence…; NO /drivers)
│   ├── layer2/                      Live engine — Logistic_24 loader + XGBoost/registry, SHAP, data providers,
│   │                                FRED macro (21 provider files), ranking (60s cache, 1 active pair), status,
│   │                                pipeline_bridge, narrative (SQLite-persisted LLM layer)
│   ├── layer3/                      Research layer — artifacts, evaluation, experiments, models, regime,
│   │                                sentiment (CentralBankSentimentEngine), gate
│   ├── layer4/                      Data-quality layer — PIT validator, config policies, lineage
│   │                                (tests/pit_tests.py now COMPILES — fixed in v2.7.1)
│   ├── src/meridian_fx/decision/    Contract-governed Decision Engine (8-stage pipeline + KI-009
│   │                                eligibility gate, RiskEngine, RealFeatureStore, Stub* registries,
│   │                                divergence/ module, temporal contracts; 180 tests)
│   ├── models/                      models/registry.json (10 entries — 1 ACTIVE, 9 below gate)
│   ├── tests/                       Backend pytest suite (20 files, 180 tests)
│   ├── pyproject.toml · requirements.txt · docker-compose.yml
├── models/                          Root artifacts: canonical/ (10 Logistic_24 .joblib + metadata),
│                                    experimental/ (EUR/USD h10, USD/BOB h20), registry.json (== backend copy)
├── Dockerfile                       NOW copies models/ + PYTHONPATH=/app/backend:/app (Docker gap closed)
├── render.yaml · runtime.txt
├── start.sh · stop.sh               Local run scripts (untracked + gitignored)
├── train_models.py · train_canonical_model{,_extended}.py · train_multi_pairs.py
├── train_experimental_models.py · evaluate_all_pairs.py · final_holdout.py
├── research_gate.py · research_gate_results{,v2}.json · research_validation_*
├── research_walkforward.py + 8 variants + *_results.json
├── shadow_test.py · shadow_test_simple.py · monitor_daily.py · monitor_model.py
├── STABLE.md                        NEW — stable-release registry (current: v2.7.5)
├── KNOWN_ISSUES.md                  NEW — authoritative known-issues ledger (KI-001…KI-009, A3/A4, P1, B)
├── scripts/audit_consistency.py · scripts/audit_registry.py · scripts/apply_gate.py
├── cache/ · logs/ · venv/           Runtime state (gitignored)
├── frontend/                        React + TypeScript + Vite contract-driven dashboard
│   ├── .env.production              Comment-only placeholder for local dev (still not pinned)
│   ├── src/pages/                   Global (regime-divergence UI) · Market · Macro · Risk · Decision · About
│   ├── src/hooks/                   12 hooks incl. useRegimeDivergence (NEW), useCanonicalDecision/Risk/Narrative
│   ├── src/components/global/       … RegimeWarningBanner + DivergencePanel (NEW)
│   ├── src/types/contracts.ts       Layer 1 §7 mirror (+ canonical contracts inside hooks)
│   └── vercel.json · _headers · _redirects
├── .env                             Runtime secrets + config (keys present, gitignored)
├── README.md                        Header now v2.7 (was stale v2.5.1) + Current Limitations section
├── report.md                        This document
└── architecture.md                  System architecture (2026-09-15)
```

> **Working-tree hygiene:** committed `HEAD` `5c75999` == `origin/main`, layer-clean at analysis start. **Observation:** an uncommitted set of Spanish→English frontend translations + README edits (13 files, staged/unstaged) appeared on the working tree during this analysis session — presumably an in-flight local pass, unrelated to `HEAD`. Remaining ignored noise: `venv/`, `backend/venv/`, `cache/`, `logs/`, `dist/`. `.trash-v2.5/` is gone.

---

## 3. Backend — the two engines (now four production surfaces)

| Package | Role | Hygiene |
| --- | --- | --- |
| `backend/src/meridian_fx/decision/` | Contract-governed Decision Engine (frozen to L2 spec) + **RiskEngine** + **KI-009 eligibility gate** + **divergence module** | verified ✅ (180 tests) |
| `backend/layer2/` | Live engine the API actually runs (data + ML + status + ranking cache + bridge + narrative) | wired into most routers |
| `backend/layer3/` | Research/evaluation layer (models, walk-forward, research gate, sentiment) | wired via `model_comparison`; `run_benchmarks.py` broken |
| `backend/layer4/` | Data-quality/PIT layer | PITValidator via tests; `pit_tests.py` now compiles; `TemporalProvenance` contracts live |

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Frozen against `docs/Product_specification/Layer_02.md` v3.4.1. **Verification:** 180 passed across 20 files (from repo root, per root `pytest.ini`). New this cycle:
- **KI-009 pre-model gate:** `DecisionPipeline.build()` short-circuits to a RESTRICTED decision (signal `UNAVAILABLE`, `actionable=False`, no scoring) when `forecast_eligibility != ELIGIBLE`, preserving the specific eligibility value; **RiskEngine is still computed** so `/risk` works for RESTRICTED pairs. `DecisionContext` unchanged; `Decision.forecast_eligibility` added.
- **Divergence module:** `divergence/{arima,metrics,report}.py` — scipy `minimize`-fit ARIMA(1,0,1) on log-returns, 90-obs rolling, one-step-ahead projection, rolling z-score (20-obs warm-up), thresholds `normal/notable/extreme/persistent`.
- **Temporal contracts:** `contracts/temporal.py` `TemporalProvenance` (PIT-7 ordering enforced) imported into `contracts/__init__`; `FeatureValue` migrated to carry provenance.
- Unchanged: partial-macro resilience (`macro=0.0` degrade), `Stub*` L4 registries (still TODO v3.0), `RealFeatureStore` VIX.

### 3.2 `layer2/` — the live engine

- **`/v1/fx/{pair}/regime-divergence`** is served directly off `DataProvider` + `get_exchange_regime` + `compute_divergence_report` — a fourth production surface, independent of the decision pipeline.
- `DecisionEngine.get_forecast` now includes **`data_provider.last_date`** (data cutoff), consumed by the adapter for `as_of`; network stack registers tz-aware UTC.
- Ranking/status/pipeline-bridge/narrative roles unchanged; registry remains single-active (USD/CHF).

---

## 4. Backend — Layer 1 FastAPI delivery API (13 routers, deployed)

`backend/layer1/` is a **real FastAPI app** (v1.0.0). CORS covers localhost/Render/Vercel/Cloudflare/ngrok + `*`. **13 routers** plus `/` and `/health` (no `/drivers`). All routes green via pytest/TestClient on 2026-09-15; 180 backend tests.

### 4.1 Endpoints — state per running service

| Method | Path | Source / notes | Health |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root + health | ✅ |
| GET | `/v1/status` | real `StatusEngine`; `InfrastructureLevel` contract fields (KI-007) | ✅ `database="degraded"` |
| GET | `/v1/market-intelligence` | **English** deterministic narrative over `RankingEngine`, non-expert context, `selected_pair_view` — still **single-pair** (USD/CHF) | ✅ / ⚠️ |
| GET | `/v1/fx/ranking` | `RankingEngine`, 60 s cache — **1 pair (USD/CHF)** after the gate | ✅ / ⚠️ |
| GET | `/v1/canonical/{pair}/decision` | `DecisionPipeline` via `PipelineBridge` — VIX real, 3 Stub registries, `horizon_days` default 5. **KI-009:** USD/CNY + USD/BOB + USD/ARS return RESTRICTED/UNKNOWN eligibility instead of scored forecast | ✅ 200 — 6 ELIGIBLE / 3 gated |
| GET | `/v1/canonical/{pair}/risk` | `RiskEngine` (same bridge) — **computed for RESTRICTED decisions too** (Opción B) | ✅ real risk, 9/9 pairs |
| GET | `/v1/canonical/{pair}/narrative` | cache-first persistent LLM narrative (SQLite, no TTL, Groq primary) | ✅ |
| POST | `/v1/canonical/{pair}/narrative/regenerate` | admin regeneration (`X-Admin-Token`; 503 if unconfigured) | ✅ |
| GET | `/v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` — Logistic_24 → heuristic; now exposes `last_date` (KI-002-A) | ✅ live |
| GET | `/v1/fx/performance/{pair}?period=` | `models/registry.json` metrics + hardcoded derivations | ✅ / ⚠️ derived |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (random-synthetic fallback) | ✅ / ⚠️ fallback |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | inline rule-based narrative over live forecast; macro hardcoded | ⚠️ rule-based |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history + XGBoost signal via `_get_model_for_pair` | ✅ live |
| GET | `/v1/fx/{pair}/forecast-dashboard` | live — spot, trends, volatility, Logistic_24/XGBoost 30/60/90d, macro | ✅ (network) |
| GET | `/v1/fx/{pair}/model-comparison` | Layer 3 `WalkForwardEvaluator.evaluate_expanding` (in-memory cache) | ✅ 200 (slow) |
| GET | `/v1/fx/{pair}/regime-divergence` | **NEW** — rolling ARIMA(1,0,1) divergence, z-score, interpretation | ✅ |

> **Changed this cycle:** `divergence` router added (13 total). **Resolved earlier/last cycle:** `/drivers` removed, `Stub*Registry`, canonical narrative. **LLM note:** `LLMFallbackManager` reachable via narrative only; `EconomicInterpreter` still unimported.

### 4.2 Model resolution now

Canonical Logistic_24 covers all 9 pairs (primary decision source); registry has 1 active (USD/CHF, ranking only). Path hazards improved: **Docker now copies `models/` and runs from `/app` with `PYTHONPATH=/app/backend:/app`**, so `models/canonical/*.joblib` and `models/registry.json` resolve in the container. Residual split: `engine.py` reads `models/canonical/*.joblib` (CWD-relative) and `ModelRegistry("backend/models/registry.json")`, while `StatusEngine`/`RankingEngine` read `models/registry.json`; `MERIDIAN_MODEL_DIR` is set but **not consumed** by engine code (currently satisfies `render.yaml` expectations only).

### 4.3 Supporting modules

- **`routers/divergence.py`** — new; `DataProvider().get_historical` + `compute_divergence_report`, serializes observed/projected/divergence series + `current_zscore` + `interpretation` + metadata (`last_date`).
- **`routers/canonical.py`** — pipeline = `RealFeatureStore()` + 3 `Stub*` registries (unchanged; TODO v3.0).
- **`routers/intelligence.py`** — English rewrite (6a1f85c).
- **`adapters/decision_engine_adapter.py`** — `_derive_as_of()` from `forecast['data_provider']['last_date']`; wall-clock fallback logged (KI-002-A).
- **`data/forecast_data.py`** dead; **`decision/`** dead; **`llm/`** partially reached via narrative.

---

## 5. Backend — Layer 3 research layer (`backend/layer3/`)

Unchanged since last report. The **only** live coupler remains `layer1/routers/model_comparison.py`; nothing in `layer2` imports it.

| Area | Files | Purpose | Maturity |
| --- | --- | --- | --- |
| `artifacts/registry.py` | research model registry | Persist research-approved models | ✅ implemented — schema **incompatible** with `backend/models/registry.json` |
| `evaluation/walk_forward.py` | `evaluate`, `evaluate_expanding` | Rolling/expanding backtest | ✅ `evaluate()` healthy |
| `evaluation/run_benchmarks.py` | CLI runner | Per-window benchmark tables | ❌ **still crashes** — `engine.xgb_model` AttributeError |
| `evaluation/model_evaluator.py` | `ModelEvaluator` | Simple OOS (last 20%) | ⚠️ random-fallback on predict failure |
| `experiments/run.py` | E0–E7 | Sequential experiments | ❌ still **hardcoded** metrics |
| `experiments/real_experiments.py` | `RealExperimentRunner` | Real walk-forward E0–E7 | ⚠️ unblocked but unverified |
| `macro/regime.py` | `MacroRegimeEngine` | Regime classification | ✅ works |
| `models/arima.py` | `ARIMAModel` | ARIMA control | ⚠️ unrunnable — `statsmodels` absent (deliberately untouched; the divergence module does not use it) |
| `models/elastic_net.py` / `models/ensemble.py` | control models | ✅ works | |
| `rag/agents.py` | `CentralBankSentimentEngine` | Fed/BoJ sentiment | ⚠️ keyword scorer, not RAG |
| `research_gate/*` | gate/real_gate/full_gate | 4-gate approval | ⚠️ `gate.py` works; `full_gate.py` passes `features={}` |

### 5.1 / 5.2 — Research Gate pipeline and canonical/walkforward/shadow research

Unchanged from last report: `research_gate.py` → `research_gate_results_v2.json` → `models/experimental/` candidates (EUR/USD h10 CANDIDATE, USD/BOB h20 CANDIDATE_WITH_WARNINGS) unconsumed by the API; canonical `models/canonical/` (10 `.joblib`) is the runtime primary source; walkforward/shadow/monitor scripts remain research-only.

---

## 6. Backend — Layer 4 data-quality layer (progress)

| Area | Purpose | Maturity |
| --- | --- | --- |
| `quality/pit_validator.py` — `PITValidator` (PIT-1…PIT-7) | Point-in-Time compliance | ✅ correct (exercised by `test_pit_adversarial.py`) |
| `config/policies.py` | Versioned config | ✅ implemented, **standalone** |
| `lineage/models.py` | Provenance | ✅ implemented, **standalone** |
| `tests/pit_tests.py` | layer-4 unit tests | ✅ **now compiles** (dead code after early return removed, v2.7.1) — but CI does not run it (see §10) |

**Wiring:** only `backend/tests/test_pit_adversarial.py` and the new temporal/`as_of` tests exercise PITValidator semantics. Runtime forecast paths still don't validate PIT end-to-end (KI-002-A/B/C open); the canonical pipeline's three L4 registries are **stubs**. Positive: `FeatureValue` now carries a real `TemporalProvenance` chain (event/release/source/system times + confidence per field), and the adapter derives `as_of` from the market data cutoff.

---

## 7. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 · TS 5 · Vite 5 (5174) · Tailwind 3 · TanStack Query 5 · axios · date-fns · React Router 6 · Recharts 2**. Spanish backup tree, `.trash-v2.5/`, and `MarketConvention` are gone. Working tree carries an in-flight English-translation pass (unstaged, see §2 note).

### 7.1 Routes & composition (6 pages, 12 hook modules)

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence`, **`useRegimeDivergence(pair,90,'1y')`** (banner + panel + projection) |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice` (1y), `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair, 5)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair, 5)`, `useCanonicalNarrative` |
| `/about` | AboutPage | (narrative) |

**Hooks (12):** + `useRegimeDivergence` (NEW — `apiClient`, 5 min staleTime) alongside `useCanonicalDecision`, `useCanonicalRisk` (**both now migrated to `apiClient`**, previously raw fetch), `useCanonicalNarrative`, `useForecastDashboard`, `useMarketIntelligence`, `usePrice`, `useRanking`, `useActivePair`, `useForecast`, `usePerformancePeriod` (nav), `usePolling` (unused). **Universe:** `pairUniverseFromRanking()` returns `CANONICAL_FX_PAIRS` — 9-pair selector restored on live data (fixes the v2.7 collapse). Domain contracts (decision/risk/narrative/divergence) declared inside hooks; `types/contracts.ts` remains the frozen Layer 1 §7 mirror; `types/gaps.ts` G1–G5. ⚠️ `forecast_eligibility` is **not yet in the frontend decision contract** — RESTRICTED/UNKNOWN decisions render as a generic non-actionable state without the eligibility reason.

### 7.2 Presentational surface

`common/*`, `decision/*` (12 incl. DecisionProvenance, DecisionNarrative), `forecast/*`, `global/*` (**+ RegimeWarningBanner, DivergencePanel**; PriceChartSignalIQ now accepts `projectedSeries` overlay), `market/*`, `macro/*`, `risk/*`, `layout/*`. Orphans: `common/MarketConvention.tsx` **removed**; `usePolling`, `utils/status.ts` (test-only) remain.

### 7.3 Verification — all green

| Check | Last report (09-14) | Now (09-15) |
| --- | --- | --- |
| Backend pytest | 132 passed / 13 files | **180 passed** ✅ (20 files) |
| Frontend typecheck | ✅ PASS | ✅ **PASS** |
| Frontend tests | 56 passed / 0 failed (7 files) | **56 passed / 0 failed** ✅ (7 files) |
| Frontend build | ✅ PASS (1,434 kB / 296 kB gzip) | ✅ **PASS** (1,495 kB / 304 kB gzip, minify off) |

### 7.4 Remaining frontend caveats

4 hooks still raw-`fetch` with no retry/backoff (`usePrice`, `useRanking`, `useMarketIntelligence`, `useForecastDashboard`); `usePolling` orphaned; bundle **1,495 kB** unminified (warning suppressed); many UI strings still Spanish vs `lang="en"` (in-flight English pass on the working tree); `forecast_eligibility` not surfaced on Decision page.

---

## 8. Models & training

- **Production registry** (`models/registry.json`, identical root/backend): **10 models, `v1.0`** — **1 active (USD/CHF xgb, auc 0.733, n=319)** after the v2.7 promotion gate (`MIN_AUC 0.52`, `MIN_N_SAMPLES 300`); 9 CANDIDATE.
- **Canonical Logistic_24** (`models/canonical/`): 9 per-pair `.joblib` (5-day forward target, PIT `policy_diff`), **primary** decision source, loaded CWD-relative; **now resolvable in Docker** because the image copies `models/` and runs from `/app`.
- **Exchange-regime classification (NEW):** `free_float` ×6, `managed_float` USD/CNY, `unknown` USD/BOB + USD/ARS (provisional — BCB/BCRA verification pending v3.0). Gated pairs return RESTRICTED/UNKNOWN decisions, not directional forecasts.
- **Experimental** (`models/experimental/`): USD/BOB h20 + EUR/USD h10 gate candidates — unconsumed.
- `train_models.py` deprecated; CLI training/research scripts unchanged.

---

## 9. Deployment & operations

| Target | What | Evidence |
| --- | --- | --- |
| **Render** (backend) | Docker web service, `/health`, `uvicorn layer1.main:app` :10000 | `render.yaml`; Dockerfile now **copies `models/`**, `PYTHONPATH=/app/backend:/app`, `MERIDIAN_MODEL_DIR=/app/models` (gap closed) |
| **Cloudflare Pages** (frontend) | static SPA, `_headers`, `_redirects`, `.cloudflareignore` | `frontend/*` |
| **Vercel** (frontend) | Vite build → `dist`, SPA rewrites | `frontend/vercel.json` |
| **CI** | **NEW** GitHub Actions (`ci.yml`): Python 3.11 compile + `pytest backend/layer4/tests/`; Node 20 build + `npm test` | ⚠️ backend job **collects 0 tests** (see §10) |
| **Pre-commit** | **NEW** `.pre-commit-config.yaml`: hygiene hooks + backend pytest gate (`always_run`) | enforced locally |

Operations caveats:
- **`frontend/.env.production` is still a comment-only placeholder** — production `VITE_API_URL` must be injected by pipelines; `apiClient` has no fallback.
- **MREDIAN_MODEL_DIR is set but unused in code** (engine reads `models/canonical/` and `backend/models/registry.json` relative to CWD `/app`). Works, but the env contract is aspirational.
- Ranking/market-intelligence surface **USD/CHF only** in production (backend); frontend is pinned to 9 pairs.
- FRED real data requires `FRED_API_KEY` (else simulated; partial macro degrades, doesn't block). `ADMIN_TOKEN` needed for narrative regenerate.
- Local smoke (pytest 2026-09-15): `/v1/status` `HEALTHY`, `/database` `degraded`; 180 backend green; frontend typecheck/build/tests green.

---

## 10. Models of verification & governance

The repo remains **prompt-first** (`docs/Prompts/`) with Contract policing fidelity. Frozen specs unchanged (L1 v5.1, L2 v3.4.1, L3 v5.0, L4 v3.1.1). **New tooling:** root `pytest.ini` (single entry point for the full suite), GitHub Actions CI, pre-commit hooks, `STABLE.md` (release registry), `KNOWN_ISSUES.md` (debt ledger with stable IDs — a real improvement over prose-only gaps).

- **CI gap (new):** `ci.yml` backend job runs `pytest backend/layer4/tests/`, which resolves rootdir to `backend/pyproject.toml` and **collects 0 tests** (`pit_tests.py` matches neither `test_*.py` nor `*_test.py`). The backend "tests" step is a no-op exit 0 — the actual 180-test suite is not in CI yet. Frontend job does run the real suite.
- **Governance lag (unchanged + grown):** **not** pushed through traceability → gaps → freeze loop: exchange-regime gate (KI-009), divergence surface (module + endpoint + docs + UI), `TemporalProvenance`/`FeatureValue` migration (KI-002 steps), risk-for-RESTRICTED semantics, RESTRICTED `signal_validity=UNAVAILABLE` semantics, `forecast_eligibility` on the L2 `Decision` contract, the English intelligence rewrite, plus everything carried over (canonical decision/risk/narrative, RealFeatureStore, RiskEngine, ranking cache, walkforward/shadow research). **Latest tag now `v2.7.5`** (registered stable); README header matches v2.7.

---

## 11. Current status & known gaps

**Green**
- Backend pytest **180/180** (20 files); frontend typecheck/build/tests **all pass** (56/56).
- **KI-009 eligibility gate:** RESTRICTED/UNKNOWN pairs (USD/CNY, USD/BOB, USD/ARS) no longer emit economically-meaningless directional forecasts; 6/9 pairs remain ELIGIBLE; **Risk still computed for RESTRICTED** (9/9 risk surface).
- **Regime divergence live:** `/v1/fx/{pair}/regime-divergence` + docs + frontend banner/panel/projection; empirical USD/BOB −2.43 `extreme` vs USD/CHF +0.55 `normal`.
- **Frontend universe restored to 9 pairs**; canonical decision/risk/narrative hooks all on `apiClient`.
- **Docker gap closed** (models copied, PYTHONPATH fixed); README header at v2.7; tags v2.7.5; CI + pre-commit exist; `.trash-v2.5` and `MarketConvention` removed; `pit_tests.py` compiles; KI-006/007 resolved; `as_of` now derives from market-data cutoff.
- `main` == `origin/main` at HEAD `5c75999`.

**Red / attention**
1. **Legacy ranking still USD/CHF on the backend** (v3.0 track). Frontend is pinned to 9 pairs, so the user-facing collapse is masked — but `/v1/fx/ranking` and `/v1/market-intelligence` remain single-pair, and the market-intelligence hero on Global derives from ranking.
2. **CI backend job runs zero tests** — `pytest backend/layer4/tests/` collects nothing (discovery pattern). The 180-test suite has no CI coverage; only frontend and a compile step run.
3. **KI-002 residual open** — `as_of` derivation has an explicit wall-clock fallback; `input_available_times=[as_of]` still makes PIT-2 vacuously true; VIX `FeatureValue` timestamps still synthetic; full `TemporalProvenance` not wired end-to-end. KI-003 (double Yahoo fetch) and KI-004 (no macro cache) open; KI-001 mitigated by cache only.
4. **Canonical pipeline still runs 3 `Stub` L4 registries** (DQ/Freshness/Drift; TODO v3.0).
5. **Gated pairs leak through the narrative/decision surfaces as generic non-actionable** — `forecast_eligibility` is not in the frontend contract/UI, so a RESTRICTED vs INSUFFICIENT_EDGE distinction is invisible to users.
6. **Layer 3 tail unchanged** — `run_benchmarks.py` crashes; `run.py` hardcoded; ARIMA unrunnable (`statsmodels`); L3 registry schema incompatible.
7. **LLM partial** — narrative uses `LLMFallbackManager` (Groq), but `EconomicInterpreter` unimported and `/interpretation` `include_macro` still hardcoded.
8. **Hardcoded/simulated remnants** — `/historical` random fallback; `/performance` hardcoded ece/max_dd/regime; FRED simulated without key; `FORECAST_DATA`/`layer1/decision/`/drivers-era methods dead; `MERIDIAN_MODEL_DIR` set but unconsumed.
9. **Frontend debt** — 4 hooks raw-fetch; `usePolling` orphan; Spanish strings vs `lang="en"` (mid-translation); 1,495 kB unminified bundle; `forecast_eligibility` unsurfaced.
10. **Governance/ops lag** — new surfaces (regime gate, divergence, temporal contracts, risk-for-RESTRICTED, English intelligence) not through the freeze loop; `.env.production` still an empty placeholder; CI gravity wrong (backend tests not actually run).

---

## 12. Recommendations

1. **Fix CI now (cheapest high-value):** point the backend job at the full suite (`pytest` from repo root via `pytest.ini`, or `pytest backend/tests -c pytest.ini`), install root/backend requirements in the job, and make the frontend job's install match `package-lock.json` (already `npm ci`). Consider moving the layer4 `pit_tests.py` to a `test_*` name so it is actually discovered.
2. **Close KI-002 (v2.8):** remove the wall-clock `as_of` fallback, populate `input_available_times`/`derived_available_time` with real per-input `source_available_time`, capture VIX observation timestamps, then mark KI-002-A/B/C resolved and delete/replace the diagnostic tests.
3. **Land the exchange-regime gate in the contract/governance loop:** freeze the provisional `EXCHANGE_REGIME_BY_PAIR` mapping with sources + effective dates, propagate `forecast_eligibility` to the frontend contract/Decision page (distinguish RESTRICTED from INSUFFICIENT_EDGE), and decide the RESTRICTED narrative treatment.
4. **Complete the canonical pipeline (v2.7→v2.8):** replace the three Stub registries with `PITValidator`-backed providers; push canonical decision/risk/narrative + divergence through traceability → gaps → freeze → validation.
5. **Unify ranking or drop it from Global:** either back `/v1/fx/ranking` with the canonical pipeline (v3.0 track B) or stop deriving the Global hero/market-intelligence from the legacy 1-pair ranking in the meantime.
6. **Clean model-path resolution:** consume `MERIDIAN_MODEL_DIR` in `engine.py`/`StatusEngine`/registry loaders (single resolution point), fold the canonical models into the gate methodology, and delete or align `train_models.py`.
7. **Cut the Layer 3/4 tail:** port `run_benchmarks.py` to `_get_model_for_pair` (or delete), replace hardcoded `run.py`, decide on `statsmodels`, reconcile the L3 registry schema.
8. **Resolve the LLM question fully:** wire `EconomicInterpreter` into `/interpretation` or delete it; remove the hardcoded `include_macro` block; make narrative `ADMIN_TOKEN`/SQLite deployment-aware.
9. **Frontend hardening:** finish the English pass, move the remaining 4 fetch hooks to `apiClient`, delete `usePolling`, and consider code-splitting + `minify` for the 1.5 MB bundle.
10. **Close the ops/governance book:** pin `VITE_API_URL` for production, keep the `KNOWN_ISSUES.md`/`STABLE.md` cadence (they are working well), and re-run `scripts/audit_consistency.py` + `scripts/audit_registry.py` after the v2.8 work.