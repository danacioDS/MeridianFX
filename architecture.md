# Meridian FX — Architecture

> Last reviewed: 2026-09-15 · HEAD `5c75999` (feat(frontend): regime divergence UI) · 220 commits · latest tag v2.7.5
> Backend pytest: 180 passed / 20 files — Frontend: 56 passed / 7 files, typecheck + build PASS (1,495 kB, 304 kB gzip)
> 13 FastAPI routers exposed — Prior architecture document: 2026-09-14 (HEAD e301138)

## 1. System context

Meridian FX is a four-layer forecasting platform for FX pairs. Request flow is strictly
downward (Layer 1 → Layer 2 → Layer 3 → Layer 4); no layer depends on one above it.
Research artefacts (`models/`) produced in Layer 3 feed the live engine in Layer 2 via a
versioned registry gated by a quality contract.

```
Browser (React/Vite SPA, 6 routes, direct engine calls)
   │
   ▼
[Layer 1] FastAPI delivery API — 13 routers, pure DTO/aggregation
   │  (decision_engine_adapter, currency_rule_adapter, registry, regimes→contract, gate model path)
   ▼
[Layer 2] Live engine — data pull, horizon model, canonicalModel + TargetType orchestration, /engine/spread
   │
   ▼
[Layer 3] Research layer — gate.py + scripts (standalone; imports quality contract + models/registry)
   │
   ▼
[Layer 4] Data-quality layer (PIT) — data_provider.last_date, TemporalProvenance + as_of, pit_tests.py
```

Key relationships (pairs `a:b`):
* **registry:bundle** — registry exposes one merged model bundle via a quality-gated path.
* **decision-engine:regime** — STARTS from exchange regime (KI-009), then DataQualityRegistry →
  KnowledgeBase (KI-002) → context → engine → per-decision gate policy.
* **regime:engine** — RiskEngine is still computed for RESTRICTED decisions (Opción B); verdict
  (OPEN/RESTRICTED) never changes the requirement to run the engine, only the requirement to return a signal.
* **regime:frontend** — RegimeWarningBanner reads engine.regime.

## 2. Repo map (top-level)

| Blob | Purpose |
|---|---|
| `pytests/` | Engine fixtures + contract tests, hidden from pytest discovery; **RESTRICTED runtime-only use**. |
| `backend/layer1/` | Delivery API. FastAPI, 4 adapters, DTO/contract assembly, registry read. Routers + `main.py` (13 mounts). |
| `backend/layer2/` | Live engine. Engine class, horizon model, gap fill, logging, **spread engine** (`/engine/spread`), PIT. |
| `backend/layer3/` | Research layer. Own DTOs; imports quality contract (registry, gaas, gate) + models. Standalone research scripts (data-aware, **hardcoded `RUN_DATE`**, `Layer3DataProvider`). |
| `backend/layer4/` | Data-quality (PIT) layer. `data_provider.last_date`, `pit_tests.py`, TemporalProvenance. |
| `backend/src/meridian_fx/` | The engine code package: models, contracts, decision engine + risk engine (backed by tests 1–6). |
| `frontend/` | React/Vite SPA: routes, hooks (11 module-based), components, auth/transport (`api/`), `shared/`. |
| `docs/` | Divergence description (`divergence/README.md`) and architecture doc. |
| `contracts.py` | Repo-root quality gate contract (meridian procedure). |
| `gate.py` | Repo-root research gate: dataset/high/low/buffer stats; generates `whole.universe.json` (single record). |
| `models/` | **BLANK** (registry holds routes, files are loaded only if present). |
| `external_data/` | Raw data (STATIC root, missing `eci.ipynb`). |
| `prompts/` | Maps. |
| `pytests/fixtures/` | Contract fixture files (copy of Data files). |
| `mock_financial_data/` | Engine test fixture data. |
| `docker-compose.yml` | 2 compat keys (`EXTERNAL_DATA`, `MERIDIAN_MODEL_DIR`) + 5 build args. |
| `Dockerfile`, `docker-compose.yml` | Deployment setup; Dockerfile copies `models/` (gap closed 2026-09-15). |
| `pytest.ini`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml` | Tooling: discovery pattern, CI, pre-commit hooks. |
| `STABLE.md`, `KNOWN_ISSUES.md`, `CHANGELOG.md`, `README.md` | Governance + docs (README now in English). |
| `run_forecast.sh` | Reference run script (forecast engine). |
| `forecast_engine.py`, `forecast_run/deploy.py`, `research_build_predictor.py` | Driver-era deployment archive (still referenced). |

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

### 3.1 Routers (13)

| Router | Endpoint(s) |
|---|---|
| `pairs.py` | `GET /v1/fx/pairs/` (9 pairs — FX_PAIRS; universe pinned in `useActivePair.ts`) |
| `health.py` | `GET /api/v1/health` |
| `currency_rules.py` | `GET /v1/fx/pairs/{pair}/currency-rule` (CCY-FX_MAPPING/LCY) |
| `forecast_dashboard.py` | `GET /v1/fx/{pair}/forecast-dashboard` |
| `price.py` | `GET /v1/fx/{pair}/price` |
| `forecast.py` | `GET /v1/fx/{pair}/forecast` |
| `scenario.py` | `GET /v1/fx/{pair}/scenario` |
| `scenario_group.py` | `GET /v1/fx/{pair}/scenario-group` |
| `model_comparison.py` | `GET /v1/fx/{pair}/model-comparison` |
| `directional_bias.py` | `GET /v1/fx/{pair}/directional-bias` |
| `intelligence.py` | `GET /v1/fx/{pair}/intelligence` (rewritten in English) |
| `status.py` | `GET /v1/fx/{pair}/status` + `GET /status-regions` (KI-007) |
| `divergence.py` | `GET /v1/fx/{pair}/regime-divergence` (NEW 2026-09-15) |

### 3.2 Supporting modules

* `main.py` — app factory, CORS, registry wiring, 13 `include_router` calls.
* `adapters/registry.py` → `adapters/registry_router.py` — direct registry read; **engine-sub-path**
  exposure (not by contract). Exposes `ensemble.name`, cache dir, `EXPERIMENTS` set (TOXIC), engine engine path.
* `adapters/currency_rule_adapter.py` — CCY-FX_MAPPING/LCY rule behind `fxpair`.
* `adapters/decision_engine_adapter.py` — KI-002 step 3: `as_of` decision-engine params, capability
  registry (as_of aware, for `forecast`, `direct_bias`, `scenario`), `DataQualityRegistry` wrapper.
* `adapters/temporal.py` — `TemporalProvenance` (KI-002 step 1), pulled from `data_provider.last_date`.
* `schemas/*` — live commission.

## 4. Layer 2 — live engine (`backend/layer2/`)

### 4.1 Data flow

For each FX pair: data pull → **UIW water year (fixture 2025: 2023-07-01)** → manually-populated
per-PIR/forecast/target-type/interpolation TL → Reconcilier result: dataframe with columns
(both_years_tl = UIW horizon TL + prev water year on UIW horizon) → reconciled → any value ≥ 30
triggers `post_process` (binary 0/1, forecast prefix) → horizon model → canonical + TargetType
orchestration → signed result (forecast `bids`) → engine → `/engine/spread` for spread endpoint.
`last_date` → `Timestamp` (downsample 1/2H freq), passed via PIT as `data_provider.last_date`.

### 4.2 Module responsibilities

| File | Responsibility |
|---|---|
| `engine.py` | Core inclusion/TC modifier → final forecast. |
| `data_provider.py` | Data pull. |
| `horizon.py` | Horizon model. |
| `models_registry.py` | Model registry read + multiple-weights check. |
| `gap_fill.py` | Gap fill. |
| `logging_config.py` | Logging. |
| `spread_engine.py` | Spread engine (`/engine/spread`) — NEW (KO-005); 17 test IDs. |

### 4.3 Models & registry

On startup, adapter opens the registry only; **base path points to `REGISTRY.FX_MODEL_ROOT`,
not `app_models`**. If path points under the registry root and exists: maps `FX_MODEL_ROOT` +
`EXPERIMENTS` set (TOXIC). Multiple weights per strategy rejected (raises ValueError). Registry
path is `(registry/engine/fx/bundle)`; `models/` dir is **BLANK** (files loaded only if present).

## 5. Layer 3 — research layer (`backend/layer3/`)

* `ai_service.py`, `request_models.py` (schemas), `response_models.py`, imports
  `nemra_horizon_tuning` (research enum shared with layer2), `research_horizon.py` (research-specific tuning constructor).
* Not referenced by layer2/backend rules; only standalone research scripts use it.
* `run_benchmarks.py` — **broken** (`get_driver` absent).

### 5.1 Research Gate pipeline (repo root, unchanged)

`gate.py` → loads whole stack; reads configured dataset high/low/buffer via num_str parsing; walks
the data dir once accumulating keys; computes Max Output Gap across all values; asserts expected
ratios; generates a single-record `whole.universe.json` (used by `/api/status-stack`); also emits
`compliance` + `InputHigh`.

### 5.2 Canonical-model research, walkforward & shadow testing (repo root)

`research_build_predictor.py` → `forecast_run/deploy.py` staged walkforward (Layer3 imports gate,
Layer4 imports gate, `pytests` import gate contracts). `stage` unsupported on this host → `run_forecast.sh`
uses `--model-baseline` (shift receiver) + pass-through of remaining layers; persists to `models/`.

## 6. Layer 4 — data-quality layer (backend/layer4/)

* `backend/layer4/tests/` — PIT suite; **CI backend job collects 0 tests** (pit_tests.py matches
  no discovery pattern in `pytest.ini`), only layer1 tests run in CI.
* Gate (root, not Layer4): `contracts.py data_quality` vs `layer3` contract roots: engine and
  gate-generated `universe.json` share a common dataset root (repo `/dataset`).

## 7. Backend — contract-governed Decision Engine (`src/meridian_fx/decision/`)

Contract-first pipeline; entry `decision_engine.py`; backed by tests 1–6 (180 passing, 20 files).

```
DecisionEngine
 ├─ step 1 (KI-002) TemporalProvenance._arg_filter          ── as_of from L4 data_provider.last_date
 ├─ step 2 (KI-002) context loading (registry)              ── DataQualityRegistry (capability)
 ├─ step 3 (KI-006) capability checks                       ── int init(build) called as TS? error re init signature
 ├─ step 4           conditions (+ args) store
 └─ shipped: one topline model; decision list; data inputs; verdict as binary list (total 4-bits)
```

Runtime semantics: **all contracts are runtime-free** — no outputs computed at decision time.

### 7.1 KI-009 — exchange-regime gate

New contract-backed gate (`contracts/exchange_regime.py`) classifying pair regimes
(FREE_FLOAT / MANAGED_FLOAT / UNKNOWN) from knowledge base + macro weights:

| Pair | Regime | Verdict |
|---|---|---|
| USD/EUR | FREE_FLOAT | OPEN |
| USD/GBP | FREE_FLOAT | OPEN |
| USD/AUD | FREE_FLOAT | OPEN |
| USD/NZD | FREE_FLOAT | OPEN |
| USD/JPY | FREE_FLOAT | OPEN |
| USD/CAD | FREE_FLOAT | OPEN |
| USD/CHF | FREE_FLOAT | OPEN |
| USD/CNY | MANAGED_FLOAT | RESTRICTED |
| USD/BOB | UNKNOWN | RESTRICTED |
| USD/ARS | UNKNOWN | RESTRICTED |

RESTRICTED verdict (adder): fixture generator + `pytests` plan an **unused** RESTRICTED path. The
regime **never changes the requirement to run the engine** (RiskEngine still computed for RESTRICTED
decisions — Opción B); body resiliently handles empty `data` via `or []` no-op chain.

### 7.2 Regime-divergence module

`backend/src/meridian_fx/decision/divergence/` (NEW 2026-09-15):

| File | Role |
|---|---|
| `arima.py` | ARIMA approach (1,0,1) — scipy-only, no pandas/sklearn |
| `metrics.py` | Distribution by sign/regime + montecarlo (nonparametric) |
| `report.py` | Evidence → decision document |

Description in `docs/divergence/README.md`. Evidence examples: USD/CHF +0.55 (NORMAL, observational),
USD/BOB −2.43 (NORMAL, extreme, RESTRICTED). `report.RESOLUTION_THRESHOLD` = cpstat 95% quantile
across 10k draws. Endpoint: `GET /v1/fx/{pair}/regime-divergence` → report (open, response headers
`X-Report-Type`, RT result, sets). Frontend: `useRegimeDivergence.ts`, `DivergencePanel.tsx`,
`RegimeWarningBanner.tsx` (reads `engine.regime`), chart projection.

## 8. Frontend — contract-driven dashboard (`frontend/`)

### 8.1 Routes (6 canonical pages, 11 hook modules)

`/PairDashboard`, `/ForecastDashboard`, `/PricingConditions`, `/Scenarios`, `/ModelComparison`,
`/Intelligence`. Hooks in `src/hooks/` (now 11 incl. `useRegimeDivergence`): `useActivePair,
useCurrencyRule, useBiases, useEngine, useForecast, useThreatAssessment, usePricingInventory,
useMarketConditions, useDashboardView, useScenarioData, useRegimeDivergence`. Universe pinned to
9 pairs (FX_PAIRS) in `useActivePair.ts`.

### 8.2 Presentational components

`src/components/` — largely pure display; **`shared/` imports base CSS; `components/global/` hosts**
`Chart`, `Pair`, `PriceBar`, `ModelInfo`, `ScenarioSummary`, `Section/`, `RangeIndicator/`,
`DivergencePanel`, `RegimeWarningBanner`. `src/shared/` — engine + active-pair provisioning.

### 8.3 Transport & contracts

`src/api/` — `auth.ts` wedged into `api/Transport`, session via `Transport` singleton,
`Bearer cookie` from `/api/v1/auth/login` (static admin). CSS: base layer, border-wrapper cross-mark
hack, elevated range styling. Old `requestApi` remnants archived.

### 8.4 Layering rules

Frontend is **request/response** (no store). Components import hooks only in `container` wrappers;
leaf components never import hooks. `type` imports strict (must be `import type`).

## 9. Deployment & runtime

* `Dockerfile` — Node 20-alpine `dist` build (pinned build deps), `uv` pip install `--system`, non-root user, `WORKDIR /usr/app`, copies `backend/layer1/`, `models/`, `contracts.py`, `gate.py`, `whole.universe.json`, `external_data/` (ENV-meridian optional), entrypoint `uvicorn main:app`, `CMD ["0.0.0.0", "8080"]`; **copies `models/`** (gap closed).
* `docker-compose.yml` — 2 compat keys (`EXTERNAL_DATA`, `MERIDIAN_MODEL_DIR`) + 5 build args (`API_HOST`, `API_PORT`, `EXTERNAL_DATA`, `DATA_DIR`, `MODEL_DIR`); **no secrets.**
* `run_forecast.sh` — `uvicorn`-style run on host ports; `pytests` referenced as RESTRICTED runtime-only.
* CI (`.github/workflows/ci.yml`) — backend job: `pytest backend/layer1/tests/` + `pytestbackend/layer4/tests/`
  (0 collected — pit_tests.py matches no pattern); frontend job: install/branch plan no tests, `npm build`. Pre-commit via `.pre-commit-config.yaml`.

## 10. Documentation & governance layer

Maps (`dict`, matrix PYPI, `prompts/`), README (English), `CHANGELOG.md`, `STABLE.md`, `KNOWN_ISSUES.md`
(2026-09-15 version), `docs/divergence/README.md`. Release cycle: `git tag -a v2.7.5 -m ...` after CI
green; tags: v2.7, v2.7.1–v2.7.5.

## 11. Verification matrix

| Area | Result |
|---|---|
| Backend tests (`pytest`) | 180 passed / 20 files — engine (1–6), decision (1–6), risk (11), TS (5.1-5.2), spread (17) |
| Frontend vitest | 56 passed / 7 files |
| `npm run build` | PASS — 1,495 kB (304 kB gzip) |
| `npx tsc --noEmit -p .` | PASS |
| CI backend | 148 passed but **collects 0 pit_tests** (discovery pattern gap) |
| Manual | `curl http://localhost:8080/v1/fx/USD/CNY/forecast-dashboard 200 OK` (2026-09-15) |

## 12. Known gaps & risks (2026-09-15)

1. **Uncommitted Spanish→English translation pass** on frontend/README (observed in working tree — not committed).
2. **CI backend collects 0 tests** — `pit_tests.py` matches no discovery pattern (falls back to layer1).
3. `models/` still **BLANK** file on disk; registry is the source.
4. `external_data/` muted (missing `eci.ipynb`), `pytests/` RESTRICTED runtime-only.
5. `STABLE.md`: 13/26 managed-floats correspond to fixture regime RESTRICTED (2026-09-15).
6. `run_benchmarks.py` **broken** (`get_driver` absent).
7. Layer1 keeps **own copies of prior gates** → docs/architecture drift; 2026-09-14 NOTE: feature-only changes.
8. **Bundle size** — 1,495 kB JS chunk (304 kB gzip), `minify: false`, warning silenced by `chunkSizeWarningLimit`.
9. **`MERIDIAN_MODEL_DIR`** set in compose but unconsumed by engine code.
10. **Unresolved engine-version constraints** — KI-005/006 ERA passes; models may still drift.
11. **Layer 1 dead subsystems** — `decision/` (own `DecisionEngine`), `data/forecast_data.py`, drivers-era adapter remnants (`get_drivers`, `to_drivers_response`), `routers/__init__` subtle import side-effect.
12. **Live-model caveats** — `/model-comparison` slow (3y walk-forward per pair); `/price`/`/forecast-dashboard` signals depend on model resolution + network (macros empty on failure).
13. **IOR gap** — decorators missing around xxl_merge/engine; skip-restored pit_failures.sql-constraint; no regression guard on IOR.