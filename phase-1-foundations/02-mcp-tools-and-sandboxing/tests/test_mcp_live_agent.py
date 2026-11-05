"""Live API integration test: Incident Sentinel using governed MCP tools."""

import json
import os
import pytest
from openai import OpenAI
from pydantic import BaseModel, Field
from solution.mcp_server import dispatch_tool_call


class AgentTriageDecision(BaseModel):
    """Schema for agent's final triage conclusion."""
    root_cause: str = Field(..., description="Root cause identified from MCP diagnostics")
    recommended_action: str = Field(..., description="Actionable fix for the outage")
    risk_level: str = Field(..., description="P1, P2, or P3 risk assessment")


def test_live_agent_queries_mcp_tools() -> None:
    """MANDATORY LIVE API GATE:

    The agent connects to the live OpenAI model, selects the governed MCP tool
    to inspect PostgreSQL connection activity, receives the observation, and
    produces a structured triage report.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key, "OPENAI_API_KEY must be configured in .env"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    client = OpenAI(api_key=api_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_database_diagnostics",
                "description": "Execute a safe, read-only diagnostic query to inspect active database connections and locks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Read-only SQL query (SELECT pg_stat_activity...)"},
                        "service": {"type": "string", "description": "Target service name (e.g. auth-service)"},
                        "max_rows": {"type": "integer", "description": "Max rows to return (default 5)"},
                    },
                    "required": ["query", "service"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are Incident Sentinel. You have access to governed MCP diagnostic tools. "
                "Inspect active connections on auth-service to identify why requests are timing out."
            ),
        },
        {
            "role": "user",
            "content": "ALERT: Service 'auth-service' database connection pool exhausted. Diagnose immediate connection state.",
        },
    ]

    # Step 1: Initial call where model decides to call the MCP tool
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    choice = response.choices[0]
    assert choice.message.tool_calls is not None
    tool_call = choice.message.tool_calls[0]
    assert tool_call.function.name == "query_database_diagnostics"

    # Step 2: Dispatch tool execution via our governed MCP dispatcher
    tool_args = json.loads(tool_call.function.arguments)
    observation = dispatch_tool_call(tool_call.function.name, tool_args)
    assert "connection rows" in observation

    # Step 3: Feed observation back to model for structured diagnosis
    messages.append(choice.message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": observation,
    })

    final_completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=AgentTriageDecision,
    )

    decision = final_completion.choices[0].message.parsed
    assert decision is not None
    assert len(decision.root_cause) > 10
    assert len(decision.recommended_action) > 10
    assert decision.risk_level in ["P1", "P2", "P3"]
