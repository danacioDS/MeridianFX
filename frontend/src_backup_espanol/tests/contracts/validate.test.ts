/**
 * Contract validation — infrastructure tests.
 *
 * Requirements:
 *  - Contract types match Layer 1 v5.1 §7 (field inventory identical).
 *  - No extra fields beyond the contract.
 *  - No missing required fields.
 *  - Nullable fields accept null (nullability preserved).
 *
 * Field lists are transcribed from docs/Product_specification/Layer_01.md §7.
 */
import { describe, expect, it } from "vitest";
import type {
  DriversResponse,
  ForecastResponse,
  PerformanceResponse,
  RankingResponse,
  StatusResponse,
} from "../../types/contracts";

function assertContractMatches(instance: object, requiredFields: readonly string[]): void {
  const actualKeys = Object.keys(instance).sort();
  const expectedKeys = [...requiredFields].sort();
  expect(actualKeys).toEqual(expectedKeys);
  requiredFields.forEach((field) => {
    expect(Object.prototype.hasOwnProperty.call(instance, field)).toBe(true);
  });
}

describe("ForecastResponse — Layer 1 v5.1 §7.1", () => {
  it("matches the contract field inventory (no missing, no extra)", () => {
    const fixture: ForecastResponse = {
      prediction_id: "pred-001",
      pair: "USDJPY",
      timestamp: "2026-08-27T00:00:00.000Z",
      as_of: "2026-08-27T00:00:00.000Z",
      delivery_state: "ELIGIBLE",
      delivery_reason: "ok",
      delivery_warning: null,
      prediction: null,
      decision: null,
      data_quality: null,
      drivers: null,
      lineage: null,
    };

    assertContractMatches(fixture, [
      "prediction_id",
      "pair",
      "timestamp",
      "as_of",
      "delivery_state",
      "delivery_reason",
      "delivery_warning",
      "prediction",
      "decision",
      "data_quality",
      "drivers",
      "lineage",
    ]);
  });

  it("preserves nullability of optional artifacts", () => {
    const fixture: ForecastResponse = {
      prediction_id: "pred-001",
      pair: "USDJPY",
      timestamp: "2026-08-27T00:00:00.000Z",
      as_of: "2026-08-27T00:00:00.000Z",
      delivery_state: "UNAVAILABLE",
      delivery_reason: "unavailable",
      delivery_warning: null,
      prediction: null,
      decision: null,
      data_quality: null,
      drivers: null,
      lineage: null,
    };
    expect(fixture.delivery_warning).toBeNull();
    expect(fixture.prediction).toBeNull();
    expect(fixture.decision).toBeNull();
    expect(fixture.data_quality).toBeNull();
  });
});

describe("DriversResponse — Layer 1 v5.1 §7.2", () => {
  it("matches the contract field inventory (no missing, no extra)", () => {
    const fixture: DriversResponse = {
      prediction_id: "pred-001",
      pair: "USDJPY",
      timestamp: "2026-08-27T00:00:00.000Z",
      shap: [],
      macro_regime: {
        risk: "Neutral",
        policy: "Neutral",
        growth: "Moderate",
        inflation: "Moderate",
      },
      rag: {
        fed: { sentiment: 0.2, expectation_gap: 0.1 },
        boj: { sentiment: -0.1, expectation_gap: 0.05 },
      },
      narrative: "Narrative from Layer 3.",
      risks: ["Risk A"],
      event_sensitivity: ["Event B"],
    };

    assertContractMatches(fixture, [
      "prediction_id",
      "pair",
      "timestamp",
      "shap",
      "macro_regime",
      "rag",
      "narrative",
      "risks",
      "event_sensitivity",
    ]);
  });
});

describe("RankingResponse — Layer 1 v5.1 §7.3", () => {
  it("matches the contract field inventory (no missing, no extra)", () => {
    const fixture: RankingResponse = {
      snapshot_timestamp: "2026-08-27T00:00:00.000Z",
      as_of: "2026-08-27T00:00:00.000Z",
      opportunities: [
        {
          rank: 1,
          pair: "USDJPY",
          direction: "LONG",
          opportunity_score: 0.87,
          edge_ratio: 1.4,
          actionable: true,
          confidence: 0.72,
          decision_quality: 0.8,
          position_size: 0.05,
          prediction_id: "pred-001",
          decision_id: "dec-001",
        },
      ],
      top_opportunity: "USDJPY",
      total_actionable: 1,
      total_pairs: 4,
    };

    assertContractMatches(fixture, [
      "snapshot_timestamp",
      "as_of",
      "opportunities",
      "top_opportunity",
      "total_actionable",
      "total_pairs",
    ]);
  });

  it("keeps position_size as the supported field (never recommendation)", () => {
    const fixture: RankingResponse = {
      snapshot_timestamp: "2026-08-27T00:00:00.000Z",
      as_of: "2026-08-27T00:00:00.000Z",
      opportunities: [
        {
          rank: 1,
          pair: "USDJPY",
          direction: "LONG",
          opportunity_score: 0.87,
          edge_ratio: 1.4,
          actionable: true,
          confidence: 0.72,
          decision_quality: 0.8,
          position_size: 0.05,
          prediction_id: "pred-001",
          decision_id: "dec-001",
        },
      ],
      top_opportunity: null,
      total_actionable: 0,
      total_pairs: 0,
    };
    expect(fixture.opportunities[0].position_size).toBe(0.05);
    expect(fixture.top_opportunity).toBeNull();
  });
});

describe("PerformanceResponse — Layer 1 v5.1 §7.4", () => {
  it("matches the contract field inventory (no missing, no extra)", () => {
    const fixture: PerformanceResponse = {
      pair: "USDJPY",
      period: "3M",
      as_of: "2026-08-27T00:00:00.000Z",
      statistical: {
        directional_accuracy: 0.62,
        auc: 0.58,
        brier_score: 0.24,
        ece: 0.03,
        log_loss: 0.69,
      },
      economic: {
        sharpe_ratio: 1.1,
        sharpe_net: 0.9,
        max_drawdown: -0.08,
        profit_factor: 1.3,
        win_rate: 0.55,
        total_return: 0.12,
      },
      regime_performance: [
        { regime: "Risk-On", sharpe: 1.2, da: 0.6, count: 40 },
      ],
      degradation: {
        current_sharpe: 1.1,
        historical_sharpe: 1.3,
        drift_detected: false,
        drift_severity: "none",
      },
    };

    assertContractMatches(fixture, [
      "pair",
      "period",
      "as_of",
      "statistical",
      "economic",
      "regime_performance",
      "degradation",
    ]);
  });
});

describe("StatusResponse — Layer 1 v5.1 §7.7", () => {
  it("matches the contract field inventory (no missing, no extra)", () => {
    const fixture: StatusResponse = {
      system_status: "ACTIVE",
      reason: "System operating normally",
      timestamp: "2026-08-27T00:00:00.000Z",
      infrastructure: {
        api: "healthy",
        database: "healthy",
        pipeline: "healthy",
        cache: "healthy",
      },
      intelligence: {
        data_quality: { overall: 0.95, status: "good" },
        model_performance: "healthy",
        model_drift: "healthy",
        decision_validity: "valid",
        safe_mode_state: "OFF",
      },
      metrics: {
        data_freshness: 0.99,
        prediction_coverage: 0.98,
      },
      latest_prediction: "2026-08-27T00:00:00.000Z",
      last_successful_ingestion: "2026-08-27T00:00:00.000Z",
      next_scheduled_inference: "2026-08-27T01:00:00.000Z",
    };

    assertContractMatches(fixture, [
      "system_status",
      "reason",
      "timestamp",
      "infrastructure",
      "intelligence",
      "metrics",
      "latest_prediction",
      "last_successful_ingestion",
      "next_scheduled_inference",
    ]);
  });

  it("preserves nullable timestamps without substitution", () => {
    const fixture: StatusResponse = {
      system_status: "DEGRADED",
      reason: "Reduced quality",
      timestamp: "2026-08-27T00:00:00.000Z",
      infrastructure: {
        api: "healthy",
        database: "healthy",
        pipeline: "healthy",
        cache: "degraded",
      },
      intelligence: {
        data_quality: { overall: 0.7, status: "degraded" },
        model_performance: "degraded",
        model_drift: "warning",
        decision_validity: "degraded",
        safe_mode_state: "UNKNOWN",
      },
      metrics: {
        data_freshness: 0.8,
        prediction_coverage: 0.7,
      },
      latest_prediction: null,
      last_successful_ingestion: null,
      next_scheduled_inference: null,
    };
    expect(fixture.latest_prediction).toBeNull();
    expect(fixture.last_successful_ingestion).toBeNull();
    expect(fixture.next_scheduled_inference).toBeNull();
  });
});