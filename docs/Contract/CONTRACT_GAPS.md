# CONTRACT_GAPS.md — Meridian FX

**Prompt -1 v2.0 — Contract Freeze & Repository Audit (evidence-grounded)**

**Version:** v2.0
**Date:** 2026-08-27
**Frozen base:** `docs/Product_specification/Layer_01.md` (L1 v5.1)

**Reconciliation:** this document unifies the repository's canonical registry **G1–G9**
(`docs/Contract/CONTRACT_GAPS.md` v1, mirrored as `CONTRACT_GAP_MAP` in
`frontend/src/types/gaps.ts:41-54`) with the draft inventory **G-01…G-09** supplied with the
prompt, and adds gaps surfaced by this audit (EC-1…EC-4, RA, CA) that were previously
mis-classified as VERIFIED.

Gap rendering policy (enforced, not optional):
- All gap consumers render via `NotAvailable` (`components/common/NotAvailable.tsx:17-39`).
- `FEATURE_STATE.NOT_AVAILABLE` / `UNSUPPORTED_BY_CONTRACT` only — **no fallback, no client-side
  derivation** (`utils/gaps.ts:11-18`, `NO_FALLBACK_ALLOWED`, `NO_DERIVATION_ALLOWED`).
- `isActionable()` is presentation-only and never substitutes for a missing field
  (`utils/status.ts:6-7`).

---

## 1. Canonical gaps (G1–G9) — unified registry

| Gap | Scope | Pasted-matrix alias | Classification | Evidence |
| --- | ----- | ------------------- | -------------- | -------- |
| G1 | Forecast history — endpoint `/v1/fx/{pair}/forecast/history` exists (§8 SLA L1:815) but has **no §7 response structure**; service/hook absent | G-01 | OPTIONAL | types/gaps.ts:42,44 |
| G2 | Health check — `/v1/health` (§8 SLA L1:809) with no response structure; UI panel absent | G-02 | OPTIONAL | types/gaps.ts:46 |
| G3 | `position_size_recommendation` — referenced capability with no L1 field (only supported `decision.position_size`, §7.1/TS:65) | G-03 (renamed mint-size→position) | OPTIONAL | types/gaps.ts:48 |
| G4 | Regime panel — `/v1/fx/regime` defined as data source (§3 L1:142,159; §10 L1:879) but **no RegimeResponse structure** in §7 | G-04 | OPTIONAL | types/gaps.ts:50 |
| G5 | Macro/economic calendar — module referenced (`Global Overview`, HLD:397-408) with no contract field or endpoint | G-09 | OPTIONAL | types/gaps.ts:52 |
| G6 | `isActionable()` client-side derivation — prohibited | G-07 | NEVER (policy) | utils/status.ts:6-7 |
| G7 | Forecast history page/link (consumer of G1) | G-08 | OPTIONAL | gaps.ts 11-18 |
| G8 | Health status page/panel (consumer of G2) | — | OPTIONAL | gaps.ts 11-18 |
| G9 | Lineage UI module — §7.5/§7.6 structures fully defined (TS:372-383,386-447) but no UI module in scope | G-06 | OPTIONAL (deferred) | contracts.ts 372-447 |

Reference count: 6 canonical contracts (Forecast, Drivers, Ranking, Performance, Status, Lineage) —
core 5 fully supported; all 9 gaps OPTIONAL; **0 BLOCKING**.

## 2. Audit-surfaced gaps (previously mis-classified as VERIFIED in draft matrix)

| Gap | Scope | Why it is a gap | Evidence |
| --- | ----- | --------------- | -------- |
| EC-1 | Spread cost display (economic filter) | No `economic_filter`/cost block in L1 §7 | CRM: `grep spread Layer_01.md` → 0 hits in §7 |
| EC-2 | Slippage cost display | same | 0 hits in §7 |
| EC-3 | Commission cost display | same | 0 hits in §7 |
| EC-4 | Required minimum edge display | same | 0 hits in §7 |
| RA | Global regime alignment gauge | No regime field in §7.1/§7.3; `regime_performance` exists only in §7.4 | PRED 634-641; §7.3 TS only |
| CA | Calibration curve / calibration status | No `calibration` block in §7.4 | `grep calibration Layer_01.md` → 0 hits |
| DF-P | Data freshness within Forecast.data_quality | `DataQuality` = {overall, status} only; metric lives in `StatusResponse.metrics.data_freshness` (§7.7:787, TS:546) | PRED 775-779; TS 514-519 |

All above are OPTIONAL. Consumers must render `UNSUPPORTED_BY_CONTRACT`.

## 3. Scope boundary (deferred by design, NOT gaps)

| Item | Status | Reason |
| ---- | ------ | ------ |
| `GET /v1/fx/lineage/…` services/hooks | out of scope | structures §7.5/§7.6 defined; backend + UI deferred to a later layer |

## 4. Freeze impact

- **BLOCKING gaps: 0.** Frontend freeze can be declared against the 5 core contracts and 5 core
  endpoints (all VERIFIED in CONTRACT_TRACEABILITY.md §1.3).
- **OPTIONAL gaps:** G1–G9 + EC/RA/CA/DF-P remain behind `NOT_AVAILABLE` renders; each has an
  explicit "GAP-owner" escalation path — a gap is reclassified BLOCKING only when a frozen UI datum
  requires it and no `NOT_AVAILABLE` path is acceptable.
- Governance: a new contract field may only be introduced by editing L1 under the contract-freeze
  process; frontend never derives it.