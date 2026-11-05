"""Red-team tests verifying SQL mutation blocking and read-only query governance."""

import pytest
from solution.exceptions import SQLMutationBlockedError
from solution.schemas import DatabaseQueryRequest
from solution.sql_guard import execute_diagnostic_sql, validate_read_only_query


def test_valid_select_query_permitted() -> None:
    """Verify that legitimate diagnostic SELECT queries pass validation and execute."""
    req = DatabaseQueryRequest(
        query="SELECT * FROM pg_stat_activity WHERE state = 'active'",
        service="auth-service",
        max_rows=5,
    )
    result = execute_diagnostic_sql(req)
    assert result.security_audit == "PASS_READ_ONLY"
    assert "Service: auth-service" in result.output
    assert "connection rows" in result.output


def test_sql_drop_table_blocked() -> None:
    """Verify that destructive DROP statements are immediately blocked."""
    with pytest.raises(SQLMutationBlockedError) as exc_info:
        validate_read_only_query("DROP TABLE users CASCADE;")
    assert "DROP" in str(exc_info.value)


def test_sql_delete_statement_blocked() -> None:
    """Verify that DELETE statements are blocked."""
    with pytest.raises(SQLMutationBlockedError) as exc_info:
        validate_read_only_query("DELETE FROM sessions WHERE expired = true;")
    assert "DELETE" in str(exc_info.value)


def test_sql_update_statement_blocked() -> None:
    """Verify that UPDATE statements are blocked."""
    with pytest.raises(SQLMutationBlockedError) as exc_info:
        validate_read_only_query("UPDATE accounts SET balance = 1000000;")
    assert "UPDATE" in str(exc_info.value)


def test_sql_multi_statement_chaining_blocked() -> None:
    """Verify that multi-statement SQL injection attacks (query stacking) are blocked."""
    stacked_attack = "SELECT 1; DROP TABLE audit_logs;"
    with pytest.raises(SQLMutationBlockedError) as exc_info:
        validate_read_only_query(stacked_attack)
    assert "chaining is blocked" in str(exc_info.value).lower()


def test_sql_non_read_only_command_blocked() -> None:
    """Verify that non-SELECT commands like INSERT or GRANT are blocked."""
    with pytest.raises(SQLMutationBlockedError):
        validate_read_only_query("INSERT INTO roles (role) VALUES ('admin');")

    with pytest.raises(SQLMutationBlockedError):
        validate_read_only_query("GRANT ALL PRIVILEGES ON DATABASE prod TO hacker;")
