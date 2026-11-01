"""CrewAI assistant configuration."""

from dataclasses import dataclass


@dataclass
class CrewAIConfig:
    """CrewAI assistant configuration."""

    semantic_cache_enabled: bool = True
    semantic_cache_similarity_threshold: float = 0.95
    semantic_cache_ttl_seconds: int = 86400  # 24 hours
