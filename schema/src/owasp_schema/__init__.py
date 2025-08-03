"""OWASP Schema package.

This package provides JSON schemas for OWASP projects.
"""

import importlib.resources
import json

__version__ = "0.1.0"
__author__ = "Arkadii Yakovets <arkadii.yakovets@owasp.org>"
__license__ = "MIT"


# Load all JSON schemas
def _load_schemas():
    """Load all JSON schema files from the package directory."""
    schemas = {}
    for schema_name in ("chapter", "committee", "project", "common"):
        schema_path = importlib.resources.files(__package__).joinpath(f"{schema_name}.json")
        with schema_path.open(encoding="utf-8") as f:
            schemas[schema_name] = json.load(f)

    return schemas


# Load schemas at module import time
SCHEMAS = _load_schemas()


def get_schema(schema_name: str) -> dict:
    """Get a specific schema by name.

    Args:
        schema_name: Name of the schema (without .json extension)

    Returns:
        The schema as a dictionary

    Raises:
        KeyError: If the schema doesn't exist

    """
    if schema_name not in SCHEMAS:
        available_schemas = list(SCHEMAS.keys())
        error_message = f"Schema '{schema_name}' not found. Available schemas: {available_schemas}"
        raise KeyError(error_message)
    return SCHEMAS[schema_name]


def list_schemas() -> list[str]:
    """List all available schema names.

    Returns:
        List of available schema names

    """
    return list(SCHEMAS.keys())


def get_all_schemas() -> dict[str, dict]:
    """Get all available schemas.

    Returns:
        Dictionary mapping schema names to their content

    """
    return SCHEMAS.copy()


chapter_schema = get_schema("chapter")
committee_schema = get_schema("committee")
project_schema = get_schema("project")
common_schema = get_schema("common")

__all__ = [
    "__author__",
    "__license__",
    "__version__",
    "chapter_schema",
    "committee_schema",
    "common_schema",
    "get_all_schemas",
    "get_schema",
    "list_schemas",
    "project_schema",
]
