"""Chapter schema tests."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import tests_data_dir
from utils.schema_validators import validate_data


def test_positive(chapter_schema):
    """Test valid chapter schema cases."""
    for file_path in Path(tests_data_dir / "chapter/positive").rglob("*.yaml"):
        yaml_data = yaml.safe_load(file_path.read_text())
        assert validate_data(chapter_schema, yaml_data) is None


@pytest.mark.parametrize(
    ("file_path", "error_message"),
    [
        ("blog-invalid.yaml", "'invalid-blog-uri' is not a 'uri'"),
        ("blog-null.yaml", "None is not a 'uri'"),
        ("events-empty.yaml", "[] should be non-empty"),
        ("events-non-unique.yaml", "events are non-unique"),
        ("name-empty.yaml", "'' is too short"),
        ("name-none.yaml", "None is not of type 'string'"),
        ("website-null.yaml", "None is not of type 'string'"),
    ],
)
def test_negative(chapter_schema, file_path, error_message):
    """Test invalid chapter schema cases."""
    yaml_data = yaml.safe_load(Path(tests_data_dir / "chapter/negative" / file_path).read_text())
    assert validate_data(chapter_schema, yaml_data) == error_message
