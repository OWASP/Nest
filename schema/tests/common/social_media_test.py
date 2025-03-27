"""Test cases for the social-media schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "social_media"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description_empty.yaml", "'' is too short"),
        ("description_null.yaml", "None is not of type 'string'"),
        (
            "platform_empty.yaml",
            "'' is not one of ['bluesky', 'linkedin', 'x', 'youtube']",
        ),
        (
            "platform_invalid.yaml",
            "'bitcoin' is not one of ['bluesky', 'linkedin', 'x', 'youtube']",
        ),
        (
            "platform_null.yaml",
            "None is not one of ['bluesky', 'linkedin', 'x', 'youtube']",
        ),
        ("platform_undefined.yaml", "'platform' is a required property"),
        ("url_empty.yaml", "'' is not a 'uri'"),
        ("url_invalid.yaml", "'https://bsky' is not a 'uri'"),
        ("url_null.yaml", "None is not of type 'string'"),
        ("url_undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid cases for the social-media schema."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid cases for the social-media schema."""
    common_positive_test(common_schema, SCHEMA_NAME)
