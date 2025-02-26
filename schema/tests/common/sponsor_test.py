"""Test cases for the sponsor schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "sponsor"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description-empty.yaml", "'' is too short"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("logo-empty.yaml", "'' is not a 'uri'"),
        ("logo-null.yaml", "None is not a 'uri'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("url-empty.yaml", "'' is not a 'uri'"),
        ("url-null.yaml", "None is not a 'uri'"),
        ("url-undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the sponsor schema."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the sponsor schema."""
    common_positive_test(common_schema, SCHEMA_NAME)
