"""Tests for Report content Slack shortcut handlers and submission."""

from unittest.mock import Mock

from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    ALREADY_REPORTED_TEXT,
    FEATURE_OFF_TEXT,
    MISSING_MESSAGE_TEXT,
    PRIVATE_CHANNEL_TEXT,
    SELF_REPORT_TEXT,
    SUBMIT_FAILED_TEXT,
    SUCCESS_TEXT,
    decode_metadata,
    encode_metadata,
)
from apps.slack.shortcuts.report_content import (
    ReportContent,
    load_submission_context,
    post_content_report_alert,
)
from tests.unit.apps.slack.conftest import disabled_workspace, enabled_workspace


class TestReportContentShortcut:
    def test_feature_off(self, mocker):
        """Test unconfigured workspace gets an ephemeral error."""
        ack = Mock()
        respond = Mock()
        client = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=disabled_workspace(content_report_alert_channel_id=""),
        )

        ReportContent().handle(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=FEATURE_OFF_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_self_report_rejected(self, mocker):
        """Test reporters cannot report their own messages."""
        ack = Mock()
        respond = Mock()
        client = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )

        ReportContent().handle(
            ack,
            {
                "user": {"id": "U_SAME"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_SAME", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=SELF_REPORT_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_already_reported(self, mocker):
        """Test an existing content report skips the modal."""
        ack = Mock()
        respond = Mock()
        client = Mock()
        conversation = Mock(is_private=False)
        conversation.has_fresh_metadata = True
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=conversation,
        )
        mocker.patch(
            "apps.slack.utils.report.ContentReport.exists_for",
            return_value=True,
        )

        ReportContent().handle(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        respond.assert_called_once_with(text=ALREADY_REPORTED_TEXT, response_type="ephemeral")
        client.views_open.assert_not_called()

    def test_opens_modal(self, mocker):
        """Test a valid shortcut persists the message and opens the modal."""
        ack = Mock()
        respond = Mock()
        client = Mock()
        workspace = enabled_workspace(
            content_report_alert_channel_id="C_ALERT",
            slack_workspace_id="T1",
        )
        conversation = Mock(
            is_im=True,
            is_mpim=False,
            is_private=False,
            slack_channel_id="D1",
        )
        conversation.has_fresh_metadata = True
        message = Mock(pk=5, text="spam text", raw_data={"user": "U_OTHER"})
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=workspace,
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

        ReportContent().handle(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "spam text"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.com/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        client.views_open.assert_called_once()
        _, kwargs = client.views_open.call_args
        assert kwargs["trigger_id"] == "trig"
        assert kwargs["view"]["title"]["text"] == "Report Content"
        assert decode_metadata(kwargs["view"]["private_metadata"])[2] == (ReportSource.SHORTCUT)
        respond.assert_not_called()


class TestReportContentSubmission:
    def test_consent_and_report_type_required(self):
        """Test missing consent and category both return modal errors."""
        ack = Mock()

        ReportContent().handle_view(
            ack,
            {"view": {"state": {"values": {}}}, "user": {"id": "U_REP"}},
            Mock(),
        )

        _, kwargs = ack.call_args
        assert kwargs["response_action"] == "errors"
        assert "consent" in kwargs["errors"]
        assert "report_type" in kwargs["errors"]

    def test_consent_required_when_category_selected(self):
        """Test missing consent alone returns a consent modal error."""
        ack = Mock()

        ReportContent().handle_view(
            ack,
            {
                "view": {
                    "state": {
                        "values": {
                            "report_type": {
                                "report_type": {"selected_option": {"value": "spam"}},
                            },
                        }
                    }
                },
                "user": {"id": "U_REP"},
            },
            Mock(),
        )

        _, kwargs = ack.call_args
        assert kwargs["response_action"] == "errors"
        assert "consent" in kwargs["errors"]
        assert "report_type" not in kwargs["errors"]

    def test_report_type_required_when_consent_given(self):
        """Test missing category alone returns a report-type modal error."""
        ack = Mock()

        ReportContent().handle_view(
            ack,
            {
                "view": {
                    "state": {
                        "values": {
                            "consent": {
                                "consent": {"selected_options": [{"value": "agreed"}]},
                            },
                        }
                    }
                },
                "user": {"id": "U_REP"},
            },
            Mock(),
        )

        _, kwargs = ack.call_args
        assert kwargs["response_action"] == "errors"
        assert "report_type" in kwargs["errors"]
        assert "consent" not in kwargs["errors"]

    def test_successful_submit(self, mocker):
        """Test consenting submit posts an embed alert and records the report as spam."""
        ack = Mock()
        client = Mock()
        client.chat_postMessage.return_value = {"ts": "alert.ts"}
        workspace = enabled_workspace(
            content_report_alert_channel_id="C_ALERT",
            content_report_alert_user_ids=["U_MOD"],
            slack_workspace_id="T1",
        )
        conversation = Mock(
            is_im=True,
            is_mpim=False,
            is_private=False,
            is_public_channel=False,
            slack_channel_id="D1",
        )
        conversation.content_origin = Mock(return_value="direct message by <@U_OTHER>")
        message = Mock(
            pk=5,
            text="spam body",
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER", "text": "spam body"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", ReportSource.SHORTCUT),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=workspace,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=message)))),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.acquire",
            return_value="owner",
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.renew",
            return_value=True,
        )
        release = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.release")
        record = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.record")
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.fetch_permalink",
            return_value="",
        )
        post_ephemeral = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        ReportContent().handle_view(
            ack,
            {
                "user": {"id": "U_REP"},
                "team": {"id": "T1"},
                "view": {
                    "private_metadata": encode_metadata(
                        5,
                        "https://hooks.slack.com/r",
                        ReportSource.SHORTCUT,
                    ),
                    "state": {
                        "values": {
                            "report_type": {
                                "report_type": {
                                    "selected_option": {"value": "spam"},
                                }
                            },
                            "consent": {
                                "consent": {
                                    "selected_options": [{"value": "agreed"}],
                                }
                            },
                        }
                    },
                },
            },
            client,
        )

        client.chat_postMessage.assert_called_once()
        _, kwargs = client.chat_postMessage.call_args
        assert kwargs["channel"] == "C_ALERT"
        assert "spam body" in kwargs["text"]
        assert "<@U_REP>" in kwargs["text"]
        record.assert_called_once_with(
            conversation,
            "1.0",
            "spam",
            "alert.ts",
            source=ReportSource.SHORTCUT,
            reporter_user_ids=["U_REP"],
            reaction_count=None,
            message=message,
        )
        release.assert_called_once_with(conversation, "1.0", "owner")
        post_ephemeral.assert_called_once_with("https://hooks.slack.com/r", SUCCESS_TEXT)

    def test_acquire_failure_posts_already_reported(self, mocker):
        """Test submit posts already-reported when lock acquisition fails."""
        ack = Mock()
        client = Mock()
        conversation = Mock(is_private=False, slack_channel_id="D1")
        message = Mock(
            pk=5,
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", ReportSource.SHORTCUT),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=message)))),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.acquire",
            return_value=None,
        )
        post_ephemeral = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        ReportContent().handle_view(
            ack,
            {
                "user": {"id": "U_REP"},
                "team": {"id": "T1"},
                "view": {
                    "private_metadata": "x",
                    "state": {
                        "values": {
                            "report_type": {
                                "report_type": {"selected_option": {"value": "spam"}},
                            },
                            "consent": {
                                "consent": {"selected_options": [{"value": "agreed"}]},
                            },
                        }
                    },
                },
            },
            client,
        )

        post_ephemeral.assert_called_once_with(
            "https://hooks.slack.com/r",
            ALREADY_REPORTED_TEXT,
        )


class TestReportContentHelpers:
    def test_incomplete_shortcut_payload_ignored(self, mocker):
        """Test incomplete shortcut payloads are ignored."""
        ack = Mock()
        client = Mock()
        get_workspace = mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id"
        )

        ReportContent().handle(ack, {"user": {"id": "U_REP"}}, client, Mock())

        ack.assert_called_once()
        get_workspace.assert_not_called()
        client.views_open.assert_not_called()

    def test_post_alert_renew_failure(self, mocker):
        """Test renew failure posts already-reported and releases the lock."""
        conversation = Mock(slack_channel_id="C1")
        message = Mock(slack_message_id="1.0", conversation=conversation)
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.renew",
            return_value=False,
        )
        release = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.release")
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        post_content_report_alert(
            client=Mock(),
            workspace=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
            message=message,
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            source="shortcut",
            owner="owner",
            report_type="spam",
        )

        post.assert_called_once_with("https://hooks.slack.com/r", ALREADY_REPORTED_TEXT)
        release.assert_called_once()

    def test_post_alert_deliver_failure(self, mocker):
        """Test deliver failure posts submit-failed ephemeral."""
        conversation = Mock(
            is_im=False,
            is_mpim=False,
            is_private=False,
            is_public_channel=True,
            slack_channel_id="C1",
        )
        conversation.content_origin = Mock(return_value="<#C1>")
        message = Mock(
            slack_message_id="1.0",
            text="hi",
            raw_data={},
            conversation=conversation,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.renew",
            return_value=True,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.fetch_permalink",
            return_value="",
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.post_alert",
            return_value=False,
        )
        release = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.release")
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        post_content_report_alert(
            client=Mock(),
            workspace=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
            message=message,
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            source="shortcut",
            owner="owner",
            report_type="spam",
        )

        post.assert_called_once_with("https://hooks.slack.com/r", SUBMIT_FAILED_TEXT)
        release.assert_called_once()

    def test_load_submission_invalid_metadata(self, mocker):
        """Test invalid submission metadata is ignored."""
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "bad"},
            )
            is None
        )
        post.assert_not_called()

    def test_load_submission_feature_off(self, mocker):
        """Test submit path rejects workspaces without content reporting."""
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=disabled_workspace(),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.com/r", FEATURE_OFF_TEXT)

    def test_load_submission_missing_message(self, mocker):
        """Test submit path rejects missing stored messages."""
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.com/r", MISSING_MESSAGE_TEXT)

    def test_load_submission_self_report(self, mocker):
        """Test submit path rejects self-reports."""
        message = Mock(
            slack_message_id="1.0",
            conversation=Mock(is_private=False),
            raw_data={"user": "U_REP"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=message)))),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.com/r", SELF_REPORT_TEXT)

    def test_load_submission_private_channel(self, mocker):
        """Test submit path rejects private channels."""
        message = Mock(
            slack_message_id="1.0",
            conversation=Mock(is_private=True),
            raw_data={"user": "U_OTHER"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=message)))),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.com/r", PRIVATE_CHANNEL_TEXT)

    def test_load_submission_already_reported(self, mocker):
        """Test submit path rejects messages that were already reported."""
        conversation = Mock(is_private=False)
        message = Mock(
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.com/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=message)))),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=True,
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.com/r", ALREADY_REPORTED_TEXT)

    def test_submission_context_none_after_ack(self, mocker):
        """Test submission returns after ack when context cannot be loaded."""
        ack = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.load_submission_context",
            return_value=None,
        )

        ReportContent().handle_view(
            ack,
            {
                "user": {"id": "U_REP"},
                "view": {
                    "state": {
                        "values": {
                            "report_type": {
                                "report_type": {"selected_option": {"value": "spam"}},
                            },
                            "consent": {
                                "consent": {"selected_options": [{"value": "agreed"}]},
                            },
                        }
                    }
                },
            },
            Mock(),
        )

        assert ack.call_count == 1
        assert ack.call_args == ((),)
