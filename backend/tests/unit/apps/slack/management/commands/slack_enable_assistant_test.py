"""Tests for verified Slack channel setup."""

import pytest
from django.core.management.base import CommandError
from django.utils import timezone
from slack_sdk.errors import SlackApiError

from apps.slack.management.commands import slack_enable_assistant
from apps.slack.models import Conversation, Workspace


@pytest.fixture
def records(mocker):
    """Provide existing model instances with mocked database persistence."""
    workspace = Workspace(pk=1)
    conversation = Conversation(
        workspace=workspace,
        is_nest_bot_assistant_enabled=False,
        slack_metadata_synced_at=timezone.now(),
        is_private=True,
        name="existing",
        sync_messages=False,
    )
    mocker.patch.object(conversation, "save")
    mocker.patch.object(slack_enable_assistant.transaction, "atomic")
    workspaces = mocker.patch.object(slack_enable_assistant.Workspace, "objects")
    conversations = mocker.patch.object(slack_enable_assistant.Conversation, "objects")
    workspaces.get_or_create.return_value = (workspace, False)
    conversations.filter.return_value.first.return_value = conversation
    conversations.get.return_value = conversation
    return workspace, conversation, workspaces, conversations


def test_enable_existing_channel_preserves_settings(records):
    """Repeated enabling preserves synchronized channel metadata and local settings."""
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
    """New channels use Slack metadata only after checking the requested workspace."""
    workspace, conversation, _, conversations = records
    conversations.filter.return_value.first.return_value = None
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    channel = {
        "id": "C123",
        "is_private": is_private,
        "is_channel": True,
        "context_team_id": "T123",
    }
    app.client.conversations_info.return_value = {"channel": channel}
    update = mocker.patch.object(
        slack_enable_assistant.Conversation, "update_data", return_value=conversation
    )
    slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    app.client.conversations_info.assert_called_once_with(channel="C123")
    update.assert_called_once_with(channel, workspace)


def test_unsynchronized_existing_channel_keeps_settings(records, mocker):
    """Refresh every Slack field while retaining local synchronization preferences."""
    _, conversation, _, _ = records
    conversation.slack_metadata_synced_at = None
    conversation.sync_messages = True
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    channel = {
        "id": "C123",
        "is_private": False,
        "context_team_id": "T123",
        "name": "updated",
        "is_archived": True,
        "is_group": True,
        "is_mpim": True,
    }
    app.client.conversations_info.return_value = {"channel": channel}
    slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    assert conversation.is_private is False
    assert conversation.slack_metadata_synced_at is not None
    assert conversation.is_archived is True
    assert conversation.is_group is True
    assert conversation.is_mpim is True
    assert conversation.name == "updated"
    assert conversation.sync_messages is True
    assert conversation.workspace_id == 1


@pytest.mark.parametrize("synced", [True, False])
def test_reject_channel_from_another_workspace(records, mocker, synced):
    """Reject workspace conflicts before refreshing or reassigning the conversation."""
    _, conversation, _, _ = records
    conversation.workspace_id = 2
    if not synced:
        conversation.slack_metadata_synced_at = None
    update = mocker.patch.object(slack_enable_assistant.Conversation, "update_data")
    with pytest.raises(CommandError, match="different workspace"):
        slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    conversation.save.assert_not_called()
    update.assert_not_called()


@pytest.mark.parametrize(
    "failure", ["api", "incomplete", "unconfigured", "missing_team", "wrong_team"]
)
def test_unverified_privacy_never_enables_channel(records, mocker, failure):
    """Missing or conflicting Slack metadata prevents enabling the assistant."""
    _, conversation, _, _ = records
    conversation.slack_metadata_synced_at = None
    app = mocker.patch.object(slack_enable_assistant.SlackConfig, "app")
    if failure == "api":
        app.client.conversations_info.side_effect = SlackApiError(
            "denied", {"error": "missing_scope"}
        )
    elif failure == "incomplete":
        app.client.conversations_info.return_value = {"channel": {"id": "C123"}}
    elif failure in {"missing_team", "wrong_team"}:
        channel = {"id": "C123", "is_private": False}
        if failure == "wrong_team":
            channel["context_team_id"] = "T_OTHER"
        app.client.conversations_info.return_value = {"channel": channel}
    else:
        mocker.patch.object(slack_enable_assistant.SlackConfig, "app", None)
    with pytest.raises(CommandError):
        slack_enable_assistant.Command().handle(workspace_id="T123", channel_id="C123")
    assert conversation.is_nest_bot_assistant_enabled is False
    conversation.save.assert_not_called()
