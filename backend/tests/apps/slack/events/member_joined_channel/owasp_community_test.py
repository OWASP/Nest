"""Tests for OwaspCommunity member joined channel event handler."""

from pathlib import Path

from apps.slack.constants import OWASP_COMMUNITY_CHANNEL_ID
from apps.slack.events.member_joined_channel.owasp_community import OwaspCommunity


class TestOwaspCommunity:
    """Test cases for OwaspCommunity event handler."""

    def test_direct_message_template_path_returns_none(self):
        """Test that direct_message_template_path returns None."""
        handler = OwaspCommunity()

        assert handler.direct_message_template_path is None

    def test_ephemeral_message_template_path(self):
        """Test that ephemeral_message_template_path returns correct path."""
        handler = OwaspCommunity()

        result = handler.ephemeral_message_template_path

        assert isinstance(result, Path)
        assert (
            str(result) == "events/member_joined_channel/owasp_community/ephemeral_message.jinja"
        )

    def test_matcher_matches_owasp_community_channel_only(self):
        """Slack sends channel ID without #; matcher must match constants."""
        handler = OwaspCommunity()
        channel_id = OWASP_COMMUNITY_CHANNEL_ID.lstrip("#")
        matcher = handler.matchers[0]

        assert matcher({"channel": channel_id})
        assert not matcher({"channel": "C00000000"})
