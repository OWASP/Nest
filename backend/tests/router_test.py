import json
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(str(Path.cwd() / "backend"))

from apps.ai.router.intent import IntentRouter


class TestIntentRouterComplex(unittest.TestCase):
    def setUp(self):
        """Set up a fresh Router and Mock Redis before each test."""
        # Start patching the Redis Client
        self.redis_patcher = patch("apps.ai.router.intent.RedisRouterClient")
        self.MockRedisClass = self.redis_patcher.start()

        # Create a fake Redis connection object
        self.mock_redis = MagicMock()
        self.MockRedisClass.return_value.get_connection.return_value = self.mock_redis

        # Initialize the router (this loads spaCy real-time, which is fine)
        self.router = IntentRouter()

    def tearDown(self):
        """Clean up after each test."""
        self.redis_patcher.stop()

    def test_01_cache_hit_performance(self):
        """Return cached data immediately if Redis has it, without running spaCy."""
        # 1. Simulate a Redis Hit
        fake_cache_response = json.dumps({"intent": "CACHED_INTENT", "confidence": 1.0})
        self.mock_redis.get.return_value = fake_cache_response

        # 2. Run the function
        result = self.router.get_intent("Any random query")

        # 3. Assertions
        assert result["intent"] == "CACHED_INTENT"
        self.mock_redis.get.assert_called_once()  # Redis was checked

    def test_02_circuit_breaker_resilience(self):
        """Fallback to spaCy if Redis crashes, without crashing the app."""
        # 1. Simulate Redis blowing up (Connection Error)
        self.mock_redis.get.side_effect = Exception("Redis Connection Refused")

        # 2. Run logic (should not raise error)
        result = self.router.get_intent("Where can I download the repo?")

        # 3. Assertions
        assert result["intent"] == "STATIC"  # Should still calculate intent via spaCy
        assert result["source"] == "spacy_heuristic"

    def test_03_spacy_entity_extraction(self):
        """Check if spaCy correctly finds entities like 'OWASP' or 'GitHub'."""
        self.mock_redis.get.return_value = None  # Force Cache Miss

        # Query with multiple keywords
        query = "Is there an official OWASP license for this github repo?"
        result = self.router.get_intent(query)

        assert result["intent"] == "STATIC"
        assert result["confidence"] == 1.0

        # FIX: Convert result to lowercase so 'OWASP' matches 'owasp'
        extracted_keyword = result["args"]["keyword"].lower()
        assert extracted_keyword in ["license", "github", "repo", "owasp"]

    def test_04_dynamic_fallback(self):
        """Return DYNAMIC for ambiguous queries."""
        self.mock_redis.get.return_value = None

        query = "I am feeling confused about the architecture."
        result = self.router.get_intent(query)

        assert result["intent"] == "DYNAMIC"
        assert result["confidence"] == 0.0

    def test_05_edge_cases(self):
        """Handle empty strings and symbols as edge cases."""
        self.mock_redis.get.return_value = None

        # Empty string
        result = self.router.get_intent("")
        assert result["intent"] == "DYNAMIC"

        # Symbols
        result = self.router.get_intent("??? !!! @@@")
        assert result["intent"] == "DYNAMIC"


if __name__ == "__main__":
    unittest.main()
