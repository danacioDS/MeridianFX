/**
 * Currency Universe - Orden fijo para MeridianFX
 * 
 * Market convention: 
 * - Base currency / Quote currency
 * - EUR/USD → 1 EUR = X USD
 * - GBP/USD → 1 GBP = X USD
 * - USD/JPY → 1 USD = X JPY
 * - USD/CNY → 1 USD = X CNY
 * - USD/MXN → 1 USD = X MXN
 * - USD/BRL → 1 USD = X BRL
 * - USD/ARS → 1 USD = X ARS
 * - USD/BOB → 1 USD = X BOB
 * - USD/CHF → 1 USD = X CHF
 */

export const FX_PAIRS = [
  "EUR/USD",
  "GBP/USD",
  "USD/JPY",
  "USD/CNY",
  "USD/MXN",
  "USD/BRL",
  "USD/ARS",
  "USD/BOB",
  "USD/CHF"
] as const;

export type FXPair = typeof FX_PAIRS[number];

export const FX_MARKET_CONVENTION = {
  title: "Market convention",
  text: "FX pairs are displayed using standard market quotation conventions. The first currency is the base currency and the second is the quote currency."
} as const;

export const FX_PAIR_LABELS: Record<FXPair, { base: string; quote: string; description: string }> = {
  "EUR/USD": { base: "EUR", quote: "USD", description: "Euro / US Dollar" },
  "GBP/USD": { base: "GBP", quote: "USD", description: "British Pound / US Dollar" },
  "USD/JPY": { base: "USD", quote: "JPY", description: "US Dollar / Japanese Yen" },
  "USD/CNY": { base: "USD", quote: "CNY", description: "US Dollar / Chinese Yuan" },
  "USD/MXN": { base: "USD", quote: "MXN", description: "US Dollar / Mexican Peso" },
  "USD/BRL": { base: "USD", quote: "BRL", description: "US Dollar / Brazilian Real" },
  "USD/ARS": { base: "USD", quote: "ARS", description: "US Dollar / Argentine Peso" },
  "USD/BOB": { base: "USD", quote: "BOB", description: "US Dollar / Bolivian Boliviano" },
  "USD/CHF": { base: "USD", quote: "CHF", description: "US Dollar / Swiss Franc" }
};

export const DEFAULT_PAIR = "USD/CNY" as const;
