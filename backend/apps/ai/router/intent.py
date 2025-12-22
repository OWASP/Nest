"""Intent router for classifying user queries using spaCy and Redis cache."""
import contextlib
import hashlib
import json
import logging

import spacy
from spacy.matcher import Matcher

from .client import RedisRouterClient

logger = logging.getLogger(__name__)


class IntentRouter:
    """Router for classifying user queries as STATIC or DYNAMIC intents."""

    def __init__(self):
        """Initialize IntentRouter with Redis connection and spaCy model."""
        self.redis = RedisRouterClient().get_connection()

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.exception(
                "❌ Model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm"
            )
            raise

        self.matcher = Matcher(self.nlp.vocab)
        self._register_patterns()

    def _register_patterns(self):
        """Define linguistic patterns that signify a STATIC intent.

        'LEMMA' means it matches base words (run -> running, ran).
        'LOWER' means case-insensitive matching.
        """
        patterns = [
            [{"LEMMA": "maintainer"}],
            [{"LEMMA": "leader"}],
            [{"LOWER": "github"}, {"LEMMA": "repo", "OP": "?"}],
            [{"LOWER": "cve"}],
            [{"LOWER": "owasp"}],
            [{"LEMMA": "download"}],
            [{"LEMMA": "install"}],
            [{"LEMMA": "version"}],
            [{"LEMMA": "license"}],
        ]

        self.matcher.add("STATIC_INDICATOR", patterns)

    def _get_cache_key(self, query: str) -> str:
        """Create a unique SHA256 hash of the query for caching."""
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        return f"nestbot_cache:intent:{query_hash}"

    def get_intent(self, user_query: str) -> dict:
        """Classify the user query as STATIC or DYNAMIC intent and cache the result."""
        cache_key = self._get_cache_key(user_query)

        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info("⚡ Intent Cache Hit: %s", cache_key)
                return json.loads(cached_data)
        except Exception as e:  # noqa: BLE001 - Intentional fail-open policy
            logger.warning("Redis Circuit Breaker Triggered: %s", e)

        doc = self.nlp(user_query)
        matches = self.matcher(doc)

        intent_type = "DYNAMIC"
        confidence = 0.0
        matched_keyword = None

        if matches:
            intent_type = "STATIC"
            confidence = 1.0
            match_id, start, end = matches[0]
            matched_span = doc[start:end]
            matched_keyword = matched_span.text

        result = {
            "intent": intent_type,
            "confidence": confidence,
            "source": "spacy_heuristic",
            "args": {
                "query": user_query,
                "keyword": matched_keyword,
                "entities": [ent.text for ent in doc.ents],
            },
        }

        with contextlib.suppress(Exception):  # noqa: BLE001 - Intentional fail-open policy
            self.redis.set(cache_key, json.dumps(result), ex=3600)

        return result