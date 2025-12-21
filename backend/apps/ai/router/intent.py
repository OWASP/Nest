"""Intent router for classifying user queries using Redis cache."""

import contextlib
import hashlib
import json
import logging

from .client import RedisRouterClient

logger = logging.getLogger(__name__)


class IntentRouter:
    """Router for classifying user queries as STATIC or DYNAMIC intents."""

    def __init__(self):
        """Initialize IntentRouter with Redis connection."""
        self.redis = RedisRouterClient().get_connection()

    def _get_cache_key(self, query: str) -> str:
        """Create a unique SHA256 hash of the query for caching."""
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        return f"nestbot_cache:intent:{query_hash}"

    def get_intent(self, user_query: str) -> dict:
        """Decide if a query is STATIC (Deterministic) or DYNAMIC (LLM)."""
        cache_key = self._get_cache_key(user_query)

        # --- 1. CIRCUIT BREAKER / CACHE CHECK ---
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info("⚡ Intent Cache Hit: %s", cache_key)
                return json.loads(cached_data)
        except Exception as e:  # noqa: BLE001 - Intentional fail-open policy
            # RFC 3.1.3: Fail-Open Policy
            # If Redis is down, log it and continue to Heuristics
            logger.warning("Redis Circuit Breaker Triggered: %s", e)

        # --- 2. HEURISTICS (The "Rule-Based" Brain) ---
        # RFC 3.1.1: Regex Pre-filter
        # These keywords strongly suggest a factual lookup
        static_keywords = [
            "leader",
            "maintainer",
            "cve",
            "github",
            "repo",
            "version",
            "download",
            "link",
            "url",
        ]

        intent_type = "DYNAMIC"  # Default to AI
        confidence = 0.0

        if any(w in user_query.lower() for w in static_keywords):
            intent_type = "STATIC"
            confidence = 1.0

        result = {"intent": intent_type, "confidence": confidence, "source": "heuristic"}

        # --- 3. WRITE BACK TO CACHE ---
        with contextlib.suppress(Exception):
            # RFC 3.1.2: Cache result for 1 hour (3600s)
            self.redis.set(cache_key, json.dumps(result), ex=3600)

        return result
