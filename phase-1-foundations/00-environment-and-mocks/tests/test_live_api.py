"""Live API verification tests.

MANDATORY GATE: Executes against real frontier model API using credentials from root .env.
Do not mock model responses in this file.
"""

import os
import pytest
from solution.environment import EnvironmentConfig, verify_live_model_connectivity
from solution.triage_client import (
    IncidentAlert,
    TriageClient,
    TriageDecision,
    TriageResult,
)


def test_live_api_probe_connectivity() -> None:
    """Verify live connectivity and measure latency to the model endpoint."""
    config = EnvironmentConfig.from_env()
    probe_result = verify_live_model_connectivity(
        api_key=config.openai_api_key,
        model=config.openai_model,
    )

    assert probe_result["status"] == "connected"
    assert probe_result["latency_ms"] > 0
    assert len(probe_result["response_id"]) > 0


def test_live_api_incident_triage_p1(sample_p1_alert: IncidentAlert) -> None:
    """Execute live model inference for a critical P1 incident alert."""
    config = EnvironmentConfig.from_env()
    client = TriageClient(api_key=config.openai_api_key, model=config.openai_model)

    result = client.triage_incident(sample_p1_alert)

    # 1. Structural and schema validation
    assert isinstance(result, TriageResult)
    decision = result.decision
    assert isinstance(decision, TriageDecision)
    assert decision.incident_id == "INC-8021"
    assert decision.severity == "P1"
    assert len(decision.root_cause_hypothesis) > 10
    assert len(decision.recommended_action) > 10

    # 2. Hard deterministic business constraint: P1 must not permit auto-remediation
    assert decision.automated_remediation_allowed is False

    # 3. Operational telemetry validation
    metadata = result.metadata
    assert metadata.latency_ms > 0
    assert metadata.prompt_tokens > 0
    assert metadata.completion_tokens > 0
    assert metadata.total_tokens == metadata.prompt_tokens + metadata.completion_tokens


def test_live_api_incident_triage_p2(sample_p2_alert: IncidentAlert) -> None:
    """Execute live model inference for a degraded P2 incident alert."""
    config = EnvironmentConfig.from_env()
    client = TriageClient(api_key=config.openai_api_key, model=config.openai_model)

    result = client.triage_incident(sample_p2_alert)

    assert isinstance(result, TriageResult)
    decision = result.decision
    assert decision.incident_id == "INC-4109"
    assert decision.severity in ["P2", "P1"]
    assert len(decision.root_cause_hypothesis) > 10
    assert len(decision.recommended_action) > 10

    # Operational metrics
    assert result.metadata.latency_ms > 0
    assert result.metadata.total_tokens > 0
