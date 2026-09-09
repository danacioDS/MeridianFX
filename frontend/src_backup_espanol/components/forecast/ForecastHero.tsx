/**
 * Forecast hero — presentational only.
 */
import type { ForecastResponse, PredictionInterval } from "../../types/contracts";
import {
  formatDirection,
  formatPercent,
  formatProbability,
  getDirectionArrow,
} from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface ForecastHeroProps {
  forecast: ForecastResponse | null;
  modelVersion?: string | null;
  horizon?: string | null;
}

export function ForecastHero({
  forecast,
  modelVersion,
  horizon,
}: ForecastHeroProps): JSX.Element {
  const prediction = forecast?.prediction;

  if (!prediction) {
    return (
      <NotAvailable
        feature="forecast"
        reason={
          forecast?.delivery_reason ??
          "UNSUPPORTED_BY_CONTRACT: prediction payload absent (delivery_state not ELIGIBLE)"
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-6">
      <div className="flex items-center gap-2">
        <span aria-hidden="true" className="text-xl">
          {getDirectionArrow(prediction.direction)}
        </span>
        <span className="text-2xl font-bold text-text-primary">
          {formatDirection(prediction.direction)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <Metric label="Probability">
          {formatProbability(prediction.probability)}
          <span className="ml-1 text-xs text-text-secondary">(calibrated)</span>
        </Metric>

        <Metric label="Model Version">{modelVersion ?? "—"}</Metric>

        <Metric label="Expected Return">{formatPercent(prediction.expected_return)}</Metric>

        <Metric label="Expected Volatility">
          {formatPercent(prediction.expected_volatility)}
        </Metric>

        <Metric label="95% Prediction Interval">
          <IntervalBounds interval={prediction.prediction_interval} />
        </Metric>

        <Metric label="Horizon">{horizon ?? "—"}</Metric>
      </div>
    </div>
  );
}

function Metric({ label, children }: { label: string; children: React.ReactNode }): JSX.Element {
  return (
    <div className="flex items-baseline justify-between gap-2">
      <dt className="text-xs text-text-secondary">{label}</dt>
      <dd className="text-sm font-medium text-text-primary">{children}</dd>
    </div>
  );
}

function IntervalBounds({ interval }: { interval: PredictionInterval | null | undefined }): JSX.Element {
  if (!interval || interval.lower === undefined || interval.upper === undefined) {
    return <span className="text-text-secondary">—</span>;
  }
  return (
    <span>
      {formatPercent(interval.lower)} to {formatPercent(interval.upper)}
    </span>
  );
}
