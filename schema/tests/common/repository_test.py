"""Test cases for the repository schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("changelog-invalid.yaml", "'changes.md' is not a 'uri'"),
        ("code_of_conduct-invalid.yaml", "'conduct.md' is not a 'uri'"),
        ("contribution_guide-invalid.yaml", "'contribute.md' is not a 'uri'"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("url-empty.yaml", "'' is not a 'uri'"),
        ("url-invalid.yaml", "'github/repo' is not a 'uri'"),
        ("url-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the repository schema."""
    common_negative_test(common_schema, "repository", file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the repository schema."""
    common_positive_test(common_schema, "repository")
