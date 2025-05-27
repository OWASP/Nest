from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
import pytest


@pytest.fixture
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
def setup_cache():
    cache.clear()
    yield
    cache.clear()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
def test_clear_cache_command(setup_cache):
    cache.set('test_key_1', 'test_value_1')
    cache.set('test_key_2', 'test_value_2')
    cache.set('test_key_3', {'nested': 'data'})
    
    assert cache.get('test_key_1') == 'test_value_1'
    assert cache.get('test_key_2') == 'test_value_2'
    assert cache.get('test_key_3') == {'nested': 'data'}
    
    call_command('clear_cache')
    
    assert cache.get('test_key_1') is None
    assert cache.get('test_key_2') is None
    assert cache.get('test_key_3') is None


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
def test_clear_cache_command_empty_cache(setup_cache):
    cache.clear()
    assert cache.get('any_key') is None
    
    call_command('clear_cache')
    
    assert cache.get('any_key') is None


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
def test_clear_cache_command_with_timeout_keys(setup_cache):
    cache.set('timeout_key', 'timeout_value', timeout=3600)  # 1 hour timeout
    
    assert cache.get('timeout_key') == 'timeout_value'
    
    call_command('clear_cache')
    
    assert cache.get('timeout_key') is None
