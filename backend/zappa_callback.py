"""Zappa callback handlers."""

# ruff: noqa: T201

import re
import tarfile
import tempfile
from pathlib import Path


def clean_package(zappa):
    """Clean up Zappa package before deployment."""
    print("Cleaning Zappa package...")

    archive_path = zappa.zip_path
    if not archive_path.endswith(".tar.gz"):
        print(f"Unsupported archive format: {archive_path}")
        return

    excludes = zappa.zappa_settings.get(zappa.api_stage, {}).get("regex_excludes")
    if not excludes:
        print("No regex_excludes provided, skipping")
        return

    full_path = Path.cwd() / archive_path
    print(f"Original package size: {full_path.stat().st_size / 1024 / 1024:.2f} MB")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        with tarfile.open(full_path, "r:gz") as tf:
            tf.extractall(temp_path, filter="data")
        full_path.unlink()

        with tarfile.open(full_path, "w:gz") as tf:
            for filepath in temp_path.rglob("*"):
                if filepath.is_file() and not any(re.search(p, str(filepath)) for p in excludes):
                    tf.add(filepath, filepath.relative_to(temp_path))

    print(f"New package size: {full_path.stat().st_size / 1024 / 1024:.2f} MB")
