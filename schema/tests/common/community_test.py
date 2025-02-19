import pytest

from tests.conftest import common_negative_test, common_positive_test


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("description-empty.yaml", "'' is not a description"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("platform-empty.yaml", "'' is not one of ['discord', 'slack']"),
        ("platform-invalid.yaml", "'telegram' is not one of ['discord', 'slack']"),
        ("platform-null.yaml", "None is not one of ['discord', 'slack']"),
        ("url-empty.yaml", "'' is not a 'uri'"),
        ("url-invalid.yaml", "'discord.com/invalid' is not a 'uri'"),
        ("url-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(common_schema, file_path, error_message):
    common_negative_test(common_schema, "community", file_path, error_message)


def test_positive(common_schema):
    common_positive_test(common_schema, "community")