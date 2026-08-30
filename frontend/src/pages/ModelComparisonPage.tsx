/**
 * Model Comparison Page — Compara XGBoost, Logistic y Ensemble.
 */
import { useActivePair } from "../hooks/useActivePair";
import { useModelComparison, ModelMetrics } from "../hooks/useModelComparison";
import { Panel } from "../components/common/Panel";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ApiError } from "../components/common/ApiError";
import { UniverseSelector } from "../components/common/UniverseSelector";
import { useRanking, pairUniverseFromRanking } from "../hooks";

const MODEL_NAMES: Record<string, string> = {
  xgboost: "XGBoost",
  logistic: "Logistic Regression",
  ensemble: "Ensemble (XGB + Logistic)",
};

const MODEL_COLORS: Record<string, string> = {
  xgboost: "#00D4AA",
  logistic: "#4A9EFF",
  ensemble: "#F5A623",
};

export function ModelComparisonPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const { data, isLoading, error, refetch } = useModelComparison(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  if (isLoading) return <LoadingSpinner label={`Cargando comparación para ${pair}...`} />;
  if (error) return <ApiError message={error.message} onRetry={() => refetch()} />;
  if (!data) return <div>No hay datos disponibles</div>;

  const { results, best_model, initial_train_years } = data;

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">
          {pair} · Model Comparison
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {/* Tabla de comparación */}
      <Panel title="📊 Model Performance Comparison">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line">
                <th className="text-left py-2 px-3 text-muted">Model</th>
                <th className="text-right py-2 px-3 text-muted">Sharpe</th>
                <th className="text-right py-2 px-3 text-muted">Profit Factor</th>
                <th className="text-right py-2 px-3 text-muted">DA</th>
                <th className="text-right py-2 px-3 text-muted">AUC</th>
                <th className="text-right py-2 px-3 text-muted">Net Return</th>
                <th className="text-right py-2 px-3 text-muted">Windows</th>
                <th className="text-right py-2 px-3 text-muted">Status</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(results).map(([key, metrics]) => {
                const isBest = key === best_model;
                const color = MODEL_COLORS[key] || "#8A8A9A";
                const name = MODEL_NAMES[key] || key;
                const m = metrics as ModelMetrics;
                const passGate = m.sharpe > 0.3 && m.profit_factor > 1.2;
                
                return (
                  <tr 
                    key={key} 
                    className={`border-b border-line/50 ${isBest ? 'bg-primary/5' : ''}`}
                  >
                    <td className="py-2 px-3 font-medium">
                      <span className="flex items-center gap-2">
                        <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                        {name}
                        {isBest && <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">★ Best</span>}
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      <span className={m.sharpe > 0.3 ? 'text-bull' : 'text-bear'}>
                        {m.sharpe.toFixed(3)}
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      <span className={m.profit_factor > 1.2 ? 'text-bull' : 'text-bear'}>
                        {m.profit_factor.toFixed(3)}
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      {(m.da * 100).toFixed(1)}%
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      {m.auc.toFixed(3)}
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      <span className={m.net_return > 0 ? 'text-bull' : 'text-bear'}>
                        {(m.net_return * 100).toFixed(2)}%
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 font-mono">
                      {m.n_windows}
                    </td>
                    <td className="text-right py-2 px-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${passGate ? 'bg-bull/20 text-bull' : 'bg-bear/20 text-bear'}`}>
                        {passGate ? '✅ PASS' : '❌ FAIL'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        <div className="mt-4 text-xs text-muted border-t border-line pt-3">
          <p>Evaluación walk-forward con {initial_train_years} años de entrenamiento inicial.</p>
          <p>El modelo con mejor Sharpe es seleccionado como <strong>Best</strong>.</p>
        </div>
      </Panel>

      {/* Resumen */}
      <Panel title="🎯 Research Gate Decision">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted">Best Model:</span>
            <span className="text-lg font-bold text-primary">
              {best_model ? MODEL_NAMES[best_model] || best_model : 'N/A'}
            </span>
            {best_model && results[best_model] && results[best_model].sharpe > 0.3 && 
             results[best_model].profit_factor > 1.2 && (
              <span className="px-3 py-1 bg-bull/20 text-bull rounded-full text-sm font-medium">
                ✅ APPROVED
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-muted">Best Sharpe</div>
              <div className="font-mono text-sm">
                {best_model && results[best_model] ? results[best_model].sharpe.toFixed(3) : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Best PF</div>
              <div className="font-mono text-sm">
                {best_model && results[best_model] ? results[best_model].profit_factor.toFixed(3) : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Best DA</div>
              <div className="font-mono text-sm">
                {best_model && results[best_model] ? ((results[best_model].da) * 100).toFixed(1) + '%' : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Windows</div>
              <div className="font-mono text-sm">
                {best_model && results[best_model] ? results[best_model].n_windows : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </Panel>
    </section>
  );
}
