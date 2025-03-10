"""Test cases for the tag schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "tag"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description_empty.yaml", "'' is too short"),
        ("description_null.yaml", "None is not of type 'string'"),
        ("tag_empty.yaml", "'' is too short"),
        ("tag_null.yaml", "None is not of type 'string'"),
        ("tag_undefined.yaml", "'value' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid tag schema cases."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid tag schema cases."""
    common_positive_test(common_schema, SCHEMA_NAME)
