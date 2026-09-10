import {
  formatDirection,
  formatProbability,
  getDirectionArrow,
  formatNumber,
} from "../../utils";
import { formatPercentRaw } from "./formatRaw";

export interface MarketHeroForecast {
  direction: string;
  probability: number;
  expected_return: number;
  volatility: number;
  ci_95_lower: number;
  ci_95_upper: number;
  model: {
    type: string;
    version: string;
  };
}

interface MarketHeroProps {
  forecast: MarketHeroForecast | null;
  horizon?: string;
}

export function MarketHero({
  forecast,
  horizon = "30d",
}: MarketHeroProps): JSX.Element {
  if (!forecast) {
    return (
      <div className="p-5 bg-panel-2 rounded-lg border border-line">
        <div className="text-sm text-muted">
          Forecast no disponible
        </div>
      </div>
    );
  }

  const arrow = getDirectionArrow(forecast.direction);
  const direction = formatDirection(forecast.direction);
  const probability = formatProbability(forecast.probability);
  const expectedReturn = formatPercentRaw(forecast.expected_return);
  const volatility = formatPercentRaw(forecast.volatility);

  const directionClass =
    forecast.direction.toUpperCase() === "UP"
      ? "text-bull"
      : forecast.direction.toUpperCase() === "DOWN"
        ? "text-bear"
        : "text-ink";

  return (
    <div className="p-5 bg-panel-2 rounded-lg border border-line space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wide text-muted">
            Forecast · {horizon}
          </div>

          <div className={`text-2xl font-bold mt-1 ${directionClass}`}>
            {arrow} {direction}
          </div>

          <div className="text-sm text-muted mt-1">
            Probability {probability}
          </div>
        </div>

        <div className="text-right">
          <div className="text-xs text-muted">Model</div>
          <div className="text-sm font-medium text-ink">
            {forecast.model.type} · {forecast.model.version}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div className="text-xs text-muted">Expected return</div>
          <div className="text-lg font-semibold text-ink">
            {expectedReturn}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">Volatility</div>
          <div className="text-lg font-semibold text-ink">
            {volatility}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">CI 95% lower</div>
          <div className="text-lg font-semibold text-ink">
            {formatNumber(forecast.ci_95_lower, 4)}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">CI 95% upper</div>
          <div className="text-lg font-semibold text-ink">
            {formatNumber(forecast.ci_95_upper, 4)}
          </div>
        </div>
      </div>
    </div>
  );
}
