# FRONTEND_CONTRACT_FREEZE.md — Meridian FX

**Prompt -1 v2.0 — Contract Freeze & Repository Audit (evidence-grounded)**

**Version:** v2.0
**Date:** 2026-08-27
**Frozen base:** `docs/Product_specification/Layer_01.md` — Layer 1 v5.1 (Sections 3, 5, 7, 8, 10)

---

## 1. Freeze declaration

**STATUS: ✅ FREEZE WITH OPTIONAL GAPS**

The frontend contract surface is **frozen** effective with this audit. Evidence-based basis:

- **Contract data structures — 5/5 VERIFIED:**
  ForecastResponse (§7.1), DriversResponse (§7.2), RankingResponse (§7.3), PerformanceResponse (§7.4),
  StatusResponse (§7.7). LineageResponse (§7.5/§7.6) structures defined, UI deferred.
  Types: `frontend/src/types/contracts.ts` (571 lines) mirror the spec verbatim —
  traceability in `CONTRACT_TRACEABILITY.md` §1.2. ✅
- **TypeScript interfaces — VERIFIED:** `contracts.ts` matches L1 §7 field names, types, nullability. ✅
- **REST endpoints — 5/5 core VERIFIED:** `/v1/fx/{pair}/forecast`, `/v1/fx/{pair}/drivers`,
  `/v1/fx/ranking`, `/v1/fx/performance/{pair}?period=`, `/v1/status`
  (services: forecast.ts:12, drivers.ts:10, ranking.ts:11, performance.ts:10, status.ts:12). ✅
- **Hooks / services — VERIFIED:** 5 data hooks (useForecast/useDrivers/useRanking/usePerformance/
  useStatus) consuming exactly the 5 services above. ✅
- **Field mapping — VERIFIED:** 44 UI data paths map to frozen fields (traceability matrix §2);
  `utils/status.ts`/`utils/gaps.ts` are presentation-only, no derivation. ✅
- **BLOCKING gaps — 0** (`CONTRACT_GAPS.md` §1, §4). ✅

## 2. Freeze rules (binding)

1. **No contract variation.** UI code may reference ONLY fields defined in the frozen L1 §7 surface.
2. **No client-side derivation.** Any value not present in the payload is rendered
   `NOT_AVAILABLE` / `UNSUPPORTED_BY_CONTRACT` (`NotAvailable.tsx:17-39`, `utils/gaps.ts:11-18`).
3. **No fallback data.** Absent/gapped datums render the gap state; never substitute an alternate
   endpoint or local synthesis.
4. **Gaps change frozen state only by explicit decision.** A gap flips BLOCKING only via the
   GAP-owner escalation; otherwise it stays `NOT_AVAILABLE`.
5. **L1 is the single authority.** Any new field requires the L1 edit process; the audit matrix
   (`CONTRACT_TRACEABILITY.md`) is the verification evidence set.
6. Python Layer 2 backend already implements these contracts; its test/protocol conformance suite
   (99 tests) is unchanged by this freeze (see `CONTRACT_TRACEABILITY.md` §4 endpoint mapping parity).

## 3. Not frozen today (honest status)

| Item | Status |
| ---- | ------ |
| Module UI components (ForecastSummary, ActionabilityPanel, SHAPChart, RAGPanel, RankingTable, MetricsSummary, DegradationPanel, StatusPage panels, …) | ASSUMED — mockup modules not yet implemented (component dirs empty; 5 module pages are placeholders `pages/*.tsx:5-15`). Constraints already in place (hooks, services, types, NotAvailable, model-reader wiring as designed in Prompt 0 architecture). |
| Mockup HTML artifact | not present in repository — element inventory sourced from the prompt-supplied mockup list (HLD references 6 modules, `02_product_specification.md:395-408`). |
| Lineage UI (G9) | deferred |
| Preview red-lines (G1–G9 + EC-1…EC-4, RA, CA, DF-P) | OPTIONAL; rendered `NOT_AVAILABLE` |
| Legacy/mock UI | none exists — all pages route to scaffolding (`App.tsx:33-42`) |

## 4. Conformance evidence (used for this freeze)

| Artifact | Evidence |
| -------- | -------- |
| Spec / structures | Layer_01.md §7 (511-795); §8 SLA (799-823); §10 dashboards (863-903) |
| Types | contracts.ts 34-571 |
| Gap registry | types/gaps.ts:41-54; CONTRACT_GAPS.md |
| Services / hooks | services/*.ts; hooks/*.ts |
| Presentation maps | utils/status.ts, utils/gaps.ts, components/common/NotAvailable.tsx |
| Previous freeze doc | this file (v2.0 replaces v1; draft trusts were corrected in traceability §3) |

## 5. Sign-off summary

- Contract layer: **FROZEN** (5 core contracts, 5 core endpoints, 44 data paths VERIFIED).
- Component layer: **NOT YET IMPLEMENTED** — pending Prompt X (mode follows Prompt 0 architecture;
  harness contracts preserved).
- **0 BLOCKING gaps. 0 VERIFIED rows retracted.** All static-verifiable rows remain standing;
  9 falsified draft claims were corrected (traceability §3).