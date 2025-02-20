"""Project schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


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


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        (
            "audience-invalid.yaml",
            "'hacker' is not one of ['breaker', 'builder', 'defender']",
        ),
        ("audience-empty.yaml", "'' is not one of ['breaker', 'builder', 'defender']"),
        ("audience-null.yaml", "None is not one of ['breaker', 'builder', 'defender']"),
        ("audience-undefined.yaml", "'audience' is a required property"),
        ("blog-invalid.yaml", "'https://invalid/' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
        ("community-empty.yaml", "[] should be non-empty"),
        (
            "community-invalid.yaml",
            "'another-invalid-url' is not a 'uri'",
        ),
        ("community-null.yaml", "None is not of type 'array'"),
        ("demo-empty.yaml", "[] should be non-empty"),
        ("demo-invalid.yaml", "'https://invalid/' is not a 'uri'"),
        (
            "demo-non-unique.yaml",
            "['https://example.com/', 'https://example.com/'] has non-unique elements",
        ),
        ("demo-null.yaml", "None is not of type 'array'"),
        ("documentation-empty.yaml", "[] should be non-empty"),
        (
            "documentation-invalid.yaml",
            "'xyz-abc' is not a 'uri'",
        ),
        ("documentation-null.yaml", "None is not of type 'array'"),
        ("downloads-empty.yaml", "[] should be non-empty"),
        (
            "downloads-invalid.yaml",
            "'xyz-abc' is not a 'uri'",
        ),
        (
            "downloads-non-unique.yaml",
            "['https://abc.com/download', 'https://abc.com/download'] has non-unique elements",
        ),
        ("downloads-null.yaml", "None is not of type 'array'"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("events-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("events-null.yaml", "None is not of type 'array'"),
        ("level-invalid.yaml", "2.5 is not one of [2, 3, 3.5, 4]"),
        (
            "license-invalid-value.yaml",
            "'INVALID-LICENSE-VALUE' is not one of ['AGPL-3.0', 'Apache-2.0', 'BSD-2-Clause', "
            "'BSD-3-Clause', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'EUPL-1.2', 'GPL-2.0', "
            "'GPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MIT', 'MPL-2.0', 'OTHER']",
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
        ("mailing-list-empty.yaml", "'' is not a 'uri'"),
        ("mailing-list-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing-list-null.yaml", "None is not a 'uri'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("repositories-changelog-empty.yaml", "'' is not a 'uri'"),
        ("repositories-changelog-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("repositories-changelog-null.yaml", "None is not a 'uri'"),
        ("repositories-code-of-conduct-empty.yaml", "'' is not a 'uri'"),
        ("repositories-code-of-conduct-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("repositories-code-of-conduct-null.yaml", "None is not a 'uri'"),
        ("repositories-contribution-guide-empty.yaml", "'' is not a 'uri'"),
        ("repositories-contribution-guide-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("repositories-contribution-guide-null.yaml", "None is not a 'uri'"),
        ("repositories-empty.yaml", "[] should be non-empty"),
        (
            "repositories-non-unique.yaml",
            "['https://example.com/repo1', 'https://example.com/repo1'] has non-unique elements",
        ),
        ("repositories-null.yaml", "None is not of type 'array'"),
        ("repositories-url-empty.yaml", "'' is not a 'uri'"),
        ("repositories-url-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("repositories-url-null.yaml", "None is not of type 'string'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-null.yaml", "None is not of type 'array'"),
        ("sponsors-undefined.yaml", "'url' is a required property"),
        ("website-empty.yaml", "'' is too short"),
        ("website-null.yaml", "None is not of type 'string'"),
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
