from unittest.mock import MagicMock, patch

import openai

from apps.ai.engine import FALLBACK_RESPONSE, Engine


def test_engine_resilience_on_error():
    """Verify Engine returns fallback message if OpenAI API raises exception."""
    # Mock OS environ to pass init check
    with patch.dict("os.environ", {"DJANGO_OPEN_AI_SECRET_KEY": "fake-key"}):
        engine = Engine()

        # Mock client to raise error
        engine.openai_client.chat.completions.create = MagicMock(
            side_effect=openai.OpenAIError("API Down")
        )

        response = engine.generate_answer("Hello", [])

        assert response == FALLBACK_RESPONSE
