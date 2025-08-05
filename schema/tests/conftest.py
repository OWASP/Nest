"""OWASP Schema tests configuration."""

from pathlib import Path

import pytest
import yaml

from owasp_schema import chapter_schema as chapter_schema_module
from owasp_schema import committee_schema as committee_schema_module
from owasp_schema import common_schema as common_schema_module
from owasp_schema import project_schema as project_schema_module
from owasp_schema.utils.schema_validators import validate_data

tests_dir = Path(__file__).resolve().parent
tests_data_dir = tests_dir / "data"


# Fixtures.
@pytest.fixture
def chapter_schema():
    return chapter_schema_module


@pytest.fixture
def common_schema():
    return common_schema_module


@pytest.fixture
def project_schema():
    return project_schema_module


@pytest.fixture
def committee_schema():
    return committee_schema_module


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
