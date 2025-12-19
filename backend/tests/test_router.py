import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# --- PATH FIX ---
# Ensure Python can find the 'backend' folder
sys.path.append(os.path.join(os.getcwd(), 'backend'))
# ----------------

from apps.ai.router.intent import IntentRouter

class TestIntentRouterComplex(unittest.TestCase):

    def setUp(self):
        """Runs before every single test. Sets up a fresh Router and Mock Redis."""
        # Start patching the Redis Client
        self.redis_patcher = patch('apps.ai.router.intent.RedisRouterClient')
        self.MockRedisClass = self.redis_patcher.start()
        
        # Create a fake Redis connection object
        self.mock_redis = MagicMock()
        self.MockRedisClass.return_value.get_connection.return_value = self.mock_redis
        
        # Initialize the router (this loads spaCy real-time, which is fine)
        self.router = IntentRouter()

    def tearDown(self):
        """Runs after every test to clean up."""
        self.redis_patcher.stop()

    def test_01_cache_hit_performance(self):
        """Test: If Redis has data, we should return it immediately and NOT run spaCy."""
        # 1. Simulate a Redis Hit
        fake_cache_response = json.dumps({"intent": "CACHED_INTENT", "confidence": 1.0})
        self.mock_redis.get.return_value = fake_cache_response

        # 2. Run the function
        result = self.router.get_intent("Any random query")

        # 3. Assertions
        self.assertEqual(result["intent"], "CACHED_INTENT")
        self.mock_redis.get.assert_called_once() # Redis was checked

    def test_02_circuit_breaker_resilience(self):
        """Test: If Redis crashes, the app should NOT crash. It should fallback to spaCy."""
        # 1. Simulate Redis blowing up (Connection Error)
        self.mock_redis.get.side_effect = Exception("Redis Connection Refused")

        # 2. Run logic (should not raise error)
        try:
            result = self.router.get_intent("Where can I download the repo?")
        except Exception:
            self.fail("Router crashed when Redis failed! Circuit breaker is broken.")

        # 3. Assertions
        self.assertEqual(result["intent"], "STATIC") # Should still calculate intent via spaCy
        self.assertEqual(result["source"], "spacy_heuristic")

    def test_03_spacy_entity_extraction(self):
        """Test: Does spaCy correctly find entities like 'OWASP' or 'GitHub'?"""
        self.mock_redis.get.return_value = None # Force Cache Miss

        # Query with multiple keywords
        query = "Is there an official OWASP license for this github repo?"
        result = self.router.get_intent(query)

        self.assertEqual(result["intent"], "STATIC")
        self.assertEqual(result["confidence"], 1.0)
        
        # FIX: Convert result to lowercase so 'OWASP' matches 'owasp'
        extracted_keyword = result["args"]["keyword"].lower()
        self.assertIn(extracted_keyword, ["license", "github", "repo", "owasp"])

    def test_04_dynamic_fallback(self):
        """Test: Ambiguous queries should return DYNAMIC."""
        self.mock_redis.get.return_value = None

        query = "I am feeling confused about the architecture."
        result = self.router.get_intent(query)

        self.assertEqual(result["intent"], "DYNAMIC")
        self.assertEqual(result["confidence"], 0.0)

    def test_05_edge_cases(self):
        """Test: Empty strings and symbols."""
        self.mock_redis.get.return_value = None

        # Empty string
        result = self.router.get_intent("")
        self.assertEqual(result["intent"], "DYNAMIC")

        # Symbols
        result = self.router.get_intent("??? !!! @@@")
        self.assertEqual(result["intent"], "DYNAMIC")

if __name__ == '__main__':
    unittest.main()