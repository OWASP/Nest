from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
import pytest


# cache configuration
TEST_CACHE_SETTINGS = {
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    }
}


@pytest.fixture
@override_settings(**TEST_CACHE_SETTINGS)
def setup_cache():
    cache.clear()
    yield
    cache.clear()


def assert_cache_keys_exist(keys_values):
    for key, expected_value in keys_values.items():
        assert cache.get(key) == expected_value


def assert_cache_keys_none(keys):
    for key in keys:
        assert cache.get(key) is None


@override_settings(**TEST_CACHE_SETTINGS)
def test_clear_cache_command(setup_cache):
    test_data = {
        'test_key_1': 'test_value_1',
        'test_key_2': 'test_value_2',
        'test_key_3': {'nested': 'data'}
    }
    
    for key, value in test_data.items():
        cache.set(key, value)
    
    assert_cache_keys_exist(test_data)
    
    call_command('clear_cache')
    
    assert_cache_keys_none(test_data.keys())


@override_settings(**TEST_CACHE_SETTINGS)
def test_clear_cache_command_empty_cache(setup_cache):
    cache.clear()
    assert cache.get('any_key') is None
    
    call_command('clear_cache')
    
    assert cache.get('any_key') is None


@override_settings(**TEST_CACHE_SETTINGS)
def test_clear_cache_command_with_timeout_keys(setup_cache):
    cache.set('timeout_key', 'timeout_value', timeout=3600)  # 1 hour timeout
    
    assert cache.get('timeout_key') == 'timeout_value'
    
    call_command('clear_cache')
    
    assert cache.get('timeout_key') is None
