"""Custom exceptions for deterministic agent execution boundaries - Starter Lab."""

class AgentError(Exception):
    """Base exception for all agent runtime errors."""

class StepCeilingExceededError(AgentError):
    """Raised when the agent exceeds its maximum permitted reasoning steps."""

class BudgetExceededError(AgentError):
    """Raised when the session cost or token budget threshold is exceeded."""

class ToolExecutionError(AgentError):
    """Raised when an internal tool execution fails deterministically."""

class SchemaRepairFailedError(AgentError):
    """Raised when an agent fails to self-correct invalid output after maximum attempts."""
