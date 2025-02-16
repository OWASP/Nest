from pathlib import Path
import pytest
import yaml
from utils.schema_validators import validate_data
from tests.conftest import tests_data_dir


def test_positive(project_schema):
    """Test valid project YAML files to ensure they pass schema validation."""
    for file_path in Path(tests_data_dir / "project/positive").rglob("*.yaml"):
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        try:
            assert validate_data(project_schema, data) is None
        except Exception as e:
            pytest.fail(f"Validation failed for {file_path.name}: {e}")


@pytest.mark.parametrize(
    "file_path, expected_error",
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
        ("demo-invalid.yaml", "'https://invalid/' is not a 'uri'"),
        ("demo-null.yaml", "None is not a 'uri'"),
        ("documentation-empty.yaml", "[] should be non-empty"),
        ("documentation-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("documentation-null.yaml", "None is not of type 'array'"),
        ("downloads-empty.yaml", "[] should be non-empty"),
        ("downloads-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("downloads-non-unique.yaml", "has non-unique elements"),
        ("downloads-null.yaml", "None is not of type 'array'"),
        ("events-empty.yaml", "[] should be non-empty"),
        ("events-non-unique.yaml", "has non-unique elements"),
        ("events-invalid.yaml", "'xyz-abc' is not a 'uri'"),
        ("events-null.yaml", "None is not of type 'array'"),
        ("leaders-email-empty.yaml", "is too short"),
        ("leaders-email-null.yaml", "is too short"),
        ("level-invalid.yaml", "2.5 is not one of [2, 3, 3.5, 4]"),
        ("license-invalid-value.yaml", "'INVALID-LICENSE-VALUE' is not one of"),
        ("mailing-list-empty.yaml", "'' is not a 'uri'"),
        ("mailing-list-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("mailing-list-null.yaml", "None is not a 'uri'"),
        ("name-empty.yaml", "'' is too short"),
        ("name-null.yaml", "None is not of type 'string'"),
        ("repositories-empty.yaml", "[] should be non-empty"),
        ("repositories-non-unique.yaml", "has non-unique elements"),
        ("repositories-null.yaml", "None is not of type 'array'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("social-media-platform-invalid.yaml", "'bitcoin' is not one of"),
        ("social-media-url-empty.yaml", "'' is not a 'uri'"),
        ("social-media-url-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social-media-url-null.yaml", "None is not of type 'string'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-null.yaml", "None is not of type 'array'"),
        ("sponsors-undefined.yaml", "'url' is a required property"),
        ("website-empty.yaml", "'' is too short"),
        ("website-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(project_schema, file_path, expected_error):
    """Test invalid project YAML files to ensure proper validation errors."""
    file_path = Path(tests_data_dir / "project/negative" / file_path)

    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    with pytest.raises(Exception) as exc_info:
        validate_data(project_schema, data)

    error_message = str(exc_info.value)
    assert (
        expected_error in error_message
    ), f"Unexpected error for {file_path.name}: {error_message}"
