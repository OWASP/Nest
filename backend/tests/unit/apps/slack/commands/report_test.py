"""Tests for the /report Slack slash command."""

from unittest.mock import Mock

from apps.slack.commands.report import Report
from apps.slack.enums import ReportSource
from apps.slack.utils.report_modal import (
    FEATURE_OFF_TEXT,
    INVALID_LINK_TEXT,
    NOT_VISIBLE_TEXT,
    USAGE_TEXT,
    decode_metadata,
)


def enabled_workspace(**kwargs):
    """Return a workspace mock with content reporting enabled."""
    workspace = Mock(**kwargs)
    workspace.is_content_reporting_enabled = True
    return workspace


def disabled_workspace(**kwargs):
    """Return a workspace mock with content reporting disabled."""
    workspace = Mock(**kwargs)
    workspace.is_content_reporting_enabled = False
    return workspace


class TestReportCommand:
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
                "response_url": "https://hooks.slack.test/r",
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
                "response_url": "https://hooks.slack.test/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=INVALID_LINK_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

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
                "response_url": "https://hooks.slack.test/r",
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
        ack = Mock()
        respond = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "https://owasp.slack.com/archives/C123/p1700000000123456",
                "response_url": "https://hooks.slack.test/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=NOT_VISIBLE_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_opens_modal_with_command_source(self, mocker):
        """Test a readable permalink opens the shared modal with command source."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        workspace = enabled_workspace(
            content_report_alert_channel_id="C_ALERT",
            slack_workspace_id="T1",
        )
        conversation = Mock(is_im=False, is_mpim=False, slack_channel_id="C123")
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
            "apps.slack.shortcuts.report_content.Conversation.get_or_create_for_report",
            return_value=conversation,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.update_data",
            return_value=message,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Member.objects.get_or_create",
            return_value=(Mock(), False),
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
                "response_url": "https://hooks.slack.test/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        client.views_open.assert_called_once()
        _, kwargs = client.views_open.call_args
        assert kwargs["view"]["callback_id"] == "report_content_submit"
        assert decode_metadata(kwargs["view"]["private_metadata"])[2] == (ReportSource.COMMAND)
        respond.assert_not_called()

    def test_owasp_subcommand_uses_response_url_without_respond(self, mocker):
        """Test /owasp report works when Owasp delegates without a respond helper."""
        mocker.patch("apps.slack.commands.report.settings.SLACK_COMMANDS_ENABLED", new=True)
        post_ephemeral = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")
        ack = Mock()
        client = Mock()

        Report().handler(
            ack,
            {
                "user_id": "U_REP",
                "team_id": "T1",
                "text": "",
                "response_url": "https://hooks.slack.test/r",
                "trigger_id": "trig",
            },
            client,
        )

        post_ephemeral.assert_called_once_with("https://hooks.slack.test/r", USAGE_TEXT)
        client.views_open.assert_not_called()
