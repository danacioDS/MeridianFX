/**
 * Base API client — transport layer only.
 *
 * Responsibilities:
 *  - Base URL and authentication headers (from config)
 *  - Timeout (30s) and error handling
 *  - Retry with exponential backoff (up to 3 retries)
 *
 * MUST NOT transform response payloads, rename backend fields, normalize domain
 * semantics, calculate values, or inject defaults into domain fields.
 * Endpoint methods are NOT implemented here (see services/*).
 */
import axios, { AxiosError } from "axios";
import { getConfig } from "../config";

declare module "axios" {
  export interface AxiosRequestConfig {
    /** Retry counter used by the exponential-backoff interceptor. */
    retryCount?: number;
  }
}

const config = getConfig();

/** Maximum number of retries before failing a request. */
export const MAX_RETRIES = 3;

/** Base delay for exponential backoff, in milliseconds. */
export const BASE_RETRY_DELAY_MS = 500;

/** Default request timeout, in milliseconds. */
export const REQUEST_TIMEOUT_MS = 30_000;

/** Whether a failed request is safe to retry (network error or server error). */
function isRetryable(error: AxiosError): boolean {
  if (!error.response) return true;
  const { status } = error.response;
  return status >= 500 || status === 429;
}

function wait(delayMs: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, delayMs);
  });
}

export const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
    ...(config.apiKey ? { authorization: `Bearer ${config.apiKey}` } : {}),
  },
});

apiClient.interceptors.response.use(undefined, async (error: AxiosError) => {
  const original = error.config;
  if (!original || !isRetryable(error)) return Promise.reject(error);

  const attemptCount = (original.retryCount ?? 0) + 1;
  if (attemptCount > MAX_RETRIES) return Promise.reject(error);

  original.retryCount = attemptCount;
  const delayMs = BASE_RETRY_DELAY_MS * 2 ** (attemptCount - 1);
  await wait(delayMs);
  return apiClient(original);
});