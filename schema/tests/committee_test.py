"""Committee schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("community-empty.yaml", "[] should be non-empty"),
        (
            "community-non-unique.yaml",
            "[{'platform': 'discord', 'url': 'https://discord.com/example'}, "
            "{'platform': 'discord', 'url': 'https://discord.com/example'}] "
            "has non-unique elements",
        ),
        ("community-null.yaml", "None is not of type 'array'"),
        ("description-null.yaml", "None is not of type 'string'"),
        ("description-undefined.yaml", "'description' is a required property"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "[{'url': 'https://example.com/event1'}, "
            "{'url': 'https://example.com/event1'}] has non-unique elements",
        ),
        ("events-null.yaml", "None is not of type 'array'"),
        ("mailing_list-empty.yaml", "[] should be non-empty"),
        ("mailing_list-null.yaml", "None is not of type 'array'"),
        ("members-empty.yaml", "[] is too short"),
        ("members-null.yaml", "None is not of type 'array'"),
        ("members-undefined.yaml", "'members' is a required property"),
        ("logo-empty.yaml", "[] should be non-empty"),
        ("logo-null.yaml", "None is not of type 'array'"),
        (
            "logo-non-unique.yaml",
            "[{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}, "
            "{'small': 'https://example.com/smallLogo.png', "
            "'medium': 'https://example.com/mediumLogo.png', "
            "'large': 'https://example.com/largeLogo.png'}] has non-unique elements",
        ),
        ("meeting-minutes-null.yaml", "None is not of type 'array'"),
        ("meeting-minutes-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("name-empty.yaml", "[] should be non-empty"),
        ("name-undefined.yaml", "'name' is a required property"),
        ("resources-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("resources-null.yaml", "None is not of type 'array'"),
        ("scope-null.yaml", "None is not of type 'string'"),
        ("scope-invalid.yaml", "'scope' is a required property"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("sponsors-null.yaml", "None is not of type 'array'"),
        ("tags-empty.yaml", "[] is too short"),
        ("tags-null.yaml", "None is not of type 'array'"),
        ("tags-undefined.yaml", "'tags' is a required property"),
        ("website-empty.yaml", "[] should be non-empty"),
        ("website-null.yaml", "None is not of type 'array'"),
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
