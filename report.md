# Meridian FX — Repository Report

**Date:** 2026-08-30 · **Branch:** `main` (in sync with `origin/main`) · **History:** 31 commits (2026-08-25 → 2026-08-29) · **Latest tag:** `v2.3.0`

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

Since the previous report (2026-08-29), the repo shipped **FASE 7 + `v2.3.0`**: a SignalIQ-style Global Intelligence page (currency selector, live spot, interactive price chart), a rebuilt Forecast Dashboard, and two new **real-data** Layer 1 endpoints — `GET /v1/fx/{pair}/price` and `GET /v1/fx/{pair}/forecast-dashboard` (trends, volatility, XGBoost 30/60/90-day forecasts, FRED macro context). Crucially, the **frontend is green again**: TypeScript clean, 55/55 tests, and a passing production build (previously red). `requirements.txt` went from empty to a full backend dependency manifest.

The repo remains a working multi-layer application: a real FastAPI delivery service (`layer1/`), a live Layer 2 engine wired to XGBoost/SHAP/multi-source market data/FRED macro (`layer2/`), and a bilingual rebuilt frontend. Several live endpoints are still served by hardcoded or simulated data.

---

## 2. Repository layout

```
MeridianFX/
├── docs/                        Frozen specs, prompts, and contract governance (Domain / HLD / LLD / Product_specification / Contract / Prompts)
├── src/meridian_fx/decision/    Layer 2 Decision Engine (contract-governed, 8-stage pipeline, tests)
├── layer1/                      FastAPI delivery API — implemented (routers, models, adapters, LLM, decision)
├── layer2/                      Live engine — XGBoost, SHAP, data providers (Yahoo/Alpha Vantage/Twelve/FRED), macro, ranking
├── tests/                       Backend pytest suite (11 files)
├── frontend/                    React + TypeScript + Vite contract-driven dashboard (+ Recharts)
├── models/                      Trained XGBoost (.pkl) + logistic models and registry.json
├── cache/                       Runtime forecast + macro caches
├── train_models.py              XGBoost training script (registers into ModelRegistry)
├── test_macro.py                MacroService tests
├── pyproject.toml               Backend project config (pydantic, pytest)
├── requirements.txt             Backend dependencies — POPULATED (2026-08-30 update)
├── vite.config.ts               Frontend Vite config (port 5174)
├── README.md                    Product overview + quickstart
├── report.md                    This document
└── architecture.md              System architecture
```

> **Working-tree hygiene:** `cache/forecast_cache.json` is modified (uncommitted runtime cache). An untracked stray file `ión estable 2.3.0 - Global Intelligence con gráfico SignalIQ, ...` sits at the repo root — an accidental file created from a copy-pasted commit message (contains the `v2.3.0` commit body); it should be deleted.

---

## 3. Backend — the two engines

The backend has **two cooperating codebases** with distinct roles:

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

`layer1/` is a **real FastAPI app** (`main.py`, title "Meridian FX API" v1.0.0), with CORS restricted to `localhost:5174` / `127.0.0.1:5174`, **9 routers**, `/` and `/health`.

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
| GET | `/v1/fx/{pair}/price?period=` | **live** — spot, 100-point history, XGBoost signal (`layer1/routers/price.py`) |
| GET | `/v1/fx/{pair}/forecast-dashboard` | **live** — spot, trends 1m/3m/6m/1y, volatility, XGBoost 30/60/90d, macro (`layer1/routers/forecast_dashboard.py`) |

The two newest endpoints (`price`, `forecast-dashboard`) are the only forecast-flavored routes backed by **real market + ML data** (via `layer2.DataProvider` + `TechnicalFeatures` + `DecisionEngine.xgb_model` + `MacroService`); the legacy `/forecast` route remains hardcoded.

### 4.2 Supporting modules

- **`models/responses.py`** — Pydantic response models mirroring Layer 1 §7.1–7.7 (`ForecastResponse`, `DriversResponse`, `RankingResponse`, `PerformanceResponse`, `StatusResponse`).
- **`adapters/decision_to_response.py`** — `DecisionAdapter` maps dicts → response models (only exercised by `performance`).
- **`decision/`** — `decision_context.py` (`DecisionContext`, `MacroContext`, `DecisionEngine.build_context`), `economic_filter.py` (cost-aware variant), `signal_validity.py` (thesis/invalidation conditions).
- **`llm/`** — `base.py` (`LLMProvider` ABC), `providers.py` (Groq live; GLM/Gemini stubs; rule-based `FallbackLLM`), `manager.py` (fallback chain), `interpreter.py` (`EconomicInterpreter` → bilingual Spanish economic bullets).

**Observations:**
- There are **two classes both named `DecisionEngine`** — Layer 1's `decision/decision_context.py` (interpretation context) vs Layer 2's `engine.py` (forecasting). They are distinct by purpose.
- `ForecastResponse`/`DecisionAdapter` exist but `/forecast`, `/price`, and `/forecast-dashboard` return **raw dicts**, not the Pydantic response models.
- `EconomicInterpreter.interpret()` currently **always** uses the rule-based fallback — the Groq chain is built but not invoked.
- Performance/status are hardcoded/mock; the drivers macro-regime & RAG sections are placeholders.

---

## 5. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 + TypeScript + Vite (port 5174) + Tailwind + TanStack Query + axios + date-fns + React Router + Recharts** (Recharts added in `v2.3.0` for the interactive charts). Contract root `frontend/src/types/contracts.ts` mirrors Layer 1 v5.1 §7; gaps live in `types/gaps.ts` (G1–G5).

### 5.1 Routes & composition

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useForecastDashboard`, `useActivePair` |
| `/forecast` | ForecastPage | `useForecastDashboard`, `useRanking`, `useActivePair`, `useMacroContext` |
| `/drivers` | DriversPage | `useDrivers`, `useRanking`, `useActivePair` |
| `/evaluation` | EvaluationPage | `usePerformance`, `usePerformancePeriod`, `useActivePair` |
| `/status` | StatusPage | `useStatus` |
| `/price` | PricePage | `usePrice`, `useRanking`, `useActivePair` |
| `/about` | AboutPage | (narrative) |

Notes since the last report: `/historical` is **no longer routed** (`HistoricalPage.tsx` is now orphaned); a new `/price` route (PricePage) was added. The old `/forecast` data hooks were superseded: both GlobalPage and ForecastPage now consume the live `/forecast-dashboard` endpoint via `useForecastDashboard`, which replaced the contract-driven `useForecast`/`useInterpretation` wiring on those pages.

Navigation state is URL-shared via `?pair=` and `?period=`. Two data-access styles coexist: the older contract-driven `services/*` (axios, retry+backoff) used by `usePerformance`/`useStatus`, and the newer direct-`fetch` hooks using `import.meta.env.VITE_API_URL` (`useForecastDashboard`, `usePrice`, `useForecast`, `useRanking`, `useDrivers`, `useInterpretation`, `useMacro`).

### 5.2 SignalIQ-style Global Intelligence + rebuilt Forecast Dashboard (v2.3.0)

- `GlobalPage` — SignalIQ-inspired layout: currency `UniverseSelector`, live spot header (price, Δ day, forecast badge), `PriceChartSignalIQ` (area chart with gradient, hover tooltip, 30d/90d/6m/1y range), 30/60/90-day XGBoost prediction cards, FRED macro context, and the ranking table.
- `ForecastPage` — rebuilt around the live `/forecast-dashboard` payload: `SpotCard`, `TrendCard` (1m/3m/6m/1y returns), `ForecastCard` (30/60/90d), `MacroPanel`, plus the FRED macro grid.
- New shared components: `PriceChartSignalIQ`, `PriceChartWithHover`, `ForecastCard`, `SpotCard`, `TrendCard`.
- Both pages reuse `RegimeStrip` (mockup) with **hardcoded inputs** (`regime="UNKNOWN"`, `vix={16.8}`, `riskAppetite={0.72}`).

### 5.3 Macro dashboard (FRED) — FASE 5.4

`components/macro/MacroPanel.tsx` + `hooks/useMacro.ts` (tag `v2.3.0-macro-panel`). Renders an 8-indicator macro grid (Fed Funds, inflation, unemployment, GDP, 10Y/2Y yields, 10-2 spread, confidence), policy/growth/inflation signal badges, and FX-relevance, fed by `GET /v1/fx/interpretation?pair=USD/JPY&include_macro=true` and `GET /v1/fx/macro/status`. Wired into `ForecastPage` (5-min refetch, 4-min staleTime).

### 5.4 Presentational surface (~34 components)

`common/*` (Panel, StatusBadge, RegimeBar, UniverseSelector, TabNav, NotAvailable, ApiError, LoadingSpinner, ErrorBoundary, ThemeProvider, MetricsHelp, Header), `global/*` (RankingTable, RankingCard, EarlyWarnings, PriceChartSignalIQ, PriceChartWithHover), `forecast/*` (ForecastHero, ForecastCard, SpotCard, TrendCard, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity, + unexported mockup WhyNow/DataTimestamps), `drivers/*` (ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel), `evaluation/*` (PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator), `status/*` (SystemStatus, InfrastructureStatus), `layout/*` (Header, Footer, MainLayout), `macro/*` (MacroPanel), `mockup/*` (Gauge, PipelineStepper, RegimeStrip, SHAPBar). `Header` now lives under `layout/` (nav includes Price).

### 5.5 Verification — ✅ all green again

| Check | Previous report | Now |
| --- | --- | --- |
| Backend pytest | 99 passed | **99 passed** ✅ |
| Frontend typecheck (`npm run typecheck`) | FAILS | **clean** ✅ |
| Frontend tests (`npm test`) | not re-verified | **55 passed** ✅ |
| Frontend build (`npm run build`) | FAILS | **OK** ✅ |

The previous red items were repaired:
- `SystemStatus.tsx` no longer reads `.status` on the string-enum health types (`model_performance`, `model_drift`, `decision_validity` rendered verbatim via `Row`).
- `DEFAULT_STATUS_COLOR` is exported from `utils/status.ts`; `getSignalStrengthLabel` now accepts `number | string` (matches the corrected tests).

One build warning remains (non-blocking): the main bundle is > 500 kB (722 kB minified) — chunking/code-splitting suggested.

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
- Frontend: typecheck clean, **55/55 tests**, production build OK — previously red, now repaired.
- Layer 1 FastAPI app integrated with Layer 2 (`ranking`, `historical`, `drivers`, `price`, `forecast-dashboard`, `interpretation`/macro) — the last two are the first **real-data** forecast/price routes.
- Full live engine: multi-source market data failover, XGBoost + ModelRegistry, SHAP explainers, FRED macro subsystem, ranking over 9 pairs.
- Frontend gained the FRED macro dashboard + SignalIQ-style Global Intelligence; bilingual (ES/EN) UI; `requirements.txt` populated.

**Red / attention**
1. **Live endpoints are largely hardcoded/mock/simulated**: `/forecast` uses static `FORECAST_DATA` (+ random fallback), `/performance` is mock, `/status` hardcoded HEALTHY, drivers macro/RAG are placeholders, and FRED returns **simulated** data because `FRED_API_KEY` is not set. Real-data routes: `ranking`, `historical`, `drivers` (SHAP), and the new `price`/`forecast-dashboard`.
2. **Duplicate `FORECAST_DATA`** maintained in `forecast.py` and `interpretation.py` — no single source of truth (and `/forecast` still bypasses the live engine).
3. **Two `DecisionEngine` classes** with the same name in Layer 1 vs Layer 2 — confusing; consider renaming.
4. **`EconomicInterpreter` never invokes the LLM chain** (always rule-based fallback).
5. **Contract-shape drift in active pages** vs `contracts.ts` (GlobalPage/ForecastPage check `direction === 'UP'`; hardcoded `vix={16.8}`/`riskAppetite`/`regime="UNKNOWN"` in `RegimeStrip`; `RankingTable` locally derives returns — the no-derivation guardrail is not consistently honored by the newer pages).
6. **Env-key mismatch**: services use `VITE_API_BASE_URL`, direct-fetch hooks use `VITE_API_URL`; `.env` sets only the latter (works by coincidence of defaults).
7. **Dead/stale artifacts**: `*.bak` ×5 (`transformer.py.bak`, `engine.py.bak`, `UniverseSelector.tsx.bak`, `Sidebar.tsx.bak`, `forecast.py.bak`), orphaned `HistoricalPage.tsx` (route removed), unused `WhyNow`/`DataTimestamps`/`ForecastHero`, unused `mockup/*` (`Gauge`, `PipelineStepper`, `SHAPBar`), empty `data/historical/`.
8. **Git hygiene**: stray untracked file at repo root (copy-pasted `v2.3.0` commit message); `cache/forecast_cache.json` modified (uncommitted). Branch is in sync with `origin/main`.

---

## 9. Recommendations

1. **Route `/forecast` through the live engine** — `forecast-dashboard` already computes real trends/forecasts; reuse it (or share a single 9-pair data module) so `/forecast` and `/interpretation` stop duplicating `FORECAST_DATA`.
2. **Invoke the LLM chain** in `EconomicInterpreter.interpret()` (currently bypassed), with the rule-based fallback retained as the safety net.
3. **Resolve the dual-`DecisionEngine` naming** and document the relationship between `src/meridian_fx/decision/` (contract-governed) and `layer2/` (live engine) — they are currently unconnected.
4. **Align the newer pages to the contract discipline** (Global/Forecast): remove hardcoded `VIX`/`riskAppetite` and the `direction === 'UP'` derivation; consume `contracts.ts` enums.
5. **Tidy governance docs** for the new pages (Global Intelligence, Forecast rebuild, `price`/`forecast-dashboard` endpoints) so traceability/gap registries stay in sync with what ships.
6. **Clean up**: delete the stray root file and the `.bak`/orphaned/unused components, remove or populate `data/historical/`, and align env keys (`VITE_API_BASE_URL` vs `VITE_API_URL`).
7. **Re-run the audit loop** if contract shape changes are made during frontend work (traceability → gaps → freeze → validation), per the established governance model.