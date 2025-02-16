from pathlib import Path

import pytest
import yaml
from utils.schema_validators import validate_data

from tests.conftest import tests_data_dir


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


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("blog-invalid.yaml", "'invalid-blog-uri' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
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
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        (
            "social-media-platform-invalid.yaml",
            "'bitcoin' is not one of ['bluesky', 'linkedin', 'x', 'youtube']",
        ),
        ("social-media-url-empty.yaml", "'' is not a 'uri'"),
        ("social-media-url-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social-media-url-null.yaml", "None is not of type 'string'"),
        ("mailing-list-empty.yaml", "'' is not a 'uri'"),
        ("mailing-list-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing-list-null.yaml", "None is not a 'uri'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-name-undefined.yaml", "'name' is a required property"),
        ("sponsors-undefined.yaml", "'url' is a required property"),
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
