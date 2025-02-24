"""Chapter schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("blog-invalid.yaml", "'invalid-blog-uri' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
        ("community-empty.yaml", "[] should be non-empty"),
        ("community-null.yaml", "None is not of type 'array'"),
        ("community-non-unique.yaml", "has non-unique elements"),
        ("country-empty.yaml", "'' is too short"),
        ("country-null.yaml", "None is not of type 'string'"),
        ("country-undefined.yaml", "'country' is a required property"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("events-null.yaml", "None is not of type 'array'"),
        ("leader-empty.yaml", "[] is too short"),
        ("leader-undefined.yaml", "'leader' is a required property"),
        ("logo-empty.yaml", "[] should be non-empty"),
        ("logo-non-unique.yaml", "has non-unique elements"),
        ("logo-null.yaml", "None is not of type 'array'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-non-unique.yaml", "has non-unique elements"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-non-unique.yaml", "has non-unique elements"),
        ("sponsors-null.yaml", "Additional properties are not allowed ('sponsor' was unexpected)"),
        ("tags-empty.yaml", "[] should be non-empty"),
        ("tags-non-unique.yaml", "has non-unique elements"),
        ("tags-null.yaml", "None is not of type 'array'"),
        ("tags-undefined.yaml", "'tags' is a required property"),
        ("website-empty.yaml", "'' is too short"),
        ("website-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(chapter_schema, file_path, error_message):
    assert (
        validate_data(
            chapter_schema,
            yaml.safe_load(
                Path(tests_data_dir / "chapter/negative" / file_path).read_text(),
            ),
        )
        == error_message
    )


def test_positive(chapter_schema):
    for file_path in Path(tests_data_dir / "chapter/positive").rglob("*.yaml"):
        assert (
            validate_data(
                chapter_schema,
                yaml.safe_load(
                    file_path.read_text(),
                ),
            )
            is None
        )
