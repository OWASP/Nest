"""Shared constants and helpers for ``fetch_nest_dump`` and ``upload_nest_dump``."""

from __future__ import annotations

import os
from pathlib import Path

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
NEST_DUMP_S3_OBJECT_KEY = "nest.dump"
SHARED_DATA_BUCKET_OWNER_ACCOUNT_ID = "160885282306"


def backend_root() -> Path:
    """Return the ``backend/`` directory (parent of ``scripts/``)."""
    return Path(__file__).resolve().parent.parent


def nest_dump_path() -> Path:
    """Return the resolved path to ``backend/data/nest.dump``."""
    return (backend_root() / "data" / "nest.dump").resolve()


def shared_data_bucket() -> str:
    """Name of the shared public-data bucket (override with ``SHARED_DATA_BUCKET``)."""
    return os.environ.get("SHARED_DATA_BUCKET", "owasp-nest-shared-data")


def shared_data_bucket_owner_account_id() -> str:
    """Return the bucket owner account ID for ``ExpectedBucketOwner``."""
    return os.environ.get("SHARED_DATA_BUCKET_OWNER", SHARED_DATA_BUCKET_OWNER_ACCOUNT_ID)
