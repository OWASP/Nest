"""Tests for Slack event model."""

from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from apps.slack.commands.owasp import COMMAND as OWASP_COMMAND
from apps.slack.models.event import Event

test_command = "/test"
test_command_text = "test command"


@pytest.fixture
def event_model():
    return Event()


def test_event_str():
    event = Event(user_id="U123", user_name="user", trigger="command")
    assert str(event) == "Event from user triggered by command"

    event = Event(user_id="U123", trigger="command")
    assert str(event) == "Event from U123 triggered by command"


def test_from_slack_basic(event_model):
    context = {"channel_id": "C123", "user_id": "U123"}
    payload = {"channel_name": "general", "user_name": "user", "type": "message"}

    event_model.from_slack(context, payload)

    assert event_model.channel_id == "C123"
    assert event_model.channel_name == "general"
    assert event_model.user_id == "U123"
    assert event_model.user_name == "user"
    assert event_model.trigger == "message"
    assert event_model.command == ""
    assert event_model.text == ""


def test_from_slack_with_command(event_model):
    context = {"channel_id": "C123", "user_id": "U123"}
    payload = {
        "channel_name": "general",
        "user_name": "user",
        "command": test_command,
        "text": "some text",
    }

    event_model.from_slack(context, payload)

    assert event_model.command == "test"
    assert event_model.text == "some text"
    assert event_model.trigger == "test"


def test_from_slack_with_owasp_command(event_model):
    context = {"channel_id": "C123", "user_id": "U123"}
    payload = {
        "channel_name": "general",
        "user_name": "user",
        "command": f"/{OWASP_COMMAND}",
        "text": "subcommand arg1 arg2",
    }

    event_model.from_slack(context, payload)

    assert event_model.command == OWASP_COMMAND.lstrip("/")
    assert event_model.text == "subcommand arg1 arg2"
    assert event_model.trigger == OWASP_COMMAND.lstrip("/")


def test_from_slack_with_owasp_command_no_args(event_model):
    context = {"channel_id": "C123", "user_id": "U123"}
    payload = {
        "channel_name": "general",
        "user_name": "user",
        "command": f"/{OWASP_COMMAND}",
        "text": "subcommand",
    }

    event_model.from_slack(context, payload)

    assert event_model.command == OWASP_COMMAND.lstrip("/")
    assert event_model.text == "subcommand"
    assert event_model.trigger == OWASP_COMMAND.lstrip("/")


def test_from_slack_with_action_id(event_model):
    context = {"channel_id": "C123", "user_id": "U123"}
    payload = {"channel_name": "general", "user_name": "user", "action_id": "button_click"}

    event_model.from_slack(context, payload)

    assert event_model.trigger == "button_click"


def test_create_with_save(monkeypatch):
    mock_save = MagicMock()
    monkeypatch.setattr(Event, "save", mock_save)

    context = {"user_id": "U123"}
    payload = {"user_name": "user"}

    event = Event.create(context, payload)

    assert mock_save.called
    assert event.user_id == "U123"
    assert event.user_name == "user"


def test_create_without_save(monkeypatch):
    mock_save = MagicMock()
    monkeypatch.setattr(Event, "save", mock_save)

    context = {"user_id": "U123"}
    payload = {"user_name": "user"}

    event = Event.create(context, payload, save=False)

    assert not mock_save.called
    assert event.user_id == "U123"
    assert event.user_name == "user"


@patch("django.db.models.base.Model.save", MagicMock())
@patch("django.db.models.base.Model.delete", MagicMock())
@patch("django.db.models.query.QuerySet.filter", MagicMock())
@patch("django.db.models.query.QuerySet.all", MagicMock())
@patch("django.db.connections", MagicMock())
@patch("django.db.connection", MagicMock())
class EventModelTest(TestCase):
    databases = []

    def setUp(self):
        self.context = {"channel_id": "C12345", "user_id": "U12345"}
        self.payload = {
            "channel_name": "general",
            "command": f"/{OWASP_COMMAND}",
            "text": test_command_text,
            "user_name": "testuser",
        }

    def test_event_creation(self):
        event = Event.create(self.context, self.payload, save=False)
        assert event.channel_id == "C12345"
        assert event.channel_name == "general"
        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == test_command_text
        assert event.trigger == OWASP_COMMAND.lstrip("/")
        assert event.user_id == "U12345"
        assert event.user_name == "testuser"

    def test_event_str(self):
        event = Event.create(self.context, self.payload, save=False)
        assert str(event) == "Event from testuser triggered by owasp"

    def test_event_from_slack(self):
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.channel_id == "C12345"
        assert event.channel_name == "general"
        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == test_command_text
        assert event.trigger == OWASP_COMMAND.lstrip("/")
        assert event.user_id == "U12345"
        assert event.user_name == "testuser"

    def test_event_from_slack_with_action_id(self):
        self.payload.pop("command")
        self.payload["action_id"] = "action_123"
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.trigger == "action_123"

    def test_event_from_slack_with_type(self):
        self.payload.pop("command")
        self.payload["type"] = "message"
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.trigger == "message"

    def test_event_from_slack_empty_context(self):
        empty_context = {}
        event = Event()

        with pytest.raises(KeyError):
            event.from_slack(empty_context, self.payload)

    def test_event_from_slack_empty_payload(self):
        empty_payload = {}
        event = Event()
        event.from_slack(self.context, empty_payload)

        assert event.channel_id == "C12345"
        assert event.channel_name == ""
        assert event.command == ""
        assert event.text == ""
        assert event.trigger == ""
        assert event.user_id == "U12345"
        assert event.user_name == ""

    def test_event_from_slack_owasp_command_complex_args(self):
        self.payload["text"] = "subcommand arg1 arg2 arg3 with spaces"
        event = Event()
        event.from_slack(self.context, self.payload)

        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == "subcommand arg1 arg2 arg3 with spaces"
        assert event.trigger == OWASP_COMMAND.lstrip("/")

    def test_event_from_slack_owasp_command_empty_text(self):
        self.payload["text"] = ""
        event = Event()
        event.from_slack(self.context, self.payload)

        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == ""

    def test_event_from_slack_multiple_triggers(self):
        self.payload["command"] = test_command
        self.payload["action_id"] = "action_123"
        self.payload["type"] = "message"

        event = Event()
        event.from_slack(self.context, self.payload)

        assert event.trigger == "test"

        self.payload.pop("command")
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.trigger == "action_123"

        self.payload.pop("action_id")
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.trigger == "message"

    def test_create_method_exceptions(self):
        @patch("apps.slack.models.event.Event.save")
        def test_save_called_with_params(self, mock_save):
            Event.create(self.context, self.payload)
            mock_save.assert_called_once()

    def test_event_from_slack_owasp_command_whitespace_only(self):
        self.payload["text"] = "  "
        event = Event()
        event.from_slack(self.context, self.payload)
        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == "  "
        assert event.trigger == OWASP_COMMAND.lstrip("/")


class TestEvent:
    def test_str_representation(self):
        event = Event(user_name="test_user", user_id="U123", trigger="test_command")
        assert str(event) == "Event from test_user triggered by test_command"
        event = Event(user_id="U123", trigger="test_command")
        assert str(event) == "Event from U123 triggered by test_command"

    def test_from_slack_basic(self):
        event = Event()
        context = {"user_id": "U123", "channel_id": "C123"}
        payload = {"channel_name": "general", "user_name": "user123", "type": "message"}
        event.from_slack(context, payload)

        assert event.channel_id == "C123"
        assert event.channel_name == "general"
        assert event.user_id == "U123"
        assert event.user_name == "user123"
        assert event.trigger == "message"

    def test_from_slack_with_command(self):
        event = Event()
        context = {"user_id": "U123"}
        payload = {"command": test_command, "text": "hello world"}
        event.from_slack(context, payload)

        assert event.command == "test"
        assert event.text == "hello world"
        assert event.trigger == "test"

    def test_from_slack_with_owasp_command_success(self):
        event = Event()
        context = {"user_id": "U123"}
        payload = {"command": f"/{OWASP_COMMAND}", "text": "events conference"}
        event.from_slack(context, payload)

        assert event.command == OWASP_COMMAND.lstrip("/")
        assert event.text == "events conference"
        assert event.trigger == "events"

    def test_from_slack_with_owasp_command_empty_text(self):
        event = Event()
        context = {"user_id": "U123"}
        payload = {"command": OWASP_COMMAND, "text": ""}
        event.from_slack(context, payload)

        assert event.command == "owasp"
        assert event.text == ""
        assert event.trigger == "owasp"

    def test_from_slack_with_owasp_command_exception(self):
        event = Event()
        context = {"user_id": "U123"}
        payload = {"command": OWASP_COMMAND, "text": "    "}
        event.from_slack(context, payload)

        assert event.command == "owasp"
        assert event.text == "    "
        assert event.trigger == "owasp"

    def test_create_with_save(self):
        context = {"user_id": "U123"}
        payload = {"user_name": "user123", "type": "message"}
        with patch.object(Event, "save") as mock_save:
            event = Event.create(context, payload)
            assert event.user_id == "U123"
            assert event.user_name == "user123"
            assert event.trigger == "message"
            mock_save.assert_called_once()

    def test_create_without_save(self):
        context = {"user_id": "U123"}
        payload = {"user_name": "user123", "type": "message"}
        with patch.object(Event, "save") as mock_save:
            event = Event.create(context, payload, save=False)
            assert event.user_id == "U123"
            mock_save.assert_not_called()
