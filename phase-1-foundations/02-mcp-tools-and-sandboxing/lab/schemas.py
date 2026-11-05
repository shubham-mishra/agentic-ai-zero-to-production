"""Pydantic schemas and version adapters for MCP tools - Starter Lab."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from .exceptions import SchemaMigrationError


class LegacyDatabaseQueryRequest(BaseModel):
    """Deprecated v1 tool schema for database queries."""
    sql_string: str = Field(..., description="Legacy raw SQL string parameter")
    target_db: str = Field(..., description="Legacy database target name")


class DatabaseQueryRequest(BaseModel):
    """Modern v2 tool schema enforcing typed service names and row limits."""
    query: str = Field(..., description="Read-only diagnostic SQL statement")
    service: str = Field(..., description="Target service identifier (e.g. auth-service)")
    max_rows: int = Field(default=10, ge=1, le=100, description="Hard ceiling on returned rows")


class SandboxScriptRequest(BaseModel):
    """Schema for isolated bash or python script execution."""
    script: str = Field(..., description="Diagnostic script to execute in container sandbox")
    timeout_seconds: int = Field(default=5, ge=1, le=30, description="Execution timeout limit")
    memory_limit_mb: int = Field(default=64, ge=16, le=256, description="Memory ceiling in megabytes")


class ToolExecutionResult(BaseModel):
    """Standardized response payload for all MCP tools."""
    output: str
    is_error: bool = False
    security_audit: str = "PASS"


def adapt_tool_payload(raw_payload: Dict[str, Any]) -> DatabaseQueryRequest:
    """Adapts deprecated v1 tool payloads into modern v2 DatabaseQueryRequest schemas."""
    # TODO: Step 1 - Check if raw_payload has 'sql_string' (v1 schema); map to DatabaseQueryRequest.
    # TODO: Step 2 - Otherwise parse directly as DatabaseQueryRequest (v2 schema).
    # TODO: Step 3 - Raise SchemaMigrationError if parsing fails.
    raise NotImplementedError("TODO: Implement adapt_tool_payload")
