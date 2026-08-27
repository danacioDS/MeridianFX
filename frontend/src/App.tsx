/**
 * Application root.
 *
 * Wires routing, QueryClientProvider, and ThemeProvider around the layout.
 * No analytical logic lives here — modules consume backend contracts verbatim.
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "./components/common";
import { MainLayout } from "./components/layout";
import {
  DriversPage,
  EvaluationPage,
  ForecastPage,
  GlobalPage,
  StatusPage,
} from "./pages";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});

export default function App(): JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<MainLayout />}>
              <Route path="/" element={<GlobalPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/drivers" element={<DriversPage />} />
              <Route path="/evaluation" element={<EvaluationPage />} />
              <Route path="/status" element={<StatusPage />} />
              <Route path="*" element={<GlobalPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}