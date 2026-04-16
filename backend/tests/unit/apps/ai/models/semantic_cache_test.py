"""Tests for SemanticCache model."""

import math
from unittest.mock import Mock, patch

from apps.ai.models.chunk import EMBEDDING_DIMENSIONS
from apps.ai.models.semantic_cache import SemanticCache
from apps.common.models import TimestampedModel


class TestSemanticCacheModel:
    def test_meta_class_attributes(self):
        assert SemanticCache._meta.db_table == "ai_semantic_cache"
        assert SemanticCache._meta.verbose_name == "Semantic Cache"

    def test_inheritance_from_timestamped_model(self):
        assert issubclass(SemanticCache, TimestampedModel)

    def test_confidence_field_properties(self):
        field = SemanticCache._meta.get_field("confidence")
        assert math.isclose(field.default, 0.0)
        assert field.verbose_name == "Confidence"

    def test_intent_field_properties(self):
        field = SemanticCache._meta.get_field("intent")
        assert field.max_length == 50
        assert field.blank is True
        assert field.default == ""
        assert field.verbose_name == "Intent"

    def test_query_embedding_field_properties(self):
        field = SemanticCache._meta.get_field("query_embedding")
        assert field.verbose_name == "Query Embedding"
        assert field.dimensions == EMBEDDING_DIMENSIONS

    def test_query_text_field_properties(self):
        field = SemanticCache._meta.get_field("query_text")
        assert field.verbose_name == "Query Text"

    def test_response_text_field_properties(self):
        field = SemanticCache._meta.get_field("response_text")
        assert field.verbose_name == "Response Text"

    def test_str_method(self):
        cache = SemanticCache()
        cache.id = 42
        cache.query_text = "What is OWASP Top 10?"
        result = str(cache)
        assert "SemanticCache 42" in result
        assert "What is OWASP Top 10?" in result

    def test_str_method_truncates_long_query(self):
        cache = SemanticCache()
        cache.id = 1
        cache.query_text = "A" * 200
        result = str(cache)
        assert "SemanticCache 1" in result
        assert len(result) < 200


class TestSemanticCacheGetCachedResponse:
    @patch("apps.ai.embeddings.factory.get_embedder")
    @patch("apps.ai.models.semantic_cache.SemanticCache.objects")
    def test_cache_hit_returns_response_text(self, mock_objects, mock_get_embedder):
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * EMBEDDING_DIMENSIONS
        mock_get_embedder.return_value = mock_embedder

        mock_result = Mock()
        mock_result.id = 1
        mock_result.distance = 0.02
        mock_result.response_text = "Cached response"

        (
            mock_objects.filter.return_value.annotate.return_value.filter
        ).return_value.order_by.return_value.first.return_value = mock_result

        result = SemanticCache.get_cached_response("test query 1")

        assert result == "Cached response"
        mock_embedder.embed_query.assert_called_once_with("test query 1")

    @patch("apps.ai.embeddings.factory.get_embedder")
    @patch("apps.ai.models.semantic_cache.SemanticCache.objects")
    def test_cache_miss_returns_none(self, mock_objects, mock_get_embedder):
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * EMBEDDING_DIMENSIONS
        mock_get_embedder.return_value = mock_embedder

        (
            mock_objects.filter.return_value.annotate.return_value.filter
        ).return_value.order_by.return_value.first.return_value = None

        result = SemanticCache.get_cached_response("unknown query")

        assert result is None

    @patch("apps.ai.embeddings.factory.get_embedder")
    @patch("apps.ai.models.semantic_cache.SemanticCache.objects")
    def test_custom_similarity_threshold(self, mock_objects, mock_get_embedder):
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * EMBEDDING_DIMENSIONS
        mock_get_embedder.return_value = mock_embedder

        (
            mock_objects.filter.return_value.annotate.return_value.filter.return_value
        ).order_by.return_value.first.return_value = None

        SemanticCache.get_cached_response("test", similarity_threshold=0.8, ttl_seconds=3600)

        mock_objects.filter.assert_called_once()
        mock_embedder.embed_query.assert_called_once_with("test")


class TestSemanticCacheStoreResponse:
    @patch("apps.ai.embeddings.factory.get_embedder")
    @patch("apps.ai.models.semantic_cache.SemanticCache.save")
    def test_store_response_creates_and_saves(self, mock_save, mock_get_embedder):
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * EMBEDDING_DIMENSIONS
        mock_get_embedder.return_value = mock_embedder

        result = SemanticCache.store_response(
            query="test query 2",  # NOSONAR duplicate string literal
            response="test response 1",
            intent="rag",
            confidence=0.9,
        )

        mock_save.assert_called_once()
        mock_embedder.embed_query.assert_called_once_with("test query 2")
        assert result.query_text == "test query 2"
        assert result.response_text == "test response 1"
        assert result.intent == "rag"
        assert math.isclose(result.confidence, 0.9)

    @patch("apps.ai.embeddings.factory.get_embedder")
    @patch("apps.ai.models.semantic_cache.SemanticCache.save")
    def test_store_response_default_intent_and_confidence(self, mock_save, mock_get_embedder):
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * EMBEDDING_DIMENSIONS
        mock_get_embedder.return_value = mock_embedder

        result = SemanticCache.store_response(
            query="test query",
            response="test response",
        )

        assert result.intent == ""
        assert math.isclose(result.confidence, 0.0)
