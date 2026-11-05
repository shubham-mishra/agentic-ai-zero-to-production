"""Phase 1 Module 2: Tool Sandboxing, FastMCP, and Schema Governance (Solution Package)."""

from .exceptions import (
    ToolSecurityError,
    SQLMutationBlockedError,
    SandboxViolationError,
    SchemaMigrationError,
)
from .schemas import (
    LegacyDatabaseQueryRequest,
    DatabaseQueryRequest,
    SandboxScriptRequest,
    ToolExecutionResult,
    adapt_tool_payload,
)
from .sql_guard import (
    validate_read_only_query,
    execute_diagnostic_sql,
    FORBIDDEN_SQL_PATTERNS,
)
from .sandbox_runner import IsolatedSandboxRunner
from .mcp_server import (
    mcp,
    query_database_diagnostics,
    execute_sandboxed_script,
    dispatch_tool_call,
)

__all__ = [
    "ToolSecurityError",
    "SQLMutationBlockedError",
    "SandboxViolationError",
    "SchemaMigrationError",
    "LegacyDatabaseQueryRequest",
    "DatabaseQueryRequest",
    "SandboxScriptRequest",
    "ToolExecutionResult",
    "adapt_tool_payload",
    "validate_read_only_query",
    "execute_diagnostic_sql",
    "FORBIDDEN_SQL_PATTERNS",
    "IsolatedSandboxRunner",
    "mcp",
    "query_database_diagnostics",
    "execute_sandboxed_script",
    "dispatch_tool_call",
]
