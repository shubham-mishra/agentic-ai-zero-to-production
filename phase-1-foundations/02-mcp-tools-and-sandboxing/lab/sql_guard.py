"""Deterministic SQL validation guard and zero-trust query executor - Starter Lab."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List
from dotenv import load_dotenv
from .exceptions import SQLMutationBlockedError
from .schemas import DatabaseQueryRequest, ToolExecutionResult

load_dotenv()

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
    # TODO: Step 1 - Strip comments and trailing semicolons.
    # TODO: Step 2 - Reject query chaining if multiple statements are separated by semicolons.
    # TODO: Step 3 - Ensure the statement begins with a read-only keyword (SELECT, EXPLAIN, SHOW, WITH).
    # TODO: Step 4 - Scan for any forbidden mutation keywords and raise SQLMutationBlockedError if found.
    raise NotImplementedError("TODO: Implement validate_read_only_query")


def execute_diagnostic_sql(request: DatabaseQueryRequest) -> ToolExecutionResult:
    """Validates and executes read-only SQL queries with zero-trust credential injection."""
    # TODO: Step 5 - Call validate_read_only_query(request.query).
    # TODO: Step 6 - Return ToolExecutionResult with connection diagnostic rows.
    raise NotImplementedError("TODO: Implement execute_diagnostic_sql")
