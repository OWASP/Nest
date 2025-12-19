import json
import hashlib
import logging
from .client import RedisRouterClient

logger = logging.getLogger(__name__)

class IntentRouter:
    def __init__(self):
        self.redis = RedisRouterClient().get_connection()

    def _get_cache_key(self, query: str) -> str:
        # Create a unique SHA256 hash of the query for caching
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        return f"nestbot_cache:intent:{query_hash}"

    def get_intent(self, user_query: str) -> dict:
        """
        Decides if a query is STATIC or DYNAMIC and returns arguments.
        """
        cache_key = self._get_cache_key(user_query)

        # --- 1. CIRCUIT BREAKER / CACHE CHECK ---
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info(f"⚡ Intent Cache Hit: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Redis Circuit Breaker Triggered: {e}")

        # --- 2. HEURISTICS ---
        static_keywords = [
            "leader", "maintainer", "cve", "github", "repo", 
            "version", "download", "link", "url"
        ]
        
        intent_type = "DYNAMIC"
        confidence = 0.0
        matched_keyword = None  # We want to know WHICH word triggered it

        # Loop through keywords to find a match
        for word in static_keywords:
            if word in user_query.lower():
                intent_type = "STATIC"
                confidence = 1.0
                matched_keyword = word
                break  # Stop checking after first match

        # --- 3. BUILD THE DICTIONARY (THE FIX) ---
        result = {
            "intent": intent_type,
            "confidence": confidence,
            "source": "heuristic",
            # NEW SECTION: Arguments for the Service Layer
            "args": {
                "query": user_query,           # The service needs the raw text
                "keyword": matched_keyword,    # The service might want to know why we picked this
                "timestamp": 12345             # Example of other data you could pass
            }
        }

        # --- 4. WRITE BACK TO CACHE ---
        try:
            self.redis.set(cache_key, json.dumps(result), ex=3600)
        except Exception:
            pass 

        return result        """
        Decides if a query is STATIC (Deterministic) or DYNAMIC (LLM).
        """
        cache_key = self._get_cache_key(user_query)

        # --- 1. CIRCUIT BREAKER / CACHE CHECK ---
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info(f"⚡ Intent Cache Hit: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            # RFC 3.1.3: Fail-Open Policy
            # If Redis is down, log it and continue to Heuristics
            logger.warning(f"Redis Circuit Breaker Triggered: {e}")

        # --- 2. HEURISTICS (The "Rule-Based" Brain) ---
        # RFC 3.1.1: Regex Pre-filter
        # RFC: Deterministic Rules based on Project Entities
        static_keywords = [
            # Entities
            "leader", "maintainer", "cve", "github", "repo", "repository",
            "license", "documentation", "docs", "version",
            # Actions
            "download", "install", "update", "link", "url"
        ]
        
        intent_type = "DYNAMIC" # Default to AI
        confidence = 0.0

        if any(w in user_query.lower() for w in static_keywords):
            intent_type = "STATIC"
            confidence = 1.0

        result = {
            "intent": intent_type,
            "confidence": confidence,
            "source": "heuristic"
        }

        # --- 3. WRITE BACK TO CACHE ---
        try:
            # RFC 3.1.2: Cache result for 1 hour (3600s)
            self.redis.set(cache_key, json.dumps(result), ex=3600)
        except Exception:
            pass  # Fail silently on write

        return result