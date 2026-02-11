from unittest.mock import patch

from apps.slack.commands.owasp import Owasp
from apps.slack.models.event import Event


class TestEventModel:
    def test_from_slack_with_owasp_command(self):
        context = {"channel_id": "C111", "user_id": "U111"}
        payload = {
            "channel_name": "general",
            "command": Owasp().command_name,
            "text": "/owasp help",
            "user_name": "Alice",
        }
        event = Event()
        event.from_slack(context, payload)
        assert event.channel_id == "C111"
        assert event.channel_name == "general"
        assert event.command == "owasp"
        assert event.text == "help"
        assert event.trigger == "owasp"
        assert event.user_id == "U111"
        assert event.user_name == "Alice"

    def test_from_slack_with_non_owasp_command(self):
        context = {"channel_id": "C222", "user_id": "U222"}
        payload = {
            "channel_name": "random",
            "command": "/other",
            "text": "just some text",
            "user_name": "Bob",
        }
        event = Event()
        event.from_slack(context, payload)
        assert event.channel_id == "C222"
        assert event.channel_name == "random"
        assert event.command == "other"
        assert event.text == "just some text"
        assert event.trigger == "other"
        assert event.user_id == "U222"
        assert event.user_name == "Bob"

    def test_str_method(self):
        event = Event()
        event.user_name = "Charlie"
        event.user_id = "U333"
        event.trigger = "testtrigger"
        assert str(event) == "Event from Charlie triggered by testtrigger"
        event.user_name = ""
        assert str(event) == "Event from U333 triggered by testtrigger"

    def test_create_method_save_true(self):
        context = {"channel_id": "C444", "user_id": "U444"}
        payload = {
            "channel_name": "dev",
            "command": Owasp().command_name,
            "text": "/owasp info",
            "user_name": "Dana",
        }
        with patch.object(Event, "save") as mock_save:
            event = Event.create(context, payload, save=True)
        mock_save.assert_called_once()
        assert event.channel_id == "C444"
        assert event.channel_name == "dev"
        assert event.command == "owasp"
        assert event.text == "info"
        assert event.user_id == "U444"
        assert event.user_name == "Dana"

    def test_create_method_save_false(self):
        context = {"channel_id": "C555", "user_id": "U555"}
        payload = {
            "channel_name": "support",
            "command": "/other",
            "text": "query",
            "user_name": "Eve",
        }
        with patch.object(Event, "save") as mock_save:
            event = Event.create(context, payload, save=False)
        mock_save.assert_not_called()
        assert event.channel_id == "C555"
        assert event.channel_name == "support"
        assert event.command == "other"
        assert event.text == "query"
        assert event.user_id == "U555"
        assert event.user_name == "Eve"

    def test_from_slack_value_error_in_command_parsing(self):
        """Test from_slack handles ValueError when parsing command text."""
        context = {"channel_id": "C666", "user_id": "U666"}
        payload = {
            "channel_name": "test",
            "command": Owasp().command_name,
            "text": "",
            "user_name": "Frank",
        }
        event = Event()
        event.from_slack(context, payload)
        
        assert event.command == "owasp"
        assert event.text == ""
