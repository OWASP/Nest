"""Tests for the /report Slack slash command."""

from unittest.mock import Mock

from apps.slack.commands.owasp import Owasp
from apps.slack.commands.report import Report
from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    DM_NOT_VISIBLE_TEXT,
    FEATURE_OFF_TEXT,
    INVALID_LINK_TEXT,
    NOT_VISIBLE_TEXT,
    USAGE_TEXT,
    decode_metadata,
)
from tests.unit.apps.slack.conftest import disabled_workspace, enabled_workspace


class TestReportCommand:
    def test_commands_disabled_is_noop(self, mocker):
        """Test /report does nothing when Slack commands are disabled."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=False)
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        ack.assert_called_once_with()
        respond.assert_not_called()
        client.views_open.assert_not_called()

    def test_incomplete_payload_ignored(self, mocker):
        """Test incomplete /report payloads are logged and ignored."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        warning = mocker.patch("apps.slack.commands.report.logger.warning")
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        warning.assert_called_once_with("Ignoring incomplete /report command payload")
        respond.assert_not_called()
        client.views_open.assert_not_called()

    def test_usage_when_empty(self, mocker):
        """Test empty /report text returns usage help."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=USAGE_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_invalid_link(self, mocker):
        """Test invalid permalink text is rejected."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "not-a-link",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=INVALID_LINK_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_slack_formatted_link_with_spaces_in_label(self, mocker):
        """Test Slack mrkdwn links with spaces in the label still parse."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        open_modal = mocker.patch("apps.slack.commands.report.open_report_content_modal")
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value={"user": "U_OTHER", "ts": "1700000000.123456", "text": "spam"},
        )
        ack = Mock()
        respond = Mock()
        client = Mock()
        link = (
            "<https://owasp.slack.com/archives/C123/p1700000000123456"
            "|Message with spaces in label>"
        )

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": link,
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        open_modal.assert_called_once()
        _, kwargs = open_modal.call_args
        assert kwargs["channel_id"] == "C123"
        assert kwargs["message_payload"]["ts"] == "1700000000.123456"
        respond.assert_not_called()

    def test_feature_off(self, mocker):
        """Test unconfigured workspace gets an ephemeral error."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=disabled_workspace(content_report_alert_channel_id=""),
        )
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=FEATURE_OFF_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_not_visible(self, mocker):
        """Test messages NestBot cannot fetch are rejected."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value=None,
        )
        mocker.patch(
            "apps.slack.commands.report.Conversation.get_by_channel_id",
            return_value=None,
        )
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=NOT_VISIBLE_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_dm_not_visible_suggests_shortcut_only(self, mocker):
        """Test DM load failures suggest the message shortcut, not adding NestBot."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value=None,
        )
        mocker.patch(
            "apps.slack.commands.report.Conversation.get_by_channel_id",
            return_value=None,
        )
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/D123ABCDEF/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=DM_NOT_VISIBLE_TEXT, response_type="ephemeral")
        assert "Add NestBot" not in DM_NOT_VISIBLE_TEXT
        client.views_open.assert_not_called()

    def test_mpim_conversation_not_visible_suggests_shortcut(self, mocker):
        """Test known MPIM load failures use the DM-not-visible copy."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value=None,
        )
        mocker.patch(
            "apps.slack.commands.report.Conversation.get_by_channel_id",
            return_value=Mock(is_im=False, is_mpim=True),
        )
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/G123ABCDEF/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=DM_NOT_VISIBLE_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_opens_modal_with_command_source(self, mocker):
        """Test a readable permalink opens the shared modal with command source."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        workspace = enabled_workspace(
            content_report_alert_channel_id="C_ALERT",
            slack_workspace_id="T1",
        )
        conversation = Mock(
            is_im=False,
            is_mpim=False,
            is_private=False,
            slack_channel_id="C123",
        )
        conversation.has_fresh_metadata = True
        conversation.has_slack_metadata = True
        message = Mock(pk=7, text="spam", raw_data={"user": "U_OTHER", "ts": "1700000000.123456"})
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=workspace,
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value={"user": "U_OTHER", "ts": "1700000000.123456", "text": "spam"},
        )
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=conversation,
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.utils.report.Message.update_data",
            return_value=message,
        )
        mocker.patch(
            "apps.slack.utils.report.Member.objects.get_or_create",
            return_value=(Mock(), False),
        )
        ack = Mock()
        respond = Mock()
        client = Mock()
        client.views_open.return_value = {"view": {"id": "V1"}}

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        client.views_open.assert_called_once()
        client.views_update.assert_called_once()
        view = client.views_update.call_args.kwargs["view"]
        assert view["callback_id"] == "report_content_submit"
        assert decode_metadata(view["private_metadata"])[2] == (ReportSource.COMMAND)
        respond.assert_not_called()

    def test_injects_message_ts_when_payload_missing_ts(self, mocker):
        """Test /report injects message_ts when load_payload omits ts."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        open_modal = mocker.patch("apps.slack.commands.report.open_report_content_modal")
        mocker.patch(
            "apps.slack.commands.report.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.commands.report.Message.load_payload",
            return_value={"user": "U_OTHER", "text": "spam"},
        )

        Report().handler(
            Mock(),
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            Mock(),
            Mock(),
        )

        _, kwargs = open_modal.call_args
        assert kwargs["message_payload"]["ts"] == "1700000000.123456"

    def test_uses_response_url_without_respond(self, mocker):
        """Test Report.handler falls back to response_url without a respond helper."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        post_ephemeral = mocker.patch("apps.slack.utils.report.post_ephemeral_url")
        ack = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
        )

        post_ephemeral.assert_called_once_with("https://hooks.slack.com/r", USAGE_TEXT)
        client.views_open.assert_not_called()

    def test_owasp_report_empty_remainder_shows_usage(self, mocker):
        """Test /owasp report with no args clears text and shows usage via respond."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        report_handler = mocker.spy(Report, "handler")
        ack = Mock()
        respond = Mock()
        client = Mock()

        Owasp().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "report",
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        report_handler.assert_called_once()
        command = report_handler.call_args.args[2]
        assert command["text"] == ""
        assert report_handler.call_args.kwargs["respond"] is respond
        respond.assert_called_once_with(text=USAGE_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()
