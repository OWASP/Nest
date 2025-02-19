"""OWASP Schema tests configuration."""

import json
from pathlib import Path

import pytest
import yaml

from utils.schema_validators import validate_data

tests_dir = Path(__file__).resolve().parent
tests_data_dir = tests_dir / "data"
schema_dir = tests_dir.parent


# Fixtures.
@pytest.fixture()
def chapter_schema():
    with Path(schema_dir / "chapter.json").open() as file:
        yield json.load(file)


@pytest.fixture()
def common_schema():
    with Path(schema_dir / "common.json").open() as file:
        yield json.load(file)


@pytest.fixture()
def project_schema():
    with Path(schema_dir / "project.json").open() as file:
        yield json.load(file)


# Base functions.
def common_negative_test(common_schema, attribute_name, file_path, error_message):
    assert (
        validate_data(
            common_schema["definitions"][attribute_name],
            yaml.safe_load(
                Path(
                    tests_data_dir / f"common/{attribute_name}/negative" / file_path,
                ).read_text(),
            ),
        )
        == error_message
    )


def common_positive_test(common_schema, attribute_name):
    for file_path in Path(tests_data_dir / f"common/{attribute_name}/positive").rglob(
        "*.yaml",
    ):
        assert (
            validate_data(
                common_schema["definitions"][attribute_name],
                yaml.safe_load(
                    file_path.read_text(),
                ),
            )
            is None
        )