import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description-null.yaml", "None is not of type 'string'"),
        ("logo-empty.yaml", "'' is not a 'uri'"),
        ("logo-null.yaml", "None is not of type 'string'"),
        ("name-empty.yaml", "'' is not a 'string'"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("url-empty.yaml", "'' is not a 'uri'"),
        ("url-null.yaml", "None is not of type 'string'"),
        ("url-undefined.yaml", "'url' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    common_negative_test(common_schema, "sponsor", file_path, error_message)


def test_positive(common_schema):
    common_positive_test(common_schema, "sponsor")
