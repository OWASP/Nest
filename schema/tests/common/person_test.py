import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("email-empty.yaml", "'' is not a 'email'"),
        ("email-invalid.yaml", "'name@invalid' is not a 'email'"),
        ("github-empty.yaml", "'' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github-invalid.yaml", "'!123' does not match '^[a-zA-Z0-9-]{1,39}$'"),
        ("github-null.yaml", "None is not of type 'string'"),
        ("github-undefined.yaml", "'github' is a required property"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    common_negative_test(common_schema, "person", file_path, error_message)


def test_positive(common_schema):
    common_positive_test(common_schema, "person")
