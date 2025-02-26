"""Committee schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


def test_positive(committee_schema):
    for file_path in Path(tests_data_dir / "committee/positive").rglob("*.yaml"):
        assert (
            validate_data(
                committee_schema,
                yaml.safe_load(
                    file_path.read_text(),
                ),
            )
            is None
        )


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("community-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("community-null.yaml", "None is not of type 'array'"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("description-undefined.yaml", "'description' is a required property"),
        ("events-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("events-null.yaml", "None is not of type 'array'"),
        ("leaders-empty.yaml", "[] is too short"),
        ("leaders-null.yaml", "None is not of type 'array'"),
        ("leaders-undefined.yaml", "'leaders' is a required property"),
        ("logo-large-empty.yaml", "'' is not a 'uri'"),
        ("logo-large-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-large-null.yaml", "None is not a 'uri'"),
        ("logo-medium-empty.yaml", "'' is not a 'uri'"),
        ("logo-medium-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-medium-null.yaml", "None is not a 'uri'"),
        ("logo-small-empty.yaml", "'' is not a 'uri'"),
        ("logo-small-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-small-null.yaml", "None is not a 'uri'"),
        ("mailing-list-empty.yaml", "'' is not a 'uri'"),
        ("mailing-list-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing-list-null.yaml", "None is not a 'uri'"),
        ("meeting-minutes-null.yaml", "None is not of type 'array'"),
        ("meeting-minutes-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("pitch-empty.yaml", "'' is too short"),
        ("resources-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("resources-null.yaml", "None is not of type 'array'"),
        ("scope-null.yaml", "None is not of type 'string'"),
        ("scope-invalid.yaml", "'scope' is a required property"),
        ("social-media-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("sponsors-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("sponsors-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("tags-empty.yaml", "[] is too short"),
        ("tags-null.yaml", "None is not of type 'array'"),
        ("tags-undefined.yaml", "'tags' is a required property"),
        ("website-empty.yaml", "'' is not a 'uri'"),
        ("website-null.yaml", "None is not a 'uri'"),
        ("website-invalid-url.yaml", "'https://xyz' is not a 'uri'"),
    ],
)
def test_negative(committee_schema, file_path, error_message):
    assert (
        validate_data(
            committee_schema,
            yaml.safe_load(
                Path(tests_data_dir / "committee/negative" / file_path).read_text(),
            ),
        )
        == error_message
    )
