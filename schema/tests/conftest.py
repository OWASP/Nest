import json
from pathlib import Path
import pytest

# Resolve paths
TESTS_DIR = Path(__file__).resolve().parent
TESTS_DATA_DIR = TESTS_DIR / "data"
SCHEMA_DIR = TESTS_DIR.parent / "schema"  # Updated to point to schema directory


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
def tests_data_dir():
    """Fixture to provide the test data directory path."""
    return TESTS_DATA_DIR


@pytest.fixture
def chapter_schema():
    """Fixture to load the chapter schema JSON."""
    schema_path = SCHEMA_DIR / "chapter.json"
    schema = load_json(schema_path)
    
    # Load referenced schema files
    definitions_dir = SCHEMA_DIR / "definitions"
    for ref_file in definitions_dir.glob("*.json"):
        ref_schema = load_json(ref_file)
        # Store definition in schema if needed
        if "$defs" not in schema:
            schema["$defs"] = {}
        schema["$defs"][ref_file.stem] = ref_schema
    
    return schema


@pytest.fixture
def project_schema():
    """Fixture to load the project schema JSON."""
    schema_path = SCHEMA_DIR / "project.json"
    schema = load_json(schema_path)
    
    # Load referenced schema files
    definitions_dir = SCHEMA_DIR / "definitions"
    for ref_file in definitions_dir.glob("*.json"):
        ref_schema = load_json(ref_file)
        # Store definition in schema if needed
        if "$defs" not in schema:
            schema["$defs"] = {}
        schema["$defs"][ref_file.stem] = ref_schema
    
    return schema


def pytest_sessionstart(session):
    """Create necessary test directories at the start of test session."""
    # Create test data directories if they don't exist
    for test_type in ["chapter", "project"]:
        for case_type in ["positive", "negative"]:
            (TESTS_DATA_DIR / test_type / case_type).mkdir(parents=True, exist_ok=True)


# Export the paths for use in tests
tests_data_dir = TESTS_DATA_DIR
schema_dir = SCHEMA_DIR
