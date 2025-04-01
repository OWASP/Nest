"""Test cases for the GSOC Slack event handler."""

from unittest.mock import MagicMock

from django.conf import settings
from django.test import override_settings
from hypothesis import given
from hypothesis import strategies as st

from apps.slack.constants import OWASP_GSOC_CHANNEL_ID
from apps.slack.events.member_joined_channel.gsoc import gsoc_handler


class TestGsocEventHandler:
    """Test cases for the GSOC Slack event handler."""

    @override_settings(DATABASES={"default": settings.DATABASES["fuzz_tests"]})
    @given(
        channel_id=st.text(),
    )
    def test_check_gsoc_handler(self, channel_id):
        """Test the check_gsoc_handler function."""
        gsoc_module = __import__(
            "apps.slack.events.member_joined_channel.gsoc",
            fromlist=["gsoc_handler"],
        )
        check_gsoc_handler = getattr(
            gsoc_module,
            "check_gsoc_handler",
            lambda x: x.get("channel") == OWASP_GSOC_CHANNEL_ID,
        )

        check_gsoc_handler({"channel": channel_id})

    @override_settings(DATABASES={"default": settings.DATABASES["fuzz_tests"]})
    @given(
        events_enabled=st.booleans(),
    )
    def test_handler_responses(self, events_enabled):
        """Test the GSOC event handler responses."""
        settings.SLACK_EVENTS_ENABLED = events_enabled
        mock_slack_event = {"user": "U123456", "channel": OWASP_GSOC_CHANNEL_ID}
        mock_slack_client = MagicMock()
        mock_slack_client.conversations_open.return_value = {"channel": {"id": "C123456"}}

        gsoc_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())
