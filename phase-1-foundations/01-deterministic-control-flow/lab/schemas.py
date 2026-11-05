"""Strict Pydantic schemas for deterministic tool calls and agent outputs - Starter Lab."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ToolName = Literal["query_database_logs", "check_service_health", "restart_pod_sandbox"]

class ToolCallRequest(BaseModel):
    """Deterministic contract for an agent requesting tool execution."""
    tool_name: ToolName = Field(..., description="Target tool name to execute")
    service: str = Field(..., description="Target service parameter for the tool")
    limit: Optional[int] = Field(default=5, description="Log limit parameter if querying logs")
    dry_run: Optional[bool] = Field(default=True, description="Safety flag for restart tool")

class AgentStepOutput(BaseModel):
    """Schema representing a single step of agent reasoning."""
    thought: str = Field(..., description="Agent internal chain-of-thought analysis")
    action: Optional[ToolCallRequest] = Field(default=None, description="Action to take, or None if finished")
    is_final: bool = Field(default=False, description="Whether the incident triage is complete")
    final_diagnosis: Optional[str] = Field(default=None, description="Final incident conclusion if finished")

class IncidentSessionBudget(BaseModel):
    """Enforces hard budget and token constraints for an agent execution session."""
    max_steps: int = Field(default=5, ge=1, le=10, description="Hard ceiling on execution iterations")
    max_tokens: int = Field(default=10000, ge=10, description="Maximum total tokens allowed per session")
    max_cost_usd: float = Field(default=0.05, ge=0.0001, description="Hard financial spend ceiling in USD")
    price_per_1k_input_tokens: float = Field(default=0.00015, description="Input token price in USD for gpt-4o-mini")
    price_per_1k_output_tokens: float = Field(default=0.00060, description="Output token price in USD for gpt-4o-mini")

class SessionExecutionMetrics(BaseModel):
    """Real-time accounting of session resource consumption."""
    step_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0

    def record_usage(self, prompt: int, completion: int, budget: IncidentSessionBudget) -> None:
        """Update metrics and compute financial cost deterministically."""
        # TODO: Step 5 - Increment step_count, prompt_tokens, completion_tokens, and total_tokens.
        # TODO: Step 6 - Compute financial cost using input and output token rates and update total_cost_usd.
        raise NotImplementedError("TODO: Implement SessionExecutionMetrics.record_usage")
