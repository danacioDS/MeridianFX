import { useActivePair, pairUniverseFromRanking } from "../hooks/useActivePair";
import { useInterpretation } from "../hooks/useInterpretation";
import { useForecastDashboard } from "../hooks/useForecastDashboard";
import { useRanking } from "../hooks/useRanking";
import { UniverseSelector } from "../components/common/UniverseSelector";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ApiError } from "../components/common/ApiError";
import { Panel } from "../components/common/Panel";

export function ForecastPage() {
  const { pair, setPair } = useActivePair();
  
  // Obtener ranking para el universo de pares
  const ranking = useRanking();
  const currencies = pairUniverseFromRanking(ranking.data);
  
  // Obtener interpretación
  const interpretation = useInterpretation(pair);
  
  // Obtener dashboard data
  const dashboard = useForecastDashboard(pair);

  // Manejar errores
  if (interpretation.isError) {
    return (
      <div className="container mx-auto p-6">
        <ApiError 
          message={interpretation.error?.message || "Error loading forecast"} 
          onRetry={() => interpretation.refetch()} 
        />
      </div>
    );
  }

  if (dashboard.isError) {
    return (
      <div className="container mx-auto p-6">
        <ApiError 
          message={dashboard.error?.message || "Error loading dashboard"} 
          onRetry={() => dashboard.refetch()} 
        />
      </div>
    );
  }

  // Cargando
  if (interpretation.isLoading || dashboard.isLoading || ranking.isLoading) {
    return (
      <div className="container mx-auto p-6">
        <LoadingSpinner />
      </div>
    );
  }

  // Datos
  const data = interpretation.data;
  const dashboardData = dashboard.data;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Selector de pares */}
      <UniverseSelector 
        currencies={currencies}
        selected={pair}
        onChange={setPair}
      />

      {/* Header */}
      <Panel title="Forecast Dashboard">
        <div className="p-4">
          <p className="text-gray-500">
            Predicciones para {pair}
          </p>
        </div>
      </Panel>

      {/* Interpretación */}
      {data && (
        <Panel title="Interpretación del Mercado">
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Dirección</p>
                <p className="text-xl font-bold text-green-600 dark:text-green-400">
                  {data.signal?.direction || "N/A"}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Probabilidad</p>
                <p className="text-xl font-bold">
                  {data.signal?.probability ? (data.signal.probability * 100).toFixed(1) + "%" : "N/A"}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Convicción</p>
                <p className="text-xl font-bold">
                  {data.signal?.strength || "N/A"}
                </p>
              </div>
            </div>
            {data.narrative && (
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm">{data.narrative}</p>
              </div>
            )}
          </div>
        </Panel>
      )}

      {/* Datos del Dashboard */}
      {dashboardData && (
        <Panel title="Datos del Mercado">
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Precio Spot</p>
                <p className="text-xl font-bold">
                  {dashboardData.spot?.price?.toFixed(4) || "N/A"}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Volatilidad</p>
                <p className="text-xl font-bold">
                  {dashboardData.volatility?.toFixed(2) || "N/A"}%
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Tendencia 1M</p>
                <p className="text-xl font-bold">
                  {dashboardData.trends?.["1m"]?.direction || "N/A"}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Tendencia 6M</p>
                <p className="text-xl font-bold">
                  {dashboardData.trends?.["6m"]?.direction || "N/A"}
                </p>
              </div>
            </div>
          </div>
        </Panel>
      )}

      {/* Forecasts */}
      {dashboardData?.forecasts && (
        <Panel title="Predicciones">
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(dashboardData.forecasts).map(([horizon, forecast]: [string, any]) => (
                <div key={horizon} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">{horizon}</p>
                  <p className="text-lg font-bold">
                    {forecast.direction || "N/A"}
                  </p>
                  <p className="text-sm">
                    Prob: {(forecast.probability * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-500">
                    Retorno esperado: {forecast.expected_return?.toFixed(2) || "N/A"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      )}
    </div>
  );
}

export default ForecastPage;
