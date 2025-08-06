"""Tests for the owasp_schema package."""

import pytest

from owasp_schema import __version__, get_all_schemas, get_schema, list_schemas


def test_list_schemas():
    """Test that list_schemas returns expected schema names."""
    schemas = list_schemas()
    assert isinstance(schemas, list)
    assert "chapter" in schemas
    assert "committee" in schemas
    assert "project" in schemas


def test_get_schema():
    """Test that get_schema returns valid schema data."""
    chapter_schema = get_schema("chapter")
    assert isinstance(chapter_schema, dict)
    assert "$schema" in chapter_schema
    assert "title" in chapter_schema


def test_get_schema_invalid():
    """Test that get_schema raises KeyError for invalid schema names."""
    with pytest.raises(KeyError):
        get_schema("nonexistent_schema")


def test_get_all_schemas():
    """Test that get_all_schemas returns all schemas."""
    all_schemas = get_all_schemas()
    assert isinstance(all_schemas, dict)
    assert "chapter" in all_schemas
    assert "committee" in all_schemas
    assert "project" in all_schemas


def test_schema_structure():
    """Test that schemas have expected structure."""
    chapter_schema = get_schema("chapter")
    committee_schema = get_schema("committee")
    project_schema = get_schema("project")

    # Check that all schemas have required fields
    for schema_name, schema in [
        ("chapter", chapter_schema),
        ("committee", committee_schema),
        ("project", project_schema),
    ]:
        assert "$schema" in schema, f"Schema {schema_name} missing $schema"
        assert "title" in schema, f"Schema {schema_name} missing title"
        assert "type" in schema, f"Schema {schema_name} missing type"


def test_package_version():
    """Test that package version is accessible."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"
