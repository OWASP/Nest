"""Pytest path setup for tools tests."""

from __future__ import annotations

import sys
from pathlib import Path

GITHUB_SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[2] / ".github" / "scripts"
if str(GITHUB_SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(GITHUB_SCRIPTS_DIRECTORY))
