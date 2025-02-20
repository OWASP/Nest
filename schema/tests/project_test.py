"""Test cases for the project schema validation."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


def test_positive(project_schema):
    """Test valid cases for the project schema."""
    for file_path in Path(tests_data_dir / "project/positive").rglob("*.yaml"):
        assert (
            validate_data(
                project_schema,
                yaml.safe_load(
                    file_path.read_text(),
                ),
            )
            is None
        )


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("audience-invalid.yaml", "'hacker' is not one of ['breaker', 'builder', 'defender']"),
        ("audience-empty.yaml", "'' is not one of ['breaker', 'builder', 'defender']"),
        ("audience-null.yaml", "None is not one of ['breaker', 'builder', 'defender']"),
        ("audience-undefined.yaml", "'audience' is a required property"),
        ("blog-invalid.yaml", "'https://invalid/' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
        ("demo-invalid.yaml", "'https://invalid/' is not a 'uri'"),
        ("demo-null.yaml", "None is not a 'uri'"),
        ("documentation-empty.yaml", "[] should be non-empty"),
        ("documentation-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("documentation-null.yaml", "None is not of type 'array'"),
        ("downloads-empty.yaml", "[] should be non-empty"),
        ("downloads-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        (
            "downloads-non-unique.yaml",
            "'https://abc.com/download' has non-unique elements",
        ),
        ("downloads-null.yaml", "None is not of type 'array'"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "'https://example.com/event1' has non-unique elements",
        ),
        ("events-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("events-null.yaml", "None is not of type 'array'"),
        ("level-invalid.yaml", "2.5 is not one of [2, 3, 3.5, 4]"),
        ("license-invalid-value.yaml", "'INVALID-LICENSE-VALUE' is not valid license value"),
        ("mailing-list-empty.yaml", "'' is not a 'uri'"),
        ("mailing-list-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing-list-null.yaml", "None is not a 'uri'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("website-empty.yaml", "'' is too short"),
        ("website-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(project_schema, file_path, error_message):
    """Test invalid cases for the project schema."""
    assert (
        validate_data(
            project_schema,
            yaml.safe_load(
                Path(tests_data_dir / "project/negative" / file_path).read_text(),
            ),
        )
        == error_message
    )
