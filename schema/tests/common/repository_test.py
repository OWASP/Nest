"""Test cases for the repository schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "repository"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("changelog-empty.yaml", "'' is not a 'uri'"),
        ("changelog-null.yaml", "None is not a 'uri'"),
        ("code_of_conduct-empty.yaml", "'' is not a 'uri'"),
        ("code_of_conduct-null.yaml", "None is not a 'uri'"),
        ("contribution_guide-empty.yaml", "'' is not a 'uri'"),
        ("contribution_guide-null.yaml", "None is not a 'uri'"),
        ("description-empty.yaml", "'' is too short"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("url-empty.yaml", "'' is not a 'uri'"),
        ("url-invalid.yaml", "'github/repo' is not a 'uri'"),
        ("url-null.yaml", "None is not a 'uri'"),
        ("url-undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the repository schema."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the repository schema."""
    common_positive_test(common_schema, SCHEMA_NAME)
