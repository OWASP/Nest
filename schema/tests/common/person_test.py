"""Test cases for the person schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("email-empty.yaml", "'' is not an 'email'"),
        ("email-null.yaml", "None is not of type 'string'"),
        ("github-empty.yaml", "'' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github-invalid.yaml", "'user@name' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github-null.yaml", "None is not of type 'string'"),
        ("github-undefined.yaml", "'github' is a required property"),
        ("email-empty.yaml", "'' is not of type 'string'"),
        ("email-null.yaml", "None is not of type 'string'"),
        ("name-empty.yaml", "'' is not of type 'string'"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("slack-empty.yaml", "'' does not match '^[a-zA-Z0-9._-]{1,21}$'"),
        ("slack-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the person schema."""
    common_negative_test(common_schema, "person", file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the person schema."""
    common_positive_test(common_schema, "person")
