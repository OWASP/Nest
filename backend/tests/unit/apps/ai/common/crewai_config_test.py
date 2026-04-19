"""Tests for CrewAI configuration."""

import math

from apps.ai.common.crewai_config import CrewAIConfig


class TestCrewAIConfig:
    def test_default_values(self):
        config = CrewAIConfig()

        assert config.semantic_cache_enabled is True
        assert math.isclose(config.semantic_cache_similarity_threshold, 0.95)
        assert config.semantic_cache_ttl_seconds == 86400

    def test_custom_values(self):
        config = CrewAIConfig(
            semantic_cache_enabled=False,
            semantic_cache_similarity_threshold=0.8,
            semantic_cache_ttl_seconds=3600,
        )

        assert config.semantic_cache_enabled is False
        assert math.isclose(config.semantic_cache_similarity_threshold, 0.8)
        assert config.semantic_cache_ttl_seconds == 3600
