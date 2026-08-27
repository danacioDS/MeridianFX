
---

# 📋 MERIDIAN FX — PROMPT 0 v1.2

## FRONTEND BOOTSTRAP & INFRASTRUCTURE — FINAL — FROZEN — EXECUTION READY

---

## 0. NON-NEGOTIABLE ENGINEERING RULES

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NON-NEGOTIABLE ENGINEERING RULES                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FRONTEND IS CONTRACT-DRIVEN.                                                ║
║  PROMPT 0 IS BOOTSTRAP & INFRASTRUCTURE — NOT INTELLIGENCE.                 ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  BACKEND-OWNED INTELLIGENCE                                             │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  The frontend MUST treat analytical values as authoritative backend    │ ║
║  │  output.                                                               │ ║
║  │                                                                         │ ║
║  │  The frontend MUST NOT:                                                │ ║
║  │  • calculate                                                           │ ║
║  │  • infer                                                               │ ║
║  │  • rank                                                                │ ║
║  │  • score                                                               │ ║
║  │  • classify                                                            │ ║
║  │  • recommend                                                           │ ║
║  │  • estimate                                                            │ ║
║  │  • derive                                                              │ ║
║  │  • substitute                                                          │ ║
║  │  • replace null with default values                                    │ ║
║  │  • infer missing values from adjacent fields                           │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  CONTRACT BOUNDARY ENFORCEMENT                                          │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │                                                                         │ ║
║  │  DOMAIN TYPES:                                                          │ ║
║  │  All domain/data types MUST originate from Layer 1 contracts.          │ ║
║  │                                                                         │ ║
║  │  INFRASTRUCTURE TYPES:                                                  │ ║
║  │  Infrastructure-only types such as ApiStatus, UI state types, and      │ ║
║  │  configuration types MAY be defined by the frontend because they do    │ ║
║  │  not represent backend intelligence or domain semantics.               │ ║
║  │                                                                         │ ║
║  │  API ENVELOPE:                                                          │ ║
║  │  ApiResponse<T> MUST NOT be used to redefine or wrap Layer 1 domain   │ ║
║  │  responses unless the backend transport contract explicitly defines    │ ║
║  │  that envelope. If the backend returns ForecastResponse directly,      │ ║
║  │  use it directly.                                                      │ ║
║  │                                                                         │ ║
║  │  NULL / UNDEFINED SEMANTICS:                                            │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  The frontend MUST preserve backend nullability semantics.             │ ║
║  │                                                                         │ ║
║  │  MUST NOT:                                                             │ ║
║  │  • replace null with 0                                                 │ ║
║  │  • replace null with false                                             │ ║
║  │  • replace null with ""                                                │ ║
║  │  • invent default analytical values                                    │ ║
║  │  • infer missing values from adjacent fields                           │ ║
║  │                                                                         │ ║
║  │  UNSUPPORTED FEATURES:                                                  │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  CONTRACT_STATUS = UNSUPPORTED_BY_CONTRACT                              │ ║
║  │  FEATURE_STATE = NOT_AVAILABLE                                          │ ║
║  │  NO_FALLBACK_ALLOWED = TRUE                                             │ ║
║  │  NO_DERIVATION_ALLOWED = TRUE                                           │ ║
║  │                                                                         │ ║
║  │  CONTRACT EQUALITY:                                                     │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  .decision.position_size                                                │ ║
║  │  ≠                                                                      │ ║
║  │  position_size_recommendation                                            │ ║
║  │                                                                         │ ║
║  │  A supported field MUST NOT be repurposed to satisfy an unsupported    │ ║
║  │  field.                                                                │ ║
║  │                                                                         │ ║
║  │  PRESENTATION LOGIC:                                                    │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  Formatting and visual mapping are allowed.                            │ ║
║  │  Business, analytical, economic, or decision logic is not.             │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  SECURITY:                                                              │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  VITE_API_KEY MUST NOT contain a production secret.                    │ ║
║  │  Production authentication MUST use a secure architecture              │ ║
║  │  appropriate for browser clients.                                      │ ║
║  │  For development, use placeholder values only.                         │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  TESTING:                                                               │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  Prompt 0 MUST include minimal infrastructure tests:                   │ ║
║  │  - Formatting functions preserve values                                │ ║
║  │  - Status mapping is one-to-one                                        │ ║
║  │  - Unsupported features return NOT_AVAILABLE                           │ ║
║  │  - Services do not transform responses                                 │ ║
║  │  - Hooks return responses unchanged                                    │ ║
║  │  - NO analytical logic in any file                                     │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  CONTRACT REFERENCE:                                                        ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  • Layer 1 v5.1: Section 7 "Response Structures"                            ║
║  • CONTRACT_TRACEABILITY.md: From Prompt -1                                 ║
║  • CONTRACT_GAPS.md: From Prompt -1                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 1. PROMPT 0: FRONTEND BOOTSTRAP & INFRASTRUCTURE

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PROMPT 0: FRONTEND BOOTSTRAP & INFRASTRUCTURE            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  TASK: Create the project structure and foundational infrastructure for     ║
║        the Meridian FX frontend.                                             ║
║                                                                              ║
║  PRECONDITIONS:                                                              ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  • Prompt -1 completed (CONTRACT_TRACEABILITY.md exists)                    ║
║  • Prompt -1 completed (CONTRACT_GAPS.md exists)                            ║
║  • Prompt -1 completed (FRONTEND_CONTRACT_FREEZE.md exists)                 ║
║  • Freeze status: ✅ FREEZE WITH OPTIONAL GAPS                              ║
║                                                                              ║
║  SPECIFICATION REFERENCE:                                                   ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  • Layer 1 v5.1: Section 3 "API Endpoints"                                  ║
║  • Layer 1 v5.1: Section 7 "Response Structures"                            ║
║  • Layer 1 v5.1: Section 10 "Dashboard Pages"                               ║
║  • Frontend Mockup: Complete                                                ║
║  • CONTRACT_TRACEABILITY.md: From Prompt -1                                 ║
║  • CONTRACT_GAPS.md: From Prompt -1                                         ║
║                                                                              ║
║  REQUIRED OUTPUTS:                                                          ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║                                                                              ║
║  1. PROJECT STRUCTURE:                                                      ║
║     frontend/                                                               ║
║     ├── src/                                                               ║
║     │   ├── components/                                                    ║
║     │   │   ├── common/       ← Shared components                          ║
║     │   │   ├── forecast/     ← Forecast module (placeholder)              ║
║     │   │   ├── drivers/      ← Drivers module (placeholder)               ║
║     │   │   ├── global/       ← Global module (placeholder)                ║
║     │   │   ├── evaluation/   ← Evaluation module (placeholder)            ║
║     │   │   └── status/       ← Status module (placeholder)                ║
║     │   ├── services/         ← API clients                                ║
║     │   ├── hooks/            ← React hooks                               ║
║     │   ├── types/            ← TypeScript contracts                      ║
║     │   │   ├── contracts.ts  ← Domain types (from Layer 1)               ║
║     │   │   ├── infrastructure.ts ← ApiStatus, PollingConfig              ║
║     │   │   ├── gaps.ts       ← UNSUPPORTED_BY_CONTRACT, NOT_AVAILABLE    ║
║     │   │   └── index.ts                                                   ║
║     │   ├── utils/            ← Utilities                                  ║
║     │   ├── config/           ← Configuration                              ║
║     │   ├── pages/            ← Page components (placeholder)              ║
║     │   ├── tests/            ← Infrastructure tests                       ║
║     │   │   ├── services/     ← Service tests                              ║
║     │   │   ├── hooks/        ← Hook tests                                 ║
║     │   │   ├── utils/        ← Utility tests                              ║
║     │   │   └── contracts/    ← Contract validation tests                  ║
║     │   ├── App.tsx                                                       ║
║     │   └── main.tsx                                                      ║
║     ├── public/                                                            ║
║     ├── package.json                                                       ║
║     ├── tsconfig.json                                                      ║
║     ├── vite.config.ts                                                     ║
║     ├── tailwind.config.js                                                 ║
║     ├── vitest.config.ts                                                   ║
║     ├── .env                                                               ║
║     ├── .env.example                                                       ║
║     └── README.md                                                          ║
║                                                                              ║
║  2. CONFIGURATION:                                                          ║
║     - .env:                                                                 ║
║       VITE_API_BASE_URL=http://localhost:8000                              ║
║       VITE_API_KEY=dev_placeholder_key_only                                ║
║       VITE_POLLING_INTERVAL=60000                                          ║
║       VITE_ENVIRONMENT=development                                         ║
║     - .env.example:                                                         ║
║       VITE_API_BASE_URL=http://localhost:8000                              ║
║       VITE_API_KEY=your_dev_key_here                                       ║
║       VITE_POLLING_INTERVAL=60000                                          ║
║       VITE_ENVIRONMENT=development                                         ║
║       # SECURITY: Never commit real API keys to version control            ║
║     - package.json dependencies:                                            ║
║       - react@18                                                           ║
║       - react-dom@18                                                       ║
║       - typescript@5                                                       ║
║       - vite@5                                                             ║
║       - @tanstack/react-query@5                                            ║
║       - axios@1                                                            ║
║       - recharts@2                                                         ║
║       - date-fns@3                                                         ║
║       - tailwindcss@3                                                      ║
║       - react-router-dom@6                                                ║
║       - vitest@1                                                           ║
║       - @testing-library/react@14                                         ║
║                                                                              ║
║  3. DESIGN SYSTEM (BASELINE):                                               ║
║     - Dark theme:                                                           ║
║       - background: #0A0A0F                                                ║
║       - surface: #14141D                                                   ║
║       - primary: #00D4AA                                                   ║
║       - text-primary: #FFFFFF                                              ║
║       - text-secondary: #8A8A9A                                            ║
║       - border: #2A2A3A                                                    ║
║     - Typography: Inter                                                    ║
║     - Responsive: desktop (1200px+) and tablet (768px+)                   ║
║     - Status colors:                                                        ║
║       - success: #00D4AA                                                   ║
║       - warning: #F5A623                                                   ║
║       - error: #FF6B6B                                                     ║
║       - info: #4A9EFF                                                      ║
║                                                                              ║
║  4. DOMAIN TYPES (FROM LAYER 1 CONTRACTS):                                  ║
║     - types/contracts.ts:                                                   ║
║       MUST match Layer 1 v5.1 Section 7 exactly:                           ║
║       - ForecastResponse                                                    ║
║       - RankingResponse                                                     ║
║       - DriversResponse                                                     ║
║       - PerformanceResponse                                                 ║
║       - StatusResponse                                                      ║
║       - HealthResponse (if exists in contract)                             ║
║     - Each type MUST include field-level JSDoc comments referencing         ║
║       the Layer 1 specification section.                                    ║
║     - NULL/UNDEFINED: Preserve backend nullability semantics.              ║
║       DO NOT replace null with default values.                             ║
║                                                                              ║
║  5. INFRASTRUCTURE TYPES (FRONTEND-ONLY):                                   ║
║     - types/infrastructure.ts:                                              ║
║       - ApiStatus = "IDLE" | "LOADING" | "SUCCESS" | "ERROR"              ║
║       - PollingConfig = { interval: number; enabled: boolean }            ║
║       - NOTE: ApiResponse<T> is NOT defined unless backend explicitly      ║
║         returns an envelope. Use domain types directly.                    ║
║     - types/gaps.ts:                                                       ║
║       - CONTRACT_STATUS: "SUPPORTED" | "UNSUPPORTED_BY_CONTRACT"          ║
║       - FEATURE_STATE: "AVAILABLE" | "NOT_AVAILABLE"                       ║
║       - NO_FALLBACK_ALLOWED = true                                         ║
║       - NO_DERIVATION_ALLOWED = true                                       ║
║       - CONTRACT_GAP_MAP: Record<string, string>                          ║
║     - types/index.ts:                                                      ║
║       - Export all types                                                   ║
║                                                                              ║
║  6. API CLIENT (TRANSPORT LAYER ONLY):                                     ║
║     - services/api.ts:                                                     ║
║       - Base axios client                                                  ║
║       - Authentication headers                                              ║
║       - Error handling                                                      ║
║       - Retry logic (3 retries, exponential backoff)                       ║
║       - Timeout: 30 seconds                                                 ║
║       - MUST NOT:                                                          ║
║         - transform response payloads                                      ║
║         - rename backend fields                                            ║
║         - normalize domain semantics                                       ║
║         - calculate values                                                 ║
║         - inject defaults into domain fields                               ║
║       - DO NOT implement endpoint methods — only base client              ║
║                                                                              ║
║  7. SERVICES (DOMAIN ENDPOINT ADAPTERS):                                    ║
║     - services/forecast.ts:                                                 ║
║       - getForecast(pair: string): Promise<ForecastResponse>               ║
║       - Returns the raw backend response (no transformation)               ║
║       - NOTE: getForecastHistory is UNSUPPORTED_BY_CONTRACT               ║
║     - services/ranking.ts:                                                 ║
║       - getRanking(): Promise<RankingResponse>                             ║
║       - Returns the raw backend response                                   ║
║     - services/drivers.ts:                                                 ║
║       - getDrivers(pair: string): Promise<DriversResponse>                 ║
║       - Returns the raw backend response                                   ║
║     - services/performance.ts:                                             ║
║       - getPerformance(pair: string, period: string):                      ║
║         Promise<PerformanceResponse>                                       ║
║       - Returns the raw backend response                                   ║
║     - services/status.ts:                                                  ║
║       - getStatus(): Promise<StatusResponse>                               ║
║       - Returns the raw backend response                                   ║
║       - NOTE: getHealth() is UNSUPPORTED_BY_CONTRACT                      ║
║     - services/index.ts:                                                   ║
║       - Export all services                                                ║
║                                                                              ║
║  8. CUSTOM HOOKS (DATA FETCHING ONLY):                                     ║
║     - hooks/useForecast.ts:                                                 ║
║       - useForecast(pair: string) → { data, isLoading, error, refetch }   ║
║       - Uses TanStack Query                                                 ║
║       - Returns raw backend response without transformation                ║
║       - NOTE: useForecastHistory is UNSUPPORTED_BY_CONTRACT               ║
║     - hooks/useRanking.ts:                                                 ║
║       - useRanking() → { data, isLoading, error, refetch }                ║
║       - Returns raw backend response                                       ║
║     - hooks/useDrivers.ts:                                                 ║
║       - useDrivers(pair: string) → { data, isLoading, error, refetch }    ║
║       - Returns raw backend response                                       ║
║     - hooks/usePerformance.ts:                                             ║
║       - usePerformance(pair: string, period: string) →                     ║
║         { data, isLoading, error, refetch }                                ║
║       - Returns raw backend response                                       ║
║     - hooks/useStatus.ts:                                                  ║
║       - useStatus() → { data, isLoading, error, refetch }                 ║
║       - Returns raw backend response                                       ║
║     - hooks/usePolling.ts:                                                 ║
║       - usePolling<T>(fn: () => Promise<T>, interval: number,             ║
║         enabled?: boolean) → { data, isLoading, error, refetch }          ║
║       - MAY control request/refetch timing only                           ║
║       - MUST NOT transform analytical data                                ║
║       - MUST NOT calculate derived metrics                                ║
║       - MUST NOT infer state                                               ║
║       - MUST NOT modify backend responses                                  ║
║       - MUST NOT implement business rules                                  ║
║       - MUST return the original resolved value without transformation    ║
║     - hooks/index.ts:                                                      ║
║       - Export all hooks                                                   ║
║                                                                              ║
║  9. UTILITY FUNCTIONS (PRESENTATION ONLY):                                 ║
║     - utils/format.ts:                                                     ║
║       - formatCurrency(value: number): string                              ║
║       - formatPercent(value: number): string                               ║
║       - formatDateTime(value: string): string                              ║
║       - formatDate(value: string): string                                  ║
║       - formatNumber(value: number, decimals: number): string              ║
║       - formatProbability(value: number): string                           ║
║       - formatDirection(value: string): string                             ║
║       - formatEdgeRatio(value: number): string                             ║
║       - formatSharpe(value: number): string                                ║
║       - formatDrawdown(value: number): string                              ║
║       - formatStatus(value: string): string                                ║
║       - NOTE: These MUST be pure formatting functions                     ║
║       - NOTE: MUST NOT calculate, infer, or derive                        ║
║       - NOTE: MUST NOT replace null values with defaults                  ║
║     - utils/status.ts:                                                    ║
║       - getStatusColor(status: string): string                            ║
║         │                                                                  ║
║         │  ╔═════════════════════════════════════════════════════════════╗ ║
║         │  ║  STATUS UTILITIES MUST ONLY map an existing backend        ║ ║
║         │  ║  status to a presentation label/color.                     ║ ║
║         │  ║  They MUST NOT infer, calculate, reinterpret, or derive   ║ ║
║         │  ║  business/system status.                                  ║ ║
║         │  ╚═════════════════════════════════════════════════════════════╝ ║
║       - getStatusLabel(status: string): string                            ║
║       - getSignalStrengthLabel(strength: string): string                 ║
║       - getDeliveryStateLabel(state: string): string                     ║
║       - NOTE: Decision logic like "isActionable" MUST NOT be in          ║
║         this file. Use decision.actionable directly.                     ║
║     - utils/gaps.ts:                                                      ║
║       - isUnsupported(feature: string): boolean                          ║
║       - getFeatureState(feature: string): "AVAILABLE" | "NOT_AVAILABLE"  ║
║       - CONTRACT_GAP_MAP: Record<string, string> referencing             ║
║         CONTRACT_GAPS.md                                                  ║
║     - utils/index.ts:                                                     ║
║       - Export all utilities                                              ║
║                                                                              ║
║  10. ERROR HANDLING:                                                       ║
║      - components/common/ErrorBoundary.tsx:                               ║
║        - Catches component-level errors                                   ║
║        - Displays fallback UI                                              ║
║      - components/common/LoadingSpinner.tsx:                              ║
║        - Loading state indicator                                           ║
║      - components/common/NotAvailable.tsx:                                ║
║        - Displays "Feature not available" state                           ║
║        - Reason: UNSUPPORTED_BY_CONTRACT                                  ║
║        - NO_FALLBACK_ALLOWED = true                                       ║
║        - NO_DERIVATION_ALLOWED = true                                     ║
║      - components/common/ApiError.tsx:                                    ║
║        - Displays API error state                                          ║
║        - Retry button                                                      ║
║      - components/common/index.ts:                                        ║
║        - Export all common components                                     ║
║                                                                              ║
║  11. APP LAYOUT (BASIC):                                                   ║
║      - App.tsx:                                                           ║
║        - Router configuration                                              ║
║        - QueryClientProvider                                               ║
║        - ThemeProvider                                                     ║
║      - components/layout/Sidebar.tsx:                                     ║
║        - Navigation items: Global, Forecast, Drivers, Evaluation, Status  ║
║        - Meridian FX logo                                                 ║
║        - Active route highlighting                                         ║
║      - components/layout/Header.tsx:                                      ║
║        - Page title                                                        ║
║        - System status indicator (from useStatus)                         ║
║        - Last updated timestamp                                            ║
║        - Refresh button                                                    ║
║      - components/layout/MainLayout.tsx:                                  ║
║        - Composes Sidebar + Header + Content                              ║
║        - Responsive: sidebar collapses on tablet                          ║
║                                                                              ║
║  12. PAGES (PLACEHOLDER STRUCTURE):                                        ║
║      - pages/GlobalPage.tsx:                                               ║
║        - Placeholder with "Global Intelligence" title                     ║
║      - pages/ForecastPage.tsx:                                             ║
║        - Placeholder with "Forecast Dashboard" title                       ║
║      - pages/DriversPage.tsx:                                              ║
║        - Placeholder with "Drivers & Explanation" title                   ║
║      - pages/EvaluationPage.tsx:                                           ║
║        - Placeholder with "Evaluation & Performance" title                ║
║      - pages/StatusPage.tsx:                                               ║
║        - Placeholder with "System Status" title                           ║
║      - pages/index.ts:                                                     ║
║        - Export all pages                                                  ║
║                                                                              ║
║  13. INFRASTRUCTURE TESTS:                                                 ║
║      - tests/utils/format.test.ts:                                         ║
║        - Formatting functions preserve values                              ║
║        - No null replacement                                               ║
║      - tests/utils/status.test.ts:                                         ║
║        - Status mapping is one-to-one                                      ║
║        - No logic inference                                                ║
║      - tests/utils/gaps.test.ts:                                           ║
║        - Unsupported features return NOT_AVAILABLE                         ║
║        - NO_FALLBACK_ALLOWED is true                                       ║
║        - NO_DERIVATION_ALLOWED is true                                     ║
║      - tests/services/forecast.test.ts:                                    ║
║        - Services do not transform responses                               ║
║        - Response === input                                                ║
║      - tests/hooks/useForecast.test.ts:                                    ║
║        - Hooks return responses unchanged                                  ║
║      - tests/contracts/validate.test.ts:                                   ║
║        - Contract types match Layer 1                                      ║
║        - No extra fields                                                   ║
║        - No missing required fields                                        ║
║      - tests/index.ts:                                                     ║
║        - Test runner configuration                                         ║
║                                                                              ║
║  14. README.md:                                                            ║
║      - Setup instructions                                                   ║
║      - Environment variables                                                ║
║      - Security note: Never commit real API keys                           ║
║      - Contract traceability reference                                      ║
║      - UNSUPPORTED_BY_CONTRACT features list                               ║
║      - Link to CONTRACT_GAPS.md                                             ║
║      - Note: All domain data comes from Layer 1 contracts                  ║
║      - Note: Frontend does not calculate, infer, or derive intelligence    ║
║                                                                              ║
║  CONSTRAINTS:                                                               ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  • DO NOT implement any analytical logic                                    ║
║  • DO NOT implement components beyond placeholder structure                 ║
║  • DO NOT implement data visualization components                          ║
║  • DO NOT implement module-specific logic                                   ║
║  • DO NOT invent contracts or fields                                       ║
║  • DO NOT derive missing values                                            ║
║  • DO NOT approximate missing data                                          ║
║  • DO NOT replace null values with defaults                                ║
║  • ALL domain types MUST come from Layer 1 contracts                       ║
║  • ALL UNSUPPORTED_BY_CONTRACT features must use NOT_AVAILABLE state      ║
║  • Use evidence from CONTRACT_TRACEABILITY.md                              ║
║  • Use gaps from CONTRACT_GAPS.md                                           ║
║  • position_size (supported) ≠ position_size_recommendation (unsupported)  ║
║  • NO_FALLBACK_ALLOWED = true for all gaps                                 ║
║  • NO_DERIVATION_ALLOWED = true for all gaps                               ║
║  • VITE_API_KEY is for development only — never commit production secrets  ║
║                                                                              ║
║  IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 2. CONTRACT BOUNDARY ENFORCEMENT — EXPLICIT RULES

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONTRACT BOUNDARY ENFORCEMENT — EXPLICIT RULES           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 1: Domain Types vs. Infrastructure Types                          │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  Domain types (ForecastResponse, etc.) MUST match Layer 1 exactly.     │ ║
║  │  Infrastructure types (ApiStatus, PollingConfig) MAY be defined        │ ║
║  │  by the frontend.                                                       │ ║
║  │  ApiResponse<T> is NOT defined unless backend explicitly returns       │ ║
║  │  an envelope. Use domain types directly.                               │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 2: No Analytical Logic                                            │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  No calculation, inference, ranking, scoring, classification,          │ ║
║  │  recommendation, estimation, derivation, or substitution.              │ ║
║  │  Use backend output directly.                                           │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 3: Position Size vs. Position Size Recommendation                │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  .decision.position_size → SUPPORTED → render as provided              │ ║
║  │  position_size_recommendation → UNSUPPORTED → NOT_AVAILABLE            │ ║
║  │  DO NOT derive recommendation from position_size.                      │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 4: No Actionability Logic                                        │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  DO NOT implement isActionable(). Use decision.actionable directly.   │ ║
║  │  The backend determines actionability.                                 │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 5: Status Utilities — Presentation Only                          │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  getStatusColor() and getStatusLabel() MUST only map existing          │ ║
║  │  backend status to presentation label/color.                           │ ║
║  │  They MUST NOT infer, calculate, or derive status.                     │ ║
║  │  ✅ "healthy" → "Healthy", color: green                                │ ║
║  │  ❌ prediction_coverage < 0.8 → "warning"                              │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 6: usePolling — Infrastructure Only                             │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  usePolling MAY control request/refetch timing only.                  │ ║
║  │  MUST NOT transform analytical data.                                  │ ║
║  │  MUST NOT calculate derived metrics.                                  │ ║
║  │  MUST NOT infer state.                                                │ ║
║  │  MUST NOT modify backend responses.                                   │ ║
║  │  MUST NOT implement business rules.                                   │ ║
║  │  MUST return the original resolved value without transformation.      │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 7: Unsupported Features — No Fallback, No Derivation            │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  CONTRACT_STATUS = UNSUPPORTED_BY_CONTRACT                             │ ║
║  │  FEATURE_STATE = NOT_AVAILABLE                                          │ ║
║  │  NO_FALLBACK_ALLOWED = TRUE                                            │ ║
║  │  NO_DERIVATION_ALLOWED = TRUE                                          │ ║
║  │  DO NOT use supported fields to satisfy unsupported fields.           │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 8: Null / Undefined Semantics                                    │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  MUST preserve backend nullability semantics.                          │ ║
║  │  MUST NOT replace null with 0, false, "", or default values.          │ ║
║  │  MUST NOT infer missing values from adjacent fields.                   │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 9: Security — No Secrets in Frontend                             │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  VITE_API_KEY MUST NOT contain a production secret.                    │ ║
║  │  Production authentication MUST use a secure architecture.             │ ║
║  │  Never commit real API keys to version control.                        │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  RULE 10: Prompt 1 — Validation, Not Redefinition                     │ ║
║  │  ────────────────────────────────────────────────────────────────────── │ ║
║  │  Prompt 1 AUDITS / VALIDATES the generated TypeScript contracts        │ ║
║  │  against Layer 1.                                                      │ ║
║  │  Prompt 1 MUST NOT redefine or invent contracts.                      │ ║
║  │  Prompt 1 MUST NOT modify contracts automatically.                    │ ║
║  │  Result: PASS → proceed, FAIL → report → human/backend decision       │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. PROMPT 0 — EXECUTION SUMMARY

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PROMPT 0 v1.2 — EXECUTION SUMMARY                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  ITEM                           │ STATUS                               │ ║
║  ├─────────────────────────────────┼──────────────────────────────────────┤ ║
║  │  Project structure              │ ✅ Defined (15 directories)          │ ║
║  │  Configuration                  │ ✅ Defined (.env, package.json)      │ ║
║  │  Design system                  │ ✅ Defined (dark theme, colors)      │ ║
║  │  Domain types                   │ ✅ Defined (5 contracts from L1)     │ ║
║  │  Infrastructure types           │ ✅ Defined (ApiStatus, etc.)         │ ║
║  │  Gap types                      │ ✅ Defined (UNSUPPORTED_BY_CONTRACT) │ ║
║  │  API client (transport)         │ ✅ Defined (axios base)              │ ║
║  │  Service methods                │ ✅ Defined (5 services)              │ ║
║  │  Hooks                          │ ✅ Defined (5 hooks)                 │ ║
║  │  Utilities                      │ ✅ Defined (formatting only)         │ ║
║  │  Error handling                 │ ✅ Defined (ErrorBoundary, states)   │ ║
║  │  App layout                     │ ✅ Defined (Sidebar, Header, Layout) │ ║
║  │  Pages                          │ ✅ Defined (5 placeholder pages)     │ ║
║  │  Infrastructure tests           │ ✅ Defined (5 test suites)           │ ║
║  │  README                         │ ✅ Defined                           │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  CONTRACT INTEGRITY:                                                         ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  ✅ All domain types from Layer 1 contracts                                  ║
║  ✅ Infrastructure types defined separately                                 ║
║  ✅ ApiResponse<T> not defined unless backend envelope exists               ║
║  ✅ All gaps marked UNSUPPORTED_BY_CONTRACT                                 ║
║  ✅ No analytical logic                                                     ║
║  ✅ No invented contracts                                                   ║
║  ✅ position_size ≠ position_size_recommendation                           ║
║  ✅ No isActionable() function                                              ║
║  ✅ Status utilities are presentation-only                                  ║
║  ✅ usePolling is infrastructure-only                                       ║
║  ✅ Null/undefined semantics preserved                                      ║
║  ✅ Security: VITE_API_KEY placeholder only                                 ║
║  ✅ Tests: infrastructure tests defined                                     ║
║  ✅ Evidence from CONTRACT_TRACEABILITY.md                                  ║
║  ✅ NO_FALLBACK_ALLOWED = true                                              ║
║  ✅ NO_DERIVATION_ALLOWED = true                                            ║
║                                                                              ║
║  PROMPT 0 EXECUTION READINESS: ✅ 10/10                                     ║
║                                                                              ║
║  MERIDIAN FX FRONTEND IMPLEMENTATION READINESS:                             ║
║  PENDING SUBSEQUENT PROMPTS (1-11)                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## ¿Qué sigue?

| Opción | Descripción |
|--------|------------|
| **A** | ✅ COMPLETADO — Prompt 0 v1.2 definido y congelado |
| **B** | Ejecutar **Prompt 1: TypeScript Contracts Validation (AUDIT ONLY)** |
| **C** | Ejecutar **Prompt 4: Common Components** |
| **D** | Ejecutar **Prompt 5-9: Módulos específicos** |

**¿Cuál prefieres?** 🚀