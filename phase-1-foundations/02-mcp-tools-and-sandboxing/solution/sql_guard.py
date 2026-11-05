"""Deterministic SQL validation guard and zero-trust query executor."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List
from dotenv import load_dotenv
from .exceptions import SQLMutationBlockedError
from .schemas import DatabaseQueryRequest, ToolExecutionResult

load_dotenv()

# Forbidden SQL keywords that represent state mutations or privilege escalations
FORBIDDEN_SQL_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
]


def validate_read_only_query(query: str) -> None:
    """Deterministically inspects SQL queries to ensure zero write mutations."""
    # Strip comments and extra whitespace
    cleaned = re.sub(r"--.*$", "", query, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL).strip()

    # Block statement chaining (semicolons separating queries)
    # Allow a single trailing semicolon, but not internal semicolons
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    if len(statements) > 1:
        raise SQLMutationBlockedError("Multi-statement SQL query chaining is blocked for security.")

    if not statements:
        raise SQLMutationBlockedError("Query statement cannot be empty.")

    single_stmt = statements[0]

    # Verify query starts with permitted read-only command
    if not re.match(r"^(SELECT|EXPLAIN|SHOW|WITH)\b", single_stmt, flags=re.IGNORECASE):
        raise SQLMutationBlockedError(
            f"Only read-only statements (SELECT, EXPLAIN, SHOW) are permitted. Blocked statement: {single_stmt[:30]}"
        )

    # Check for forbidden mutation keywords anywhere in query
    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(pattern, single_stmt, flags=re.IGNORECASE):
            matched = re.search(pattern, single_stmt, flags=re.IGNORECASE).group(0)  # type: ignore[union-attr]
            raise SQLMutationBlockedError(f"SQL mutation keyword '{matched.upper()}' is strictly prohibited.")


def execute_diagnostic_sql(request: DatabaseQueryRequest) -> ToolExecutionResult:
    """Validates and executes read-only SQL queries with zero-trust credential injection."""
    validate_read_only_query(request.query)

    # Simulated diagnostics for service databases
    # In production, this connects via SQLAlchemy using credentials from .env
    query_lower = request.query.lower()

    if "pg_stat_activity" in query_lower or "connection" in query_lower:
        rows = [
            {"pid": 1042, "usename": "auth_app", "state": "idle in transaction", "query": "SELECT * FROM sessions FOR UPDATE"},
            {"pid": 1043, "usename": "auth_app", "state": "active", "wait_event_type": "Lock", "query": "SELECT token FROM oauth_tokens"},
            {"pid": 1044, "usename": "auth_app", "state": "active", "wait_event_type": "ClientRead", "query": "SELECT * FROM users"},
        ]
        formatted = f"Service: {request.service}\nReturned {min(len(rows), request.max_rows)} connection rows:\n"
        for r in rows[:request.max_rows]:
            formatted += f"  - PID {r['pid']} ({r['usename']}): state={r['state']}, query={r['query']}\n"
        return ToolExecutionResult(output=formatted, security_audit="PASS_READ_ONLY")

    return ToolExecutionResult(
        output=f"Executed read-only query on {request.service}. Returned 0 anomalous rows.",
        security_audit="PASS_READ_ONLY",
    )
