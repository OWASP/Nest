"""Pytest path setup for tools tests."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
COMPLIANCE_SCRIPTS_DIRECTORY = TOOLS_ROOT / "compliance"
GITHUB_SCRIPTS_DIRECTORY = TOOLS_ROOT.parent / ".github" / "scripts"
SECURITY_SCRIPTS_DIRECTORY = TOOLS_ROOT / "security"

for directory in (
    COMPLIANCE_SCRIPTS_DIRECTORY,
    GITHUB_SCRIPTS_DIRECTORY,
    SECURITY_SCRIPTS_DIRECTORY,
):
    path = str(directory)
    if path not in sys.path:
        sys.path.insert(0, path)
