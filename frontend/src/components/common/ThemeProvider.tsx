/**
 * Theme provider (infrastructure).
 *
 * Applies the Meridian FX dark design system as the baseline. This is
 * infrastructure only: it controls presentation, never domain semantics.
 */
import { createContext, useEffect, type ReactNode } from "react";

const ThemeContext = createContext<"dark">("dark");

interface ThemeProviderProps {
  /** Application tree. */
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps): JSX.Element {
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  return <ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>;
}