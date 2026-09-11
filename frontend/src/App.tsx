import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MainLayout } from "./components/layout/MainLayout";
import { GlobalPage } from "./pages/GlobalPage";
import { MarketPage } from "./pages/MarketPage";
import { MacroPage } from "./pages/MacroPage";
import { AboutPage } from "./pages/AboutPage";
import { RiskPage } from "./pages/RiskPage";
import { DecisionPage } from "./pages/DecisionPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,      // 5 min — no refetch si <5min
      gcTime: 10 * 60 * 1000,         // 10 min — mantener en memoria
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route element={<MainLayout />}>
            {/* ─── v2.4 canonical navigation ─── */}
            <Route path="/"         element={<GlobalPage />} />
            <Route path="/market"   element={<MarketPage />} />
            <Route path="/macro"    element={<MacroPage />} />
            <Route path="/risk"     element={<RiskPage />} />
            <Route path="/decision" element={<DecisionPage />} />
            <Route path="/about"    element={<AboutPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
