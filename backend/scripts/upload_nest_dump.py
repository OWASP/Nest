"""Upload ``data/nest.dump`` to the shared S3 bucket (signed; needs IAM ``s3:PutObject``).

Run from ``backend/`` with Poetry so boto3 resolves credentials from the host (e.g. ``~/.aws``).

Override bucket with ``SHARED_DATA_BUCKET`` (default ``owasp-nest-shared-data``).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from scripts.common import (
    AWS_REGION,
    NEST_DUMP_S3_OBJECT_KEY,
    nest_dump_path,
    shared_data_bucket,
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=str(nest_dump_path()),
        help="Path to nest.dump (default: backend/data/nest.dump)",
    )
    return parser.parse_args()


def main() -> int:
    """Upload the dump file to S3."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()
    local_path = Path(args.path).resolve()
    bucket = shared_data_bucket()

    if not local_path.is_file():
        logger.warning("Dump file not found: %s", local_path)
        return 1

    client = boto3.client("s3", region_name=AWS_REGION)
    logger.info("Uploading %s -> s3://%s/%s", local_path, bucket, NEST_DUMP_S3_OBJECT_KEY)
    try:
        client.upload_file(
            str(local_path),
            bucket,
            NEST_DUMP_S3_OBJECT_KEY,
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Upload failed: %s", exc)
        return 1

    logger.info("Upload complete.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
