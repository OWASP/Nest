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
        (
            "community-non-unique.yaml",
            "[{'platform': 'discord', 'url': 'https://discord.com/example'}, "
            "{'platform': 'discord', 'url': 'https://discord.com/example'}] "
            "has non-unique elements",
        ),
        ("community-null.yaml", "None is not of type 'array'"),
        ("country-null.yaml", "None is not of type 'string'"),
        ("country-undefined.yaml", "'country' is a required property"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("events-null.yaml", "[] should be non-empty"),
        ("leader-empty.yaml", "[] is too short"),
        ("leader-undefined.yaml", "'leaders' is a required property"),
        ("logo-empty.yaml", "[] should be non-empty"),
        (
            "logo-non-unique.yaml",
            "[{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}, "
            "{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}] has non-unique elements",
        ),
        ("logo-null.yaml", "None is not of type 'array'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        (
            "social-media-non-unique.yaml",
            "[{'platform': 'youtube', 'url': 'https://youtube.com/channel/123'}, "
            "{'platform': 'youtube', 'url': 'https://youtube.com/channel/123'}] "
            "has non-unique elements",
        ),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        (
            "sponsors-non-unique.yaml",
            "[{'name': 'CyberSec Corp', 'url': 'https://cybersec.com'}, "
            "{'name': 'CyberSec Corp', 'url': 'https://cybersec.com'}] has non-unique elements",
        ),
        ("sponsors-null.yaml", "None is not of type 'array'"),
        ("tags-empty.yaml", "[] is too short"),
        ("tags-non-unique.yaml", "['chapter-tag-1', 'chapter-tag-1'] is too short"),
        ("tags-null.yaml", "None is not of type 'array'"),
        ("tags-undefined.yaml", "'tags' is a required property"),
        ("website-empty.yaml", "['example-tag-1'] is too short"),
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
