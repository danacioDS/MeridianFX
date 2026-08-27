# 📋 MERIDIAN FX — PROMPT -1 v2.0

## CONTRACT FREEZE & REPOSITORY AUDIT

### SPECIFICATION — FROZEN — EXECUTION READY

---

## 0. NON-NEGOTIABLE ENGINEERING RULES

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NON-NEGOTIABLE ENGINEERING RULES                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FRONTEND IS CONTRACT-DRIVEN.                                                ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  The frontend MUST NOT assume that a UI requirement implies             │ ║
║  │  the existence of a backend field.                                      │ ║
║  │                                                                         │ ║
║  │  For every rendered datum:                                              │ ║
║  │                                                                         │ ║
║  │  UI datum → Component → Hook → Service → Endpoint → Contract → Layer   │ ║
║  │                                                                         │ ║
║  │  DO NOT:                                                                │ ║
║  │  - invent contracts                                                     │ ║
║  │  - modify existing contracts                                            │ ║
║  │  - hardcode analytical values                                           │ ║
║  │  - interpret or transform intelligence — only format                    │ ║
║  │  - infer missing values                                                 │ ║
║  │  - calculate substitutes                                                │ ║
║  │  - create new API endpoints                                             │ ║
║  │  - silently resolve contract gaps                                       │ ║
║  │  - render UNSUPPORTED_BY_CONTRACT as if it were financial data          │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  CONTRACT REFERENCE:                                                        ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  • Layer 1 v5.1: /specs/layer1_v5.1_frozen.md                              ║
║  • Layer 2 v3.4.1: /specs/layer2_v3.4.1_frozen.md                          ║
║  • Layer 3 v5.0: /specs/layer3_v5.0_frozen.md                              ║
║  • Layer 4 v3.1.1: /specs/layer4_v3.1.1_frozen.md                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 1. PROMPT -1: CONTRACT FREEZE & REPOSITORY AUDIT (v2.0)

TASK: Perform a real repository audit. Build a complete contract traceability
matrix with EVIDENCE for every UI element in the mockup. Classify gaps. Produce
a freeze decision based on evidence.

REQUIRED ACTIONS:

1. CONTRACT DISCOVERY — locate all frozen contract specifications; extract ALL
   response structures from Layer 1 Section 7; build a complete field inventory.
2. REPOSITORY AUDIT — locate all frontend components, hooks, services, and
   endpoint definitions.
3. TRACEABILITY MATRIX — for EVERY UI element in the mockup, trace with EVIDENCE:

   UI → Component → Hook → Service → Endpoint → Contract → Field → Layer

   For each step record: file path, line number (or function name), spec section.
4. CLASSIFY EACH MAPPING:
   - VERIFIED: Evidence found in repository AND specification
   - ASSUMED: Mentioned in specification but not found in repository
   - UNVERIFIED: Could not establish the mapping
5. GAP CLASSIFICATION:
   - BLOCKING GAP: Core workflow dependency → STOP implementation until resolved
   - OPTIONAL GAP: Non-critical feature → render NOT_AVAILABLE
     (reason: UNSUPPORTED_BY_CONTRACT) or omit
6. PRODUCE THREE ARTIFACTS:
   - CONTRACT_TRACEABILITY.md: Complete mapping with evidence
   - CONTRACT_GAPS.md: All gaps with severity classification
   - FRONTEND_CONTRACT_FREEZE.md: Freeze declaration
7. DETERMINE FREEZE STATUS:
   - BLOCKING GAPS exist → DO NOT FREEZE
   - only OPTIONAL GAPS → FREEZE with gaps documented
   - NO gaps → FREEZE

EVIDENCE FORMAT per mapping:
  UI Element / Component / Hook / Service / Endpoint / Contract / Field / Layer / Status

RULE FOR OPTIONAL GAPS:
  Never render UNSUPPORTED_BY_CONTRACT as if it were financial data.
  Use: Feature state: NOT_AVAILABLE, reason: UNSUPPORTED_BY_CONTRACT.
  UI decides: show absence state or omit component.

NON-NEGOTIABLE:
  • Do NOT invent contracts to fill gaps
  • Do NOT implement BLOCKING GAP features without contract resolution
  • Do NOT silently choose an interpretation
  • Do NOT mark UNVERIFIED as VERIFIED without evidence
  • Do NOT proceed to Prompt 0 if BLOCKING GAPS exist
  • IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.

---

## 2. CONTRACT TRACEABILITY MATRIX — WITH EVIDENCE

| UI ELEMENT | TRACE | STATUS | EVIDENCE |
|---|---|---|---|
| (full matrix built during execution — see CONTRACT_TRACEABILITY.md) | | | |

## 3. CONTRACT GAPS — DETAILED CLASSIFICATION

| ID | UI ELEMENT | CONTRACT STATUS | SEVERITY | RESOLUTION |
|---|---|---|---|---|
| G-01 | Forecast history | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-02 | Health check endpoint | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-03 | Position size recommendation (frontend derived) | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-04 | Suggested actions | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-05 | Technical analysis summary | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-06 | Calibration status | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-07 | Cross-correlation heatmap | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-08 | Early warnings | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |
| G-09 | Macro calendar | Not in Layer 1 contracts | OPTIONAL | Omit or placeholder |

## 4. CONTRACT LAYER OWNERSHIP

Contracts exposed through Layer 1 API; Layer 1 composes from L2 (Decision),
L3 (Prediction), L4 (Evaluation). Frontend consumes ONLY Layer 1 contracts.

## 5. ENDPOINT VERIFICATION

| ENDPOINT | CONTRACT | LAYER | STATUS |
|---|---|---|---|
| /v1/fx/{pair}/forecast | ForecastResponse | Layer 1 | VERIFIED |
| /v1/fx/{pair}/forecast/history | NOT IN CONTRACT | N/A | OPTIONAL GAP |
| /v1/fx/{pair}/drivers | DriversResponse | Layer 1 | VERIFIED |
| /v1/fx/ranking | RankingResponse | Layer 1 | VERIFIED |
| /v1/fx/performance/{pair} | PerformanceResponse | Layer 1 | VERIFIED |
| /v1/status | StatusResponse | Layer 1 | VERIFIED |
| /v1/health | NOT IN CONTRACT | N/A | OPTIONAL GAP |

## 6. FRONTEND CONTRACT FREEZE DECLARATION

Determined during execution from the three artifacts.

---

# RESUMEN — PROMPT -1 v2.0

NEXT STEP: PROMPT 0 — Frontend Bootstrap & Configuration

## ¿Qué sigue?

| Opción | Descripción |
|--------|------------|
| **A** | ✅ COMPLETADO — Prompt -1 v2.0 ejecutado, freeze status: FREEZE |
| **B** | Ejecutar **Prompt 0: Frontend Bootstrap & Configuration** |
| **C** | Revisar los 9 OPTIONAL GAPS y decidir si se resuelven o se omiten |
| **D** | Pasar a **Layer 1 Implementation Prompts** |