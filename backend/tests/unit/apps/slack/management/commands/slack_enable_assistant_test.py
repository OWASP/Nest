"""Tests for enabling a Slack assistant channel."""

from types import SimpleNamespace

import pytest
from django.core.management.base import CommandError

from apps.slack.management.commands import slack_enable_assistant


@pytest.fixture
def records(mocker):
    workspace = SimpleNamespace(pk=1)
    conversation = mocker.Mock(workspace_id=1, is_nest_bot_assistant_enabled=False)
    mocker.patch.object(slack_enable_assistant.transaction, "atomic")
    workspaces = mocker.patch.object(slack_enable_assistant.Workspace, "objects")
    conversations = mocker.patch.object(slack_enable_assistant.Conversation, "objects")
    workspaces.get_or_create.return_value = (workspace, False)
    conversations.get_or_create.return_value = (conversation, False)
    return workspace, conversation, workspaces, conversations


@pytest.mark.parametrize("created", [True, False])
def test_enable_new_or_existing_channel(records, created):
    workspace, conversation, workspaces, conversations = records
    conversations.get_or_create.return_value = (conversation, created)

    slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")

    workspaces.get_or_create.assert_called_once_with(slack_workspace_id="T123")
    conversations.get_or_create.assert_called_once_with(
        slack_channel_id="C123",
        defaults={"workspace": workspace, "is_channel": True},
    )
    assert conversation.is_nest_bot_assistant_enabled is True
    conversation.save.assert_called_once_with(update_fields=["is_nest_bot_assistant_enabled"])


def test_repeated_enable_preserves_other_channel_settings(records):
    _, conversation, _, _ = records
    conversation.is_nest_bot_assistant_enabled = True
    conversation.name = "existing-channel"
    conversation.sync_messages = False
    command = slack_enable_assistant.Command()

    command.handle(workspace_id="T123", channel_id="C123")
    command.handle(workspace_id="T123", channel_id="C123")

    assert conversation.is_nest_bot_assistant_enabled is True
    assert conversation.name == "existing-channel"
    assert conversation.sync_messages is False
    assert conversation.workspace_id == 1


def test_reject_channel_from_another_workspace(records):
    _, conversation, _, _ = records
    conversation.workspace_id = 2

    with pytest.raises(CommandError, match="different workspace"):
        slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")

    assert conversation.is_nest_bot_assistant_enabled is False
    conversation.save.assert_not_called()
