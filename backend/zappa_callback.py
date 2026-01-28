"""Zappa callback handlers."""

# ruff: noqa: T201

import re
import shutil
import tarfile
import tempfile
from pathlib import Path

import boto3


def clean_package(zappa):
    """Clean up Zappa package before deployment."""
    print("Cleaning Zappa package...")

    archive_path = zappa.zip_path
    if not archive_path.endswith(".tar.gz"):
        print(f"Unsupported archive format: {archive_path}")
        return

    if not (excludes := zappa.zappa_settings.get(zappa.api_stage, {}).get("regex_excludes")):
        print("No regex_excludes provided, skipping")
        return

    full_path = Path.cwd() / archive_path
    print(f"Original package size: {full_path.stat().st_size / 1024 / 1024:.2f} MB")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        new_archive_path = temp_path / "new.tar.gz"

        # nosemgrep: trailofbits.python.tarfile-extractall-traversal.tarfile-extractall-traversal # noqa: ERA001, E501
        with tarfile.open(full_path, "r:gz") as tf:  # NOSONAR archive is trusted
            tf.extractall(temp_path, filter="data")

        with tarfile.open(new_archive_path, "w:gz") as tf:  # NOSONAR archive is trusted
            for filepath in temp_path.rglob("*"):
                if filepath == new_archive_path:
                    continue
                if filepath.is_file() and not any(re.search(p, str(filepath)) for p in excludes):
                    tf.add(filepath, filepath.relative_to(temp_path))

        full_path.unlink()
        shutil.move(new_archive_path, full_path)

    print(f"New package size: {full_path.stat().st_size / 1024 / 1024:.2f} MB")


def update_alias(zappa):
    """Update Lambda alias to latest published version."""
    print("Updating Lambda alias...")

    client = boto3.client("lambda")
    versions = client.list_versions_by_function(FunctionName=zappa.lambda_name)["Versions"]

    if not (published := [v["Version"] for v in versions if v["Version"] != "$LATEST"]):
        print("No published versions found, skipping alias update")
        return

    try:
        client.update_alias(
            FunctionName=zappa.lambda_name, Name="live", FunctionVersion=published[-1]
        )
        print(f"Alias 'live' now points to version {published[-1]}")
    except client.exceptions.ResourceNotFoundException:
        print("Alias 'live' not found, skipping alias update")


def cleanup_versions(zappa, keep=5):
    """Delete old Lambda versions."""
    print("Cleaning up old Lambda versions...")

    client = boto3.client("lambda")
    versions = client.list_versions_by_function(FunctionName=zappa.lambda_name)["Versions"]
    published = [v for v in versions if v["Version"] != "$LATEST"]

    if len(published) <= keep:
        print(f"Only {len(published)} versions exist, nothing to delete")
        return

    to_delete = published[:-keep]
    for version in to_delete:
        client.delete_function(FunctionName=version["FunctionArn"])

    print(f"Deleted {len(to_delete)} old versions, kept {keep}")


def post(zappa):
    """Post deploy callback."""
    update_alias(zappa)
    cleanup_versions(zappa)
