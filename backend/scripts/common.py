"""Shared constants and helpers for ``fetch_nest_dump`` and ``upload_nest_dump``."""

from __future__ import annotations

import os
from pathlib import Path

AWS_REGION = "us-east-2"
NEST_DUMP_S3_OBJECT_KEY = "nest.dump"


def backend_root() -> Path:
    """Return the ``backend/`` directory (parent of ``scripts/``)."""
    return Path(__file__).resolve().parent.parent


def nest_dump_path() -> Path:
    """Return the resolved path to ``backend/data/nest.dump``."""
    return (backend_root() / "data" / "nest.dump").resolve()


def shared_data_bucket() -> str:
    """Name of the shared public-data bucket (override with ``SHARED_DATA_BUCKET``)."""
    return os.environ.get("SHARED_DATA_BUCKET", "owasp-nest-shared-data")
