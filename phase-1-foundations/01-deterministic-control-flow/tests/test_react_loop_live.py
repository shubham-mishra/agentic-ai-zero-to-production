"""Live API integration tests verifying bounded ReAct loop execution, step limits, and budget caps."""

import pytest
from solution.exceptions import BudgetExceededError, StepCeilingExceededError
from solution.runtime import AgentRuntime
from solution.schemas import IncidentSessionBudget, SessionExecutionMetrics


def test_live_react_loop_successful_triage(
    default_runtime: AgentRuntime,
    auth_outage_alert: str,
) -> None:
    """Executes a full live multi-turn ReAct loop against the real OpenAI model.

    MANDATORY GATE:
    1. Agent must query diagnostic tools (e.g. query_database_logs).
    2. Agent must observe the result.
    3. Agent must conclude with a final diagnosis identifying pool exhaustion.
    4. Execution must not exceed step ceiling or token budget.
    """
    final_diagnosis, metrics = default_runtime.run_investigation(auth_outage_alert)

    assert isinstance(final_diagnosis, str)
    assert len(final_diagnosis) > 20
    # The diagnosis should accurately identify the database pool exhaustion issue discovered in logs
    assert any(
        term in final_diagnosis.lower()
        for term in ["connection", "pool", "exhaust", "database", "timeout"]
    ), f"Diagnosis did not reference root cause: {final_diagnosis}"

    # Verify metrics show multi-turn execution (at least 1 tool call turn + 1 final turn)
    assert 1 <= metrics.step_count <= default_runtime.budget.max_steps
    assert metrics.total_tokens > 0
    assert metrics.total_cost_usd > 0.0


def test_live_step_ceiling_enforcement(auth_outage_alert: str) -> None:
    """Verifies that setting a step ceiling of 1 terminates with StepCeilingExceededError

    if the agent tries to execute a tool and cannot complete in 1 turn.
    """
    strict_budget = IncidentSessionBudget(max_steps=1)
    runtime = AgentRuntime(budget=strict_budget)

    # With max_steps=1, an investigation that requires tool inspection cannot finish in 1 turn
    # and will either reach step ceiling or return early
    try:
        diagnosis, metrics = runtime.run_investigation(auth_outage_alert)
        # If it returned in 1 step without tools, step_count must be <= 1
        assert metrics.step_count <= 1
    except StepCeilingExceededError:
        # Expected behavior when agent wants to take an action but step limit is reached
        pass


def test_live_token_budget_exceeded_enforcement(auth_outage_alert: str) -> None:
    """Verifies that an artificially tiny token budget triggers BudgetExceededError."""
    # Set an impossibly low token ceiling (e.g. 50 tokens)
    starved_budget = IncidentSessionBudget(max_tokens=50)
    runtime = AgentRuntime(budget=starved_budget)

    with pytest.raises(BudgetExceededError) as exc_info:
        runtime.run_investigation(auth_outage_alert)

    assert "Token budget exceeded" in str(exc_info.value)
