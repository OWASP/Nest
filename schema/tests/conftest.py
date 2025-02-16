import json
from pathlib import Path
import pytest

# Resolve paths
TESTS_DIR = Path(__file__).resolve().parent
TESTS_DATA_DIR = TESTS_DIR / "data"
SCHEMA_DIR = TESTS_DIR.parent


def load_json(file_path):
    """Helper function to load JSON files safely."""
    try:
        with file_path.open() as file:
            return json.load(file)
    except FileNotFoundError:
        pytest.fail(f"File not found: {file_path}")
    except json.JSONDecodeError:
        pytest.fail(f"Invalid JSON format: {file_path}")


@pytest.fixture
def chapter_schema():
    """Fixture to load the chapter schema JSON."""
    return load_json(SCHEMA_DIR / "chapter.json")


@pytest.fixture
def project_schema():
    """Fixture to load the project schema JSON."""
    return load_json(SCHEMA_DIR / "project.json")
