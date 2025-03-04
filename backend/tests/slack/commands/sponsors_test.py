from unittest.mock import Mock, patch

import pytest
from django.conf import settings

from apps.slack.commands.sponsors import sponsors_handler
from apps.slack.common.presentation import EntityPresentation

# Constants for truncation values
NAME_TRUNCATION_LIMIT = 80
SUMMARY_TRUNCATION_LIMIT = 300


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "https://example.com"
        yield mock


@pytest.fixture(autouse=True)
def mock_sponsors_count():
    with patch("apps.owasp.models.sponsor.Sponsor.objects.count") as mock:
        mock.return_value = 50
        yield mock


class TestSponsorsHandler:
    @pytest.fixture()
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_client(self):
        client = Mock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_ack(self):
        return Mock()

    @pytest.fixture(autouse=True)
    def mock_get_blocks(self):
        with patch("apps.slack.commands.sponsors.get_blocks") as mock:
            mock.return_value = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "OWASP Sponsors Information - Search results for: diamond",
                    },
                }
            ]
            yield mock

    @pytest.mark.parametrize(
        ("commands_enabled", "search_query", "expected_calls"),
        [
            (True, "", 1),
            (True, "diamond", 1),
            (True, "platinum", 1),
            (False, "", 0),
            (False, "search term", 0),
        ],
    )
    def test_sponsors_handler_command_states(
        self, mock_client, mock_command, mock_ack, commands_enabled, search_query, expected_calls
    ):
        """Test sponsor handler with different command states and search queries."""
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = search_query

        sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)

        mock_ack.assert_called_once()

        assert mock_client.chat_postMessage.call_count == expected_calls
        if expected_calls > 0:
            mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])

    @pytest.mark.parametrize(
        ("search_query", "expected_text"),
        [
            ("", "OWASP Sponsors Information - Search results for: diamond"),
            ("diamond", "OWASP Sponsors Information - Search results for: diamond"),
            ("platinum", "OWASP Sponsors Information - Search results for: diamond"),
        ],
    )
    def test_sponsors_handler_fallback_text(
        self, mock_client, mock_command, mock_ack, search_query, expected_text
    ):
        """Test fallback text generation with different search queries."""
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = search_query

        sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)

        mock_client.chat_postMessage.assert_called_once()
        assert mock_client.chat_postMessage.call_args[1]["text"] == expected_text

    def test_sponsors_handler_presentation_config(
        self, mock_client, mock_command, mock_ack, mock_get_blocks
    ):
        """Test that presentation configuration is correctly passed to get_blocks."""
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "test"

        sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)

        mock_get_blocks.assert_called_once()
        _, kwargs = mock_get_blocks.call_args
        presentation = kwargs["presentation"]
        assert isinstance(presentation, EntityPresentation)
        assert presentation.include_feedback is True
        assert presentation.include_metadata is True
        assert presentation.include_pagination is False
        assert presentation.include_timestamps is True
        assert presentation.name_truncation == NAME_TRUNCATION_LIMIT
        assert presentation.summary_truncation == SUMMARY_TRUNCATION_LIMIT

    def test_sponsors_handler_search_query_processing(
        self, mock_client, mock_command, mock_ack, mock_get_blocks
    ):
        """Test search query processing and stripping."""
        settings.SLACK_COMMANDS_ENABLED = True
        test_queries = ["  test  ", "test", "   TEST   ", "Test  "]

        for query in test_queries:
            mock_command["text"] = query
            sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)

            mock_get_blocks.assert_called_with(
                search_query=query.strip(),
                limit=10,
                presentation=pytest.approx(
                    EntityPresentation(
                        include_feedback=True,
                        include_metadata=True,
                        include_pagination=False,
                        include_timestamps=True,
                        name_truncation=80,
                        summary_truncation=300,
                    )
                ),
            )

    def test_sponsors_handler_channel_error(self, mock_client, mock_command, mock_ack):
        """Test handling of channel opening errors."""
        settings.SLACK_COMMANDS_ENABLED = True
        mock_client.conversations_open.side_effect = Exception("Channel error")

        with pytest.raises(Exception, match="Channel error"):
            sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)

        mock_client.chat_postMessage.assert_not_called()

    def test_sponsors_handler_message_error(self, mock_client, mock_command, mock_ack):
        """Test handling of message posting errors."""
        settings.SLACK_COMMANDS_ENABLED = True
        mock_client.chat_postMessage.side_effect = Exception("Message error")

        with pytest.raises(Exception, match="Message error"):
            sponsors_handler(ack=mock_ack, command=mock_command, client=mock_client)
