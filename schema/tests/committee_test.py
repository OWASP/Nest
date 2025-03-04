"""Committee schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("community_empty.yaml", "[] should be non-empty"),
        (
            "community_non_unique.yaml",
            "[{'platform': 'discord', 'url': 'https://discord.com/example'}, "
            "{'platform': 'discord', 'url': 'https://discord.com/example'}] "
            "has non-unique elements",
        ),
        ("community_null.yaml", "None is not of type 'array'"),
        ("description_null.yaml", "None is not of type 'string'"),
        ("description_undefined.yaml", "'description' is a required property"),
        ("events_empty.yaml", "[] should be non-empty"),
        ("events_invalid.yaml", "'xyz-abc' is not a 'uri'"),
        (
            "events_non_unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("events_null.yaml", "None is not of type 'array'"),
        ("group_mail_empty.yaml", "'' is not a 'email'"),
        ("group_mail_null.yaml", "None is not a 'email'"),
        ("members_empty.yaml", "[] is too short"),
        ("members_null.yaml", "None is not of type 'array'"),
        ("members_undefined.yaml", "'members' is a required property"),
        ("logo_empty.yaml", "[] should be non-empty"),
        ("logo_null.yaml", "None is not of type 'array'"),
        (
            "logo_non_unique.yaml",
            "[{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}, "
            "{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}] has non-unique elements",
        ),
        ("meeting_minutes_null.yaml", "None is not of type 'array'"),
        ("meeting_minutes_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("name_empty.yaml", "'' is too short"),
        ("name_undefined.yaml", "'name' is a required property"),
        ("resources_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("resources_null.yaml", "None is not of type 'array'"),
        ("scope_null.yaml", "None is not of type 'string'"),
        ("scope_invalid.yaml", "'scope' is a required property"),
        ("social_media_empty.yaml", "[] should be non-empty"),
        ("social_media_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social_media_null.yaml", "None is not of type 'array'"),
        ("sponsors_empty.yaml", "[] should be non-empty"),
        ("sponsors_invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("sponsors_null.yaml", "None is not of type 'array'"),
        ("tags_empty.yaml", "[] is too short"),
        ("tags_null.yaml", "None is not of type 'array'"),
        ("tags_undefined.yaml", "'tags' is a required property"),
        ("website_empty.yaml", "'' is not a 'uri'"),
        ("website_invalid_url.yaml", "'https://xyz' is not a 'uri'"),
        ("website_null.yaml", "None is not a 'uri'"),
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
