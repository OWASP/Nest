"""Test cases for the event schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "event"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description_empty.yaml", "'' is too short"),
        ("description_null.yaml", "None is not of type 'string'"),
        ("title_empty.yaml", "'' is too short"),
        ("title_null.yaml", "None is not of type 'string'"),
        ("url_empty.yaml", "'' is not a 'uri'"),
        ("url_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("url_null.yaml", "None is not a 'uri'"),
        ("url_undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid event schema cases."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid event schema cases."""
    common_positive_test(common_schema, SCHEMA_NAME)
