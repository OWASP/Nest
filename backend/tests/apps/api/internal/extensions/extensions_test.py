"""Tests for extensions __init__ module."""

import pytest


class TestExtensionsModule:
    """Test cases for the extensions module."""

    def test_module_imports_successfully(self):
        """Test that the extensions module can be imported."""
        try:
            import apps.api.internal.extensions  # noqa: F401

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import extensions module: {e}")

    def test_module_has_docstring(self):
        """Test that the extensions module has a docstring."""
        import apps.api.internal.extensions

        assert apps.api.internal.extensions.__doc__ is not None
        assert "Strawberry extensions" in apps.api.internal.extensions.__doc__

    def test_cache_module_is_accessible(self):
        """Test that cache module is accessible from extensions package."""
        try:
            from apps.api.internal.extensions import cache  # noqa: F401

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import cache from extensions: {e}")

    def test_cache_extension_class_is_accessible(self):
        """Test that CacheExtension class is accessible."""
        from apps.api.internal.extensions.cache import CacheExtension

        assert CacheExtension is not None
        assert hasattr(CacheExtension, "resolve")
        assert hasattr(CacheExtension, "ROLE_AWARE_FIELDS")

    def test_cache_functions_are_accessible(self):
        """Test that cache utility functions are accessible."""
        from apps.api.internal.extensions.cache import (
            generate_key,
            invalidate_cache,
            invalidate_module_cache,
            invalidate_program_cache,
        )

        assert callable(generate_key)
        assert callable(invalidate_cache)
        assert callable(invalidate_program_cache)
        assert callable(invalidate_module_cache)

    def test_cache_constants_are_accessible(self):
        """Test that cache constants are accessible."""
        from apps.api.internal.extensions.cache import CACHE_MISS

        assert CACHE_MISS is not None
        assert isinstance(CACHE_MISS, object)
