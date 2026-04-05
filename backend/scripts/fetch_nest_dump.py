"""Download ``data/nest.dump`` from S3 when the remote ETag differs from the last run.

Uses anonymous (unsigned) S3 access - the object must allow public ``GetObject``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from scripts.common import (
    AWS_REGION,
    NEST_DUMP_S3_OBJECT_KEY,
    nest_dump_path,
    shared_data_bucket,
)

logger = logging.getLogger(__name__)


def strip_etag_quotes(etag: str) -> str:
    """Normalize S3 ETag values (strip quotes and whitespace)."""
    return etag.strip().strip('"')


def load_local_etag(path: Path) -> str | None:
    """Return stored ETag text if ``path`` exists, else ``None``."""
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").strip()


def main() -> int:
    """Fetch ``nest.dump`` from S3 if missing or ETag changed."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    target = nest_dump_path()
    etag_path = Path(str(target) + ".etag")
    bucket = shared_data_bucket()

    client = boto3.client(
        "s3",
        config=Config(signature_version=UNSIGNED),
        region_name=AWS_REGION,
    )

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        probe = client.get_object(
            Bucket=bucket,
            Key=NEST_DUMP_S3_OBJECT_KEY,
            Range="bytes=0-0",
        )
        with probe["Body"] as stream:
            stream.read()
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Failed to read S3 object metadata: %s", exc)
        return 1

    remote_etag = strip_etag_quotes(probe["ETag"])
    local_etag = load_local_etag(etag_path)

    if target.is_file() and local_etag == remote_etag:
        logger.info("nest.dump is up to date (ETag matches).")
        return 0

    logger.info("Downloading s3://%s/%s -> %s", bucket, NEST_DUMP_S3_OBJECT_KEY, target)
    try:
        client.download_file(bucket, NEST_DUMP_S3_OBJECT_KEY, str(target))
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Download failed: %s", exc)
        return 1

    etag_path.write_text(remote_etag, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
