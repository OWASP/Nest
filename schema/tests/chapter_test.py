"""Chapter schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("blog_empty.yaml", "'' is not a 'uri'"),
        ("blog_invalid.yaml", "'invalid-blog-uri' is not a 'uri'"),
        ("blog_null.yaml", "None is not a 'uri'"),
        ("community_empty.yaml", "[] should be non-empty"),
        (
            "community_non_unique.yaml",
            "[{'platform': 'discord', 'url': 'https://discord.com/example'}, "
            "{'platform': 'discord', 'url': 'https://discord.com/example'}] "
            "has non-unique elements",
        ),
        ("community_null.yaml", "None is not of type 'array'"),
        ("country_empty.yaml", "'' should be non-empty"),
        ("country_null.yaml", "None is not of type 'string'"),
        ("country_undefined.yaml", "'country' is a required property"),
        ("events_empty.yaml", "[] should be non-empty"),
        (
            "events_non_unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("events_null.yaml", "None is not of type 'array'"),
        ("leaders_empty.yaml", "[] is too short"),
        (
            "leaders_non_unique.yaml",
            "[{'github': 'leader1'}, {'github': 'leader1'}] has non-unique elements",
        ),
        ("leaders_null.yaml", "None is not of type 'array'"),
        ("leaders_undefined.yaml", "'leaders' is a required property"),
        ("logo_empty.yaml", "[] should be non-empty"),
        (
            "logo_non_unique.yaml",
            "[{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}, "
            "{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}] has non-unique elements",
        ),
        ("logo_null.yaml", "None is not of type 'array'"),
        ("meetup_group_empty.yaml", "'' should be non-empty"),
        ("meetup_group_null.yaml", "None is not of type 'string'"),
        ("mailing_list_empty.yaml", "'' is not a 'uri'"),
        ("mailing_list_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing_list_null.yaml", "None is not a 'uri'"),
        ("name_empty.yaml", "'' is too short"),
        ("name_null.yaml", "None is not of type 'string'"),
        ("name_undefined.yaml", "'name' is a required property"),
        ("region_empty.yaml", "'' should be non-empty"),
        ("region_null.yaml", "None is not of type 'string'"),
        ("social_media_empty.yaml", "[] should be non-empty"),
        (
            "social_media_non_unique.yaml",
            "[{'platform': 'youtube', 'url': 'https://youtube.com/channel/123'}, "
            "{'platform': 'youtube', 'url': 'https://youtube.com/channel/123'}] "
            "has non-unique elements",
        ),
        ("social_media_null.yaml", "None is not of type 'array'"),
        ("sponsors_empty.yaml", "[] should be non-empty"),
        (
            "sponsors_non_unique.yaml",
            "[{'name': 'CyberSec Corp', 'url': 'https://cybersec.com'}, "
            "{'name': 'CyberSec Corp', 'url': 'https://cybersec.com'}] has non-unique elements",
        ),
        ("sponsors_null.yaml", "None is not of type 'array'"),
        ("tags_empty.yaml", "[] is too short"),
        ("tags_non_unique.yaml", "['chapter-tag-1', 'chapter-tag-1'] is too short"),
        ("tags_null.yaml", "None is not of type 'array'"),
        ("tags_undefined.yaml", "'tags' is a required property"),
        ("website_empty.yaml", "['example-tag-1'] is too short"),
        ("website_null.yaml", "None is not of type 'string'"),
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
