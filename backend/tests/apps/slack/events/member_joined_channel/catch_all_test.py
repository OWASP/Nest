from unittest.mock import MagicMock

from apps.slack.events.member_joined_channel.catch_all import catch_all_handler


class TestMemberJoinedChannel:
    """Tests for the catch_all_handler in member_joined_channel event."""

    def test_catch_all_handler_acknowledges_event(self):
        """Tests that the handler function correctly calls ack()."""
        ack = MagicMock()
        catch_all_handler(event={}, client=MagicMock(), ack=ack)
        ack.assert_called_once()
