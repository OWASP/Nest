from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.blocks import DIVIDER, SECTION_BREAK
from apps.slack.events.event import EventBase


class MockEvent(EventBase):
    event_type = "app_home_opened"


class TestEventBase:
    """Tests for the EventBase class and its functionality."""

    @pytest.fixture
    def event_instance(self):
        return MockEvent()

    @pytest.fixture
    def mock_event_payload(self):
        return {"user": "U123ABC", "channel": "C123XYZ"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "ABCDEF"}}
        return client

    def test_direct_message_template_path(self, event_instance):
        """Tests that the direct_message_template_path is derived correctly."""
        assert event_instance.direct_message_template_path == Path("events/mock_event.jinja")

    def test_ephemeral_message_template_path_is_none_by_default(self, event_instance):
        """Tests that the ephemeral message path is None by default."""
        assert event_instance.ephemeral_message_template_path is None

    def test_handler_when_events_disabled(
        self, settings, event_instance, mock_event_payload, mock_client
    ):
        """Tests that the handler exits early if events are disabled."""
        settings.SLACK_EVENTS_ENABLED = False
        ack = MagicMock()
        with patch.object(event_instance, "handle_event") as mock_handle_event:
            event_instance.handler(event=mock_event_payload, client=mock_client, ack=ack)
        ack.assert_called_once()
        mock_handle_event.assert_not_called()

    def test_handler_catches_and_logs_generic_exception(
        self, mocker, settings, event_instance, mock_event_payload, mock_client
    ):
        """Tests that a generic exception in handle_event is caught and logged."""
        settings.SLACK_EVENTS_ENABLED = True
        ack = MagicMock()
        mock_logger = mocker.patch("apps.slack.events.event.logger")
        with patch.object(
            event_instance, "handle_event", side_effect=Exception("Something went wrong")
        ):
            event_instance.handler(event=mock_event_payload, client=mock_client, ack=ack)
        ack.assert_called_once()
        mock_logger.exception.assert_called_once_with("Error handling %s", "app_home_opened")

    def test_handler_ignores_cannot_dm_bot_error(
        self, mocker, settings, event_instance, mock_event_payload, mock_client
    ):
        """Tests that a SlackApiError for 'cannot_dm_bot' is caught and ignored."""
        settings.SLACK_EVENTS_ENABLED = True
        ack = MagicMock()
        mock_logger = mocker.patch("apps.slack.events.event.logger")
        mock_slack_error = SlackApiError(
            message="Cannot DM bot", response={"ok": False, "error": "cannot_dm_bot"}
        )
        with patch.object(event_instance, "handle_event", side_effect=mock_slack_error):
            event_instance.handler(event=mock_event_payload, client=mock_client, ack=ack)
        ack.assert_called_once()
        mock_logger.warning.assert_called_once()
        mock_logger.exception.assert_not_called()

    def test_handle_event_sends_direct_message(
        self, mocker, event_instance, mock_event_payload, mock_client
    ):
        """Tests that a direct message is correctly sent."""
        mock_template = MagicMock()
        mock_template.render.return_value = "This is a direct message."
        mocker.patch.object(
            MockEvent,
            "direct_message_template",
            new_callable=mocker.PropertyMock,
            return_value=mock_template,
        )
        mocker.patch.object(
            MockEvent,
            "ephemeral_message_template",
            new_callable=mocker.PropertyMock,
            return_value=None,
        )
        event_instance.handle_event(event=mock_event_payload, client=mock_client)
        mock_client.chat_postMessage.assert_called_once()
        assert mock_client.chat_postMessage.call_args[1]["channel"] == "ABCDEF"
        mock_client.chat_postEphemeral.assert_not_called()

    def test_handler_fails_on_unknown_slack_error(
        self, settings, event_instance, mock_event_payload, mock_client
    ):
        """Tests that SlackApiErrors other than 'cannot_dm_bot' are re-raised."""
        settings.SLACK_EVENTS_ENABLED = True
        ack = MagicMock()
        mock_slack_error = SlackApiError(
            message="Other error", response={"ok": False, "error": "channel_not_found"}
        )
        with (
            patch.object(event_instance, "handle_event", side_effect=mock_slack_error),
            pytest.raises(SlackApiError),
        ):
            event_instance.handler(event=mock_event_payload, client=mock_client, ack=ack)

    def test_handle_event_sends_ephemeral_message(
        self, mocker, event_instance, mock_event_payload, mock_client
    ):
        """Tests that an ephemeral message is correctly sent."""
        mock_template = MagicMock()
        mock_template.render.return_value = "This is an ephemeral message."
        mocker.patch.object(
            MockEvent,
            "direct_message_template",
            new_callable=mocker.PropertyMock,
            return_value=None,
        )
        mocker.patch.object(
            MockEvent,
            "ephemeral_message_template",
            new_callable=mocker.PropertyMock,
            return_value=mock_template,
        )
        event_instance.handle_event(event=mock_event_payload, client=mock_client)
        mock_client.chat_postMessage.assert_not_called()
        mock_client.chat_postEphemeral.assert_called_once()
        assert mock_client.chat_postEphemeral.call_args[1]["user"] == "U123ABC"

    def test_render_blocks_no_template(self, event_instance):
        """Tests that render_blocks returns an empty list if the template is None."""
        result = event_instance.render_blocks(template=None, context={})
        assert result == []

    def test_open_conversation_no_user_id(self, event_instance, mock_client):
        """Covers the edge case where user_id is missing."""
        result = event_instance.open_conversation(client=mock_client, user_id=None)
        assert result is None
        mock_client.conversations_open.assert_not_called()

    def test_configure_events_registers_events(self, mocker):
        """Tests that subclasses are discovered and registered."""
        mock_slack_config = mocker.patch("apps.slack.events.event.SlackConfig")
        mock_app = MagicMock()
        mock_slack_config.app = mock_app
        mock_event_class = MagicMock()
        mocker.patch.object(EventBase, "get_events", return_value=[mock_event_class])
        EventBase.configure_events()
        mock_event_class.return_value.register.assert_called_once()

    def test_register(self, mocker, event_instance):
        """Tests that the register method correctly calls the app's event decorator."""
        mock_slack_config = mocker.patch("apps.slack.events.event.SlackConfig")
        mock_app = MagicMock()
        mock_slack_config.app = mock_app
        event_instance.register()
        mock_app.event.assert_called_once_with(
            event_instance.event_type, matchers=event_instance.matchers
        )

    def test_configure_events_when_app_is_none(self, mocker):
        """Tests that configure_events returns early when app is None."""
        mock_slack_config = mocker.patch("apps.slack.events.event.SlackConfig")
        mock_slack_config.app = None
        mock_logger = mocker.patch("apps.slack.events.event.logger")

        EventBase.configure_events()

        mock_logger.warning.assert_called_once_with(
            "SlackConfig.app is None. Event handlers are not registered."
        )

    def test_get_events_yields_subclasses(self):
        """Tests that get_events yields all EventBase subclasses."""
        subclasses = list(EventBase.get_events())
        assert MockEvent in subclasses
        assert EventBase not in subclasses

    def test_get_direct_message(self, mocker, event_instance, mock_event_payload):
        """Tests that get_direct_message returns blocks."""
        mock_template = MagicMock()
        mock_template.render.return_value = "Direct message content"
        mocker.patch.object(
            MockEvent,
            "direct_message_template",
            new_callable=mocker.PropertyMock,
            return_value=mock_template,
        )

        result = event_instance.get_direct_message(mock_event_payload)

        assert isinstance(result, list)

    def test_get_ephemeral_message(self, mocker, event_instance, mock_event_payload):
        """Tests that get_ephemeral_message returns blocks."""
        mock_template = MagicMock()
        mock_template.render.return_value = "Ephemeral message content"
        mocker.patch.object(
            MockEvent,
            "ephemeral_message_template",
            new_callable=mocker.PropertyMock,
            return_value=mock_template,
        )

        result = event_instance.get_ephemeral_message(mock_event_payload)

        assert isinstance(result, list)

    def test_open_conversation_catches_cannot_dm_bot_error(self, event_instance, mock_client):
        """Tests that open_conversation returns None for cannot_dm_bot error."""
        mock_slack_error = SlackApiError(
            message="Cannot DM bot", response={"ok": False, "error": "cannot_dm_bot"}
        )
        mock_client.conversations_open.side_effect = mock_slack_error

        result = event_instance.open_conversation(client=mock_client, user_id="U123ABC")

        assert result is None

    def test_open_conversation_raises_other_errors(self, event_instance, mock_client):
        """Tests that open_conversation re-raises other SlackApiErrors."""
        mock_slack_error = SlackApiError(
            message="Other error", response={"ok": False, "error": "channel_not_found"}
        )
        mock_client.conversations_open.side_effect = mock_slack_error

        with pytest.raises(SlackApiError):
            event_instance.open_conversation(client=mock_client, user_id="U123ABC")

    def test_render_blocks_with_divider(self, mocker, event_instance):
        """Tests that render_blocks handles divider sections."""
        mock_template = MagicMock()
        mock_template.render.return_value = f"{DIVIDER}"

        result = event_instance.render_blocks(template=mock_template, context={})

        assert any(block.get("type") == "divider" for block in result)

    def test_render_blocks_with_text_section(self, mocker, event_instance):
        """Tests that render_blocks handles text sections."""
        mock_template = MagicMock()
        mock_template.render.return_value = "This is some text content"

        result = event_instance.render_blocks(template=mock_template, context={})

        assert len(result) > 0
        assert result[0]["type"] == "section"

    def test_render_blocks_skips_empty_sections(self, event_instance):
        """Tests that render_blocks skips empty sections from consecutive SECTION_BREAKs."""
        mock_template = MagicMock()
        mock_template.render.return_value = f"Text before{SECTION_BREAK}{SECTION_BREAK}Text after"

        result = event_instance.render_blocks(template=mock_template, context={})

        assert len(result) == 2
        assert all(block["type"] == "section" for block in result)
