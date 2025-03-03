#!/usr/bin/env python

"""OWASP Nest backend management entry point."""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "settings.test")
    )
    os.environ.setdefault("DJANGO_CONFIGURATION", os.getenv("DJANGO_CONFIGURATION", "Test"))

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
