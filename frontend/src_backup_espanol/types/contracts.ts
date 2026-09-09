/**
 * Domain contracts — Layer 1 v5.1, Section 7 "Response Structures".
 *
 * Source of truth (frozen): docs/Product_specification/Layer_01.md
 * These types are transported verbatim from the backend. The frontend MUST NOT
 * transform, rename, normalize, or inject defaults into any field below.
 *
 * Nullability is contractual: `null` is preserved and never coerced.
 */

/* ───────────────────────── 7.1 ForecastResponse ───────────────────────── */

/** Direction of the forecast prediction. Layer 1 v5.1 §7.1. */
export type ForecastDirection = "BULLISH" | "BEARISH" | "NEUTRAL";

/** Direction of the trading decision. Layer 1 v5.1 §7.1, §7.3. */
export type DecisionDirection = "LONG" | "SHORT" | "NEUTRAL";

/** Delivery policy verdict. Layer 1 v5.1 §5 (R1) / §7.1. */
export type DeliveryState = "ELIGIBLE" | "NOT_ELIGIBLE" | "UNAVAILABLE";

/** Signal strength as classified by the backend. Layer 1 v5.1 §7.1. */
export type SignalStrength = "weak" | "moderate" | "strong";

/** Prediction interval bounds. Layer 1 v5.1 §7.1. */
export interface PredictionInterval {
  /** Lower bound of the interval. */
  lower: number;
  /** Upper bound of the interval. */
  upper: number;
}

/** Prediction payload — present only when delivery_state is ELIGIBLE. Layer 1 v5.1 §7.1. */
export interface Prediction {
  /** Direction of the predicted move (BULLISH | BEARISH | NEUTRAL). */
  direction: ForecastDirection;
  /** Calibrated probability of the prediction. */
  probability: number;
  /** Expected return of the prediction. */
  expected_return: number;
  /** Expected volatility of the predicted move. */
  expected_volatility: number;
  /** Lower/upper bounds of the prediction interval. */
  prediction_interval: PredictionInterval;
}

/** Decision payload produced by Layer 2 — present only when ELIGIBLE. Layer 1 v5.1 §7.1. */
export interface Decision {
  /** Backend-determined actionability. MUST be consumed directly. */
  actionable: boolean;
  /** Decision direction (LONG | SHORT | NEUTRAL). */
  direction: DecisionDirection;
  /** Decision confidence. */
  confidence: number;
  /** Signal strength (weak | moderate | strong). */
  signal_strength: SignalStrength;
  /** Edge ratio of the decision. */
  edge_ratio: number;
  /** Net expected return of the decision. */
  net_return: number;
  /**
   * Position size. SUPPORTED field.
   * Distinct from `position_size_recommendation` (UNSUPPORTED_BY_CONTRACT — see gaps).
   */
  position_size: number;
}

/**
 * Latest forecast for a currency pair, plus delivery state. Layer 1 v5.1 §7.1.
 * `prediction`, `decision`, `data_quality`, `drivers`, and `lineage` are `null`
 * when the artifact is absent — preserve nullability.
 */
export interface ForecastResponse {
  /** Unique prediction identifier. */
  prediction_id: string;
  /** Currency pair this forecast applies to. */
  pair: string;
  /** Timestamp of the forecast response. */
  timestamp: string;
  /** Point-in-time the underlying data was valid as of. */
  as_of: string;
  /** Delivery policy verdict (ELIGIBLE | NOT_ELIGIBLE | UNAVAILABLE). */
  delivery_state: DeliveryState;
  /** Human-readable delivery reason from the backend. */
  delivery_reason: string;
  /** Optional delivery warning — null when absent. */
  delivery_warning: string | null;
  /** Prediction payload — null when not ELIGIBLE / unavailable. */
  prediction: Prediction | null;
  /** Decision payload — null when not ELIGIBLE / unavailable. */
  decision: Decision | null;
  /** Consumed data quality (Layer 4) — null when unavailable. */
  data_quality: DataQuality | null;
  /** Driver explanation — null when unavailable. */
  drivers: DriversResponse | null;
  /** Prediction lineage — null when unavailable. */
  lineage: PredictionLineage | null;
}

/* ───────────────────────── 7.2 DriversResponse ─────────────────────────── */

/** SHAP feature contribution. Layer 1 v5.1 §7.2. */
export interface ShapContribution {
  /** Feature name. */
  feature: string;
  /** SHAP contribution value (produced by Layer 3). */
  contribution: number;
  /** Rank of the contribution. */
  rank: number;
}

/** Macro risk regime (Layer 3). Layer 1 v5.1 §7.2. */
export type RiskRegime = "Risk-On" | "Neutral" | "Risk-Off";
/** Macro policy regime (Layer 3). Layer 1 v5.1 §7.2. */
export type PolicyRegime = "Restrictive" | "Neutral" | "Accommodative";
/** Macro growth regime (Layer 3). Layer 1 v5.1 §7.2. */
export type GrowthRegime = "Strong" | "Moderate" | "Weak";
/** Macro inflation regime (Layer 3). Layer 1 v5.1 §7.2. */
export type InflationRegime = "High" | "Moderate" | "Low";

/** Macro regime context (Layer 3). Layer 1 v5.1 §7.2. */
export interface MacroRegime {
  /** Macro risk regime. */
  risk: RiskRegime;
  /** Macro policy regime. */
  policy: PolicyRegime;
  /** Macro growth regime. */
  growth: GrowthRegime;
  /** Macro inflation regime. */
  inflation: InflationRegime;
}

/** RAG central-bank signal. Layer 1 v5.1 §7.2. */
export interface RagSignal {
  /** Sentiment score (Layer 3). */
  sentiment: number;
  /** Expectation gap (Layer 3). */
  expectation_gap: number;
}

/** RAG signals for Fed and BoJ (Layer 3). Layer 1 v5.1 §7.2. */
export interface Rag {
  /** Federal Reserve signal. */
  fed: RagSignal;
  /** Bank of Japan signal. */
  boj: RagSignal;
}

/** Driver explanation for a prediction. Layer 1 v5.1 §7.2. */
export interface DriversResponse {
  /** Prediction this explanation belongs to. */
  prediction_id: string;
  /** Currency pair. */
  pair: string;
  /** Timestamp of the explanation. */
  timestamp: string;
  /** Top SHAP feature contributions. */
  shap: ShapContribution[];
  /** Macro regime context. */
  macro_regime: MacroRegime;
  /** Central-bank RAG signals. */
  rag: Rag;
  /** Executive narrative — produced by Layer 3, presented verbatim. */
  narrative: string;
  /** Listed risks — produced by Layer 3. */
  risks: string[];
  /** Event sensitivities — produced by Layer 3. */
  event_sensitivity: string[];
}

/* ───────────────────────── 7.3 RankingResponse ─────────────────────────── */

/** A ranked opportunity, ordered by Layer 2 (source of truth). Layer 1 v5.1 §7.3. */
export interface RankedOpportunity {
  /** Rank position in the ranking. */
  rank: number;
  /** Currency pair. */
  pair: string;
  /** Opportunity direction (LONG | SHORT | NEUTRAL). */
  direction: DecisionDirection;
  /** Opportunity score (Layer 2). */
  opportunity_score: number;
  /** Edge ratio. */
  edge_ratio: number;
  /** Backend-determined actionability. */
  actionable: boolean;
  /** Opportunity confidence. */
  confidence: number;
  /** Decision quality score (Layer 2). */
  decision_quality: number;
  /** Position size. SUPPORTED field — distinct from position_size_recommendation (gap). */
  position_size: number;
  /** Prediction id of the opportunity. */
  prediction_id: string;
  /** Decision id of the opportunity. */
  decision_id: string;
}

/** Opportunity ranking snapshot. Layer 1 v5.1 §7.3. */
export interface RankingResponse {
  /** When the ranking snapshot was taken. */
  snapshot_timestamp: string;
  /** Point-in-time the underlying data was valid as of. */
  as_of: string;
  /** Ranked opportunities (ordered by Layer 2). */
  opportunities: RankedOpportunity[];
  /** Top opportunity pair — null when none. */
  top_opportunity: string | null;
  /** Count of actionable opportunities. */
  total_actionable: number;
  /** Total number of ranked pairs. */
  total_pairs: number;
}

/* ───────────────────────── 7.4 PerformanceResponse ──────────────────────── */

/** Evaluation period selectable by the user. Layer 1 v5.1 §7.4. */
export type PerformancePeriod = "1M" | "3M" | "6M" | "1Y" | "ALL";

/** Drift severity classified by Layer 4. Layer 1 v5.1 §7.4. */
export type DriftSeverity = "none" | "warning" | "critical";

/** Statistical performance metrics (Layer 4). Layer 1 v5.1 §7.4. */
export interface StatisticalMetrics {
  /** Directional accuracy. */
  directional_accuracy: number;
  /** Area under the ROC curve. */
  auc: number;
  /** Brier score. */
  brier_score: number;
  /** Expected calibration error. */
  ece: number;
  /** Log loss. */
  log_loss: number;
}

/** Economic performance metrics (Layer 4). Layer 1 v5.1 §7.4. */
export interface EconomicMetrics {
  /** Sharpe ratio. */
  sharpe_ratio: number;
  /** Net Sharpe ratio. */
  sharpe_net: number;
  /** Maximum drawdown. */
  max_drawdown: number;
  /** Profit factor. */
  profit_factor: number;
  /** Win rate. */
  win_rate: number;
  /** Total return. */
  total_return: number;
}

/** Performance breakdown by regime (Layer 4). Layer 1 v5.1 §7.4. */
export interface RegimePerformance {
  /** Regime label. */
  regime: string;
  /** Sharpe within the regime. */
  sharpe: number;
  /** Directional accuracy within the regime. */
  da: number;
  /** Number of observations in the regime. */
  count: number;
}

/** Model degradation indicators (Layer 4). Layer 1 v5.1 §7.4. */
export interface PerformanceDegradation {
  /** Current period Sharpe ratio. */
  current_sharpe: number;
  /** Historical baseline Sharpe ratio. */
  historical_sharpe: number;
  /** Whether drift was detected (Layer 4). */
  drift_detected: boolean;
  /** Drift severity (none | warning | critical). */
  drift_severity: DriftSeverity;
}

/** Performance metrics for a pair and period. Layer 1 v5.1 §7.4. */
export interface PerformanceResponse {
  /** Currency pair. */
  pair: string;
  /** Evaluation period. */
  period: PerformancePeriod;
  /** Point-in-time the metrics were calculated as of. */
  as_of: string;
  /** Statistical performance metrics. */
  statistical: StatisticalMetrics;
  /** Economic performance metrics. */
  economic: EconomicMetrics;
  /** Performance breakdown by regime. */
  regime_performance: RegimePerformance[];
  /** Model degradation indicators. */
  degradation: PerformanceDegradation;
}

/* ─────────────────────── 7.5 / 7.6 Lineage structures ───────────────────── */

/** Identity + versioning of a lineage artifact (Layer 3/4). Layer 1 v5.1 §7.5. */
export interface LineageIdentity {
  /** Artifact id. */
  id: string;
  /** Artifact version. */
  version: string;
  /** Generation timestamp. */
  timestamp: string;
  /** Point-in-time the artifact was valid as of. */
  as_of: string;
}

/** Model reference in lineage. Layer 1 v5.1 §7.5. */
export interface LineageModel {
  /** Model id. */
  id: string;
  /** Model version. */
  version: string;
  /** Model type. */
  type: string;
}

/** Single feature in a lineage snapshot. Layer 1 v5.1 §7.5. */
export interface LineageFeature {
  /** Feature name. */
  name: string;
  /** Feature source. */
  source: string;
  /** Feature value at the available time. */
  value: number;
  /** Time the feature became available. */
  available_time: string;
  /** Feature vintage. */
  vintage: string;
}

/** Feature snapshot reference in lineage. Layer 1 v5.1 §7.5. */
export interface LineageFeatures {
  /** Snapshot id. */
  snapshot_id: string;
  /** Snapshot version. */
  version: string;
  /** Number of features in the snapshot. */
  feature_count: number;
  /** Feature list — included in prediction lineage; not in decision lineage. */
  feature_list?: LineageFeature[];
}

/** Data reference in lineage. Layer 1 v5.1 §7.5. */
export interface LineageData {
  /** Dataset id. */
  dataset_id: string;
  /** Dataset version. */
  version: string;
  /** PIT validation result (Layer 4). */
  pit_validation: "PASS" | "FAIL";
}

/** Source reference in lineage. Layer 1 v5.1 §7.5. */
export interface LineageSource {
  /** Source id. */
  id: string;
  /** Source name. */
  name: string;
  /** Reference period covered by the source. */
  reference_period: string;
  /** Vintage id — included in prediction lineage. */
  vintage_id?: string;
  /** Vintage time — included in prediction lineage. */
  vintage_time?: string;
  /** Available time — included in prediction lineage. */
  available_time?: string;
}

/** Prediction lineage. Layer 1 v5.1 §7.5. */
export interface PredictionLineage {
  /** The prediction artifact. */
  prediction: LineageIdentity;
  /** The model that produced the prediction. */
  model: LineageModel;
  /** The feature snapshot used. */
  features: LineageFeatures;
  /** The dataset used. */
  data: LineageData;
  /** The source data reference. */
  source: LineageSource;
}

/** Decision lineage. Layer 1 v5.1 §7.6. */
export interface DecisionLineage {
  /** The decision artifact. */
  decision: {
    /** Decision id. */
    id: string;
    /** Decision version. */
    version: string;
    /** Generation timestamp. */
    timestamp: string;
    /** Point-in-time the decision was valid as of. */
    as_of: string;
    /** Backend-determined actionability. */
    actionable: boolean;
    /** Rejection reason — null when not rejected. */
    rejection_reason: string | null;
  };
  /** Prediction reference. */
  prediction: {
    /** Prediction id. */
    id: string;
    /** Prediction version. */
    version: string;
    /** Generation timestamp. */
    timestamp: string;
  };
  /** Model reference. */
  model: LineageModel;
  /** Feature snapshot reference (counted only). */
  features: {
    /** Snapshot id. */
    snapshot_id: string;
    /** Snapshot version. */
    version: string;
    /** Number of features. */
    feature_count: number;
  };
  /** Dataset reference. */
  data: LineageData;
  /** Source reference. */
  source: LineageSource;
  /** Delivery policy reference that produced the decision. */
  policy: {
    /** Policy id. */
    id: string;
    /** Policy version. */
    version: string;
  };
  /** Decision fusion weights. */
  fusion: {
    /** Fusion version. */
    version: string;
    /** Fusion weights for quant, macro, and rag signals. */
    weights: {
      /** Quant weight. */
      quant: number;
      /** Macro weight. */
      macro: number;
      /** RAG weight. */
      rag: number;
    };
  };
}

/** Prediction lineage response. Layer 1 v5.1 §7.5. */
export interface PredictionLineageResponse {
  /** Prediction id. */
  prediction_id: string;
  /** Currency pair. */
  pair: string;
  /** Timestamp of the lineage response. */
  timestamp: string;
  /** Lineage payload. */
  lineage: PredictionLineage;
}

/** Decision lineage response. Layer 1 v5.1 §7.6. */
export interface DecisionLineageResponse {
  /** Decision id. */
  decision_id: string;
  /** Prediction id the decision references. */
  prediction_id: string;
  /** Currency pair. */
  pair: string;
  /** Timestamp of the lineage response. */
  timestamp: string;
  /** Lineage payload. */
  lineage: DecisionLineage;
}

/* ───────────────────────── 7.7 StatusResponse ───────────────────────────── */

/** Aggregated system status (Layer 1 §4.5 / R2). Layer 1 v5.1 §7.7. */
export type SystemStatus = "ACTIVE" | "DEGRADED" | "SAFE_MODE" | "HALTED";

/** Infrastructure component status. Layer 1 v5.1 §7.7. */
export type InfrastructureLevel = "healthy" | "degraded" | "unhealthy";

/** Pipeline component status (has its own `failed` state). Layer 1 v5.1 §7.7. */
export type PipelineLevel = "healthy" | "degraded" | "failed";

/** Data quality rating (Layer 4). Layer 1 v5.1 §7.7. */
export type DataQualityRating = "good" | "acceptable" | "degraded";

/** Model performance health (Layer 4). Layer 1 v5.1 §7.7. */
export type ModelPerformanceHealth = "healthy" | "warning" | "degraded";

/** Model drift health (Layer 4). Layer 1 v5.1 §7.7. */
export type ModelDriftHealth = "healthy" | "warning" | "critical";

/** Decision engine validity (Layer 2). Layer 1 v5.1 §7.7. */
export type DecisionValidity = "valid" | "degraded" | "invalid";

/** Safe mode state — reported by lower layers, consumed (never controlled). Layer 1 v5.1 §7.7. */
export type SafeModeState = "ON" | "OFF" | "UNKNOWN";

/** Infrastructure status block. Layer 1 v5.1 §7.7. */
export interface InfrastructureStatus {
  /** API component status. */
  api: InfrastructureLevel;
  /** Database component status. */
  database: InfrastructureLevel;
  /** Pipeline component status. */
  pipeline: PipelineLevel;
  /** Cache component status. */
  cache: InfrastructureLevel;
}

/** Data quality summary from Layer 4. Layer 1 v5.1 §7.7. */
export interface DataQuality {
  /** Overall data quality score. */
  overall: number;
  /** Data quality status. */
  status: DataQualityRating;
}

/** Model health summary from Layer 4. Layer 1 v5.1 §7.7. */
export interface ModelHealth {
  /** Model performance health. */
  performance: ModelPerformanceHealth;
  /** Model drift health. */
  drift: ModelDriftHealth;
}

/** Intelligence status block. Layer 1 v5.1 §7.7. */
export interface IntelligenceStatus {
  /** Data quality summary (Layer 4). */
  data_quality: DataQuality;
  /** Model performance health (Layer 4). */
  model_performance: ModelPerformanceHealth;
  /** Model drift health (Layer 4). */
  model_drift: ModelDriftHealth;
  /** Decision engine validity (Layer 2). */
  decision_validity: DecisionValidity;
  /** Safe mode state (reported by lower layers). */
  safe_mode_state: SafeModeState;
}

/** Status metrics from Layer 4. Layer 1 v5.1 §7.7. */
export interface StatusMetrics {
  /** Data freshness value (Layer 4). */
  data_freshness: number;
  /** Prediction coverage value (Layer 4). */
  prediction_coverage: number;
}

/** Consolidated system status. Layer 1 v5.1 §7.7. */
export interface StatusResponse {
  /** Aggregated system status. */
  system_status: SystemStatus;
  /** Backend-provided reason. */
  reason: string;
  /** Status aggregation timestamp. */
  timestamp: string;
  /** Infrastructure status block. */
  infrastructure: InfrastructureStatus;
  /** Intelligence status block. */
  intelligence: IntelligenceStatus;
  /** Layer 4 metrics. */
  metrics: StatusMetrics;
  /** Timestamp of the latest prediction — null when none. */
  latest_prediction: string | null;
  /** Timestamp of the last successful ingestion — null when none. */
  last_successful_ingestion: string | null;
  /** Timestamp of the next scheduled inference — null when unknown. */
  next_scheduled_inference: string | null;
}