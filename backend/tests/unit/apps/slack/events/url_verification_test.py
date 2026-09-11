from unittest.mock import MagicMock

from apps.slack.events.url_verification import UrlVerification


class TestUrlVerification:
    def test_url_verification_handler_acknowledges_challenge(self):
        """Test Slack URL verification responds with the challenge value."""
        event = {"challenge": "test_challenge"}
        ack = MagicMock()
        handler = UrlVerification()

        handler.handler(event, client=None, ack=ack)

        ack.assert_called_once_with("test_challenge")
