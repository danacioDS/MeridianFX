/**
 * Test entry / runner configuration.
 *
 * Loads jest-dom matchers for all suites. The test timezone (TZ=UTC) is pinned
 * in vitest.config.ts so datetime formatting assertions are deterministic.
 */
import "@testing-library/jest-dom/vitest";