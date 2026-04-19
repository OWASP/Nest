"""Tests for semantic cache service."""

from unittest.mock import Mock, patch

from apps.ai.models.semantic_cache import SemanticCache
from apps.ai.semantic_cache import get_cached_response, store_cached_response


class TestGetCachedResponse:
    @patch("apps.ai.semantic_cache._config")
    @patch("apps.ai.semantic_cache.SemanticCache.get_cached_response")
    def test_delegates_to_model_when_enabled(self, mock_model_get, mock_config):
        mock_config.semantic_cache_enabled = True
        mock_config.semantic_cache_similarity_threshold = 0.95
        mock_config.semantic_cache_ttl_seconds = 86400
        mock_model_get.return_value = "cached response"

        result = get_cached_response("test query 1")

        assert result == "cached response"
        mock_model_get.assert_called_once_with(
            "test query 1",
            similarity_threshold=0.95,
            ttl_seconds=86400,
        )

    @patch("apps.ai.semantic_cache._config")
    @patch("apps.ai.semantic_cache.SemanticCache.get_cached_response")
    def test_returns_none_when_disabled(self, mock_model_get, mock_config):
        mock_config.semantic_cache_enabled = False

        result = get_cached_response("test query 2")

        assert result is None
        mock_model_get.assert_not_called()


class TestStoreCachedResponse:
    @patch("apps.ai.semantic_cache._config")
    @patch("apps.ai.semantic_cache.SemanticCache.store_response")
    def test_delegates_to_model_when_enabled(self, mock_model_store, mock_config):
        mock_config.semantic_cache_enabled = True
        mock_entry = Mock(spec=SemanticCache)
        mock_model_store.return_value = mock_entry

        result = store_cached_response(
            query="test query 3",
            response="test response 1",
            intent="rag",
            confidence=0.9,
        )

        assert result == mock_entry
        mock_model_store.assert_called_once_with(
            query="test query 3",
            response="test response 1",
            intent="rag",
            confidence=0.9,
        )

    @patch("apps.ai.semantic_cache._config")
    @patch("apps.ai.semantic_cache.SemanticCache.store_response")
    def test_returns_none_when_disabled(self, mock_model_store, mock_config):
        mock_config.semantic_cache_enabled = False

        result = store_cached_response(
            query="test query",
            response="test response",
        )

        assert result is None
        mock_model_store.assert_not_called()

    @patch("apps.ai.semantic_cache._config")
    @patch("apps.ai.semantic_cache.SemanticCache.store_response")
    def test_default_intent_and_confidence(self, mock_model_store, mock_config):
        mock_config.semantic_cache_enabled = True
        mock_model_store.return_value = Mock(spec=SemanticCache)

        store_cached_response(query="test", response="resp")

        mock_model_store.assert_called_once_with(
            query="test",
            response="resp",
            intent="",
            confidence=0.0,
        )
