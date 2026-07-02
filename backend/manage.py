#!/usr/bin/env python

"""OWASP Nest backend management entry point."""

import os
import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(_SRC_DIR))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
