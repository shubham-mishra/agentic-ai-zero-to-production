"""Pytest configuration and shared fixtures for Module 0 verification."""

import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

# Ensure module directory and root are on sys.path
MODULE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load root .env
ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

from solution.triage_client import IncidentAlert, TriageClient


@pytest.fixture
def sample_p1_alert() -> IncidentAlert:
    """Fixture providing a critical P1 infrastructure alert."""
    return IncidentAlert(
        incident_id="INC-8021",
        service="auth-service",
        severity="P1",
        message="500 Internal Server Error rate exceeds 45% in us-east-1 database pool connection exhaustion",
        timestamp="2026-11-02T18:00:00Z",
    )


@pytest.fixture
def sample_p2_alert() -> IncidentAlert:
    """Fixture providing a degraded performance P2 infrastructure alert."""
    return IncidentAlert(
        incident_id="INC-4109",
        service="payment-gateway",
        severity="P2",
        message="P99 latency spiked to 2400ms across redis cache cluster nodes",
        timestamp="2026-11-02T18:05:00Z",
    )
