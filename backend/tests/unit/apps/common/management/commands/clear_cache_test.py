"""Tests for the clear_cache Django management command."""

import pytest
from django.core.cache import cache
from django.core.management import call_command


class TestClearCacheCommand:
    """Test suite for the clear_cache management command."""

    @pytest.fixture(autouse=True)
    def _setup_cache(self):
        cache.clear()
        yield
        cache.clear()

    def _assert_cache_data(self, data):
        for key, expected_value in data.items():
            assert cache.get(key) == expected_value

    def _assert_cache_no_data(self, data):
        for key in data:
            assert cache.get(key) is None

    def test_clear_cache_command(self):
        test_data = {
            "test_key_1": "test_value_1",
            "test_key_2": "test_value_2",
            "test_key_3": {"nested": "data"},
        }

        for key, value in test_data.items():
            cache.set(key, value)

        self._assert_cache_data(test_data)

        call_command("clear_cache")

        self._assert_cache_no_data(test_data)

    def test_clear_cache_command_empty_cache(self):
        assert cache.get("any_key") is None

        call_command("clear_cache")

        assert cache.get("any_key") is None

    def test_clear_cache_command_timeout(self):
        cache.set("timeout_key", "timeout_value", timeout=3600)
        assert cache.get("timeout_key") == "timeout_value"

        call_command("clear_cache")

        assert cache.get("timeout_key") is None
