"""Tools for the Incident Sentinel reasoning loop."""

from __future__ import annotations

from typing import Any, Dict
from .schemas import ToolCallRequest
from .exceptions import ToolExecutionError

def query_database_logs(service: str, limit: int = 5) -> str:
    """Diagnostic tool returning simulated production logs."""
    if service == "auth-service":
        return (
            "2026-11-05T03:15:02Z [ERROR] PoolConnectionTimeout: Connection pool exhausted (max_connections=100).\n"
            "2026-11-05T03:15:05Z [WARN] Client request latency spiked to 4100ms.\n"
            "2026-11-05T03:15:09Z [FATAL] 500 InternalServerError: unable to checkout connection from db-primary."
        )
    elif service == "payment-gateway":
        return (
            "2026-11-05T03:20:00Z [INFO] Processing batch checkout.\n"
            "2026-11-05T03:20:02Z [WARN] Redis cache miss rate at 85%."
        )
    return f"No anomalous logs found for service: {service}"

def check_service_health(service: str) -> str:
    """Simulates querying health endpoints across the cluster."""
    if service == "auth-service":
        return "STATUS: DEGRADED | Healthcheck: FAIL | ErrorRate: 48% | ActiveConnections: 100/100"
    return "STATUS: HEALTHY | Healthcheck: PASS | ErrorRate: 0.1%"

def restart_pod_sandbox(service: str, dry_run: bool = True) -> str:
    """Executes a diagnostic non-destructive restart or report."""
    if dry_run:
        return f"DRY_RUN: Pod restart simulation succeeded for {service}. No state changed."
    return f"EXECUTION: Restart signal sent to pods in service {service}."

AVAILABLE_TOOLS = {
    "query_database_logs": query_database_logs,
    "check_service_health": check_service_health,
    "restart_pod_sandbox": restart_pod_sandbox,
}

def execute_tool(tool_request: ToolCallRequest) -> str:
    """Deterministically dispatches a validated tool call request."""
    tool_fn = AVAILABLE_TOOLS.get(tool_request.tool_name)
    if not tool_fn:
        raise ToolExecutionError(f"Requested tool '{tool_request.tool_name}' is not authorized.")
    
    try:
        if tool_request.tool_name == "query_database_logs":
            return tool_fn(service=tool_request.service, limit=tool_request.limit or 5)
        elif tool_request.tool_name == "check_service_health":
            return tool_fn(service=tool_request.service)
        elif tool_request.tool_name == "restart_pod_sandbox":
            return tool_fn(service=tool_request.service, dry_run=tool_request.dry_run if tool_request.dry_run is not None else True)
        return tool_fn(service=tool_request.service)
    except Exception as exc:
        raise ToolExecutionError(f"Tool execution failed for '{tool_request.tool_name}': {exc}") from exc
