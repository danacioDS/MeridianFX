# MeridianFX — Stable Release Registry

## Current stable: v2.7.5

**Commit:** `f45b097`
**Date:** 2026-09-15
**Status:** Verified green. Working tree clean. Tags pushed to origin.

| Check | Result |
|---|---|
| Backend tests | 143 passed |
| Frontend tests | 56 passed |
| Frontend typecheck | clean |
| Frontend build | clean (1,436.77 kB / 296.21 kB gzip) |
| CI | GitHub Actions on every push |
| Working tree | clean |
| origin/main | `f45b097` at stable release checkpoint |

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

### v2.7.2 — `d476bd9`
**"UI contract coherence"**

- `ModelDivergenceNotice` rendered once instead of once per horizon
  (30d/60d/90d). Added disclosure that the three horizons use the
  same 5-day `Logistic_24` signal scaled by volatility — not separate
  multi-horizon models.
- `ActionableInfo` aligned with the backend economic contract:
  - `Edge Ratio = Net Return / Required Minimum Edge (bps)`
  - `Actionable ⟺ Edge Ratio ≥ 1.0 AND all hard gates pass`
  - `Required Minimum Edge: 10.00 bps`
- Neutral wording for the missing economic evaluation state.
- Preserved backend `Data Quality: good` categorical state while
  marking the numeric score as `⚠ STUB SCORE`.

### v2.7.3 — `609e3ad`
**"Degrade contract + regression coverage"**

- Added regression coverage for `required_data_missing=True`:
  missing macro data degrades the decision instead of incorrectly
  blocking the pipeline.
- The intended dead-code removal was not applied by the original
  refactor script; this was detected during verification.
- **Process change:** refactor scripts now verify post-conditions and
  abort on failure instead of continuing silently.

### v2.7.4 — `e7312a3`
**"Dead-code removal correction"**

- Actually removed the obsolete `_unavailable_decision()` path.
- Corrected the incomplete v2.7.3 refactor without rewriting history.
- Backend regression suite remained green at 142 tests.

### v2.7.5 — `f45b097` (CURRENT STABLE)
**"Decision timestamp coherence"**

- Captured `Decision.timestamp` once at the start of each
  `DecisionPipeline.build()`.
- Propagated the captured timestamp through normal, out-of-bounds,
  and invalid-edge decision branches.
- Added regression coverage for timestamp semantics and branch behavior.
- Backend suite verified at 143 passing tests.
- `artifact.as_of` provenance remains outside the scope of this fix and
  is part of the future PIT audit (see KI-002 residual in KNOWN_ISSUES).

---

## Known debt (documented, not hidden)

| ID | Description | Status |
|---|---|---|
| KI-001 | `decision_result` not fully PIT-deterministic without cache (residual: see KI-002, KI-003) | mitigated |
| KI-002 | `Decision.timestamp` coherence resolved; `artifact.as_of` provenance remains unaudited end-to-end | partially resolved |
| KI-003 | Double Yahoo fetch per request | open |
| KI-004 | `MacroService` without per-request cache (FRED 502 risk) | open |
| KI-005 | Obsolete `_unavailable_decision()` path | resolved in v2.7.4 |
| KI-006 | Bare `except:` clauses in defensive code paths | resolved |
| KI-007 | `/status` reports `database="NOT_CONFIGURED"` as a hardcoded state | resolved |
| KI-008 | CNBS and ECB official macro providers are incomplete | open |
| A3 | `policy_diff` PIT audit (source → effective date → alignment → feature → model) | open |
| A4 | Async / event-loop audit under ASGI + workers | open |
| P1 | `forecast-dashboard` reports `model.version="v1.0"` vs actual `Logistic_24` | registered |
| B | Legacy ranking (1 pair) vs canonical (9 pairs) divergence | deferred to v3.0 |
| Stub | L4 quality registries (`data_quality`, `freshness`, `drift`) | placeholder |

See `KNOWN_ISSUES.md` for the detailed issue registry and
`README.md §Current Limitations` for frontend-facing limitations.

---

## Roadmap

### Documentation / hygiene
- Register v2.7.5 as the current stable release.
- Maintain `KNOWN_ISSUES.md` as the detailed debt registry.
- Replace bare `except:` clauses with explicit exception handling.

### v3.0 — the real leap

1. Complete the PIT audit beginning at the adapter:
   `request → artifact → as_of → feature/data provenance → model → decision`.
2. Historical backtesting of decision quality.
3. Staging deployment (Nginx + Gunicorn).
4. Unify legacy ranking with the canonical pipeline.
5. Async / event-loop audit under production ASGI + workers.
6. Real multi-horizon models (5d / 30d / 90d).
7. Replace placeholder L4 registries with real PITValidator-backed
   implementations.

---

*This document is the authoritative pointer to the current stable
release. Update only when a new stable release is formally registered.*
