from apps.slack.events.app_mention import AppMention


class TestAppMention:
    def test_handle_event_disabled_in_conversation(self, mocker):
        event = {"channel": "C123456", "text": "Hello"}
        client = mocker.Mock()
        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        mock_logger = mocker.patch("apps.slack.events.app_mention.logger")

        handler = AppMention()
        handler.handle_event(event, client)

        mock_logger.warning.assert_called_with(
            "NestBot AI Assistant is not enabled for this conversation."
        )
        client.chat_postMessage.assert_not_called()

    def test_handle_event_no_query_in_text(self, mocker):
        event = {"channel": "C123456", "text": ""}
        client = mocker.Mock()
        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mock_logger = mocker.patch("apps.slack.events.app_mention.logger")

        handler = AppMention()
        handler.handle_event(event, client)

        mock_logger.warning.assert_called_with("No query found in app mention")
        client.chat_postMessage.assert_not_called()

    def test_handle_event_query_in_blocks(self, mocker):
        event = {
            "channel": "C123456",
            "text": "",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [{"type": "text", "text": "  Help me  "}],
                        }
                    ],
                }
            ],
            "ts": "123.456",
        }
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mock_get_blocks = mocker.patch(
            "apps.slack.events.app_mention.get_blocks",
            return_value=[{"type": "section", "text": {"text": "Response"}}],
        )

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_postMessage.assert_called()
        mock_get_blocks.assert_called_with(query="Help me")
        client.chat_update.assert_called_with(
            channel="C123456",
            ts="999.999",
            blocks=[{"type": "section", "text": {"text": "Response"}}],
            text="Help me",
        )

    def test_handle_event_simple_text_query(self, mocker):
        event = {"channel": "C123456", "text": "Simple query", "ts": "123.456"}
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mocker.patch("apps.slack.events.app_mention.get_blocks", return_value=[])

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_update.assert_called()
        _, kwargs = client.chat_update.call_args
        assert kwargs["text"] == "Simple query"

    def test_handle_event_with_thread_ts(self, mocker):
        """Test handle_event uses thread_ts when available."""
        event = {
            "channel": "C123456",
            "text": "Query",
            "ts": "123.456",
            "thread_ts": "100.000",
        }
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mocker.patch("apps.slack.events.app_mention.get_blocks", return_value=[])

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_postMessage.assert_called()
        _, kwargs = client.chat_postMessage.call_args
        assert kwargs["thread_ts"] == "100.000"

    def test_handle_event_blocks_without_text_element(self, mocker):
        """Test handle_event with blocks but no text elements."""
        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [{"type": "user", "user_id": "U123"}],
                        }
                    ],
                }
            ],
            "ts": "123.456",
        }
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mocker.patch("apps.slack.events.app_mention.get_blocks", return_value=[])

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_update.assert_called()
        _, kwargs = client.chat_update.call_args
        assert kwargs["text"] == "Fallback text"

    def test_handle_event_blocks_without_rich_text_section(self, mocker):
        """Test handle_event with blocks but no rich_text_section."""
        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [{"type": "other_type", "data": "something"}],
                }
            ],
            "ts": "123.456",
        }
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mocker.patch("apps.slack.events.app_mention.get_blocks", return_value=[])

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_update.assert_called()
        _, kwargs = client.chat_update.call_args
        assert kwargs["text"] == "Fallback text"

    def test_handle_event_blocks_not_rich_text(self, mocker):
        """Test handle_event with blocks that are not rich_text type."""
        event = {
            "channel": "C123456",
            "text": "Fallback text",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "Some text"}}],
            "ts": "123.456",
        }
        client = mocker.Mock()
        client.chat_postMessage.return_value = {"ts": "999.999"}

        mock_objects = mocker.Mock()
        mocker.patch("apps.slack.events.app_mention.Conversation.objects", mock_objects)
        mock_qs = mocker.Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        mocker.patch("apps.slack.events.app_mention.get_blocks", return_value=[])

        handler = AppMention()
        handler.handle_event(event, client)

        client.chat_update.assert_called()
        _, kwargs = client.chat_update.call_args
        assert kwargs["text"] == "Fallback text"
