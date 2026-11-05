"""FastMCP server implementation exposing governed tools to Incident Sentinel - Starter Lab."""

from __future__ import annotations

from typing import Any, Dict
from fastmcp import FastMCP
from .schemas import DatabaseQueryRequest, SandboxScriptRequest, adapt_tool_payload
from .sql_guard import execute_diagnostic_sql
from .sandbox_runner import IsolatedSandboxRunner

mcp = FastMCP("Incident-Sentinel-Tools")
sandbox_runner = IsolatedSandboxRunner()


@mcp.tool()
def query_database_diagnostics(
    query: str,
    service: str,
    max_rows: int = 10,
) -> str:
    """Execute a safe, read-only diagnostic SQL query on an infrastructure database."""
    # TODO: Step 1 - Wrap arguments in DatabaseQueryRequest and call execute_diagnostic_sql.
    raise NotImplementedError("TODO: Implement query_database_diagnostics")


@mcp.tool()
def execute_sandboxed_script(
    script: str,
    timeout_seconds: int = 5,
) -> str:
    """Execute a diagnostic python script inside an isolated sandbox with zero network access."""
    # TODO: Step 2 - Wrap arguments in SandboxScriptRequest and call sandbox_runner.execute_script.
    raise NotImplementedError("TODO: Implement execute_sandboxed_script")


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Unified dispatcher supporting schema version adaptation and tool execution."""
    # TODO: Step 3 - Dispatch query_database_diagnostics with adapt_tool_payload for backward compatibility.
    # TODO: Step 4 - Dispatch execute_sandboxed_script.
    raise NotImplementedError("TODO: Implement dispatch_tool_call")
