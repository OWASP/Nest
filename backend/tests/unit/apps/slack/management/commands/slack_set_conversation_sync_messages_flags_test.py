from unittest.mock import MagicMock

from apps.slack.management.commands.slack_set_conversation_sync_messages_flags import (
    SYNC_MESSAGES_CONVERSATIONS,
    Command,
)


class TestSetSyncMessagesCommand:
    def test_handle_method_calls_correct_orm_methods(self, mocker):
        """Unit tests the handle method by mocking the ORM."""
        mock_conversation = mocker.patch(
            "apps.slack.management.commands.slack_set_conversation_sync_messages_flags.Conversation"
        )
        mock_workspace = mocker.patch(
            "apps.slack.management.commands.slack_set_conversation_sync_messages_flags.Workspace"
        )
        mock_default_workspace = MagicMock()
        mock_workspace.get_default_workspace.return_value = mock_default_workspace
        command = Command()
        command.handle()
        mock_conversation.objects.update.assert_called_once_with(sync_messages=False)
        mock_conversation.objects.filter.assert_called_once_with(
            is_private=False,
            name__in=SYNC_MESSAGES_CONVERSATIONS,
            workspace=mock_default_workspace,
        )
        filtered_queryset_mock = mock_conversation.objects.filter.return_value
        filtered_queryset_mock.update.assert_called_once_with(sync_messages=True)
