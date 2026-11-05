"""FastMCP server implementation exposing governed tools to Incident Sentinel."""

from __future__ import annotations

from typing import Any, Dict
from fastmcp import FastMCP
from .schemas import DatabaseQueryRequest, SandboxScriptRequest, adapt_tool_payload
from .sql_guard import execute_diagnostic_sql
from .sandbox_runner import IsolatedSandboxRunner

# Initialize FastMCP Server
mcp = FastMCP("Incident-Sentinel-Tools")
sandbox_runner = IsolatedSandboxRunner()


@mcp.tool()
def query_database_diagnostics(
    query: str,
    service: str,
    max_rows: int = 10,
) -> str:
    """Execute a safe, read-only diagnostic SQL query on an infrastructure database.

    Args:
        query: Read-only SQL query (SELECT, EXPLAIN).
        service: Target service (e.g. 'auth-service').
        max_rows: Maximum rows to return (default 10).
    """
    req = DatabaseQueryRequest(query=query, service=service, max_rows=max_rows)
    result = execute_diagnostic_sql(req)
    return result.output


@mcp.tool()
def execute_sandboxed_script(
    script: str,
    timeout_seconds: int = 5,
) -> str:
    """Execute a diagnostic python script inside an isolated sandbox with zero network access.

    Args:
        script: Python code to execute.
        timeout_seconds: Timeout ceiling in seconds (default 5).
    """
    req = SandboxScriptRequest(script=script, timeout_seconds=timeout_seconds)
    result = sandbox_runner.execute_script(req)
    return result.output


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Unified dispatcher supporting schema version adaptation and tool execution."""
    if tool_name == "query_database_diagnostics":
        # Support both legacy v1 (sql_string) and modern v2 (query) via adapter
        adapted_req = adapt_tool_payload(arguments)
        result = execute_diagnostic_sql(adapted_req)
        return result.output

    elif tool_name == "execute_sandboxed_script":
        req = SandboxScriptRequest(**arguments)
        result = sandbox_runner.execute_script(req)
        return result.output

    raise ValueError(f"Unknown MCP tool: {tool_name}")
