import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("large-empty.yaml", "'' is not a 'uri'"),
        ("large-invalid.yaml", "'image/large.png' is not a 'uri'"),
        ("large-null.yaml", "None is not of type 'string'"),
        ("medium-empty.yaml", "'' is not a 'uri'"),
        ("medium-invalid.yaml", "'image/medium.png' is not a 'uri'"),
        ("medium-null.yaml", "None is not of type 'string'"),
        ("small-empty.yaml", "'' is not a 'uri'"),
        ("small-invalid.yaml", "'image/small.png' is not a 'uri'"),
        ("small-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    common_negative_test(common_schema, "logo", file_path, error_message)


def test_positive(common_schema):
    common_positive_test(common_schema, "logo")
