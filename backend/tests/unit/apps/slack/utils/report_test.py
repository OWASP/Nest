"""Tests for Slack content-report open-path helpers."""

from unittest.mock import Mock

import requests
from slack_sdk.errors import SlackApiError, SlackClientError

from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    PRIVATE_CHANNEL_TEXT,
)
from apps.slack.utils.report import (
    CONVERSATION_INFO_TIMEOUT_SECONDS,
    WORKSPACE_MISMATCH_TEXT,
    is_allowed_response_url,
    make_ephemeral,
    open_report_content_modal,
    post_ephemeral_url,
    resolve_conversation,
)
from tests.unit.apps.slack.conftest import enabled_workspace


class TestResolveConversation:
    def test_loads_flags_from_conversations_info(self, mocker):
        """Test successful conversations.info updates and returns the conversation."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock()
        updated = Mock(is_private=False, is_mpim=True)
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        channel = {"id": "G1", "is_mpim": True, "is_private": False}
        client.conversations_info.return_value = {"channel": channel}
        update = mocker.patch(
            "apps.slack.utils.report.Conversation.update_data",
            return_value=updated,
        )

        assert resolve_conversation(client, workspace, "G1") is updated
        client.conversations_info.assert_called_once_with(
            channel="G1",
            timeout=CONVERSATION_INFO_TIMEOUT_SECONDS,
        )
        update.assert_called_once_with(channel, workspace, save=True)

    def test_falls_back_on_slack_client_error(self, mocker):
        """Test SlackClientError keeps the existing conversation row."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock(is_private=False)
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        client.conversations_info.side_effect = SlackClientError("timeout")

        assert resolve_conversation(client, workspace, "G1") is existing

    def test_falls_back_on_malformed_response(self, mocker):
        """Test missing or non-dict channel payloads keep the existing conversation."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock()
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        update = mocker.patch("apps.slack.utils.report.Conversation.update_data")

        client.conversations_info.return_value = {"channel": None}
        assert resolve_conversation(client, workspace, "C1") is existing

        client.conversations_info.return_value = {"channel": {"name": "no-id"}}
        assert resolve_conversation(client, workspace, "C1") is existing

        client.conversations_info.return_value = None
        assert resolve_conversation(client, workspace, "C1") is existing
        update.assert_not_called()


class TestReportOpenPathHelpers:
    def test_make_ephemeral_prefers_respond(self, mocker):
        """Test make_ephemeral uses Bolt respond when available."""
        respond = Mock()
        post = mocker.patch("apps.slack.utils.report.post_ephemeral_url")

        make_ephemeral(respond, "https://hooks.slack.com/r")(text="hi")

        respond.assert_called_once_with(text="hi", response_type="ephemeral")
        post.assert_not_called()

    def test_make_ephemeral_falls_back_to_response_url(self, mocker):
        """Test make_ephemeral posts to response_url without respond."""
        post = mocker.patch("apps.slack.utils.report.post_ephemeral_url")

        make_ephemeral(None, "https://hooks.slack.com/r")(text="hi")

        post.assert_called_once_with("https://hooks.slack.com/r", "hi")

    def test_post_ephemeral_url_rejects_disallowed_host(self, mocker):
        """Test response_url hosts outside Slack hooks are rejected."""
        post = mocker.patch("apps.slack.utils.report.requests.post")

        post_ephemeral_url("https://evil.example/r", "hi")

        post.assert_not_called()

    def test_is_allowed_response_url_rejects_urlparse_errors(self, mocker):
        """Test malformed response_url values that raise during parse are rejected."""
        mocker.patch(
            "apps.slack.utils.report.urlparse",
            side_effect=ValueError("bad url"),
        )

        assert is_allowed_response_url("https://hooks.slack.com/r") is False

    def test_post_ephemeral_url_swallows_request_errors(self, mocker):
        """Test response_url failures are logged and ignored."""
        mocker.patch(
            "apps.slack.utils.report.requests.post",
            side_effect=requests.RequestException("boom"),
        )
        post_ephemeral_url("https://hooks.slack.com/r", "hi")

    def test_post_ephemeral_url_raises_for_status(self, mocker):
        """Test non-2xx response_url posts are treated as request failures."""
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("500")
        mocker.patch("apps.slack.utils.report.requests.post", return_value=response)

        post_ephemeral_url("https://hooks.slack.com/r", "hi")

        response.raise_for_status.assert_called_once_with()

    def test_open_modal_missing_message_ts(self):
        """Test open path rejects payloads without a message timestamp."""
        respond = Mock()
        open_report_content_modal(
            client=Mock(),
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )
        respond.assert_called_once_with(text=MISSING_MESSAGE_TEXT, response_type="ephemeral")

    def test_open_modal_workspace_mismatch(self, mocker):
        """Test ValueError from conversation lookup becomes an ephemeral error."""
        respond = Mock()
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            side_effect=ValueError("workspace mismatch"),
        )

        open_report_content_modal(
            client=Mock(),
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        respond.assert_called_once_with(
            text=WORKSPACE_MISMATCH_TEXT,
            response_type="ephemeral",
        )

    def test_open_modal_private_channel(self, mocker):
        """Test open path rejects private channels."""
        respond = Mock()
        client = Mock()
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=Mock(is_private=False),
        )
        client.conversations_info.return_value = {
            "channel": {"id": "C_PRIV", "is_private": True, "is_channel": True},
        }
        mocker.patch(
            "apps.slack.utils.report.Conversation.update_data",
            return_value=Mock(is_private=True),
        )

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C_PRIV",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        client.conversations_info.assert_called_once_with(
            channel="C_PRIV",
            timeout=CONVERSATION_INFO_TIMEOUT_SECONDS,
        )
        respond.assert_called_once_with(text=PRIVATE_CHANNEL_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_open_modal_views_open_failure(self, mocker):
        """Test views_open failures send an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.side_effect = SlackApiError(
            message="fail",
            response={"ok": False, "error": "invalid_trigger"},
        )
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=Mock(is_private=False),
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=Mock(pk=1, text="x", raw_data={}),
        )
        mocker.patch(
            "apps.slack.utils.report.Member.objects.get_or_create",
            return_value=(Mock(), False),
        )

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        respond.assert_called_once_with(text=MODAL_OPEN_FAILED_TEXT, response_type="ephemeral")

    def test_open_modal_views_open_client_error(self, mocker):
        """Test SlackClientError from views_open sends an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.side_effect = SlackClientError("timeout")
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=Mock(is_private=False),
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=Mock(pk=1, text="x", raw_data={}),
        )
        mocker.patch(
            "apps.slack.utils.report.Member.objects.get_or_create",
            return_value=(Mock(), False),
        )

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        respond.assert_called_once_with(text=MODAL_OPEN_FAILED_TEXT, response_type="ephemeral")

    def test_make_ephemeral_noop_without_destinations(self, mocker):
        """Test make_ephemeral is a no-op without respond or response_url."""
        post = mocker.patch("apps.slack.utils.report.post_ephemeral_url")

        make_ephemeral(None, "")(text="hi")

        post.assert_not_called()

    def test_open_modal_without_author(self, mocker):
        """Test open path works when the message has no author user id."""
        respond = Mock()
        client = Mock()
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=Mock(
                is_im=False,
                is_mpim=False,
                is_private=False,
                slack_channel_id="C1",
            ),
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        update = mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=Mock(pk=1, text="bot", raw_data={}),
        )
        get_or_create = mocker.patch("apps.slack.utils.report.Member.objects.get_or_create")

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "text": "bot"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.COMMAND,
            respond=respond,
        )

        update.assert_called_once()
        assert update.call_args.kwargs["author"] is None
        get_or_create.assert_not_called()
        client.views_open.assert_called_once()
        respond.assert_not_called()
