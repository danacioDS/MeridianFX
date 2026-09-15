"""Contract tests for GET /v1/status (Layer 1 §7.7).

Validates that the infrastructure status fields emitted by the endpoint
conform to the frontend contract types (Layer 1 v5.1 §7.7):

    InfrastructureLevel = "healthy" | "degraded" | "unhealthy"
    PipelineLevel       = "healthy" | "degraded" | "failed"

This covers KI-007: the endpoint previously emitted "HEALTHY" (uppercase)
and "NOT_CONFIGURED" (out of scale), both of which are invalid.
"""
from __future__ import annotations

import warnings

import pytest
from fastapi.testclient import TestClient

# Silence the starlette deprecation warning for this module only.
# (The TestClient works fine; the warning is about future httpx versions.)
pytestmark = pytest.mark.filterwarnings(
    "ignore::DeprecationWarning:starlette.testclient"
)

INFRA_LEVELS = {"healthy", "degraded", "unhealthy"}
PIPELINE_LEVELS = {"healthy", "degraded", "failed"}


@pytest.fixture(scope="module")
def status_payload():
    """Fetch /v1/status once per module (avoids repeated model loads)."""
    from backend.layer1.main import app
    client = TestClient(app)
    response = client.get("/v1/status")
    assert response.status_code == 200
    return response.json()


def test_status_returns_200(status_payload):
    assert "system_status" in status_payload
    assert "infrastructure" in status_payload


def test_infrastructure_api_is_valid_level(status_payload):
    api = status_payload["infrastructure"]["api"]
    assert api in INFRA_LEVELS, f"api={api!r} not in {INFRA_LEVELS}"


def test_infrastructure_database_is_valid_level(status_payload):
    """KI-007: database was previously 'NOT_CONFIGURED' (out of scale).

    The correct value is 'degraded' — the system functions without a
    production database; narrative persistence uses local SQLite.
    """
    database = status_payload["infrastructure"]["database"]
    assert database in INFRA_LEVELS, f"database={database!r} not in {INFRA_LEVELS}"
    assert database == "degraded", (
        f"expected 'degraded' (no production DB configured), got {database!r}"
    )


def test_infrastructure_pipeline_is_valid_level(status_payload):
    pipeline = status_payload["infrastructure"]["pipeline"]
    assert pipeline in PIPELINE_LEVELS, f"pipeline={pipeline!r} not in {PIPELINE_LEVELS}"


def test_infrastructure_cache_is_valid_level(status_payload):
    cache = status_payload["infrastructure"]["cache"]
    assert cache in INFRA_LEVELS, f"cache={cache!r} not in {INFRA_LEVELS}"
