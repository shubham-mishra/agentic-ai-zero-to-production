"""Security and governance exceptions for MCP tools and sandboxes."""

class ToolSecurityError(Exception):
    """Base exception for all tool security and sandbox policy violations."""

class SQLMutationBlockedError(ToolSecurityError):
    """Raised when an agent attempts an unauthorized SQL mutation (e.g. DROP, DELETE)."""

class SandboxViolationError(ToolSecurityError):
    """Raised when script execution violates sandbox constraints (e.g. network egress, timeout)."""

class SchemaMigrationError(Exception):
    """Raised when legacy tool payloads cannot be adapted to modern schema versions."""
