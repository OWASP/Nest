
"""Intent router for classifying user queries using spaCy and Redis cache."""
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

        # Load spaCy model (Lightweight English)
        # We do this in __init__ so it loads once when the Router starts
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model isn't downloaded
            logger.exception(
                "❌ Model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm"
            )
            raise

        # Initialize the Matcher with the model's vocabulary
        self.matcher = Matcher(self.nlp.vocab)
        self._register_patterns()

    def _register_patterns(self):
        """Define linguistic patterns that signify a STATIC intent.

        'LEMMA' means it matches base words (run -> running, ran).
        'LOWER' means case-insensitive matching.
        """
        patterns = [
            # Entities: "Who is the maintainer?","repo link"
            [{"LEMMA": "maintainer"}],
            [{"LEMMA": "leader"}],
            [
                {"LOWER": "github"},
                {"LEMMA": "repo", "OP": "?"},
            ],  # Matches "github" OR "github repo"
            [{"LOWER": "cve"}],
            [{"LOWER": "owasp"}],
            # Actions: "Where to download?", "How to install?"
            [{"LEMMA": "download"}],
            [{"LEMMA": "install"}],
            [{"LEMMA": "version"}],
            [{"LEMMA": "license"}],
        ]

        # Add these patterns under the label "STATIC_INDICATOR"
        self.matcher.add("STATIC_INDICATOR", patterns)

    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key for a given query."""
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        return f"nestbot_cache:intent:{query_hash}"

    def get_intent(self, user_query: str) -> dict:
        """Classify the user query as STATIC or DYNAMIC intent and cache the result."""
        cache_key = self._get_cache_key(user_query)

        # --- 1. CIRCUIT BREAKER / CACHE CHECK ---
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info("⚡ Intent Cache Hit: %s", cache_key)
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Redis Circuit Breaker Triggered: %s", e)

        # --- 2. SPACY PROCESSING ---
        # Process the text
        doc = self.nlp(user_query)

        # Run the Matcher
        matches = self.matcher(doc)

        intent_type = "DYNAMIC"
        confidence = 0.0
        matched_keyword = None

        # If matches are found, it's STATIC
        if matches:
            intent_type = "STATIC"
            confidence = 1.0
            # Get the string representation of the first match
            _, start, end = matches[0]
            matched_span = doc[start:end]
            matched_keyword = matched_span.text

        # --- 3. BUILD RESULT ---
        result = {
            "intent": intent_type,
            "confidence": confidence,
            "source": "spacy_heuristic",
            "args": {
                "query": user_query,
                "keyword": matched_keyword,
                # spaCy Bonus: Pass the identified entities (like 'OWASP')
                "entities": [ent.text for ent in doc.ents],
            },
        }

        # --- 4. WRITE TO CACHE ---
        import contextlib
        with contextlib.suppress(Exception):
            self.redis.set(cache_key, json.dumps(result), ex=3600)

        return result
