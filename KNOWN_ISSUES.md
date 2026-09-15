# MeridianFX — Known Issues Registry

This document is the authoritative record of known issues, tracked
technical debt, and deliberate design trade-offs. It is intended to be
read alongside `STABLE.md` (which tracks releases) and
`README.md §Current Limitations` (which tracks user-facing limits).

Issue statuses:

- **open** — known, not yet addressed.
- **mitigated** — a workaround exists but the underlying issue remains.
- **partially resolved** — some components fixed, some still open.
- **resolved** — fully addressed, with a reference to the resolving
  commit or version.
- **registered** — acknowledged, awaiting decision or scope.
- **documented as incomplete** — the code exists in the tree, is
  explicitly marked INCOMPLETE in its own docstrings, and its current
  limitations are captured here. It is not broken (it fails safely);
  it is not functional either. Tracked so no caller assumes it works.

Issue IDs are stable and never renumbered.

---

## KI-001 — `decision_result` is not fully PIT-deterministic without a cache

**Status:** mitigated
**Detected:** 2026-09-14
**Component:** `backend/layer2/pipeline_bridge.py`
**Mitigation:** per-minute in-memory decision cache in `PipelineBridge`

### Symptom

Two `GET /v1/canonical/{pair}/decision` calls within the same second
could return different `net_return` values if the underlying market
data moved between the two internal fetches. This caused the narrative
cache to miss even for logically identical decisions.

### Root cause

`PipelineBridge.evaluate_pair()` performed two independent Yahoo fetches
per request — one inside `DecisionEngineAdapter.get_prediction_artifact()`
(for the forecast), and one inside the bridge itself (for features and
the economic layer). Between the two fetches, the last price could move
by a few bps. Because `edge_ratio` and `net_return` participated in
`compute_narrative_key()`, the fingerprint changed.

### Mitigation

An in-memory cache keyed by `(pair, horizon_days, minute_bucket)` with
a 1-minute TTL ensures that within the same minute, all consumers
(`/decision`, `/risk`, `/narrative`) see the same `decision_result`.

### Residual

- `force_refresh=True` still produces different results across calls.
  The cache masks the underlying non-determinism; it does not fix it.
- The full fix requires a single data fetch per request (see KI-003)
  and an `as_of` anchored at the request boundary (see KI-002).

---

## KI-002 — `PredictionArtifact` temporal provenance is not verified

**Status:** partially resolved
**Detected:** 2026-09-14
**Components:**
- `backend/layer2/data/provider.py`
- `backend/layer2/engine.py`
- `backend/layer1/adapters/decision_engine_adapter.py`
- `backend/src/meridian_fx/decision/quality/real_providers.py`
- `backend/layer2/pipeline_bridge.py`

### Contract

Two specs define the temporal contract:

- **Layer 3 §11.2:** `as_of: datetime  // knowledge point for this prediction`.
- **Layer 4 §3:** seven PIT invariants, including:
    - PIT-1: `available_time <= T`
    - PIT-2: `derived.available_time = max(inputs.available_time)`
    - PIT-7: `event_time <= release_time <= source_available_time <= system_available_time`

The contract distinguishes five temporal concepts that MUST NOT collapse
into a single `datetime.now()`:

    event_time             — when the economic fact occurred
    release_time           — when the source published it
    source_available_time  — when the source made it available
    system_available_time  — when MeridianFX ingested it
    as_of                  — knowledge cutoff: max(source_available_time)

### Sub-issue 1 — `Decision.timestamp` consistency (RESOLVED v2.7.5)

Before v2.7.5, `DecisionPipeline` called `utcnow()` independently in
each decision branch. Fixed in v2.7.5 (`f45b097`). Two regression tests
in `backend/tests/test_pipeline.py` cover the semantics.

### Sub-issue 2 — Market data temporal propagation (OPEN — KI-002-A)

The chain is:

    DataProvider.get_historical()
        ├── result['last_date']          ← ★ data cutoff exists here
        └── result['timestamp']          ← datetime.now() (retrieval time)
                    ↓
    DecisionEngine.get_forecast()
        ├── df = result['data']          ← OK
        └── response['data_provider'] = {
                'source': ..., 'freshness': ..., 'last_price': ...,
                # ← FALTA 'last_date'
            }
                    ↓
    DecisionEngineAdapter.get_prediction_artifact()
        └── timestamp = datetime.now(timezone.utc)
            as_of=timestamp, prediction_timestamp=timestamp,
            created_at=timestamp
                    ↓
    PredictionArtifact
        as_of = wall-clock, NOT data cutoff

**Evidence:**
- `backend/layer2/data/provider.py` — `get_historical()` returns
  `result['last_date'] = df.index[-1]` (data cutoff) alongside
  `result['timestamp'] = datetime.now(timezone.utc)` (retrieval time).
- `backend/layer2/engine.py` — `get_forecast()` extracts `df = result['data']`
  but omits `result['last_date']` from the response payload.
- `backend/layer1/adapters/decision_engine_adapter.py` — the adapter reads
  `forecast` but has no data cutoff available, so it sets
  `as_of = datetime.now(timezone.utc)`.

**Impact:**
- `PredictionArtifact.as_of` does not currently satisfy the intended
  Layer 3 semantic contract ("knowledge point for this prediction").
  The type is correct (`datetime`), but the value is wall-clock time
  rather than a data-derived knowledge cutoff.
- `as_of == prediction_timestamp == created_at` (all three collapse).
- Downstream PIT validation operates on the wall-clock cutoff.

**Fix proposed:**
1. `engine.get_forecast()`: add `'last_date': result['last_date']` to the
   `data_provider` block of the response.
2. `adapter.get_prediction_artifact()`: consume the temporal provenance
   propagated by the engine and derive `as_of` from the validated
   knowledge cutoff; it MUST NOT synthesize it with `datetime.now()`.
   If the required temporal provenance is absent, fail explicitly —
   do not fall back to wall-clock time.

   Note: `last_date` alone is not sufficient. It is an observation
   timestamp, not necessarily `source_available_time`. For continuously
   published market data the two may coincide, but they are conceptually
   distinct. See KI-002-D.
3. Consider whether `last_date` alone is sufficient, or whether
   `event_time` / `release_time` / `source_available_time` need to be
   distinguished (see KI-002-D below).

### Sub-issue 3 — Layer 4 availability semantics (OPEN — KI-002-B)

`RealFeatureStore` (VIX) fetches a real Yahoo observation but assigns:

    FeatureValue(
        feature_id="vix",
        value=vix,                      # real
        available_time=as_of,            # ← inherited from caller, not observed
    )

The source observation's actual timestamp (`hist.index[-1]` from the
Yahoo fetch) is not captured or propagated.

**Impact:**
- `FeatureValue.available_time` is synthetic, not observed.
- PIT-1 validation (`available_time <= prediction_timestamp`) checks the
  synthetic cutoff against itself, which is vacuously true.
- PIT-7 (`event_time <= release_time <= source_available_time <=
  system_available_time`) cannot be evaluated — only one timestamp exists.

**Fix proposed:**
1. In `RealFeatureStore._fetch_vix()`, capture `hist.index[-1]` (the
   observation timestamp) alongside the value.
2. Use that timestamp as `source_available_time` in the constructed
   `FeatureValue`. Distinguish `source_available_time` from
   `system_available_time` (when MeridianFX ingested it).
3. This requires extending `FeatureValue` — or introducing a companion
   type — to carry the full temporal metadata chain. Design decision
   pending; see KI-002-D.

### Sub-issue 4 — PIT-2 vacuously satisfied (OPEN — KI-002-C)

`PipelineBridge.build_inputs()` populates:

    derived_available_time=as_of,
    input_available_times=[as_of],

With a single-element list, PIT-2 (`derived.available_time =
max(inputs.available_time)`) reduces to `as_of == as_of`, which is
trivially true regardless of the actual input timestamps.

**Impact:**
- The `PITValidator` reports a passing report, but the pass does not
  establish absence of look-ahead bias.
- The validator is correct; the inputs it receives are the problem.

**Fix proposed:**
- Populate `input_available_times` with the real per-input timestamps
  (from each `FeatureValue.available_time`, from the market data cutoff,
  from the macro context timestamps).
- Requires KI-002-A and KI-002-B to be resolved first.

### Sub-issue 5 — Full temporal contract design (DESIGN — KI-002-D)

**Status:** design (no code change)

This sub-issue defines the target temporal contract for the pipeline.
It is documented here before any code change, so that KI-002-A/B/C can
be implemented against a settled design rather than against the current
ad-hoc timestamps.

#### The five temporal concepts

| Concept | Meaning | Source |
| --- | --- | --- |
| `event_time` | When the economic fact occurred. | Layer 4 provider (e.g. FRED `observation_date`, market candle timestamp). |
| `release_time` | When the source published the fact. | Layer 4 provider (only when the provider exposes it). |
| `source_available_time` | When the source made the value available for query. | Layer 4 provider (often equals `release_time`). |
| `system_available_time` | When MeridianFX ingested the value. | `DataProvider` (wall-clock at ingestion). |
| `as_of` | Knowledge cutoff for a prediction: the maximum `source_available_time` across all inputs used. | Derived by the pipeline. |

**Invariant (Layer 4 §3, PIT-7):**
event_time <= release_time <= source_available_time <= system_available_time

#### Target type: `TemporalProvenance`

Location (proposed): `backend/src/meridian_fx/decision/contracts/temporal.py`.

class TemporalConfidence(str, Enum):
    VERIFIED = "verified"
    APPROXIMATED = "approximated"
    UNAVAILABLE = "unavailable"

class TemporalProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_time: datetime
    release_time: datetime | None = None
    source_available_time: datetime
    system_available_time: datetime

    event_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED
    release_time_confidence: TemporalConfidence = TemporalConfidence.UNAVAILABLE
    source_available_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED
    system_available_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED

**Notes on defaults:**

- `release_time_confidence` defaults to `UNAVAILABLE` because no current
  provider exposes a verified release timestamp.
- `event_time_confidence`, `source_available_time_confidence`, and
  `system_available_time_confidence` default to `VERIFIED`.
- Callers that know a value is approximate MUST set the corresponding
  confidence to `APPROXIMATED` explicitly.

#### Integration into existing types

**`FeatureValue`** (Layer 4 contract):

class FeatureValue(BaseModel):
    feature_id: str
    value: float | None
    provenance: TemporalProvenance

    @property
    def available_time(self) -> datetime:
        return self.provenance.source_available_time

**`PredictionArtifact`** (Layer 3 contract):

- `as_of` preserved, but its value MUST be derived from
  max(input.provenance.source_available_time for all inputs).
- `prediction_timestamp` remains wall-clock at prediction time.
- `created_at` remains wall-clock at artifact creation.

**`PipelineInputs`** (Layer 2 pipeline):

- `input_available_times` MUST be populated with the real per-input
  `source_available_time`, not `[as_of]`.
- `derived_available_time` becomes max(input_available_times) (PIT-2).

#### Provider capability matrix (current state)

| Provider | event_time | release_time | source_available_time | system_available_time |
| --- | --- | --- | --- | --- |
| Yahoo FX | VERIFIED | APPROXIMATED | APPROXIMATED | VERIFIED |
| Alpha Vantage | VERIFIED | APPROXIMATED | APPROXIMATED | VERIFIED |
| Twelve Data | VERIFIED | APPROXIMATED | APPROXIMATED | VERIFIED |
| FRED | VERIFIED | UNAVAILABLE | APPROXIMATED | VERIFIED |
| VIX (Yahoo) | VERIFIED | APPROXIMATED | APPROXIMATED | VERIFIED |

#### Timezone handling — implementation risk

`YahooSource.fetch()` converts the DataFrame index to timezone-naive.
Any code that converts a naive timestamp back to UTC MUST interpret it
as the original instant, not as local wall-clock time. Flagged as a risk
to resolve during KI-002-A, not during design.

#### `as_of` computation

as_of = max(
    input.provenance.source_available_time
    for input in inputs
    if input.provenance.source_available_time_confidence
       in (TemporalConfidence.VERIFIED, TemporalConfidence.APPROXIMATED)
)

**Rules:**

1. Computation performed once, at the point with access to all inputs.
2. `datetime.now()` MUST NOT substitute for `as_of`.
3. If no input provides `source_available_time`, fail explicitly.
4. If any input is `APPROXIMATED`, the aggregate inherits the flag.

#### PIT validation semantics

A passing PIT report is only meaningful when inputs carry verified
`source_available_time`. When inputs are approximated, the report MUST
include a flag or warning indicating PIT correctness is not fully
demonstrated.

#### Planned tests

- T-D-1: PIT-7 enforced when all four timestamps present.
- T-D-2: release_time=None accepted with reduced ordering.
- T-D-3: naive timestamps rejected (PIT-5).
- T-D-4: FeatureValue.available_time returns provenance.source_available_time.
- T-D-5: market provider has release/source APPROXIMATED.
- T-D-6: FRED has release UNAVAILABLE, source APPROXIMATED.
- T-D-7: as_of computed as max of input source_available_time.

#### Scope

**Design-only.** No code change until KI-002-A/B/C implemented against
this contract.

Not in scope: modifying providers/adapters/engine/pipeline code; adding
`TemporalConfidence` to codebase; changing tests; migrating
`PredictionArtifact`.

#### Decisions closed

| # | Decision |
| --- | --- |
| 1 | TemporalProvenance is a shared type. |
| 2 | FeatureValue.available_time becomes a derived alias. |
| 3 | FRED source_available_time is APPROXIMATED. |
| 4 | as_of = max(input.source_available_time), PIT-2. |
| 5 | Per-timestamp confidence enum. |
| 6 | release_time_confidence defaults to UNAVAILABLE. |
| 7 | Market timestamps are approximations. |
| 8 | tz-naive → UTC is an implementation risk. |
| 9 | datetime.now() MUST NOT substitute for as_of. |
| 10 | Approximated inputs do not prove historical PIT correctness. |

### Test coverage

`backend/tests/test_pit_audit.py` contains **two** diagnostic tests
that capture the current structural behavior:

- `test_ki_002_a_as_of_collapses_with_prediction_timestamp` — documents
  that `as_of`, `prediction_timestamp` and `created_at` all collapse to
  the same wall-clock value in the adapter pattern.
- `test_ki_002_c_input_available_times_makes_pit2_vacuous` — documents
  that `PipelineBridge` passes `input_available_times=[as_of]`, which
  reduces PIT-2 to a trivial identity.

These tests are **intentionally not evidence of end-to-end PIT
correctness**. They document the current failure modes and MUST be
updated or removed when the corresponding fixes land. Their purpose is
to force a conscious decision at fix time: a broken assertion is a
prompt, not a regression.

The jump from 148 → 150 tests in the suite is explained by these two
new diagnostic tests.

### Status summary

| Sub-issue | Status |
| --- | --- |
| KI-002 sub-1 (`Decision.timestamp`) | RESOLVED v2.7.5 (`f45b097`) |
| KI-002-A (market temporal propagation) | OPEN |
| KI-002-B (Layer 4 availability) | OPEN |
| KI-002-C (PIT-2 vacuous) | OPEN |
| KI-002-D (full contract design) | OPEN (design-only) |

## KI-003 — Double Yahoo fetch per request

**Status:** open
**Detected:** 2026-09-14
**Component:** `backend/layer2/pipeline_bridge.py`,
`backend/layer1/adapters/decision_engine_adapter.py`

### Description

A single request to `/v1/canonical/{pair}/decision` performs two
independent Yahoo fetches: one inside the adapter (for the forecast)
and one inside the bridge (for features and the economic layer). This
is the technical root cause of KI-001.

### Impact

- Duplicated network overhead.
- Risk of inconsistency between the forecast and the economic layer.
- Source of non-determinism, masked by the KI-001 cache but not
  eliminated.

### Fix proposed

Refactor `DecisionEngineAdapter.get_prediction_artifact()` to accept
`data` (the already-fetched snapshot) instead of fetching on its own.
The bridge performs a single fetch at the start of the request and
reuses it.

This is a scoped but invasive change: it modifies the adapter
interface. It should be done alongside the KI-002 sub-issue 2 audit,
since both touch the same code path.

---

## KI-004 — `MacroService` has no per-request cache

**Status:** open
**Detected:** 2026-09-14
**Component:** `backend/layer2/data/macro/service.py`

### Description

`MacroService.get_macro_context()` and `get_country_context()` are
called on every request without caching. If FRED returns transient
errors (e.g. HTTP 502), the macro context can differ between two
consecutive requests, changing `macro_status` and therefore
`narrative_key`.

### Impact

- Additional fingerprint instability (mitigated by KI-001, not
  resolved).
- During FRED outages, the system can oscillate between incompatible
  narratives without clear operator visibility.

### Fix proposed

Add a macro context cache with a longer TTL (e.g. 15 minutes) and a
stale-while-revalidate strategy. Macro regime changes slowly; it does
not need to be fetched on every request.

---

## KI-005 — Dead `_unavailable_decision()` path in `DecisionPipeline`

**Status:** resolved in v2.7.4 (`e7312a3`)
**Detected:** 2026-09-14
**Component:** `backend/src/meridian_fx/decision/pipeline.py`

### Description

`DecisionPipeline._unavailable_decision()` was the artifact of a
pre-v2.7 blocking contract: it returned `signal_validity=UNAVAILABLE`
when `macro_score` was `None`. After v2.7 (commit `c31f65b`), the
contract became "degrade, do not block":

- `build()` sets `macro=0.0` when `required_data_missing=True`
  (never `None`).
- `gates/engine.py` emits the warning
  `"required data missing (macro incomplete)"`.
- `signal_validity` stays `DEGRADED` (not `UNAVAILABLE`).
- The pipeline always produces a `Decision`.

The method was unreachable: `raw_macro_score()` returns `float`
(never `None`), and no code path called it.

### Resolution

- v2.7.3 (`609e3ad`) attempted the removal via an automated script.
  The script failed silently; only the test was committed.
- v2.7.4 (`e7312a3`) performed the actual removal, verified by
  `grep -c '_unavailable_decision' pipeline.py` returning 0.
- **Process change:** refactor scripts now verify post-conditions and
  abort on failure instead of continuing to commit.

### Residual

The gap that allowed the original method to exist — documenting an
intended behavior without verifying the code implements it — is a
recurring pattern. Any future documented invariant should have a
matching test.

---

## KI-006 — Bare `except:` clauses in defensive code paths

**Status:** resolved (pending commit)
**Detected:** 2026-09-14
**Component:**
- `backend/layer2/status/engine.py:60`
- `backend/layer2/status/engine.py:350`
- `backend/layer2/models/registry.py:42`
- `backend/layer3/models/arima.py:38`
- `backend/layer3/models/arima.py:58`

### Description

Five `except:` clauses without an exception type. These are not
`KeyboardInterrupt`-fatal in practice (all are inside defensive
fallbacks), but they do capture control-flow exceptions like
`KeyboardInterrupt` and `SystemExit`, which should propagate.

### Impact

- Ctrl+C during a defensive fallback can be silently swallowed.
- Linters and static analyzers flag them.
- The intent (what error was expected) is not documented.

### Fix proposed

Replace each with an explicit exception type, matching the actual
expected failure mode:

- `registry.py:42` → `except (json.JSONDecodeError, OSError):`
- `status/engine.py:60` → `except ValueError:`
- `status/engine.py:350` → `except Exception:` (psutil may raise its
  own subclasses; memory probing is best-effort)
- `arima.py:38` → `except Exception:` (intentional: ADF is diagnostic;
  default `d=0` is the correct fallback for log-returns)
- `arima.py:58` → `except Exception:` (intentional: grid search over
  (p, q) must skip combinations that fail to converge)

For the three `except Exception:` cases, add a comment marking the
catch as deliberate.

---

## KI-007 — `/status` reports `database="NOT_CONFIGURED"` hardcoded

**Status:** resolved (see commit)
**Detected:** 2026-09-14
**Component:** `backend/layer1/routers/status.py:73`

### Description

The `/v1/status` endpoint returns:

    database="NOT_CONFIGURED",  # TODO: conectar a DB real

This is a placeholder from a period when a real database was planned.
The current system uses SQLite for narrative persistence
(`backend/cache/narratives.db`) and has no traditional database for
the decision path.

### Impact

- The `/status` response reports a state that is not verified at
  runtime.
- A future operator may believe there is a database that needs
  configuring.

### Fix proposed — two options

**Option A (recommended):** rename the field or its value to reflect
the actual state, e.g.:

    database="SQLITE_LOCAL",
    # narrative store only — no decision-path database

**Option B:** if a real database is planned (e.g. Neon for v3.0
backtesting), keep the field but mark it as
`"NOT_CONFIGURED_PLANNED"` and link to the roadmap.

This is a **contract decision**, not hygiene. Do not change without
deciding first.

---

## KI-008 — Incomplete macro providers (CNBS, ECB official)

**Status:** documented as incomplete
**Detected:** 2026-09-14
**Component:**
- `backend/layer2/data/macro/providers/cnbs.py:97`
- `backend/layer2/data/macro/providers/ecb_official.py:29,50`

### Description

Two macro providers are scaffolded but not implemented:

- `cnbs.py` — parsing of the NBS (China) structure is not implemented.
- `ecb_official.py` — the ECB API integration is not implemented.

These providers are present in the codebase but do not produce
production data.

### Impact

- Risk of confusion: a provider exists in the tree but is not
  functional.
- If a caller assumes these providers work, they may get no data
  silently.

### Fix proposed — three options

**Option A:** delete the incomplete files.
**Option B:** keep them but mark explicitly in the class docstring:

    # INCOMPLETE — do not use in production. See KI-008.

**Option C:** complete one or both.

**Recommended:** Option B for now, with Option C considered in v3.0
alongside the PIT audit of macro data.

---

## A3 — `policy_diff` PIT audit

**Status:** open
**Detected:** 2026-09-14
**Component:** `backend/layer2/data/macro/service.py` (and callers)

### Description

`policy_diff` is a macro feature used by the canonical model. Its
temporal provenance has not been audited end-to-end:

    source → effective date → temporal alignment → PIT validation
      → normalization → feature → model → decision layer

### Question to answer

Can any information used by a decision have been published after the
`as_of` of that decision?

### Fix proposed

Full PIT audit of the `policy_diff` chain. Track as part of the v3.0
PIT audit.

---

## A4 — Async / event-loop audit

**Status:** open
**Detected:** 2026-09-14
**Component:** various

### Description

Calls such as `asyncio.new_event_loop()`, `run_until_complete()`, and
`asyncio.run()` exist in parts of the backend. It is not known whether
they behave correctly under the real production model
(FastAPI + ASGI + workers + concurrent requests).

### Fix proposed

Audit each call site under realistic concurrency. Do not modify
without evidence of an actual problem.

---

## P1 — `forecast-dashboard` model version mismatch

**Status:** registered
**Detected:** 2026-09-14
**Component:** `backend/layer1/routers/forecast_dashboard.py`

### Description

The forecast dashboard returns:

    "model": {
        "type": "logistic",
        "version": "v1.0",
    }

while the actual model running is `Logistic_24`. The metadata does not
match the model.

### Impact

- Misleading metadata for API consumers.
- Part of a broader legacy/canonical naming split.

### Fix proposed

Decide the correct `model.version` field semantics. Likely tied to the
broader legacy/canonical unification (item B below).

---

## B — Legacy ranking (1 pair) vs canonical pipeline (9 pairs) divergence

**Status:** deferred to v3.0
**Detected:** 2026-09-14
**Component:** `backend/layer2/ranking/engine.py`,
`backend/layer1/routers/ranking.py`,
`frontend/src/hooks/useActivePair.ts`

### Description

After the registry promotion gate (v2.7), the legacy `/v1/fx/ranking`
endpoint iterates only over registry-active models. Only USD/CHF
remains active, so the ranking returns a single pair. The canonical
pipeline still serves all 9 pairs.

Two problems result:

1. The frontend ranking surface shows 1 pair.
2. The Global page's "monitored universe" message contradicts the
   Decision page, which works for all 9 pairs.

As of v2.7.2, the frontend universe is pinned to `FX_PAIRS` (9 pairs)
to work around the collapse, but the backend `/v1/fx/ranking` itself
still returns 1 pair.

### Fix proposed

Migrate the ranking engine to consume the canonical pipeline. This is
a redesign, not a refactor: it changes what "opportunity score" means
and how many pipeline invocations happen per ranking refresh.

Track as v3.0 work.

---

## Stub L4 quality registries

**Status:** placeholder
**Detected:** 2026-09-14
**Component:** `backend/layer1/routers/canonical.py`

### Description

The canonical pipeline is initialized with three placeholder
registries:

    StubDataQualityRegistry(0.90)
    StubFreshnessRegistry(3.0)
    StubDriftRegistry(0.05)

These return fixed values. They are named `Stub*` (renamed from
`Fake*` in v2.7 for honesty) and are visible in the UI with a
`⚠ STUB` badge.

### Impact

- Quality gating is not real.
- The UI shows `Data Quality: good` from a stub, with the numeric
  score explicitly marked `⚠ STUB SCORE`.

### Fix proposed

Replace with real implementations backed by `PITValidator`. Track as
v3.0 work alongside the PIT audit.

---

## Conventions

- IDs are stable. Never renumber.
- A KI moves to **resolved** only when the fix is implemented and
  verified by a test or by an explicit post-condition check.
- A KI is **mitigated** when a workaround exists but the underlying
  issue remains.
- A KI is **partially resolved** when some components are fixed and
  others remain open. Document which is which.
- A KI is **registered** when the issue is acknowledged but no fix
  plan has been decided yet.
- Closed KIs are not deleted; they are marked resolved with a
  reference to the resolving commit or version.

---

## Resolved

- KI-005 — resolved in v2.7.4 (`e7312a3`).
- KI-006 — resolved by the "replace bare except" commit (see log).
- KI-007 — resolved by the "status infra contract" commit (see log).
  The endpoint now emits valid `InfrastructureLevel` values:

      api="healthy", database="degraded", pipeline="healthy",
      cache="healthy"|"degraded"

  `database="degraded"` reflects that no production database is
  configured; narrative persistence uses a local, ephemeral SQLite file.
  Covered by backend/tests/test_status.py (5 contract tests).
