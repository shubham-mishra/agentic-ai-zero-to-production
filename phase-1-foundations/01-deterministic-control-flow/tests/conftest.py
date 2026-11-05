"""Pytest configuration and shared fixtures for Module 1 verification."""

import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

MODULE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure module-local solution package is loaded without cross-module collision
for mod_name in list(sys.modules.keys()):
    if mod_name == "solution" or mod_name.startswith("solution."):
        del sys.modules[mod_name]

ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

from solution.runtime import AgentRuntime
from solution.schemas import IncidentSessionBudget


@pytest.fixture
def default_runtime() -> AgentRuntime:
    """Fixture providing an AgentRuntime configured with standard budgets."""
    budget = IncidentSessionBudget(
        max_steps=5,
        max_tokens=8000,
        max_cost_usd=0.03,
    )
    return AgentRuntime(budget=budget)


@pytest.fixture
def auth_outage_alert() -> str:
    """Realistic production incident alert for auth service failure."""
    return (
        "INC-4091: High error rate alert on service 'auth-service'.\n"
        "Metric: HTTP 500 error percentage = 48% over last 5 minutes.\n"
        "Customer impact: Users unable to log in to dashboard.\n"
        "Investigate root cause and recommend remediation."
    )
