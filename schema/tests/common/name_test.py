"""Test cases for the name schema validation."""

import pytest

from tests.conftest import common_negative_test, common_positive_test

SCHEMA_NAME = "name"


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [

        ("description_empty.yaml", "'' is too short"),
        ("description_null.yaml", "None is not of type 'string'"),
        ("name_empty.yaml", "'' is too short"),
        ("name_null.yaml", "None is not of type 'string'")
    ],
)
def test_negative(common_schema, file_path, error_message):
    """Test invalid name schema cases."""
    common_negative_test(common_schema, SCHEMA_NAME, file_path, error_message)


def test_positive(common_schema):
    """Test valid name schema cases."""
    common_positive_test(common_schema, SCHEMA_NAME)
