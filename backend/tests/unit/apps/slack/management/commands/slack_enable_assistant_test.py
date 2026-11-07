"""Tests for verified Slack channel setup."""

from types import SimpleNamespace

import pytest
from django.core.management.base import CommandError
from slack_sdk.errors import SlackApiError

from apps.slack.management.commands import slack_enable_assistant


@pytest.fixture
def records(mocker):
    workspace = SimpleNamespace(pk=1)
    conversation = mocker.Mock(
        workspace_id=1,
        is_nest_bot_assistant_enabled=False,
        has_slack_metadata=True,
        is_private=True,
        name="existing",
        sync_messages=False,
    )
    conversation.name = "existing"
    mocker.patch.object(slack_enable_assistant.transaction, "atomic")
    workspaces = mocker.patch.object(slack_enable_assistant.Workspace, "objects")
    conversations = mocker.patch.object(slack_enable_assistant.Conversation, "objects")
    workspaces.get_or_create.return_value = (workspace, False)
    conversations.filter.return_value.first.return_value = conversation
    return workspace, conversation, workspaces, conversations


def test_enable_existing_channel_preserves_settings(records):
    _, conversation, workspaces, _ = records
    command = slack_enable_assistant.Command()
    command.handle(workspace_id="T123", channel_id="C123")
    command.handle(workspace_id="T123", channel_id="C123")
    workspaces.get_or_create.assert_called_with(slack_workspace_id="T123")
    assert conversation.is_nest_bot_assistant_enabled is True
    assert conversation.name == "existing"
    assert conversation.sync_messages is False
    assert conversation.is_private is True
    assert conversation.workspace_id == 1
    conversation.save.assert_called_with(update_fields=["is_nest_bot_assistant_enabled"])


@pytest.mark.parametrize("is_private", [True, False])
def test_new_channel_requires_verified_privacy(records, mocker, is_private):
    workspace, conversation, _, conversations = records
    conversations.filter.return_value.first.return_value = None
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    channel = {"id": "C123", "is_private": is_private, "is_channel": True}
    app.client.conversations_info.return_value = {"channel": channel}
    update = mocker.patch.object(
        slack_enable_assistant.Conversation, "update_data", return_value=conversation
    )
    slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    app.client.conversations_info.assert_called_once_with(channel="C123")
    update.assert_called_once_with(channel, workspace)


def test_unsynchronized_existing_channel_keeps_settings(records, mocker):
    _, conversation, _, _ = records
    conversation.has_slack_metadata = False
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    app.client.conversations_info.return_value = {"channel": {"id": "C123", "is_private": True}}
    slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    assert conversation.is_private is True
    assert conversation.name == "existing"
    assert conversation.sync_messages is False
    assert conversation.workspace_id == 1


def test_reject_channel_from_another_workspace(records):
    _, conversation, _, _ = records
    conversation.workspace_id = 2
    with pytest.raises(CommandError, match="different workspace"):
        slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    conversation.save.assert_not_called()


@pytest.mark.parametrize("failure", ["api", "incomplete", "unconfigured"])
def test_unverified_privacy_never_enables_channel(records, mocker, failure):
    _, conversation, _, _ = records
    conversation.has_slack_metadata = False
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    if failure == "api":
        app.client.conversations_info.side_effect = SlackApiError(
            "denied", {"error": "missing_scope"}
        )
    elif failure == "incomplete":
        app.client.conversations_info.return_value = {"channel": {"id": "C123"}}
    else:
        mocker.patch.object(slack_enable_assistant.SlackConfig, "app", None)
    with pytest.raises(CommandError):
        slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    assert conversation.is_nest_bot_assistant_enabled is False
    conversation.save.assert_not_called()
