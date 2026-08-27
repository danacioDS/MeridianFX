# Meridian FX — Frontend

Contract-driven foreign-exchange intelligence dashboard.

**Status:** Prompt 0 v1.2 (Bootstrap) ✅ VERIFIED 2026-08-27 (47/47 tests, typecheck clean) · Prompt 1 audit ✅ PASS · **Prompt X v1.3 + Prompts 4–8 (modules) ✅ 2026-08-27** — presentational component layer + composed pages (55/55 tests, tsc clean, production build OK). Freeze: `FRONTEND_CONTRACT_FREEZE.md` (FREEZE WITH OPTIONAL GAPS). Mapping: `MIGRATION_REPORT.md`, `COMPONENT_MAPPING.md` (docs/Contract).

---

## About this project

The frontend is **contract-driven**. All domain data comes from the Layer 1 v5.1
contract (`docs/Product_specification/Layer_01.md`, Sections 3, 7, 10).

The frontend **MUST NOT** calculate, infer, rank, score, classify, recommend,
estimate, derive, or substitute analytical values. It transports backend
responses verbatim and only performs **presentation formatting**.

Contract governance:

- `docs/Contract/CONTRACT_TRACEABILITY.md` — UI datum → … → contract field traceability
- `docs/Contract/CONTRACT_GAPS.md` — gap inventory (9 OPTIONAL GAPS)
- `docs/Contract/FRONTEND_CONTRACT_FREEZE.md` — freeze declaration

## Stack

| Area | Choice |
| ---- | ------ |
| UI | React 18 + TypeScript 5 + Vite 5 |
| Data | TanStack Query 5 + Axios 1 |
| Routing | react-router-dom 6 |
| Styling | Tailwind CSS 3 (dark theme) |
| Charts (future) | Recharts 2 |
| Dates | date-fns 3 |
| Tests | Vitest 1 + Testing Library 14 |

## Getting started

```bash
npm install
npm run dev          # start dev server (http://localhost:5173)
npm run typecheck    # TypeScript no-emit check
npm test             # infrastructure test suite (vitest run)
npm run build        # typecheck + production build
```

## Environment variables

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Layer 1 API base URL |
| `VITE_API_KEY` | `dev_placeholder_key_only` | Development placeholder |
| `VITE_POLLING_INTERVAL` | `60000` | Default polling interval (ms) |
| `VITE_ENVIRONMENT` | `development` | Runtime environment label |

> **SECURITY:** `VITE_API_KEY` MUST NOT contain a production secret. Vite env
> variables are embedded in the client bundle and are visible to anyone.
> Production authentication MUST use a secure browser-appropriate architecture
> (e.g., short-lived bearer tokens via a trusted identity provider). Never
> commit real API keys to version control.

## Design system (baseline)

Dark theme:

| Token | Value |
| ----- | ----- |
| Background | `#0A0A0F` |
| Surface | `#14141D` |
| Primary | `#00D4AA` |
| Text primary | `#FFFFFF` |
| Text secondary | `#8A8A9A` |
| Border | `#2A2A3A` |
| Success | `#00D4AA` |
| Warning | `#F5A623` |
| Error | `#FF6B6B` |
| Info | `#4A9EFF` |

Typography: Inter. Responsive: desktop (1200px+) and tablet (768px+).

## UNSUPPORTED_BY_CONTRACT features

These features are NOT implemented. They render `NOT_AVAILABLE`; no fallback and
no derivation is allowed.

| Feature | Reason |
| ------- | ------ |
| `getForecastHistory` / `useForecastHistory` | No forecast history response structure in Layer 1 v5.1 §7 (G1) |
| `getHealth` | No HealthResponse structure in Layer 1 v5.1 §7 (G2) |
| `position_size_recommendation` | Field absent from Layer 1 v5.1 §7 — use supported `decision.position_size` (G3) |
| Regime panel | No RegimeResponse structure (G4) |
| Economic calendar | No contract field/endpoint (G5) |

Full inventory: `docs/Contract/CONTRACT_GAPS.md`.

## Guardrails (non-negotiable)

- Domain types originate exclusively from Layer 1 contracts (`src/types/contracts.ts`).
- Infrastructure types (`ApiStatus`, `PollingConfig`, gap flags) are frontend-only.
- No `ApiResponse<T>` envelope — Layer 1 returns domain structures directly.
- `decision.actionable` is consumed directly; no `isActionable()` exists.
- Status utilities only map backend status → label/color (presentation only).
- `usePolling` controls timing only and returns the resolved value unchanged.
- Nullability is preserved: `null` is never replaced with `0`, `false`, `""`, or defaults.

## Tests (Prompt 0 infrastructure)

| Suite | Verifies |
| ----- | -------- |
| `tests/utils/format.test.ts` | Formatting preserves values; no null replacement |
| `tests/utils/status.test.ts` | Status mapping is one-to-one; presentation only |
| `tests/utils/gaps.test.ts` | Unsupported → NOT_AVAILABLE; no fallback/derivation |
| `tests/services/forecast.test.ts` | Services return raw backend responses unchanged |
| `tests/hooks/useForecast.test.ts` | Hooks return responses unchanged |
| `tests/contracts/validate.test.ts` | Contract types match Layer 1 §7 (no extra/missing fields) |

## Project structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/        Shared components (ErrorBoundary, ApiError, …)
│   │   ├── layout/        Sidebar, Header, MainLayout
│   │   └── forecast/ drivers/ global/ evaluation/ status/   ← module placeholders
│   ├── services/          API client + domain endpoint adapters
│   ├── hooks/             Data-fetching hooks (TanStack Query)
│   ├── types/             contracts.ts (Layer 1 §7) + infra/gap types
│   ├── utils/             Presentation-only formatting + status mapping
│   ├── config/            Environment configuration
│   ├── pages/             Placeholder page shells
│   └── tests/             Infrastructure test suites
├── public/
├── .env / .env.example
├── vite.config.ts / vitest.config.ts / tailwind.config.js
└── README.md
```