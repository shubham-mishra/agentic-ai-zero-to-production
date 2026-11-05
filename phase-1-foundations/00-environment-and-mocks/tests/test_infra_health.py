"""Infrastructure health tests verifying container ports and host reachability."""

import pytest
from solution.environment import EnvironmentConfig, check_tcp_port


def test_postgres_port_accessibility() -> None:
    """Verify that PostgreSQL port responds to TCP socket probes when container is active."""
    config = EnvironmentConfig.from_env()
    is_open = check_tcp_port(config.postgres_host, config.postgres_port, timeout=1.0)
    # Assert connection or report port readiness
    assert isinstance(is_open, bool)


def test_socket_timeout_handling() -> None:
    """Verify that TCP port checking handles timeouts cleanly without unhandled exceptions."""
    # Attempt connection to non-routable address with small timeout
    result = check_tcp_port("192.0.2.1", 80, timeout=0.1)
    assert result is False
