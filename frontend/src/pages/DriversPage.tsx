import { safeToFixed } from "../utils/safeFormat";
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import {
  useCanonicalDecision,
  useRanking,
  useActivePair,
  pairUniverseFromRanking,
} from "../hooks";

export function DriversPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const canonical = useCanonicalDecision(pair, 30);
  const universe = pairUniverseFromRanking(ranking.data);

  if (canonical.isLoading) {
    return <LoadingSpinner label={`Cargando drivers para ${pair}...`} />;
  }

  if (canonical.isError) {
    return (
      <ApiError
        message={canonical.error?.message}
        onRetry={() => void canonical.refetch()}
      />
    );
  }

  const data = canonical.data;

  if (!data) {
    return (
      <div className="text-center text-muted py-8">
        No hay datos canónicos disponibles
      </div>
    );
  }

  const shapValues = [...(data.artifact?.shap_values ?? [])]
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 10);

  const macroRegime = data.artifact?.macro_regime;

  const quantScore = data.signals?.quant_score?.value ?? 0;
  const macroScore = data.signals?.macro_score?.value ?? 0;
  const ragScore = data.signals?.rag_score?.value ?? 0;

  const probabilityUp = data.artifact?.probability_up ?? 0.5;
  const confidence = data.decision?.confidence ?? 0;

  const macroStatus = data.macro_data_status;

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">
          {pair} · Drivers & Explicación
        </h2>

        <UniverseSelector
          currencies={universe}
          selected={pair}
          onChange={setPair}
        />
      </div>

      <RegimeStrip
        regime={data.regime || "UNKNOWN"}
        vix={15.0}
        riskAppetite={0.5}
      />

      {/* Signal summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Panel title="Quant Score">
          <div className="text-2xl font-semibold text-ink font-mono">
            {safeToFixed(quantScore, 4)}
          </div>
        </Panel>

        <Panel title="Macro Score">
          <div className="text-2xl font-semibold text-ink font-mono">
            {safeToFixed(macroScore, 4)}
          </div>
        </Panel>

        <Panel title="RAG Score">
          <div className="text-2xl font-semibold text-ink font-mono">
            {safeToFixed(ragScore, 4)}
          </div>
        </Panel>

        <Panel title="Probability Up">
          <div className="text-2xl font-semibold text-ink font-mono">
            {safeToFixed(probabilityUp * 100, 2)}%
          </div>
        </Panel>
      </div>

      {/* SHAP Values */}
      <Panel title="📊 Factores clave — SHAP">
        {shapValues.length > 0 ? (
          <div className="space-y-4">
            {shapValues.map((feature, index) => {
              const isPositive = feature.value > 0;
              const absValue = Math.abs(feature.value);

              const maxAbs =
                Math.max(...shapValues.map((item) => Math.abs(item.value)), 1);

              const percentage = Math.min(
                (absValue / maxAbs) * 100,
                100
              );

              return (
                <div key={`${feature.feature}-${index}`} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-ink">
                      #{index + 1} {feature.feature}
                    </span>

                    <span
                      className={`font-mono ${
                        isPositive ? "text-bull" : "text-bear"
                      }`}
                    >
                      {isPositive ? "▲" : "▼"}{" "}
                      {safeToFixed(feature.value, 4)}
                    </span>
                  </div>

                  <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        isPositive ? "bg-bull" : "bg-bear"
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>

                  <div className="text-xs text-muted">
                    Contribución SHAP: {safeToFixed(feature.value, 4)}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-sm text-muted">
            No hay valores SHAP disponibles para este modelo.
          </div>
        )}
      </Panel>

      {/* Decision */}
      <Panel title="🎯 Decisión Canónica">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-muted">Dirección</div>
            <div className="font-semibold text-ink">
              {data.decision?.direction || "NEUTRAL"}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted">Confianza</div>
            <div className="font-semibold text-ink font-mono">
              {safeToFixed(confidence * 100, 2)}%
            </div>
          </div>

          <div>
            <div className="text-xs text-muted">Edge Ratio</div>
            <div className="font-semibold text-ink font-mono">
              {safeToFixed(data.decision?.edge_ratio, 4)}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted">Accionable</div>
            <div className="font-semibold text-ink">
              {data.decision?.actionable ? "YES" : "NO"}
            </div>
          </div>
        </div>

        {!data.decision?.actionable && data.decision?.rejection_reason && (
          <div className="mt-4 text-sm text-amber">
            Rechazo: {data.decision.rejection_reason}
          </div>
        )}
      </Panel>

      {/* Macro regime */}
      <Panel title="🌍 Régimen Macro">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between border-b border-line pb-1">
              <span className="text-muted">Riesgo</span>
              <span className="font-semibold">
                {macroRegime?.risk || "—"}
              </span>
            </div>

            <div className="flex justify-between border-b border-line pb-1">
              <span className="text-muted">Política</span>
              <span className="font-semibold">
                {macroRegime?.policy || "—"}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between border-b border-line pb-1">
              <span className="text-muted">Crecimiento</span>
              <span className="font-semibold">
                {macroRegime?.growth || "—"}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-muted">Inflación</span>
              <span className="font-semibold">
                {macroRegime?.inflation || "—"}
              </span>
            </div>
          </div>
        </div>
      </Panel>

      {/* Macro data availability */}
      <Panel title="📡 Disponibilidad de datos macro">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-muted">Estado</div>
            <div className="font-semibold text-ink">
              {macroStatus?.status || "—"}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted">Base</div>
            <div className="font-semibold text-ink">
              {macroStatus?.base || "—"} ·{" "}
              {macroStatus?.base_available ? "AVAILABLE" : "UNAVAILABLE"}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted">Quote</div>
            <div className="font-semibold text-ink">
              {macroStatus?.quote || "—"} ·{" "}
              {macroStatus?.quote_available ? "AVAILABLE" : "UNAVAILABLE"}
            </div>
          </div>
        </div>

        {macroStatus?.reason && (
          <div className="mt-4 text-xs text-muted">
            {macroStatus.reason}
          </div>
        )}
      </Panel>
    </section>
  );
}
