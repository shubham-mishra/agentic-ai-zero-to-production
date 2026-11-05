"""Tests validating environment settings, credentials, and configuration parsing."""

import os
import pytest
from solution.environment import EnvironmentConfig, check_tcp_port


def test_environment_config_loads_from_env() -> None:
    """Verify that EnvironmentConfig correctly parses credentials from root .env."""
    config = EnvironmentConfig.from_env()

    assert len(config.openai_api_key) > 0, "OPENAI_API_KEY must not be empty"
    assert config.openai_model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], (
        f"Unexpected default model: {config.openai_model}"
    )
    assert config.postgres_port == 5432
    assert config.redis_port == 6379


def test_check_tcp_port_invalid_host() -> None:
    """Verify that socket checker returns False for non-existent local ports."""
    # Port 59999 should not be bound by default services
    is_open = check_tcp_port("127.0.0.1", 59999, timeout=0.2)
    assert is_open is False, "Expected unbound port to return False"
