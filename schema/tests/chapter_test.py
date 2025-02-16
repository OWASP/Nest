from pathlib import Path
import pytest
import yaml
from utils.schema_validators import validate_data
from tests.conftest import tests_data_dir


def test_positive(chapter_schema):
    """Test valid chapter YAML files to ensure they pass schema validation."""
    for file_path in Path(tests_data_dir / "chapter/positive").rglob("*.yaml"):
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        try:
            assert validate_data(chapter_schema, data) is None
        except Exception as e:
            pytest.fail(f"Validation failed for {file_path.name}: {e}")


@pytest.mark.parametrize(
    "file_path, expected_error",
    [
        ("blog-invalid.yaml", "'invalid-blog-uri' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
        ("events-empty.yaml", "[] should be non-empty"),
        ("events-non-unique.yaml", "has non-unique elements"),
        ("leader-email-empty.yaml", "is too short"),
        ("leader-email-null.yaml", "is too short"),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("social-media-empty.yaml", "[] should be non-empty"),
        ("social-media-null.yaml", "None is not of type 'array'"),
        ("social-media-platform-invalid.yaml", "'bitcoin' is not one of"),
        ("social-media-url-empty.yaml", "'' is not a 'uri'"),
        ("social-media-url-invalid.yaml", "'https://xyz' is not a 'uri'"),
        ("social-media-url-null.yaml", "None is not of type 'string'"),
        ("sponsors-empty.yaml", "[] should be non-empty"),
        ("sponsors-name-undefined.yaml", "'name' is a required property"),
        ("sponsors-undefined.yaml", "'url' is a required property"),
        ("website-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(chapter_schema, file_path, expected_error):
    """Test invalid chapter YAML files to ensure proper validation errors."""
    file_path = Path(tests_data_dir / "chapter/negative" / file_path)

    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    with pytest.raises(Exception) as exc_info:
        validate_data(chapter_schema, data)

    error_message = str(exc_info.value)
    assert (
        expected_error in error_message
    ), f"Unexpected error for {file_path.name}: {error_message}"
