# Meridian FX — Repository Report

**Date:** 2026-08-29 · **Branch:** `main` (ahead of `origin/main` by 10 commits) · **History:** 27 commits (2026-08-25 → 2026-08-28) · **Latest tag:** `v2.3.0-macro-panel`

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

Since the previous report (2026-08-27), the repo has moved from a **specification + decision-engine-only** state to a **working multi-layer application**: a real FastAPI delivery service (`layer1/`), a live Layer 2 engine wired to XGBoost/SHAP/multi-source market data/FRED macro (`layer2/`), and a rebuilt bilingual frontend with a FRED macro dashboard. It is now much closer to a *runnable* system, albeit with several live endpoints still served by hardcoded or simulated data.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs, prompts, and contract governance (Domain / HLD / LLD / Product_specification / Contract / Prompts)
├── src/meridian_fx/decision/    Layer 2 Decision Engine (contract-governed, 8-stage pipeline, tests)
├── layer1/                      FastAPI delivery API — implemented (routers, models, adapters, LLM, decision)
├── layer2/                      Live engine — XGBoost, SHAP, data providers (Yahoo/Alpha Vantage/Twelve/FRED), macro, ranking
├── tests/                       Backend pytest suite (11 files)
├── frontend/                    React + TypeScript + Vite contract-driven dashboard
├── models/                      Trained XGBoost (.pkl) + logistic models and registry.json
├── cache/                       Runtime forecast + macro caches
├── train_models.py              XGBoost training script (registers into ModelRegistry)
├── test_macro.py                MacroService tests
├── pyproject.toml               Backend project config (pydantic, pytest)
├── requirements.txt             (empty)
├── vite.config.ts               Frontend Vite config (port 5174)
├── README.md                    Product overview + quickstart
├── report.md                    This document
└── architecture.md              System architecture
```

---

## 3. Backend — the two engines

The backend now has **two cooperating codebases** with distinct roles:

### 3.1 `src/meridian_fx/decision/` — the contract-governed Decision Engine

Package root: `src/meridian_fx/decision/`. Frozen against `docs/Product_specification/Layer_02.md` v3.4.1; consuming Layer 3 v5.0 (§11.2) and Layer 4 v3.1.1 (§7) inputs. Rule on every module docstring: **IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.**

`DecisionPipeline.build(PipelineInputs) → DecisionPipelineResult` runs 8 stages — Signals → Regime+Fusion → Confidence → Costs → Economic filter → Quality → Hard gates → Sizing — plus short-circuit paths (out-of-bounds signals, invalid edge thresholds) that yield `NEUTRAL/INVALID` decisions. Key invariants are encoded as patches P1–P10 (P2: VIX only via `FeatureStore`; P3: `GateResult.signal_validity` assigned directly to `Decision`; P8: DecisionRegistry never stores Layer 1 delivery fields; P9/P10: delivery mapping + synthetic Dataset D/D2 PIT acceptance validated).

| Package | Responsibility |
| --- | --- |
| `contracts/` | Frozen domain contracts (Decision, PredictionArtifact, FusionEngine, ConfidenceCalculator, regime helpers, provider protocols) |
| `filter/` | §7.1 economic filter + §7.2 dynamic transaction costs (VIX-gated) |
| `gates/` | Precedence-ordered hard gates (data quality, PIT, economic, exposure, correlation, regime) |
| `quality/` | Decision quality from L4 registries |
| `sizing/` | Position sizing from edge × quality × VIX-volatility |
| `registries/` | Decision, Opportunity/ranking (§10), Safe-Mode registries |
| `validation/` | Contract-fidelity audit + end-to-end L1 mapping + Synthetic D/D2 PIT acceptance |
| `pipeline.py` | Composition root — orchestrates the 8 stages, defines no new contracts |

**Verification:** `python -m pytest` → **99 passed** across 11 files (~0.09s).

### 3.2 `layer2/` — the live engine (data + ML)

Package root: `layer2/`. This is the *wired* engine that actually fetches data, runs ML, and explains it.

- **Data layer** (`data/`): `DataProvider` with ordered failover **Yahoo → Alpha Vantage → Twelve Data**; `data/sources/` for each (plus `fred.py` for macro series with a simulated fallback when `FRED_API_KEY` is absent); `data/macro/` implements `MacroService` (FRED fetch) + `MacroCache` (on-disk, 24 h TTL) + `MacroTransformer` (summaries, indicators, FX relevance).
- **Features** (`features/technical.py`): 23 technical indicators (SMA/EMA, RSI, MACD, Bollinger, ATR, momentum, ROC, volatility, ADX, Aroon, Stochastic) — `get_feature_names()` is the shared column contract.
- **Models** (`models/`): `XGBoostModel` (100 est, depth 5, LR 0.05, logloss) and `LogisticModel` (baseline); `ModelRegistry` manages versioned `.pkl` artifacts via `models/registry.json`, auto-activating a model when its AUC beats the current active one.
- **Explainers** (`explainers/shap_explainer.py`): SHAP `TreeExplainer` (tree_path_dependent), log-odds→probability, top-10 contributions.
- **Ranking** (`ranking/engine.py`): `RankingEngine` over the 9 pairs that have active XGBoost models; score = 60% probability + 40% normalized edge ratio.
- **Decision filter** (`decision/filter.py`): simplified `EconomicFilter` (edge ratio, confidence, signal strength, position size) using config thresholds.
- **`engine.py`**: `DecisionEngine` with a persistent on-disk forecast cache (5-min TTL) and a heuristic (RSI/MACD) fallback. `engine.py.bak` is an unused backup.

**Key observation:** the frozen `src/meridian_fx/decision/` and the live `layer2/` both implement an "economic filter / decision" step but are **not wired to each other** — `layer1/` routers consume `layer2/` directly. The `src/` engine is the verified contract-governed design; `layer2/` is what the live API actually runs.

---

## 4. Backend — Layer 1 FastAPI delivery API (implemented)

`layer1/` is now a **real FastAPI app** (`main.py`, title "Meridian FX API" v1.0.0), with CORS restricted to `localhost:5174`, 7 routers, `/` and `/health`.

### 4.1 Endpoints

| Method | Path | Source / notes |
| --- | --- | --- |
| GET | `/` , `/health` | root + health |
| GET | `/v1/status` | **hardcoded** HEALTHY |
| GET | `/v1/fx/ranking` | `layer2.RankingEngine` (live, 9 pairs) |
| GET | `/v1/fx/{pair}/drivers` | `layer2.DecisionEngine` SHAP + mostly-placeholder macro/RAG |
| GET | `/v1/fx/{base}/{quote}/forecast` | **hardcoded** `FORECAST_DATA` (9 pairs) + random fallback |
| GET | `/v1/fx/performance/{pair}?period=` | **mock** data |
| GET | `/v1/fx/{pair}/historical` | `layer2` data + features (with stochastic fallback) |
| GET | `/v1/fx/interpretation?pair=` | Layer 1 `DecisionContext` + `EconomicInterpreter` + `MacroService` (FRED) |
| GET | `/v1/fx/macro/status` | FRED macro cache status |
| POST | `/v1/fx/macro/refresh` | force FRED refresh |

### 4.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7 (`ForecastResponse`, `DriversResponse`, `RankingResponse`, `PerformanceResponse`, `StatusResponse`).
- **`adapters/decision_to_response.py`** — `DecisionAdapter` maps dicts → response models (only exercised by `performance`).
- **`decision/`** — `decision_context.py` (`DecisionContext`, `MacroContext`, `DecisionEngine.build_context`), `economic_filter.py` (cost-aware variant), `signal_validity.py` (thesis/invalidation conditions).
- **`llm/`** — `base.py` (`LLMProvider` ABC), `providers.py` (Groq live; GLM/Gemini stubs; rule-based `FallbackLLM`), `manager.py` (fallback chain), `interpreter.py` (`EconomicInterpreter` → bilingual Spanish economic bullets).

**Observations:**
- There are **two classes both named `DecisionEngine`** — Layer 1's `decision/decision_context.py` (interpretation context) vs Layer 2's `engine.py` (forecasting). They are distinct by purpose.
- `ForecastResponse`/`DecisionAdapter` exist but the live `/forecast` route returns a raw dict, not the model.
- `EconomicInterpreter.interpret()` currently **always** uses the rule-based fallback — the Groq chain is built but not invoked.
- Performance/status are hardcoded/mock; the drivers macro-regime & RAG sections are placeholders.

---

## 5. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 + TypeScript + Vite (port 5174) + Tailwind + TanStack Query + axios + date-fns + React Router**. Contract root `frontend/src/types/contracts.ts` mirrors Layer 1 v5.1 §7; gaps live in `types/gaps.ts` (G1–G5).

### 5.1 Routes & composition

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useDrivers`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecast`, `useRanking`, `useActivePair`, `useInterpretation`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/historical` | HistoricalPage | (placeholder) |
| `/about` | AboutPage | (narrative) |

Navigation state is URL-shared via `?pair=` and `?period=`. Two data-access styles coexist: the older contract-driven `services/*` (axios, retry+backoff) used by `usePerformance`/`useStatus`, and the newer direct-`fetch` hooks using `import.meta.env.VITE_API_URL` (`useForecast`/`useRanking`/`useDrivers`/`useInterpretation`/`useMacro`).

### 5.2 Macro dashboard (FRED) — most recent addition (FASE 5.4)

`components/macro/MacroPanel.tsx` + `hooks/useMacro.ts` (added in tag `v2.3.0-macro-panel`). Renders an 8-indicator macro grid (Fed Funds, inflation, unemployment, GDP, 10Y/2Y yields, 10-2 spread, confidence), policy/growth/inflation signal badges, and FX-relevance, fed by `GET /v1/fx/interpretation?pair=USD/JPY&include_macro=true` and `GET /v1/fx/macro/status`. Wired into `ForecastPage` (5-min refetch, 4-min staleTime).

### 5.3 Presentational surface (~29 components)

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp), `global/*` (RankingTable, RankingCard, EarlyWarnings), `forecast/*` (ForecastHero, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity, + unexported mockup WhyNow/DataTimestamps), `drivers/*` (ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel), `evaluation/*` (PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator), `status/*` (SystemStatus, InfrastructureStatus), `layout/*` (Header, Footer, MainLayout), `macro/*` (MacroPanel), `mockup/*` (Gauge, PipelineStepper, RegimeStrip, SHAPBar).

### 5.4 Verification — ⚠️ current failures

| Check | Previous report | Now |
| --- | --- | --- |
| Backend pytest | 99 passed | **99 passed** ✅ |
| Frontend typecheck (`npm run typecheck`) | clean | **FAILS** ❌ |
| Frontend build (`npm run build`) | OK | **FAILS** ❌ |
| Frontend tests | 55 passed | not re-verified (see below) |

The frontend is now **red** due to type errors:
- `src/components/status/SystemStatus.tsx:52-54` — reads `intelligence.model_performance?.status`, `model_drift?.status`, `decision_validity?.status`, but `ModelPerformanceHealth`, `ModelDriftHealth`, and `DecisionValidity` are **string enums in the contract** (the `.status` accessor is invalid).
- `src/tests/utils/status.test.ts:11` — imports `DEFAULT_STATUS_COLOR`, which is **not exported** by `src/utils/status.ts`.
- `src/tests/utils/status.test.ts:85-87` — passes string arguments to `getSignalStrengthLabel`, which takes a `number`.

These are contract/shape-drift issues introduced as pages were rebuilt in the FASE iterations; they should be repaired (align `SystemStatus` to the string-enum types, export the color default, fix the test signatures) before the next release.

---

## 6. Models & training

- `models/registry.json` — **10 registered models**: 9 XGBoost (USD/CHF, GBP/USD, USD/BRL, USD/ARS, USD/MXN, USD/JPY, USD/CNY, EUR/USD, USD/BOB) + 1 logistic (USD/JPY); each with `model_id`, `pair`, `model_type`, `version`, `metrics`, `created_at`, `active`.
- `train_models.py` — trains XGBoost per pair via `DataProvider` + `TechnicalFeatures` + `XGBoostModel` + `ModelRegistry`.
- Several `layer2` stubs remain empty: `models/trainer.py`, `features/derived.py`, `features/macro.py`, `macro/intelligence.py`.

---

## 7. Documentation & governance model

The repo is **prompt-first**: `docs/Prompts/` drives each layer, and `docs/Contract/` polices contract fidelity. Freeze artifacts (unchanged): `CONTRACT_TRACEABILITY.md` (73-row matrix, 61 verified / 12 gap), `CONTRACT_GAPS.md` (16 unified gaps), `FRONTEND_CONTRACT_FREEZE.md` ("FREEZE WITH OPTIONAL GAPS", 0 blocking), `CONTRACT_VALIDATION.md`, `MIGRATION_REPORT.md`, `COMPONENT_MAPPING.md`. Frozen specs: `Product_specification/Layer_01..04` (Layer 1 v5.1 is the frontend authority; Layer 2 v3.4.1 the backend authority).

---

## 8. Current status & known gaps

**Green**
- Backend pytest: **99/99** (contract fidelity + PIT/D2 validation enforced).
- Layer 1 FastAPI app implemented and integrated with Layer 2 (`ranking`, `historical`, `drivers`, `interpretation`/macro) — closes the biggest gap flagged in the previous report.
- Full live engine: multi-source market data failover, XGBoost + ModelRegistry, SHAP explainers, FRED macro subsystem, ranking over 9 pairs.
- Frontend gained the FRED macro dashboard; bilingual (ES/EN) UI.

**Red / attention**
1. **Frontend typecheck & build fail** (SystemStatus enum `.status` access; `status.test.ts` `DEFAULT_STATUS_COLOR` + `getSignalStrengthLabel` signature). Must be repaired.
2. **Live endpoints are largely hardcoded/mock/simulated**: `/forecast` uses static `FORECAST_DATA` (+ random fallback), `/performance` is mock, `/status` hardcoded HEALTHY, drivers macro/RAG are placeholders, and FRED returns **simulated** data because `FRED_API_KEY` is not set. Only `ranking`, `historical`, and `drivers` (SHAP) fetch real market/ML data.
3. **Two `DecisionEngine` classes** with the same name in Layer 1 vs Layer 2 — confusing; consider renaming.
4. **`EconomicInterpreter` never invokes the LLM chain** (always rule-based fallback).
5. **Duplicate `FORECAST_DATA`** maintained in `forecast.py` and `interpretation.py` — no single source of truth.
6. **Contract-shape drift in active pages** vs `contracts.ts` (e.g., `ForecastPage` checks `direction === 'UP'` vs contract `BULLISH/BEARISH`; `DriversPage` reads non-contract `features[]`/`policy_signal.*`; `RankingTable` locally derives returns — the no-derivation guardrail is not consistently honored by the newer pages).
7. **Env-key mismatch**: services use `VITE_API_BASE_URL`, direct-fetch hooks use `VITE_API_URL`; `.env` sets only the latter (works by coincidence of defaults).
8. **Dead/stale artifacts**: `*.bak` files (`forecast.py.bak`, `engine.py.bak`, `Sidebar.tsx.bak`, `UniverseSelector.tsx.bak`), unused `WhyNow`/`DataTimestamps`, unused `mockup/*` components, empty `requirements.txt`, empty `data/historical/`.
9. **Git hygiene**: working tree otherwise clean (only `cache/forecast_cache.json` modified); branch ahead of `origin/main` by 10 commits (unpushed).

---

## 9. Recommendations

1. **Fix the frontend build now** (highest priority, it's red): align `SystemStatus` to the string-enum health types, export `DEFAULT_STATUS_COLOR`, correct `getSignalStrengthLabel` calls; then re-run `typecheck`, `npm test`, and `build`.
2. **Centralize forecast data**: extract a single source of truth for the 9-pair `FORECAST_DATA` (config/module shared by `forecast.py` and `interpretation.py`), or better, route `/forecast` through `layer2` ML like `ranking`/`drivers` do.
3. **Invoke the LLM chain** in `EconomicInterpreter.interpret()` (currently bypassed), with the rule-based fallback retained as the safety net.
4. **Resolve the dual-`DecisionEngine` naming** and document the relationship between `src/meridian_fx/decision/` (contract-governed) and `layer2/` (live engine) — they are currently unconnected.
5. **Tidy governance docs** for the new pages (macro, Global/Forecast/Drivers rebuild) so the traceability/gap registry stays in sync with what ships.
6. **Populate `requirements.txt`** and prune `.bak`/dead components; land the 10 unpushed commits with a reviewed PR.
7. **Re-run the audit loop** if contract shape changes are made during frontend repair (traceability → gaps → freeze → validation), per the established governance model.
