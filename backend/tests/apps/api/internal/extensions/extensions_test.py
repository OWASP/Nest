"""Tests for extensions __init__ module."""

import apps.api.internal.extensions
from apps.api.internal.extensions import cache
from apps.api.internal.extensions.cache import (
    CACHE_MISS,
    CacheExtension,
    generate_key,
    invalidate_cache,
    invalidate_module_cache,
    invalidate_program_cache,
)


class TestExtensionsModule:
    """Test cases for the extensions module."""

    def test_module_imports_successfully(self):
        """Test that the extensions module can be imported."""
        assert apps.api.internal.extensions is not None

    def test_module_has_docstring(self):
        """Test that the extensions module has a docstring."""
        assert apps.api.internal.extensions.__doc__ is not None
        assert "Strawberry extensions" in apps.api.internal.extensions.__doc__

    def test_cache_module_is_accessible(self):
        """Test that cache module is accessible from extensions package."""
        assert cache is not None

    def test_cache_extension_class_is_accessible(self):
        """Test that CacheExtension class is accessible."""
        assert hasattr(CacheExtension, "resolve")
        assert hasattr(CacheExtension, "ROLE_AWARE_FIELDS")

    def test_cache_functions_are_accessible(self):
        """Test that cache utility functions are accessible."""
        assert callable(generate_key)
        assert callable(invalidate_cache)
        assert callable(invalidate_program_cache)
        assert callable(invalidate_module_cache)

    def test_cache_constants_are_accessible(self):
        """Test that cache constants are accessible."""
        assert CACHE_MISS is not None
        assert CACHE_MISS is not False
        assert CACHE_MISS != ""
        assert CACHE_MISS != 0
