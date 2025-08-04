"""Project schema tests."""

from pathlib import Path

import pytest
import yaml

from owasp_schema.utils.schema_validators import validate_data
from tests.conftest import tests_data_dir


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        (
            "audience_invalid.yaml",
            "'hacker' is not one of ['breaker', 'builder', 'defender']",
        ),
        ("audience_empty.yaml", "'' is not one of ['breaker', 'builder', 'defender']"),
        ("audience_null.yaml", "None is not one of ['breaker', 'builder', 'defender']"),
        ("audience_undefined.yaml", "'audience' is a required property"),
        ("blog_empty.yaml", "'' is not a 'uri'"),
        ("blog_invalid.yaml", "'https://invalid/' is not a 'uri'"),
        ("blog_null.yaml", "None is not a 'uri'"),
        ("community_empty.yaml", "[] should be non-empty"),
        (
            "community_non_unique.yaml",
            "[{'platform': 'discord', 'url': 'https://discord.com/example'}, "
            "{'platform': 'discord', 'url': 'https://discord.com/example'}] "
            "has non-unique elements",
        ),
        ("community_null.yaml", "None is not of type 'array'"),
        ("demo_empty.yaml", "[] should be non-empty"),
        ("demo_invalid.yaml", "'https://invalid/' is not a 'uri'"),
        (
            "demo_non_unique.yaml",
            "['https://example.com/', 'https://example.com/'] has non-unique elements",
        ),
        ("demo_null.yaml", "None is not of type 'array'"),
        ("documentation_empty.yaml", "[] should be non-empty"),
        (
            "documentation_invalid.yaml",
            "'xyz-abc' is not a 'uri'",
        ),
        (
            "documentation_non_unique.yaml",
            "['https://example.com/docs', 'https://example.com/docs'] has non-unique elements",
        ),
        ("documentation_null.yaml", "None is not of type 'array'"),
        ("downloads_empty.yaml", "[] should be non-empty"),
        (
            "downloads_invalid.yaml",
            "'xyz-abc' is not a 'uri'",
        ),
        (
            "downloads_non_unique.yaml",
            "['https://abc.com/download', 'https://abc.com/download'] has non-unique elements",
        ),
        ("downloads_null.yaml", "None is not of type 'array'"),
        ("events_empty.yaml", "[] should be non-empty"),
        (
            "events_non_unique.yaml",
            "[{'url': 'https://example.com/event1'}, "
            "{'url': 'https://example.com/event1'}] has non-unique elements",
        ),
        ("events_null.yaml", "None is not of type 'array'"),
        ("leaders_empty.yaml", "[] is too short"),
        (
            "leaders_non_unique.yaml",
            "[{'github': 'leader1'}, {'github': 'leader1'}] has non-unique elements",
        ),
        ("leaders_null.yaml", "None is not of type 'array'"),
        ("leaders_undefined.yaml", "'leaders' is a required property"),
        ("level_invalid.yaml", "2.5 is not one of [2, 3, 3.5, 4]"),
        ("level_undefined.yaml", "'level' is a required property"),
        (
            "license_invalid.yaml",
            "'INVALID-LICENSE-VALUE' is not one of ['AGPL-3.0', 'Apache-2.0', 'BSD-2-Clause', "
            "'BSD-3-Clause', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'EUPL-1.2', 'GPL-2.0', "
            "'GPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MIT', 'MPL-2.0', 'OTHER']",
        ),
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
        ("mailing_list_empty.yaml", "'' is not of type 'array'"),
        ("mailing_list_invalid.yaml", "'https://xyz' is not of type 'array'"),
        ("mailing_list_null.yaml", "None is not of type 'array'"),
        ("name_empty.yaml", "'' is too short"),
        ("name_null.yaml", "None is not of type 'string'"),
        ("name_undefined.yaml", "'name' is a required property"),
        ("pitch_empty.yaml", "'' is too short"),
        ("pitch_null.yaml", "None is not of type 'string'"),
        ("pitch_undefined.yaml", "'pitch' is a required property"),
        ("repositories_empty.yaml", "[] should be non-empty"),
        (
            "repositories_non_unique.yaml",
            "[{'url': 'https://repo1.com'}, {'url': 'https://repo1.com'}] has non-unique elements",
        ),
        ("repositories_null.yaml", "None is not of type 'array'"),
        ("social_media_empty.yaml", "[] should be non-empty"),
        (
            "social_media_non_unique.yaml",
            "[{'platform': 'x', 'url': 'https://x.com'}, "
            "{'platform': 'x', 'url': 'https://x.com'}] has non-unique elements",
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
        ("tags_null.yaml", "None is not of type 'array'"),
        (
            "tags_non_unique.yaml",
            "['example-tag-1', 'example-tag-1', 'example-tag-1'] has non-unique elements",
        ),
        ("tags_undefined.yaml", "'tags' is a required property"),
        ("type_empty.yaml", "'' is not one of ['code', 'documentation', 'tool']"),
        ("type_null.yaml", "None is not one of ['code', 'documentation', 'tool']"),
        ("type_undefined.yaml", "'type' is a required property"),
        ("website_empty.yaml", "'' is not a 'uri'"),
        ("website_null.yaml", "None is not a 'uri'"),
    ],
)
def test_negative(project_schema, file_path, error_message):
    assert (
        validate_data(
            project_schema,
            yaml.safe_load(
                Path(tests_data_dir / "project/negative" / file_path).read_text(),
            ),
        )
        == error_message
    )


def test_positive(project_schema):
    for file_path in Path(tests_data_dir / "project/positive").rglob("*.yaml"):
        assert (
            validate_data(
                project_schema,
                yaml.safe_load(
                    file_path.read_text(),
                ),
            )
            is None
        )
