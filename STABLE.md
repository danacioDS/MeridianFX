# MeridianFX — Stable Release Registry

## Current stable: v2.7.2

**Commit:** `d476bd9`
**Date:** 2026-09-14
**Status:** Verified green. Working tree clean. Tags pushed to origin.

| Check | Result |
|---|---|
| Backend tests | 141 passed |
| Frontend tests | 56 passed |
| Frontend typecheck | clean |
| Frontend build | clean (1,436.77 kB / 296.21 kB gzip) |
| CI | GitHub Actions on every push |
| Working tree | clean |
| origin/main | `d476bd9` at stable release checkpoint |

---

## Version history (this engineering cycle)

### v2.7 — `06f9989`
**"Honesty & hardening release"**

- Registry promotion gate (MIN_AUC=0.52, MIN_N_SAMPLES=300).
- 9/10 legacy XGBoost models deactivated; only USD/CHF remains active.
- Horizon semantics aligned from default 30d to 5d across adapters,
  bridge, and routers.
- Fixed `expected_return` fallback bug in `engine.py` — previously every
  forecast silently fell through to the heuristic fallback.
- Persistent LLM narrative layer with deterministic cache identity
  (`(pair, horizon, narrative_key, prompt_version)`).
- Per-minute decision cache in `PipelineBridge` — fixes the narrative
  cache miss caused by the double-fetch bug.
- Frontend `DecisionNarrative` + `DecisionProvenance` blocks.
- 8 invariant tests (economic, narrative identity, cache).
- Honest `Fake*` → `Stub*` and `CentralBankRAGEngine` → `SentimentEngine`
  renames.
- GitHub Actions CI (backend + frontend).
- Root `pytest.ini` so `pytest` works from any CWD.
- README: `## Testing` + `## Current Limitations (v2.7)`.

### v2.7.1 — `29f7a05`
**"Hygiene pass"**

- Removed dead code after early return in `pit_tests.py`.
- Removed orphaned `MarketConvention.tsx` component.
- Silenced known `pandas_ta` DeprecationWarning / UserWarning in
  `pytest.ini`.

### v2.7.2 — `d476bd9` (CURRENT STABLE)
**"UI contract coherence"**

- `ModelDivergenceNotice` rendered once instead of once per horizon
  (30d/60d/90d). Added disclosure that the three horizons use the
  same 5-day `Logistic_24` signal scaled by volatility — not separate
  multi-horizon models.
- `ActionableInfo` aligned with the backend economic contract:
  - `Edge Ratio = Net Return / Required Minimum Edge (bps)`
  - `Actionable ⟺ Edge Ratio ≥ 1.0 AND all hard gates pass`
  - `Required Minimum Edge: 10.00 bps` (previously shown as a ratio `10x`)
- Neutral wording for the missing economic evaluation state; no
  causality inferred from absence of `requiredMinimumEdge`.
- Preserved backend `Data Quality: good` categorical state while
  marking the numeric score as `⚠ STUB SCORE`.

---

## Known debt (documented, not hidden)

| ID | Description | Status |
|---|---|---|
| KI-001 | `decision_result` not PIT-deterministic without cache | mitigated |
| KI-002 | Three `datetime.now()` calls in the decision path | open |
| KI-003 | Double Yahoo fetch per request | open |
| KI-004 | `MacroService` without per-request cache (FRED 502 risk) | open |
| A3 | `policy_diff` PIT audit (source → effective date → alignment → feature → model) | open |
| A4 | Async / event-loop audit under ASGI + workers | open |
| P1 | `forecast-dashboard` reports `model.version="v1.0"` vs actual `Logistic_24` | registered |
| B | Legacy ranking (1 pair) vs canonical (9 pairs) divergence | deferred to v3.0 |
| Stub | L4 quality registries (data_quality, freshness, drift) | placeholder |

See `KNOWN_ISSUES.md` (backend) and `README.md §Current Limitations`
(frontend) for details.

---

## Roadmap

### v2.7.3
Optional backend message correction regarding the promotion-gate state
in `/v1/market-intelligence`.

### v2.7.4
Migrate remaining raw-fetch hooks to the shared `apiClient`
(retry + backoff consistency).

### v2.7.5
Verify `target_price` units in `calculate_forecast`; fix or add
regression coverage as required.

### v3.0 — the real leap

1. PIT audit of `policy_diff`.
2. Historical backtesting of decision quality.
3. Staging deployment (Nginx + Gunicorn).
4. Unify legacy ranking with the canonical pipeline.
5. Async / event-loop audit under production ASGI + workers.
6. Real multi-horizon models (5d / 30d / 90d).
7. Replace placeholder L4 registries with real `PITValidator`-backed
   implementations.

---

*This document is the authoritative pointer to the current stable
release. Update only when a new stable release is formally registered.*
