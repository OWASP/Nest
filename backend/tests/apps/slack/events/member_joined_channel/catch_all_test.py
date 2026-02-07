import importlib
import sys
from unittest.mock import MagicMock

from apps.slack.events.member_joined_channel.catch_all import catch_all_handler


class TestMemberJoinedChannel:
    """Tests for the catch_all_handler in member_joined_channel event."""

    def test_catch_all_handler_acknowledges_event(self):
        """Tests that the handler function correctly calls ack()."""
        ack = MagicMock()
        catch_all_handler(event={}, client=MagicMock(), ack=ack)
        ack.assert_called_once()


class TestCatchAllModuleRegistration:
    """Tests for the module-level event registration in catch_all.py."""

    def test_module_registers_event_handler_when_app_exists(self, mocker):
        """Tests that the event handler is registered when SlackConfig.app exists."""
        module_name = "apps.slack.events.member_joined_channel.catch_all"
        if module_name in sys.modules:
            del sys.modules[module_name]
        mock_app = MagicMock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        importlib.import_module(module_name)
        mock_app.event.assert_called_once()
        call_args = mock_app.event.call_args
        assert call_args[0][0] == "member_joined_channel"
        assert "matchers" in call_args[1]
