"""Pytest configuration and fixtures."""

import os

import pytest
from configurations import importer

# Skip NinjaAPI registry check when running tests in parallel (pytest-xdist).
# Forked workers inherit NinjaAPI._registry from the main process, causing
# ConfigError when the same API is registered again in a worker.
os.environ.setdefault("NINJA_SKIP_REGISTRY", "1")


@pytest.fixture(scope="session", autouse=True)
def django_configurations_setup():
    importer.install()
