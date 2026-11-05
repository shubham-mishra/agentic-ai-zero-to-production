"""Environment and infrastructure configuration validator."""

from __future__ import annotations

import os
import socket
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


class EnvironmentConfig(BaseModel):
    """Schema validating required system credentials and infrastructure settings."""

    openai_api_key: str = Field(..., description="API key for frontier model access")
    openai_model: str = Field(default="gpt-4o-mini", description="Target model deployment identifier")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host address")
    postgres_port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port number")
    postgres_db: str = Field(default="agentic_ai", description="Primary application database name")
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    redis_host: str = Field(default="localhost", description="Redis cache host address")
    redis_port: int = Field(default=6379, ge=1, le=65535, description="Redis port number")

    @classmethod
    def from_env(cls) -> EnvironmentConfig:
        """Instantiate configuration by loading current environment variables."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not defined in root .env file.")

        return cls(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "agentic_ai"),
            postgres_user=os.getenv("POSTGRES_USER", "postgres"),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
        )


def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Test raw TCP socket connectivity to a required infrastructure service."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, OSError):
        return False


def verify_live_model_connectivity(
    api_key: str,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """Execute a lightweight live probe against the model API to verify credentials.

    Args:
        api_key: Active model provider API key.
        model: Target model name.

    Returns:
        Dictionary containing probe status, latency in milliseconds, and model ID.
    """
    client = OpenAI(api_key=api_key)
    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=5,
    )
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "status": "connected",
        "model": response.model,
        "latency_ms": round(duration_ms, 2),
        "response_id": response.id,
    }
