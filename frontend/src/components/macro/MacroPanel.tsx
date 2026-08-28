/**
 * Macro Panel — Muestra el contexto macro en el Dashboard
 */
import { Panel } from "../common";

interface MacroPanelProps {
  macro: {
    summary?: {
      fed_funds?: number;
      inflation?: number;
      unemployment?: number;
      gdp_growth?: number;
      yield_10y?: number;
      yield_2y?: number;
      yield_spread?: number;
      consumer_sentiment?: number;
    };
    indicators?: {
      monetary_stance?: string;
      growth_signal?: string;
      inflation_signal?: string;
    };
    fx_relevance?: string;
    source?: string;
    timestamp?: string;
  };
  isLoading?: boolean;
}

export function MacroPanel({ macro, isLoading }: MacroPanelProps): JSX.Element {
  if (isLoading) {
    return (
      <Panel title="📊 Macro Context">
        <div className="text-center text-muted py-4">Cargando datos macro...</div>
      </Panel>
    );
  }

  if (!macro || !macro.summary) {
    return (
      <Panel title="📊 Macro Context">
        <div className="text-center text-muted py-4">No hay datos macro disponibles</div>
      </Panel>
    );
  }

  const { summary, indicators, fx_relevance, source, timestamp } = macro;

  return (
    <Panel title={`📊 Macro Context ${fx_relevance === 'HIGH' ? '· 🔥 Alta relevancia FX' : ''}`}>
      <div className="space-y-3">
        {/* Grid de indicadores macro */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {summary.fed_funds !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">Fed Funds</div>
              <div className="text-sm font-mono font-semibold">{summary.fed_funds.toFixed(2)}%</div>
            </div>
          )}
          {summary.inflation !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">Inflación</div>
              <div className="text-sm font-mono font-semibold">{summary.inflation.toFixed(1)}%</div>
            </div>
          )}
          {summary.unemployment !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">Desempleo</div>
              <div className="text-sm font-mono font-semibold">{summary.unemployment.toFixed(1)}%</div>
            </div>
          )}
          {summary.gdp_growth !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">PIB</div>
              <div className={`text-sm font-mono font-semibold ${summary.gdp_growth > 0 ? 'text-bull' : 'text-bear'}`}>
                {summary.gdp_growth > 0 ? '+' : ''}{summary.gdp_growth.toFixed(1)}%
              </div>
            </div>
          )}
          {summary.yield_10y !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">US 10Y</div>
              <div className="text-sm font-mono font-semibold">{summary.yield_10y.toFixed(2)}%</div>
            </div>
          )}
          {summary.yield_2y !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">US 2Y</div>
              <div className="text-sm font-mono font-semibold">{summary.yield_2y.toFixed(2)}%</div>
            </div>
          )}
          {summary.yield_spread !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">Spread 10-2</div>
              <div className={`text-sm font-mono font-semibold ${summary.yield_spread > 0 ? 'text-bull' : 'text-bear'}`}>
                {summary.yield_spread.toFixed(2)}%
              </div>
            </div>
          )}
          {summary.consumer_sentiment !== undefined && (
            <div className="bg-panel-2 rounded-lg p-2 text-center">
              <div className="text-xs text-muted">Confianza</div>
              <div className="text-sm font-mono font-semibold">{summary.consumer_sentiment.toFixed(0)}</div>
            </div>
          )}
        </div>

        {/* Indicadores de política */}
        {indicators && (
          <div className="flex flex-wrap gap-2 text-xs">
            {indicators.monetary_stance && (
              <span className={`px-2 py-1 rounded-full ${
                indicators.monetary_stance === 'RESTRICTIVE' ? 'bg-bear-soft text-bear' :
                indicators.monetary_stance === 'ACCOMMODATIVE' ? 'bg-bull-soft text-bull' :
                'bg-panel-2 text-muted'
              }`}>
                Política: {indicators.monetary_stance}
              </span>
            )}
            {indicators.growth_signal && (
              <span className={`px-2 py-1 rounded-full ${
                indicators.growth_signal === 'STRONG' ? 'bg-bull-soft text-bull' :
                indicators.growth_signal === 'WEAK' ? 'bg-bear-soft text-bear' :
                'bg-panel-2 text-muted'
              }`}>
                Crecimiento: {indicators.growth_signal}
              </span>
            )}
            {indicators.inflation_signal && (
              <span className={`px-2 py-1 rounded-full ${
                indicators.inflation_signal === 'HIGH' ? 'bg-bear-soft text-bear' :
                indicators.inflation_signal === 'LOW' ? 'bg-bull-soft text-bull' :
                'bg-panel-2 text-muted'
              }`}>
                Inflación: {indicators.inflation_signal}
              </span>
            )}
          </div>
        )}

        {/* Fuente y timestamp */}
        <div className="text-xs text-muted border-t border-line pt-2 flex justify-between">
          <span>Fuente: {source || 'FRED'}</span>
          <span className="font-mono">{timestamp ? new Date(timestamp).toLocaleTimeString() : '—'}</span>
        </div>
      </div>
    </Panel>
  );
}
