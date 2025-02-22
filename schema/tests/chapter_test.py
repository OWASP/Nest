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
        (
            "community-empty.yaml",
            "Additional properties are not allowed ('level' was unexpected)",
        ),
        ("community-null.yaml", "None is not of type 'array'"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        (
            "leader-email-empty.yaml",
            "[{'email': '', 'github': 'leader-1-github', 'name': 'Leader 1 Name'}] is too short",
        ),
        (
            "leader-email-null.yaml",
            "[{'email': None, 'github': 'leader-1-github', 'name': 'Leader 1 Name'}] is too short",
        ),
        ("logo-large-empty.yaml", "'' is not a 'uri'"),
        ("logo-large-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-large-null.yaml", "None is not of type 'string'"),
        ("logo-medium-empty.yaml", "'' is not a 'uri'"),
        ("logo-medium-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-medium-null.yaml", "None is not of type 'string'"),
        ("logo-small-empty.yaml", "'' is not a 'uri'"),
        ("logo-small-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("logo-small-null.yaml", "None is not of type 'string'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
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
