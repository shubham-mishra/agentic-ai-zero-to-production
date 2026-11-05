"""Pytest configuration and shared fixtures for Module 2 verification."""

import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

MODULE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure module-local solution package is loaded without cross-module collision
for mod_name in list(sys.modules.keys()):
    if mod_name == "solution" or mod_name.startswith("solution."):
        del sys.modules[mod_name]

ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

from solution.sandbox_runner import IsolatedSandboxRunner


@pytest.fixture
def sandbox() -> IsolatedSandboxRunner:
    """Fixture providing an isolated sandbox runner instance."""
    return IsolatedSandboxRunner()
