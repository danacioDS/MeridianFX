/**
 * Frontend configuration (infrastructure-only).
 * Values are read from Vite environment variables. VITE_API_KEY is a
 * development placeholder and MUST NEVER contain a production secret.
 */

export interface AppConfig {
  /** Base URL of the Layer 1 API. */
  apiBaseUrl: string;
  /** Development API key placeholder. Never a production secret. */
  apiKey: string;
  /** Default polling interval in milliseconds. */
  pollingInterval: number;
  /** Runtime environment label. */
  environment: string;
}

/** Loads the effective configuration from the environment. */
export function getConfig(): AppConfig {
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
    apiKey: import.meta.env.VITE_API_KEY ?? "",
    pollingInterval: Number(import.meta.env.VITE_POLLING_INTERVAL ?? 60000),
    environment: import.meta.env.VITE_ENVIRONMENT ?? "development",
  };
}