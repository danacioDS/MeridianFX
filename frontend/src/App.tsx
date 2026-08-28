import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './components/layout/MainLayout';
import { GlobalPage, ForecastPage, DriversPage, EvaluationPage, StatusPage, HistoricalPage } from './pages';

// Crear QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 segundos
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<GlobalPage />} />
            <Route path="forecast" element={<ForecastPage />} />
            <Route path="drivers" element={<DriversPage />} />
            <Route path="evaluation" element={<EvaluationPage />} />
            <Route path="status" element={<StatusPage />} />
            <Route path="historical" element={<HistoricalPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
