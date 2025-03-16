"""Test cases for the person schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "person"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("email_empty.yaml", "'' is not a 'email'"),
        ("email_invalid.yaml", "'name@invalid' is not a 'email'"),
        ("email_null.yaml", "None is not a 'email'"),
        ("github_empty.yaml", "'' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github_invalid.yaml", "'user@name' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github_null.yaml", "None is not of type 'string'"),
        ("github_undefined.yaml", "'github' is a required property"),
        ("name_empty.yaml", "'' is too short"),
        ("name_null.yaml", "None is not of type 'string'"),
        ("slack_empty.yaml", "'' does not match '^[a-zA-Z0-9._-]{1,21}$'"),
        ("slack_null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the person schema."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the person schema."""
    common_positive_test(common_schema, SCHEMA_NAME)
