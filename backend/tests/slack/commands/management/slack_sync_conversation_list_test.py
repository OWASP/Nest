from unittest import mock

import pytest

from apps.slack.management.commands.slack_sync_conversation_list import Command
from apps.slack.models.conversation import Conversation


@pytest.fixture()
def command():
    return Command()


@pytest.mark.parametrize(
    ("argument_name", "expected_properties"),
    [
        (
            "--batch-size",
            {
                "type": int,
                "default": 200,
                "help": "Number of conversations to retrieve per request",
            },
        ),
        (
            "--delay",
            {"type": float, "default": 0.1, "help": "Delay between API requests in seconds"},
        ),
        (
            "--dry-run",
            {"action": "store_true", "help": "Fetch conversations but don't update the database"},
        ),
    ],
)
def test_add_arguments(argument_name, expected_properties):
    mock_parser = mock.Mock()
    command = Command()
    command.add_arguments(mock_parser)
    mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)


# Constants for test values
BATCH_SIZE_DEFAULT = 200
BATCH_SIZE_CUSTOM = 100
DELAY_DEFAULT = 0.1
DELAY_CUSTOM = 0.5
EXPECTED_API_CALLS = 2


@pytest.mark.parametrize(
    ("batch_size", "delay", "dry_run"),
    [
        (BATCH_SIZE_DEFAULT, DELAY_DEFAULT, False),
        (BATCH_SIZE_CUSTOM, DELAY_CUSTOM, False),
        (BATCH_SIZE_DEFAULT, DELAY_DEFAULT, True),
    ],
)
def test_handle(command, batch_size, delay, dry_run):
    # Mock SlackConfig.app
    with mock.patch(
        "apps.slack.management.commands.slack_sync_conversation_list.SlackConfig"
    ) as mock_slack_config:
        mock_app = mock.Mock()
        mock_slack_config.app = mock_app

        # Mock conversations data
        mock_conversations = [
            {"id": "C12345", "name": "general", "is_channel": True},
            {"id": "C67890", "name": "random", "is_channel": True},
        ]

        # Mock _fetch_all_conversations
        with mock.patch.object(command, "_fetch_all_conversations") as mock_fetch:
            mock_fetch.return_value = mock_conversations

            # Mock Conversation.update_data
            mock_conversation = mock.Mock(spec=Conversation)

            with (
                mock.patch.object(Conversation, "update_data") as mock_update_data,
                mock.patch.object(Conversation, "bulk_save") as mock_bulk_save,
                mock.patch.object(command.stdout, "write") as mock_stdout_write,
            ):
                mock_update_data.return_value = mock_conversation

                # Execute command
                command.handle(batch_size=batch_size, delay=delay, dry_run=dry_run)

                # Assert _fetch_all_conversations was called correctly
                mock_fetch.assert_called_once_with(mock_app, batch_size, delay)

                # Assert Conversation.update_data was called for each conversation
                if not dry_run:
                    assert mock_update_data.call_count == len(mock_conversations)
                    mock_bulk_save.assert_called_once()
                else:
                    mock_update_data.assert_not_called()
                    mock_bulk_save.assert_not_called()

                # Assert output
                mock_stdout_write.assert_any_call(mock.ANY)


def test_fetch_all_conversations(command):
    # Mock Slack app
    mock_app = mock.Mock()

    # Mock conversation data
    mock_conversations = [
        {"id": "C12345", "name": "general", "is_channel": True},
        {"id": "C67890", "name": "random", "is_channel": True},
    ]

    # Mock API responses
    first_response = {
        "ok": True,
        "channels": mock_conversations[:1],
        "response_metadata": {"next_cursor": "cursor123"},
    }
    second_response = {
        "ok": True,
        "channels": mock_conversations[1:],
        "response_metadata": {"next_cursor": ""},
    }

    # Configure mock API client
    mock_app.client.conversations_list.side_effect = [first_response, second_response]

    # Execute function
    with mock.patch(
        "apps.slack.management.commands.slack_sync_conversation_list.time.sleep"
    ) as mock_sleep:
        result = command._fetch_all_conversations(mock_app, 100, 0.1)

    # Verify API calls
    assert mock_app.client.conversations_list.call_count == EXPECTED_API_CALLS
    mock_app.client.conversations_list.assert_any_call(
        limit=100,
        exclude_archived=False,
        types="public_channel,private_channel",
        cursor=None,
        timeout=30,
    )
    mock_app.client.conversations_list.assert_any_call(
        limit=100,
        exclude_archived=False,
        types="public_channel,private_channel",
        cursor="cursor123",
        timeout=30,
    )

    # Verify sleep was called for rate limiting
    mock_sleep.assert_called_once_with(0.1)

    # Verify result
    assert result == mock_conversations


def test_fetch_all_conversations_api_error(command):
    # Mock Slack app
    mock_app = mock.Mock()

    # Mock error response
    error_response = {
        "ok": False,
        "error": "rate_limited",
    }

    # Configure mock API client
    mock_app.client.conversations_list.return_value = error_response

    # Execute function
    with (
        mock.patch("apps.slack.management.commands.slack_sync_conversation_list.time.sleep"),
        mock.patch(
            "apps.slack.management.commands.slack_sync_conversation_list.logger"
        ) as mock_logger,
    ):
        result = command._fetch_all_conversations(mock_app, 100, 0.1)

    # Verify result
    assert result == []

    # Verify logger was called
    mock_logger.exception.assert_called_once()
