"""Check backend startup without optional NestBot provider dependencies."""

import os
import subprocess
import sys
from pathlib import Path


def test_backend_starts_without_nestbot_dependencies():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import importlib.abc
import sys

class WithoutNestBot(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == 'crewai' or fullname == 'google.genai':
            raise ModuleNotFoundError(fullname)

sys.meta_path.insert(0, WithoutNestBot())
from configurations import importer
importer.install()
import django
django.setup()
""",
        ],
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[3] / "src"),
            "DJANGO_CONFIGURATION": "Test",
            "DJANGO_SETTINGS_MODULE": "settings.test",
        },
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
