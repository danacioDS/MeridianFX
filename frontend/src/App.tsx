import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MainLayout } from "./components/layout/MainLayout";
import { GlobalPage } from "./pages/GlobalPage";
import { ForecastPage } from "./pages/ForecastPage";
import { DriversPage } from "./pages/DriversPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { StatusPage } from "./pages/StatusPage";
import { AboutPage } from "./pages/AboutPage";
import { PricePage } from "./pages/PricePage";

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
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<GlobalPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/drivers" element={<DriversPage />} />
            <Route path="/evaluation" element={<EvaluationPage />} />
            <Route path="/status" element={<StatusPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/price" element={<PricePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
