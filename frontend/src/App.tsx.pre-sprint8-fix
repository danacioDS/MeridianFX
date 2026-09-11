import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MainLayout } from "./components/layout/MainLayout";
import { GlobalPage } from "./pages/GlobalPage";
import { MarketPage } from "./pages/MarketPage";
import { MacroPage } from "./pages/MacroPage";
import { ForecastPageCanonical } from "./pages/ForecastPageCanonical";
import { DriversPage } from "./pages/DriversPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { StatusPage } from "./pages/StatusPage";
import { AboutPage } from "./pages/AboutPage";
import { RiskPage } from "./pages/RiskPage";
import { DecisionPage } from "./pages/DecisionPage";
import { PricePage } from "./pages/PricePage";
import { ModelComparisonPage } from "./pages/ModelComparisonPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
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

            {/* ─── Legacy — accessible by URL, removed from menu ─── */}
            <Route path="/forecast"   element={<ForecastPageCanonical />} />
            <Route path="/drivers"    element={<DriversPage />} />
            <Route path="/evaluation" element={<EvaluationPage />} />
            <Route path="/status"     element={<StatusPage />} />
            <Route path="/price"      element={<PricePage />} />
            <Route path="/models"     element={<ModelComparisonPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
