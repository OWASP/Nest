#!/usr/bin/env python

"""OWASP Nest backend management entry point."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
    load_dotenv()
    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
