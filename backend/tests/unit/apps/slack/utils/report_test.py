"""Tests for Slack content-report open-path helpers."""

from http import HTTPStatus
from unittest.mock import Mock

from slack_sdk.errors import SlackApiError, SlackClientError

from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    ALREADY_REPORTED_TEXT,
    METADATA_UNAVAILABLE_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    PRIVATE_CHANNEL_TEXT,
    build_error_modal,
    build_loading_modal,
)
from apps.slack.utils.report import (
    CONVERSATION_INFO_TIMEOUT_SECONDS,
    RESPONSE_URL_TIMEOUT_SECONDS,
    WORKSPACE_MISMATCH_TEXT,
    is_allowed_response_url,
    make_ephemeral,
    open_report_content_modal,
    post_ephemeral_url,
    resolve_conversation,
    update_modal,
)
from tests.unit.apps.slack.conftest import enabled_workspace


def synced_conversation(**kwargs):
    """Return a conversation mock with Slack metadata already loaded."""
    conversation = Mock(is_private=False, **kwargs)
    conversation.has_fresh_metadata = True
    conversation.has_slack_metadata = True
    return conversation


class TestResolveConversation:
    def test_loads_flags_from_conversations_info(self, mocker):
        """Test successful conversations.info updates and returns the conversation."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock()
        existing.has_fresh_metadata = False
        existing.mark_direct_message_metadata.return_value = False
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

    def test_skips_conversations_info_when_metadata_is_fresh(self, mocker):
        """Test fresh Slack metadata skips the network call on the trigger path."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock(is_private=False)
        existing.has_fresh_metadata = True
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        update = mocker.patch("apps.slack.utils.report.Conversation.update_data")

        assert resolve_conversation(client, workspace, "C1") is existing
        client.conversations_info.assert_not_called()
        update.assert_not_called()

    def test_refreshes_when_metadata_is_stale(self, mocker):
        """Test stale Slack metadata still triggers conversations.info."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock()
        existing.has_fresh_metadata = False
        existing.mark_direct_message_metadata.return_value = False
        updated = Mock(is_private=False)
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        channel = {"id": "C1", "is_private": False, "is_channel": True}
        client.conversations_info.return_value = {"channel": channel}
        update = mocker.patch(
            "apps.slack.utils.report.Conversation.update_data",
            return_value=updated,
        )

        assert resolve_conversation(client, workspace, "C1") is updated
        client.conversations_info.assert_called_once()
        update.assert_called_once_with(channel, workspace, save=True)

    def test_falls_back_on_slack_client_error(self, mocker):
        """Test SlackClientError keeps the existing conversation row."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock(is_private=False, slack_channel_id="G1")
        existing.has_fresh_metadata = False
        existing.mark_direct_message_metadata.return_value = False
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        client.conversations_info.side_effect = SlackClientError("timeout")

        assert resolve_conversation(client, workspace, "G1") is existing

    def test_classifies_direct_messages_without_conversations_info(self, mocker):
        """Test D-prefixed channels skip conversations.info and mark IM metadata."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock(slack_channel_id="D123")
        existing.has_fresh_metadata = False
        existing.mark_direct_message_metadata.return_value = True
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=existing,
        )
        update = mocker.patch("apps.slack.utils.report.Conversation.update_data")

        assert resolve_conversation(client, workspace, "D123") is existing
        existing.mark_direct_message_metadata.assert_called_once_with()
        client.conversations_info.assert_not_called()
        update.assert_not_called()

    def test_falls_back_on_malformed_response(self, mocker):
        """Test missing or non-dict channel payloads keep the existing conversation."""
        client = Mock()
        workspace = enabled_workspace()
        existing = Mock(slack_channel_id="C1")
        existing.has_fresh_metadata = False
        existing.mark_direct_message_metadata.return_value = False
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
        webhook = mocker.patch("apps.slack.utils.report.WebhookClient")

        post_ephemeral_url("https://evil.example/r", "hi")

        webhook.assert_not_called()

    def test_is_allowed_response_url_rejects_urlparse_errors(self, mocker):
        """Test malformed response_url values that raise during parse are rejected."""
        mocker.patch(
            "apps.slack.utils.report.urlparse",
            side_effect=ValueError("bad url"),
        )

        assert is_allowed_response_url("https://hooks.slack.com/r") is False

    def test_post_ephemeral_url_swallows_request_errors(self, mocker):
        """Test response_url failures are logged and ignored."""
        client = Mock()
        client.send.side_effect = SlackClientError("boom")
        mocker.patch("apps.slack.utils.report.WebhookClient", return_value=client)

        post_ephemeral_url("https://hooks.slack.com/r", "hi")

        client.send.assert_called_once_with(text="hi", response_type="ephemeral")

    def test_post_ephemeral_url_logs_error_status(self, mocker):
        """Test non-2xx response_url status codes are logged without raising."""
        client = Mock()
        client.send.return_value = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, body="error")
        webhook = mocker.patch("apps.slack.utils.report.WebhookClient", return_value=client)
        logger = mocker.patch("apps.slack.utils.report.logger")

        post_ephemeral_url("https://hooks.slack.com/r", "hi")

        webhook.assert_called_once_with(
            "https://hooks.slack.com/r",
            timeout=RESPONSE_URL_TIMEOUT_SECONDS,
        )
        client.send.assert_called_once_with(text="hi", response_type="ephemeral")
        logger.error.assert_called_once()

    def test_post_ephemeral_url_success(self, mocker):
        """Test successful response_url posts via WebhookClient."""
        client = Mock()
        client.send.return_value = Mock(status_code=HTTPStatus.OK, body="ok")
        mocker.patch("apps.slack.utils.report.WebhookClient", return_value=client)
        logger = mocker.patch("apps.slack.utils.report.logger")

        post_ephemeral_url("https://hooks.slack.com/r", "hi")

        client.send.assert_called_once_with(text="hi", response_type="ephemeral")
        logger.error.assert_not_called()
        logger.exception.assert_not_called()

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
        """Test ValueError from conversation lookup updates the loading modal."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            side_effect=ValueError("workspace mismatch"),
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

        client.views_open.assert_called_once()
        assert client.views_open.call_args.kwargs["view"] == build_loading_modal()
        client.views_update.assert_called_once_with(
            view_id="V1",
            view=build_error_modal(WORKSPACE_MISMATCH_TEXT),
        )
        respond.assert_not_called()

    def test_open_modal_private_channel(self, mocker):
        """Test open path rejects private channels after exchanging trigger_id."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        conversation = Mock(is_private=False)
        conversation.has_fresh_metadata = False
        conversation.mark_direct_message_metadata.return_value = False
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=conversation,
        )
        client.conversations_info.return_value = {
            "channel": {"id": "C_PRIV", "is_private": True, "is_channel": True},
        }
        mocker.patch(
            "apps.slack.utils.report.Conversation.update_data",
            return_value=Mock(is_private=True, has_slack_metadata=True),
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
        client.views_update.assert_called_once_with(
            view_id="V1",
            view=build_error_modal(PRIVATE_CHANNEL_TEXT),
        )
        respond.assert_not_called()

    def test_open_modal_metadata_unavailable(self, mocker):
        """Test unknown privacy fails closed after a failed metadata refresh."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        conversation = Mock(is_private=False, has_slack_metadata=False)
        conversation.has_fresh_metadata = False
        conversation.mark_direct_message_metadata.return_value = False
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=conversation,
        )
        client.conversations_info.side_effect = SlackClientError("timeout")

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

        client.views_update.assert_called_once_with(
            view_id="V1",
            view=build_error_modal(METADATA_UNAVAILABLE_TEXT),
        )
        respond.assert_not_called()

    def test_open_modal_already_reported(self, mocker):
        """Test already-reported messages update the loading modal."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=synced_conversation(),
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=True,
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

        client.views_update.assert_called_once_with(
            view_id="V1",
            view=build_error_modal(ALREADY_REPORTED_TEXT),
        )

    def test_open_modal_views_open_failure(self, mocker):
        """Test views_open failures send an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.side_effect = SlackApiError(
            message="fail",
            response={"ok": False, "error": "invalid_trigger"},
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
        client.views_update.assert_not_called()

    def test_open_modal_views_open_without_view_id(self, mocker):
        """Test views_open without a view id sends an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {}}

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
        client.views_update.assert_not_called()

    def test_open_modal_build_failure_updates_error_view(self, mocker):
        """Test construction failures after views_open replace the loading modal."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        mocker.patch(
            "apps.slack.utils.report.report_modal_view",
            side_effect=RuntimeError("build failed"),
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

        client.views_update.assert_called_once_with(
            view_id="V1",
            view=build_error_modal(MODAL_OPEN_FAILED_TEXT),
        )
        respond.assert_not_called()

    def test_open_modal_views_update_failure(self, mocker):
        """Test views_update failures send an ephemeral after the loading modal opens."""
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}
        client.views_update.side_effect = SlackClientError("timeout")
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=synced_conversation(),
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=Mock(pk=1, text="hi", raw_data={"user": "U_OTHER"}),
        )
        mocker.patch(
            "apps.slack.utils.report.Member.objects.get_or_create",
            return_value=(Mock(), False),
        )
        mocker.patch(
            "apps.slack.utils.report.build_report_modal",
            return_value={"type": "modal"},
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

        client.views_update.assert_called_once()
        respond.assert_called_once_with(text=MODAL_OPEN_FAILED_TEXT, response_type="ephemeral")

    def test_update_modal_client_error(self):
        """Test update_modal returns False when Slack rejects views_update."""
        client = Mock()
        client.views_update.side_effect = SlackClientError("timeout")

        assert update_modal(client, "V1", {"type": "modal"}) is False

    def test_open_modal_views_open_client_error(self, mocker):
        """Test SlackClientError from views_open sends an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.side_effect = SlackClientError("timeout")

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
        client.views_open.return_value = {"view": {"id": "V1"}}
        conversation = synced_conversation(
            is_im=False,
            is_mpim=False,
            slack_channel_id="C1",
        )
        message = Mock(pk=1, text="bot", raw_data={})
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=conversation,
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        update = mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=message,
        )
        get_or_create = mocker.patch("apps.slack.utils.report.Member.objects.get_or_create")
        modal = {"type": "modal", "callback_id": "report_content_submit"}
        mocker.patch(
            "apps.slack.utils.report.build_report_modal",
            return_value=modal,
        )

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
        assert client.views_open.call_args.kwargs["view"] == build_loading_modal()
        client.views_update.assert_called_once_with(view_id="V1", view=modal)
        respond.assert_not_called()
