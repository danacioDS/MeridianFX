import { useActivePair } from "../hooks/useActivePair";
import { useCanonicalDecision } from "../hooks/useCanonicalDecision";
import { useInterpretation } from "../hooks/useInterpretation";
import { useForecastDashboard } from "../hooks/useForecastDashboard";
import { UniverseSelector } from "../components/common/UniverseSelector";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ApiError } from "../components/common/ApiError";
import { Panel } from "../components/common/Panel";
import { StatusBadge } from "../components/common/StatusBadge";

export function ForecastPageCanonical() {
  const { pair, setPair } = useActivePair();
  
  
  // Datos legacy (para comparación)
  const interpretation = useInterpretation(pair);
  const dashboard = useForecastDashboard(pair);
  
  // Datos canónicos (nuevos)
  const canonical = useCanonicalDecision(pair, 30);

  // Manejar errores
  if (canonical.isError) {
    return (
      <div className="container mx-auto p-6">
        <ApiError 
          message={canonical.error?.message || "Error loading canonical decision"} 
          onRetry={() => canonical.refetch()} 
        />
      </div>
    );
  }

  if (interpretation.isError) {
    return (
      <div className="container mx-auto p-6">
        <ApiError 
          message={interpretation.error?.message || "Error loading interpretation"} 
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
  if (canonical.isLoading || interpretation.isLoading || dashboard.isLoading) {
    return (
      <div className="container mx-auto p-6">
        <LoadingSpinner />
      </div>
    );
  }

  const canonicalData = canonical.data;
  const data = interpretation.data;
  const dashboardData = dashboard.data;

  // Extraer datos de la respuesta canónica
  const macroScore = canonicalData?.signals?.macro_score?.value ?? 0;
  const quantScore = canonicalData?.signals?.quant_score?.value ?? 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Selector de pares */}
      <UniverseSelector selected={pair} onChange={setPair} />

      {/* Header */}
      <Panel title="Forecast Dashboard (Canonical API)">
        <div className="p-4">
          <p className="text-gray-500">
            Predicciones para {pair} — usando el pipeline canónico
          </p>
          {canonicalData && (
            <div className="mt-2 flex items-center gap-4 text-sm">
              <span>Régimen: <strong>{canonicalData.regime}</strong></span>
              <span>Macro Score: <strong>{macroScore.toFixed(4)}</strong></span>
              <span>Quant Score: <strong>{quantScore.toFixed(4)}</strong></span>
              <StatusBadge status={canonicalData.macro_data_status?.status || "UNKNOWN"} />
            </div>
          )}
        </div>
      </Panel>

      {/* Trazabilidad Macro */}
      {canonicalData?.macro_data_status && (
        <Panel title="📊 Estado de Datos Macro">
          <div className="p-4 space-y-2 text-sm">
            <div className="flex items-center gap-4">
              <span>Base: <strong>{canonicalData.macro_data_status.base}</strong></span>
              <span>{canonicalData.macro_data_status.base_available ? '✅ Disponible' : '❌ No disponible'}</span>
              <span className="mx-2">|</span>
              <span>Quote: <strong>{canonicalData.macro_data_status.quote}</strong></span>
              <span>{canonicalData.macro_data_status.quote_available ? '✅ Disponible' : '❌ No disponible'}</span>
            </div>
            {canonicalData.macro_data_status.reason && (
              <div className="text-yellow-600 text-xs bg-yellow-50 p-2 rounded">
                {canonicalData.macro_data_status.reason}
              </div>
            )}
            <div className="flex gap-4 text-xs text-gray-500">
              <span>Policy: {canonicalData.macro_data_status.policy_differential}</span>
              <span>Growth: {canonicalData.macro_data_status.growth_differential}</span>
              <span>Rate: {canonicalData.macro_data_status.base_rate}</span>
            </div>
          </div>
        </Panel>
      )}

      {/* Régimen Macro Canónico */}
      {canonicalData?.artifact?.macro_regime && (
        <Panel title="🏛️ Régimen Macro (Canónico)">
          <div className="p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-500">Risk</p>
                <p className="font-medium">{canonicalData.artifact.macro_regime.risk}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-500">Policy</p>
                <p className="font-medium">{canonicalData.artifact.macro_regime.policy}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-500">Growth</p>
                <p className="font-medium">{canonicalData.artifact.macro_regime.growth}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-500">Inflation</p>
                <p className="font-medium">{canonicalData.artifact.macro_regime.inflation}</p>
              </div>
            </div>
          </div>
        </Panel>
      )}

      {/* Decisión Canónica */}
      {canonicalData?.decision && (
        <Panel title="🎯 Decisión (Canónica)">
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Dirección</p>
                <p className={`text-xl font-bold ${
                  canonicalData.decision.direction === 'LONG' ? 'text-green-600' :
                  canonicalData.decision.direction === 'SHORT' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
                  {canonicalData.decision.direction}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Confianza</p>
                <p className="text-xl font-bold">
                  {(canonicalData.decision.confidence * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Edge Ratio</p>
                <p className="text-xl font-bold">
                  {canonicalData.decision.edge_ratio?.toFixed(2) || "N/A"}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Accionable</p>
                <p className={`text-xl font-bold ${canonicalData.decision.actionable ? 'text-green-600' : 'text-gray-400'}`}>
                  {canonicalData.decision.actionable ? '✅ Sí' : '❌ No'}
                </p>
                {canonicalData.decision.rejection_reason && (
                  <p className="text-xs text-gray-500 mt-1">{canonicalData.decision.rejection_reason}</p>
                )}
              </div>
            </div>
          </div>
        </Panel>
      )}

      {/* SHAP Values */}
      {canonicalData?.artifact?.shap_values && canonicalData.artifact.shap_values.length > 0 && (
        <Panel title="🔍 Drivers (SHAP)">
          <div className="p-4">
            <div className="space-y-1">
              {canonicalData.artifact.shap_values.slice(0, 5).map((sv, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <span className="w-24 text-gray-500">{sv.feature}</span>
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${Math.min(Math.abs(sv.value) * 100, 100)}%` }}
                    />
                  </div>
                  <span className="w-16 text-right font-mono text-xs">
                    {sv.value > 0 ? '+' : ''}{sv.value.toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      )}

      {/* Datos Legacy para comparación */}
      {data && (
        <Panel title="📋 Interpretación (Legacy)">
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Dirección</p>
                <p className="text-xl font-bold">
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
          </div>
        </Panel>
      )}

      {/* Dashboard Legacy */}
      {dashboardData && (
        <Panel title="📈 Datos del Mercado (Legacy)">
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
    </div>
  );
}

export default ForecastPageCanonical;
