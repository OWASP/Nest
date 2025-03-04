"""Test cases for the repository schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "repository"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("changelog_empty.yaml", "'' is not a 'uri'"),
        ("changelog_null.yaml", "None is not a 'uri'"),
        ("code_of_conduct_empty.yaml", "'' is not a 'uri'"),
        ("code_of_conduct_null.yaml", "None is not a 'uri'"),
        ("contribution_guide_empty.yaml", "'' is not a 'uri'"),
        ("contribution_guide_null.yaml", "None is not a 'uri'"),
        ("description_empty.yaml", "'' is too short"),
        ("description_null.yaml", "None is not of type 'string'"),
        ("name_empty.yaml", "'' is too short"),
        ("name_null.yaml", "None is not of type 'string'"),
        ("url_empty.yaml", "'' is not a 'uri'"),
        ("url_invalid.yaml", "'github/repo' is not a 'uri'"),
        ("url_null.yaml", "None is not a 'uri'"),
        ("url_undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the repository schema."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the repository schema."""
    common_positive_test(common_schema, SCHEMA_NAME)
