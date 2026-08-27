# Meridian FX — Repository Report

**Date:** 2026-08-27 · **Branches:** (single working tree) · **History:** 17 commits (2026-08-25 → 2026-08-27)

This is an analysis of the repository as it stands today: what it is, what it contains, how it is governed, its verification status, and its known gaps and risks.

---

## 1. What this is

**Meridian FX** is an FX ("foreign exchange") intelligence product whose guiding principle is:

> *"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."*

It answers six product questions in its MVP (4 pairs: USD/JPY, EUR/USD, GBP/USD, USD/CNY):

| # | Question | Module |
| --- | --- | --- |
| 1 | What is happening in the market? | Global Overview |
| 2 | What does Meridian expect? | Forecast Dashboard |
| 3 | Why? | Drivers & Explanation |
| 4 | Is it worth acting? | Economic Filter |
| 5 | What could invalidate the signal? | Signal Validity |
| 6 | How good has Meridian been? | Performance Dashboard |

The repo is **not yet a runnable single application**. Today it contains:

1. A fully tested **backend decision engine** (Python — "Layer 2") that turns a frozen `PredictionArtifact` into a `Decision` through a deterministic, gate-driven pipeline.
2. A fully developed, contract-driven **frontend** (React + TypeScript) whose pages are wired to the Layer 1 delivery contracts the backend supplies.
3. A large **documentation + prompt suite** (Domain/HLD/LLD/Product specification/Contract/Prompts) that freezes the contracts and drives implementation by governance.

---

## 2. Repository layout

```
MeridianFX/
├── docs/
│   ├── Domain/                Commercial pitch, economic theory, data acquisition, production strategy
│   ├── High-Level Design/     Executive summary, product spec (the mockup), build strategy, roadmap, glossary, MLOps
│   ├── Low-Level Design/      Implementation plan + Layer_01..04 specifications
│   ├── Product_specification/ Frozen Layer_01..04 (the contract authority)
│   └── Contract/              Traceability matrix, gaps registry, freeze, validation audit, migration report, component mapping
│   └── Prompts/               The prompt-sequence that generated the implementation (layer prompts, frontend prompts)
├── src/meridian_fx/decision/  Python — Layer 2 Decision Engine (+ Layer 1 delivery mapping validation)
├── tests/                     Backend test suite (11 files)
├── frontend/                  React + TypeScript + Vite + Tailwind contract-driven frontend
└── pyproject.toml             Pydantic-only backend project config
```

> Observation: the root and `frontend/` README files are effectively empty, `venv/` and `.pytest_cache/` sit in the tree, and a large part of the implementation is currently **untracked** by git (backend `src/`, `tests/`, `frontend/`, and the newest `docs/Contract` + `docs/Prompts` artifacts). Housekeeping would be worthwhile before a real commit/PR cycle.

---

## 3. Backend — Layer 2 Decision Engine (Python)

Package root: `src/meridian_fx/decision/`. It is frozen against `docs/Product_specification/Layer_02.md` v3.4.1 and consumes Layer 3 v5.0 (§11.2) and Layer 4 v3.1.1 (§7) inputs. The governing rule on every module docstring: **IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.**

### 3.1 Pipeline flow (`pipeline.py`)

`DecisionPipeline.build(PipelineInputs) → DecisionPipelineResult` orchestrates:

1. **Signals** — raw quant / macro / RAG scores into `SignalComponents` (bounds-checked).
2. **Regime + Fusion** — `determine_regime()` → `FusionEngine.fuse()` (regime-weighted quant/macro/RAG fusion).
3. **Confidence** — `ConfidenceCalculator` (model confidence from prediction interval width + weighted signals + historical reliability).
4. **Costs** — `CostCalculator.calculate_total_cost()`; **VIX is read ONLY via `FeatureStore.get_feature('vix')`** (patch P2 — no alternative VIX path).
5. **Economic filter** — `EconomicFilter.apply()` → `net_return`, `edge_ratio`, `actionable` against a `required_minimum_edge` policy.
6. **Decision quality** — `DecisionQualityEngine` consuming Layer 4 registries (DataQuality / Freshness / Drift) (P5).
7. **Hard gates** — `HardGateEngine.evaluate()` (precedence-ordered: data quality, PIT availability, economic filter, exposure, correlation, regime alignment) → `GateResult` whose `signal_validity` is assigned **directly** to `Decision.signal_validity` (P3).
8. **Position sizing** — `PositionSizingEngine.calculate()` (edge × quality × VIX volatility factor; capacity check is secondary, P7).

Plus short-circuit paths for out-of-bounds signals and invalid edge thresholds, which produce `NEUTRAL/INVALID` decisions with a `RejectionReason`.

### 3.2 Module breakdown

| Package | Public API (highlight) | Role |
| --- | --- | --- |
| `contracts/` | `Decision`, `DecisionContext`, `PredictionArtifact`, `SignalComponents`, `FusionEngine`, `ConfidenceCalculator`, `determine_regime`, `compute_regime_alignment`, `FeatureStore`, `DataQualityRegistry`, `FreshnessRegistry`, `DriftRegistry`, `utcnow` | Frozen domain contracts (Pydantic); L3/L4 provider interfaces consumed, never implemented here (P5) |
| `filter/` | `EconomicFilter`, `CostCalculator`, `CostBreakdown`, `PairCategory`, `COMMISSION_BPS`, `CATEGORY_CATALOG` | §7.1 net-return/edge formula + §7.2 dynamic transaction costs (VIX-gated) |
| `gates/` | `HardGateEngine`, `GateResult`, `GateState`, `GATE_PRECEDENCE`, thresholds | Precedence-ordered hard gates + rejections |
| `quality/` | `DecisionQualityEngine`, `DecisionQuality`, `QualityLevel`, `FallbackStatus` | Quality score from L4 registries (P5, P6 status mapping) |
| `sizing/` | `PositionSizingEngine`, `PositionSizeResult`, `PositionMultipliers` | Volatility/edge/quality-based sizing (P7 secondary capacity) |
| `registries/` | `DecisionRegistry`, `OpportunityRegistry`/`OpportunityScorer`/`RankedOpportunity`, `SafeModeRegistry` | Persistence abstraction (P8 — no Layer 1 delivery fields), ranking (§10), safe-mode state for Layer 1 |
| `validation/` | `validate_contracts.py`, `validate_integration.py` | Contract-fidelity audit + end-to-end mapping to `ForecastResponse` (P9) and Synthetic Dataset D/D2 PIT acceptance (P10) |
| `pipeline.py` | `DecisionPipeline`, `PipelineInputs`, `DecisionPipelineResult` | Orchestration glue — defines NO new contracts |

### 3.3 Verification

`python -m pytest` → **99 passed** across 11 test files (contracts, quality, gates, costs, economic filter, sizing, registries, pipeline, signals/fusion, validation). Runtime ~0.08s.

---

## 4. Frontend — contract-driven dashboard (React + TypeScript)

Stack: **React 18 + TypeScript + Vite + Tailwind + TanStack Query + date-fns + React Router**. Everything is built against `frontend/src/types/contracts.ts` (571 lines; every field carries a `Layer 1 v5.1 §x` JSDoc reference — the Layer 1 delivery schema).

### 4.1 Layered architecture

```
types (contracts / gaps / infrastructure)
   → services (transport-only adapters → /v1/fx/{pair}/forecast|drivers, /v1/fx/ranking,
              /v1/fx/performance/{pair}?period=, /v1/status)
      → hooks (useForecast/useRanking/useDrivers/usePerformance/useStatus + Polling +
               useActivePair/usePerformancePeriod UI nav)
         → PRESENTATIONAL components (props-only, NO hooks, NO analysis)
            → pages (composition: hooks → props)
               → layout (Sidebar/Header/MainLayout) + routing (5 routes)
```

- **Transport layer** (`api.ts`) is pure axios: base URL, bearer key, timeout, exponential-backoff retry. It "MUST NOT transform responses."
- **Utils** (`format.ts`, `status.ts`) are presentational only — they may re-format backend values but never calculate/infer/derive (e.g. `isActionable()` is forbidden; consume `decision.actionable`).
- **Presentational components** (Prompt X v1.3): `components/common|global|forecast|drivers|evaluation|status`. Verified by grep to contain no hooks and no analysis/network logic.
- **Composition pages** (Prompts 4-8): `GlobalPage`, `ForecastPage`, `DriversPage`, `EvaluationPage`, `StatusPage`. Verified by grep to contain no `.sort/.reduce/Math.*`.
- **Gap rendering**: unsupported mockup datums render `NotAvailable` with `NO_FALLBACK_ALLOWED` / `NO_DERIVATION_ALLOWED` (e.g. Early Warnings, Key Events calendar, calibration curve, cumulative-return series, ranking-card probability/net/signal).

### 4.2 Presentational surface (23 components)

`Header, StatusBadge, RegimeBar, UniverseSelector, TabNav, Panel` (common) · `RankingCard, EarlyWarnings` (global) · `ForecastHero, ProbabilityGauge, ProbabilityChart, EconomicFilter, SignalValidity` (forecast) · `ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel` (drivers) · `PerformanceTable, CalibrationChart, CumulativeChart, DriftIndicator` (evaluation) · `SystemStatus, InfrastructureStatus` (status).

### 4.3 Verification

`npm run build` (tsc + vite) ✅ · `TZ=UTC vitest run` → **55 passed** across 7 files (contract fidelity, format/status/gaps utils, services, hooks) · production bundle ~310 kB JS / ~11 kB CSS.

---

## 5. Documentation & governance model

The repo is built **prompt-first**: the `docs/Prompts/` sequence drives each layer, and the "freeze" artifacts in `docs/Contract/` police contract fidelity:

| Artifact | Purpose |
| --- | --- |
| `CONTRACT_TRACEABILITY.md` (v2.0) | 73-row matrix mapping every frontend data element to its Layer 1 §7 source (61 verified / 12 gap rows; honest tallies) |
| `CONTRACT_GAPS.md` (v2.0) | 16 unified gaps: G1–G9 (getForecastHistory, getHealth, position_size_recommendation, regime, calendar…) + audit gaps EC-1..4 (economic-filter costs), RA, CA (calibration series), DF-P (cumulative series) |
| `FRONTEND_CONTRACT_FREEZE.md` (v2.0) | "FREEZE WITH OPTIONAL GAPS" — 0 blocking items |
| `CONTRACT_VALIDATION.md` | Prompt 1 audit: 7/7 contracts reviewed, **PASS** (F1–F3 cosmetic shared-type relaxations) |
| `MIGRATION_REPORT.md` | 66 mockup visual elements → status classification (SUPPORTED/UNSUPPORTED/AMBIGUOUS), 100% enumerated |
| `COMPONENT_MAPPING.md` | 100% data-bearing field → component → file, + page-wiring table |

Layered specs (`Product_specification/Layer_01..04`, mirrored in Low-Level Design) are the frozen source of truth for both the backend contracts (`Layer_02`) and the frontend delivery schema (`Layer_01 §7`).

---

## 6. Current status & known gaps

**Green**
- Backend Layer 2 decision engine: 99/99 tests, contract-fidelity and PIT/D2 validation enforced.
- Frontend: presentational + composition layers complete; 55/55 tests; typecheck and production build clean.
- Contract governance artifacts all written and cross-referenced; 0 blocking gaps.

**Gaps (by design, all optional/deferred — see `CONTRACT_GAPS.md`)**
- G1 — forecast history endpoint (no `getForecastHistory`); G2 — health endpoint; G3 — `position_size_recommendation` (distinct from supported `position_size`); G4 — global "Market Regime" stream (regime is per-pair via drivers only); G5 + EC-1..4 — economic calendar and the cost-breakdown fields (spread/slippage/fees/minimum edge) the mockup shows but Layer 1 does not expose; G6 — `isActionable()` (frontend must consume `decision.actionable`); G7–G9 — history/health/lineage pages deferred; RA — Risk Appetite; CA — calibration curve series; DF-P — cumulative-return series.

**Risks / observations**
1. **No Layer 1 delivery API in the repo yet.** The frontend targets `/v1/fx/...` endpoints and the backend validation maps `Decision → ForecastResponse`, but there is no FastAPI app serving those routes — the production blueprint (Render/Neon, mockup) is described in docs only.
2. **No test fixtures in the repo for a live backend** — the dashboard needs the Layer 1 service to be > a mocked contract to smoke-test end-to-end.
3. **Empty/inconsistent docs**: root `README.md` and `requirements.txt` are empty; root docs exist but are not summarized anywhere.
4. **Git hygiene**: much of the implemented work is uncommitted; `venv/`, `.pytest_cache/`, and `frontend/dist/` are present in the tree (`.gitignore` quality should be reviewed).
5. **Single-horizon / 4-pair MVP only** — everything beyond (multi-horizon, more pairs, RAG/NLP, MLflow) is explicitly deferred to V2/V3.

---

## 7. Recommendations

1. **Add the Layer 1 delivery service** (per `Product_specification/Layer_01.md`): a minimal FastAPI app that reuses Layer 2's `DecisionPipeline`/registries and emits the `ForecastResponse`/`RankingResponse`/etc. payloads the frontend already consumes — this closes the repo's biggest gap.
2. **Wire the contract-test seam**: extend the frontend `contracts/validate.test.ts` fixtures to assert exactly the shapes the API will emit, then run them against real responses.
3. **Populate the root `README.md`** (overview, quickstart, test commands, links to `architecture.md`, `docs/`) and `requirements.txt`.
4. **Clean git hygiene**: add a proper `.gitignore` (venv, caches, dist), review untracked files, and land the work in reviewed commits.
5. **Re-run the audit loop** if any contract changes are requested (traceability → gaps → freeze → validation), per the established governance model.