"""Isolated sandbox execution runner with Docker and process containment."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from typing import Optional
from .exceptions import SandboxViolationError
from .schemas import SandboxScriptRequest, ToolExecutionResult

# Dangerous patterns blocked in local sandboxing
BLOCKED_SCRIPT_PATTERNS = [
    r"rm\s+-rf\s+/",
    r":\(\)\s*{\s*:\s*\|\s*:\s*&\s*};\s*:",  # Fork bomb
    r"format\s+[A-Za-z]:",
    r"powershell.*Remove-Item.*-Recurse",
    r"socket\.",  # Outbound socket access in basic scripts
]


class IsolatedSandboxRunner:
    """Manages containerized and process-isolated script execution."""

    def __init__(self, use_docker_if_available: bool = True) -> None:
        self.use_docker = use_docker_if_available
        self._docker_client = None

        if self.use_docker:
            try:
                import docker
                self._docker_client = docker.from_env()
                # Quick ping to verify docker daemon is active
                self._docker_client.ping()
            except Exception:
                self._docker_client = None

    def execute_script(self, request: SandboxScriptRequest) -> ToolExecutionResult:
        """Executes a script inside an isolated sandbox with security boundaries."""
        # 1. Pre-execution static analysis
        for pattern in BLOCKED_SCRIPT_PATTERNS:
            if re.search(pattern, request.script, flags=re.IGNORECASE):
                raise SandboxViolationError(
                    f"Script contains forbidden dangerous pattern matching '{pattern}'."
                )

        # 2. Try Docker container execution if daemon is active
        if self._docker_client is not None:
            return self._execute_in_docker(request)

        # 3. Fallback to contained local process runner
        return self._execute_in_subprocess(request)

    def _execute_in_docker(self, request: SandboxScriptRequest) -> ToolExecutionResult:
        """Runs script in an ephemeral, network-disabled Docker container."""
        try:
            container = self._docker_client.containers.run(  # type: ignore[union-attr]
                image="python:3.12-alpine",
                command=["python", "-c", request.script],
                network_mode="none",  # Strict network isolation
                mem_limit=f"{request.memory_limit_mb}m",
                read_only=True,
                remove=True,
                stdout=True,
                stderr=True,
            )
            output = container.decode("utf-8") if isinstance(container, bytes) else str(container)
            return ToolExecutionResult(output=output, security_audit="DOCKER_ISOLATED")
        except Exception as exc:
            raise SandboxViolationError(f"Docker sandbox execution failed: {exc}") from exc

    def _execute_in_subprocess(self, request: SandboxScriptRequest) -> ToolExecutionResult:
        """Runs script in an isolated subprocess with stripped environment and strict timeout."""
        # Check for simulated network exfiltration attempts
        if "http://" in request.script or "https://" in request.script or "urllib" in request.script:
            raise SandboxViolationError("Outbound network egress is strictly blocked in sandbox.")

        # Create temporary script file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp_file:
            temp_file.write(request.script)
            temp_file_path = temp_file.name

        try:
            # Strip secrets from environment so child process cannot read API keys
            safe_env = {
                "PATH": os.getenv("PATH", ""),
                "SYSTEMROOT": os.getenv("SYSTEMROOT", ""),
            }

            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                env=safe_env,
                check=False,
            )

            if result.returncode != 0:
                return ToolExecutionResult(
                    output=f"Script error (exit {result.returncode}):\n{result.stderr}",
                    is_error=True,
                    security_audit="PROCESS_CONTAINED",
                )

            return ToolExecutionResult(
                output=result.stdout.strip() or "Script executed successfully with no output.",
                security_audit="PROCESS_CONTAINED",
            )

        except subprocess.TimeoutExpired as exc:
            raise SandboxViolationError(
                f"Execution exceeded timeout ceiling of {request.timeout_seconds} seconds."
            ) from exc
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
