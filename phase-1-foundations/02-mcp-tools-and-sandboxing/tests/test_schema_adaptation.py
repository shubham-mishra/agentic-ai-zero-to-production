"""Tests for schema versioning and backward compatibility adapters."""

import pytest
from solution.exceptions import SchemaMigrationError
from solution.schemas import adapt_tool_payload
from solution.mcp_server import dispatch_tool_call


def test_schema_adapter_upgrades_v1_payload() -> None:
    """Verify that legacy v1 query payload (sql_string, target_db) upgrades to v2."""
    v1_payload = {
        "sql_string": "SELECT count(*) FROM sessions",
        "target_db": "auth-service",
    }
    v2_req = adapt_tool_payload(v1_payload)

    assert v2_req.query == "SELECT count(*) FROM sessions"
    assert v2_req.service == "auth-service"
    assert v2_req.max_rows == 10


def test_schema_adapter_accepts_native_v2_payload() -> None:
    """Verify that native v2 payload parses directly."""
    v2_payload = {
        "query": "SELECT * FROM locks",
        "service": "payment-gateway",
        "max_rows": 25,
    }
    v2_req = adapt_tool_payload(v2_payload)

    assert v2_req.query == "SELECT * FROM locks"
    assert v2_req.service == "payment-gateway"
    assert v2_req.max_rows == 25


def test_mcp_dispatcher_supports_both_versions() -> None:
    """Verify that the unified MCP dispatcher handles both v1 and v2 payloads."""
    # Call with v1 payload
    out_v1 = dispatch_tool_call(
        "query_database_diagnostics",
        {"sql_string": "SELECT * FROM pg_stat_activity", "target_db": "auth-service"},
    )
    assert "auth-service" in out_v1

    # Call with v2 payload
    out_v2 = dispatch_tool_call(
        "query_database_diagnostics",
        {"query": "SELECT * FROM pg_stat_activity", "service": "auth-service", "max_rows": 2},
    )
    assert "auth-service" in out_v2
