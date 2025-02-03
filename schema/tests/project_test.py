from pathlib import Path

import pytest
import yaml
from utils.validators import validate_data

from tests.conftest import tests_data_dir


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
        ("audience-missing.yaml", "'audience' is a required property"),
        ("demo-none.yaml", "None is not of type 'string'"),
        ("events-empty.yaml", "[] should be non-empty"),
        (
            "events-non-unique-urls.yaml",
            "['https://example.com/event1', 'https://example.com/event1'] has non-unique elements",
        ),
        ("level-invalid.yaml", "2.5 is not one of [2, 3, 3.5, 4]"),
        (
            "license-invalid-value.yaml",
            "'INVALID-LICENSE-VALUE' is not one of ['AGPL-3.0', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'EUPL-1.2', 'GPL-2.0', 'GPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MIT', 'MPL-2.0', 'OTHER']",
        ),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("sponsors-empty-list.yaml", "[] should be non-empty"),
        ("sponsors-name-missing.yaml", "'name' is a required property"),
        ("sponsors-url-missing.yaml", "'url' is a required property"),
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
