# PROMPT 0 v1.2 — FRONTEND BOOTSTRAP & INFRASTRUCTURE — FINAL — FROZEN — EXECUTION READY

Status: pasted by user on 2026-08-27. Executed against `frontend/`.

---

## 0. NON-NEGOTIABLE ENGINEERING RULES

- FRONTEND IS CONTRACT-DRIVEN. PROMPT 0 IS BOOTSTRAP & INFRASTRUCTURE — NOT INTELLIGENCE.
- Backend-owned intelligence: the frontend MUST treat analytical values as authoritative backend output.
  The frontend MUST NOT: calculate, infer, rank, score, classify, recommend, estimate, derive,
  substitute, replace null with default values, infer missing values from adjacent fields.
- Contract boundary enforcement:
  - Domain types MUST originate from Layer 1 contracts.
  - Infrastructure types (ApiStatus, UI state, config) MAY be defined by the frontend.
  - ApiResponse<T> MUST NOT be used unless the backend explicitly defines that envelope.
  - The frontend MUST preserve backend nullability semantics (null≠0, false, "", defaults).
  - UNSUPPORTED_BY_CONTRACT → FEATURE_STATE = NOT_AVAILABLE, NO_FALLBACK_ALLOWED = TRUE,
    NO_DERIVATION_ALLOWED = TRUE.
  - CONTRACT EQUALITY: `decision.position_size` ≠ `position_size_recommendation`.
  - Presentation logic (formatting/visual mapping) is allowed; business/analytical/decision logic is not.
- Security: VITE_API_KEY MUST NOT contain a production secret; development placeholders only.
- Testing: Prompt 0 MUST include minimal infrastructure tests:
  - Formatting preserves values
  - Status mapping is one-to-one
  - Unsupported features return NOT_AVAILABLE
  - Services do not transform responses
  - Hooks return responses unchanged
  - NO analytical logic in any file
- Contract reference: Layer 1 v5.1 §7 Response Structures; CONTRACT_TRACEABILITY.md; CONTRACT_GAPS.md.

## 1. PROMPT 0: FRONTEND BOOTSTRAP & INFRASTRUCTURE

TASK: Create the project structure and foundational infrastructure for the Meridian FX frontend.

PRECONDITIONS: Prompt -1 completed (CONTRACT_TRACEABILITY.md, CONTRACT_GAPS.md,
FRONTEND_CONTRACT_FREEZE.md exist; Freeze status: FREEZE WITH OPTIONAL GAPS).

REQUIRED OUTPUTS:

1. PROJECT STRUCTURE — `frontend/src/{components/{common,forecast,drivers,global,evaluation,status},
   services,hooks,types/{contracts,infrastructure,gaps,index},utils,config,pages,tests/{services,hooks,
   utils,contracts},App.tsx,main.tsx}`, `public/`, `package.json`, `tsconfig.json`, `vite.config.ts`,
   `tailwind.config.js`, `vitest.config.ts`, `.env`, `.env.example`, `README.md`.

2. CONFIGURATION:
   - .env: VITE_API_BASE_URL=http://localhost:8000, VITE_API_KEY=dev_placeholder_key_only,
     VITE_POLLING_INTERVAL=60000, VITE_ENVIRONMENT=development
   - .env.example: same with dev placeholder + SECURITY comment
   - Dependencies: react@18, react-dom@18, typescript@5, vite@5, @tanstack/react-query@5, axios@1,
     recharts@2, date-fns@3, tailwindcss@3, react-router-dom@6, vitest@1, @testing-library/react@14.

3. DESIGN SYSTEM (BASELINE): dark theme; background #0A0A0F, surface #14141D, primary #00D4AA,
   text-primary #FFFFFF, text-secondary #8A8A9A, border #2A2A3A; Inter; desktop 1200px+ / tablet 768px+;
   status colors success #00D4AA, warning #F5A623, error #FF6B6B, info #4A9EFF.

4. DOMAIN TYPES (FROM L1): types/contracts.ts MUST match Layer 1 v5.1 §7 exactly: ForecastResponse,
   RankingResponse, DriversResponse, PerformanceResponse, StatusResponse, HealthResponse (if exists).
   Each type MUST include field-level JSDoc referencing the spec section. Preserve nullability.

5. INFRASTRUCTURE TYPES: types/infrastructure.ts (ApiStatus = IDLE|LOADING|SUCCESS|ERROR;
   PollingConfig = {interval,enabled}); ApiResponse<T> NOT defined (no backend envelope);
   types/gaps.ts (CONTRACT_STATUS = SUPPORTED|UNSUPPORTED_BY_CONTRACT; FEATURE_STATE =
   AVAILABLE|NOT_AVAILABLE; NO_FALLBACK_ALLOWED = true; NO_DERIVATION_ALLOWED = true;
   CONTRACT_GAP_MAP: Record<string,string>); types/index.ts exports all.

6. API CLIENT (TRANSPORT ONLY): services/api.ts — axios base, auth headers, error handling,
   retry 3 with exponential backoff, timeout 30s. MUST NOT transform payloads/rename fields/normalize/
   calculate/inject defaults. DO NOT implement endpoint methods.

7. SERVICES (DOMAIN ENDPOINT ADAPTERS): getForecast(pair) → ForecastResponse, getRanking() →
   RankingResponse, getDrivers(pair) → DriversResponse, getPerformance(pair, period) →
   PerformanceResponse, getStatus() → StatusResponse. All return raw response (no transformation).
   getForecastHistory / getHealth = UNSUPPORTED_BY_CONTRACT. services/index.ts exports.

8. CUSTOM HOOKS (DATA FETCHING ONLY, TanStack Query): useForecast(pair), useRanking(), useDrivers(pair),
   usePerformance(pair, period), useStatus() → {data,isLoading,error,refetch}; usePolling<T>(fn,
   interval, enabled?) timing-only, returns original resolved value unchanged. useForecastHistory =
   UNSUPPORTED_BY_CONTRACT. hooks/index.ts exports.

9. UTILITY FUNCTIONS (PRESENTATION ONLY):
   - utils/format.ts: formatCurrency, formatPercent, formatDateTime, formatDate, formatNumber,
     formatProbability, formatDirection, formatEdgeRatio, formatSharpe, formatDrawdown, formatStatus.
     Pure formatting; MUST NOT calculate/infer/derive; MUST NOT replace null with defaults.
   - utils/status.ts: getStatusColor, getStatusLabel, getSignalStrengthLabel, getDeliveryStateLabel —
     presentation mapping only; isActionable NOT allowed (use decision.actionable directly).
   - utils/gaps.ts: isUnsupported, getFeatureState, CONTRACT_GAP_MAP.
   - utils/index.ts exports.

10. ERROR HANDLING: common/ErrorBoundary.tsx (component errors + fallback UI),
    common/LoadingSpinner.tsx, common/NotAvailable.tsx (UNSUPPORTED_BY_CONTRACT, NO_FALLBACK_ALLOWED,
    NO_DERIVATION_ALLOWED), common/ApiError.tsx (retry button), common/index.ts.

11. APP LAYOUT (BASIC): App.tsx (Router + QueryClientProvider + ThemeProvider); layout/Sidebar.tsx
    (nav Global, Forecast, Drivers, Evaluation, Status; logo; active route highlight);
    layout/Header.tsx (page title, system status indicator from useStatus, last updated, refresh);
    layout/MainLayout.tsx (Sidebar + Header + Content; sidebar collapses on tablet).

12. PAGES (PLACEHOLDER): GlobalPage (Global Intelligence), ForecastPage (Forecast Dashboard),
    DriversPage (Drivers & Explanation), EvaluationPage (Evaluation & Performance),
    StatusPage (System Status), pages/index.ts.

13. INFRASTRUCTURE TESTS: tests/utils/format.test.ts (preserve values, no null replacement);
    tests/utils/status.test.ts (one-to-one mapping, no inference); tests/utils/gaps.test.ts
    (NOT_AVAILABLE, NO_FALLBACK_ALLOWED, NO_DERIVATION_ALLOWED); tests/services/forecast.test.ts
    (response === input); tests/hooks/useForecast.test.ts (responses unchanged);
    tests/contracts/validate.test.ts (match L1, no extra fields, no missing required);
    tests/index.ts (runner config).

14. README.md: setup, env vars, security note, contract traceability reference, UNSUPPORTED list,
    link to CONTRACT_GAPS.md, domain data from L1 note, no client-side intelligence note.

CONSTRAINTS: DO NOT implement analytical logic; DO NOT implement components beyond placeholder;
DO NOT implement data-visualization components; DO NOT implement module-specific logic;
DO NOT invent contracts/fields; DO NOT derive/approximate missing values; DO NOT replace null with
defaults; ALL domain types from L1; ALL unsupported features → NOT_AVAILABLE; position_size (supported)
≠ position_size_recommendation (unsupported); NO_FALLBACK_ALLOWED / NO_DERIVATION_ALLOWED = true for all
gaps; VITE_API_KEY dev-only. IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.

## 2. CONTRACT BOUNDARY ENFORCEMENT — EXPLICIT RULES

- RULE 1: Domain vs infrastructure types. ApiResponse<T> not defined unless backend envelope exists.
- RULE 2: No analytical logic (no calculation/inference/ranking/scoring/classification/recommendation/
  estimation/derivation/substitution).
- RULE 3: decision.position_size → SUPPORTED; position_size_recommendation → UNSUPPORTED → NOT_AVAILABLE.
- RULE 4: No isActionable() — use decision.actionable directly.
- RULE 5: Status utilities presentation-only ("healthy"→"Healthy"/green; never derive from e.g.
  prediction_coverage).
- RULE 6: usePolling infrastructure-only (timing; no transforms/derived metrics/state inference).
- RULE 7: Unsupported features — no fallback, no derivation.
- RULE 8: Null/undefined semantics preserved (never 0/false/""/defaults).
- RULE 9: Security — no secrets in frontend.
- RULE 10: Prompt 1 validates, does not redefine contracts (PASS→proceed; FAIL→report→decision).

## 3. PROMPT 0 — EXECUTION SUMMARY

- All 15 output items defined (project structure, configuration, design system, domain types,
  infrastructure types, gap types, API client, service methods, hooks, utilities, error handling,
  app layout, pages, infrastructure tests, README).
- Contract integrity: all domain types from L1; infra types separate; no ApiResponse<T>; all gaps
  UNSUPPORTED_BY_CONTRACT; no analytical logic; no invented contracts; position_size ≠
  position_size_recommendation; no isActionable(); status utils presentation-only; usePolling
  infrastructure-only; null semantics preserved; VITE_API_KEY placeholder; tests defined; evidence
  from CONTRACT_TRACEABILITY.md; NO_FALLBACK_ALLOWED = true; NO_DERIVATION_ALLOWED = true.
- PROMPT 0 EXECUTION READINESS: 10/10.
- MERIDIAN FX FRONTEND IMPLEMENTATION READINESS: PENDING SUBSEQUENT PROMPTS (1–11).

## ¿Qué sigue?

| Opción | Descripción |
|--------|------------|
| A | COMPLETADO — Prompt 0 v1.2 definido y congelado |
| B | Ejecutar Prompt 1: TypeScript Contracts Validation (AUDIT ONLY) |
| C | Ejecutar Prompt 4: Common Components |
| D | Ejecutar Prompt 5-9: Módulos específicos |