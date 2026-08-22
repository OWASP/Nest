"""Tests for Report content Slack shortcut helpers and handlers."""

from unittest.mock import Mock

import requests
from slack_sdk.errors import SlackApiError

from apps.slack.common.text import preview_text
from apps.slack.enums import ReportSource, ReportType
from apps.slack.models.content_report import ContentReport
from apps.slack.models.message import Message
from apps.slack.shortcuts.report_content import (
    SubmissionContext,
    handle_report_content_shortcut,
    handle_report_content_submission,
    load_submission_context,
    make_ephemeral,
    open_report_content_modal,
    post_content_report_alert,
    post_ephemeral_url,
)
from apps.slack.utils.report_modal import (
    ALREADY_REPORTED_TEXT,
    FEATURE_OFF_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    SELF_REPORT_TEXT,
    SUBMIT_FAILED_TEXT,
    SUCCESS_TEXT,
    build_report_modal,
    consent_given,
    decode_metadata,
    encode_metadata,
    selected_report_type,
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


class TestContentReportUtils:
    def test_preview_text_escapes_mrkdwn(self):
        """Test preview text is sanitized for mrkdwn."""
        assert "&lt;" in preview_text("<script>")
        assert "\\*" in preview_text("hello *bold*")

    def test_encode_decode_metadata(self):
        """Test thin private_metadata round-trips with source."""
        encoded = encode_metadata(
            42,
            "https://hooks.slack.test/response",
            ReportSource.SHORTCUT,
        )
        assert decode_metadata(encoded) == (
            42,
            "https://hooks.slack.test/response",
            ReportSource.SHORTCUT,
        )
        assert decode_metadata("not-json") is None
        assert (
            decode_metadata(encode_metadata(1, "https://hooks.slack.test/r", "not-a-source"))
            is None
        )
        assert (
            decode_metadata('{"message_db_id": 1, "response_url": "", "source": "shortcut"}')
            is None
        )

    def test_parse_message_permalink(self):
        """Test Slack archive permalink parsing."""
        assert Message.parse_permalink(
            "https://owasp.slack.com/archives/C123ABC/p1700000000123456"
        ) == ("C123ABC", "1700000000.123456", None)
        assert Message.parse_permalink(
            "<https://owasp.slack.com/archives/C123ABC/p1700000000123456"
            "?thread_ts=1700000000.000100|message>"
        ) == ("C123ABC", "1700000000.123456", "1700000000.000100")
        assert Message.parse_permalink("not-a-link") is None

    def test_is_self_report(self):
        """Test self-report detection ignores missing authors."""
        assert ContentReport.is_self_report("U1", "U1") is True
        assert ContentReport.is_self_report("U1", "U2") is False
        assert ContentReport.is_self_report("U1", None) is False

    def test_consent_given(self):
        """Test consent checkbox parsing."""
        view = {
            "state": {
                "values": {
                    "consent": {
                        "consent": {
                            "selected_options": [{"value": "agreed"}],
                        }
                    }
                }
            }
        }
        assert consent_given(view) is True
        assert consent_given({"state": {"values": {}}}) is False

    def test_selected_report_type(self):
        """Test report category select parsing."""
        view = {
            "state": {
                "values": {
                    "report_type": {
                        "report_type": {
                            "selected_option": {"value": "spam"},
                        }
                    }
                }
            }
        }
        assert selected_report_type(view) == "spam"
        assert selected_report_type({"state": {"values": {}}}) is None
        assert (
            selected_report_type(
                {
                    "state": {
                        "values": {
                            "report_type": {
                                "report_type": {
                                    "selected_option": {"value": "unknown"},
                                }
                            }
                        }
                    }
                }
            )
            is None
        )

    def test_build_report_modal_includes_preview_and_consent(self):
        """Test modal includes preview, category select, and consent checkbox."""
        message = Mock(pk=9, text="hello spam", raw_data={"user": "U_AUTHOR"})
        conversation = Mock(
            is_im=True,
            is_mpim=False,
            slack_channel_id="D123",
            content_origin="a direct message",
        )

        view = build_report_modal(
            message=message,
            conversation=conversation,
            response_url="https://hooks.slack.test/response",
            source=ReportSource.SHORTCUT,
        )

        assert view["callback_id"] == "report_content_submit"
        assert "hello spam" in view["blocks"][0]["text"]["text"]
        assert view["blocks"][1]["block_id"] == "report_type"
        assert view["blocks"][1]["element"]["options"] == [
            {"text": {"type": "plain_text", "text": label}, "value": value}
            for value, label in ReportType.choices
        ]
        assert view["blocks"][2]["block_id"] == "consent"
        assert view["blocks"][2]["label"]["text"] == "Confirm sharing with moderators"
        assert decode_metadata(view["private_metadata"]) == (
            9,
            "https://hooks.slack.test/response",
            ReportSource.SHORTCUT,
        )


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

        handle_report_content_shortcut(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.test/r",
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

        handle_report_content_shortcut(
            ack,
            {
                "user": {"id": "U_SAME"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_SAME", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.test/r",
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
        conversation = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Conversation.get_or_create_for_report",
            return_value=conversation,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=True,
        )

        handle_report_content_shortcut(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "hi"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.test/r",
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
        conversation = Mock(is_im=True, is_mpim=False, slack_channel_id="D1")
        message = Mock(pk=5, text="spam text", raw_data={"user": "U_OTHER"})
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=workspace,
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

        handle_report_content_shortcut(
            ack,
            {
                "user": {"id": "U_REP"},
                "channel": {"id": "D1"},
                "message": {"ts": "1.0", "user": "U_OTHER", "text": "spam text"},
                "team": {"id": "T1"},
                "response_url": "https://hooks.slack.test/r",
                "trigger_id": "trig",
            },
            client,
            respond,
        )

        client.views_open.assert_called_once()
        _, kwargs = client.views_open.call_args
        assert kwargs["trigger_id"] == "trig"
        assert kwargs["view"]["title"]["text"] == "Report content"
        assert decode_metadata(kwargs["view"]["private_metadata"])[2] == (ReportSource.SHORTCUT)
        respond.assert_not_called()


class TestReportContentSubmission:
    def test_consent_and_report_type_required(self):
        """Test missing consent and category both return modal errors."""
        ack = Mock()

        handle_report_content_submission(
            ack,
            {"view": {"state": {"values": {}}}, "user": {"id": "U_REP"}},
            Mock(),
        )

        _, kwargs = ack.call_args
        assert kwargs["response_action"] == "errors"
        assert "consent" in kwargs["errors"]
        assert "report_type" in kwargs["errors"]

    def test_successful_submit(self, mocker):
        """Test consenting submit posts an embed alert and records the report."""
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
            slack_channel_id="D1",
            content_origin="a direct message",
        )
        message = Mock(
            pk=5,
            text="spam body",
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER", "text": "spam body"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.test/r", ReportSource.SHORTCUT),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=workspace,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(get=Mock(return_value=message)),
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

        handle_report_content_submission(
            ack,
            {
                "user": {"id": "U_REP"},
                "team": {"id": "T1"},
                "view": {
                    "private_metadata": encode_metadata(
                        5,
                        "https://hooks.slack.test/r",
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
        post_ephemeral.assert_called_once_with("https://hooks.slack.test/r", SUCCESS_TEXT)

    def test_report_type_required(self):
        """Test missing report category returns a modal error."""
        ack = Mock()
        client = Mock()

        handle_report_content_submission(
            ack,
            {
                "view": {
                    "state": {
                        "values": {
                            "consent": {
                                "consent": {
                                    "selected_options": [{"value": "agreed"}],
                                }
                            }
                        }
                    }
                },
                "user": {"id": "U_REP"},
            },
            client,
        )

        _, kwargs = ack.call_args
        assert kwargs["response_action"] == "errors"
        assert "report_type" in kwargs["errors"]

    def test_acquire_failure_posts_already_reported(self, mocker):
        """Test submit posts already-reported when lock acquisition fails."""
        ack = Mock()
        client = Mock()
        conversation = Mock(slack_channel_id="D1")
        message = Mock(
            pk=5,
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.test/r", ReportSource.SHORTCUT),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(get=Mock(return_value=message)),
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

        handle_report_content_submission(
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
            "https://hooks.slack.test/r",
            ALREADY_REPORTED_TEXT,
        )


class TestReportContentHelpers:
    def test_make_ephemeral_prefers_respond(self, mocker):
        """Test make_ephemeral uses Bolt respond when available."""
        respond = Mock()
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        make_ephemeral(respond, "https://hooks.slack.test/r")(text="hi")

        respond.assert_called_once_with(text="hi", response_type="ephemeral")
        post.assert_not_called()

    def test_make_ephemeral_falls_back_to_response_url(self, mocker):
        """Test make_ephemeral posts to response_url without respond."""
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        make_ephemeral(None, "https://hooks.slack.test/r")(text="hi")

        post.assert_called_once_with("https://hooks.slack.test/r", "hi")

    def test_post_ephemeral_url_swallows_request_errors(self, mocker):
        """Test response_url failures are logged and ignored."""
        mocker.patch(
            "apps.slack.shortcuts.report_content.requests.post",
            side_effect=requests.RequestException("boom"),
        )
        post_ephemeral_url("https://hooks.slack.test/r", "hi")

    def test_open_modal_missing_message_ts(self, mocker):
        """Test open path rejects payloads without a message timestamp."""
        respond = Mock()
        open_report_content_modal(
            client=Mock(),
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.test/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )
        respond.assert_called_once_with(text=MISSING_MESSAGE_TEXT, response_type="ephemeral")

    def test_open_modal_views_open_failure(self, mocker):
        """Test views_open failures send an ephemeral error."""
        respond = Mock()
        client = Mock()
        client.views_open.side_effect = SlackApiError(
            message="fail",
            response={"ok": False, "error": "invalid_trigger"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Conversation.get_or_create_for_report",
            return_value=Mock(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=False,
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.update_data",
            return_value=Mock(pk=1, text="x", raw_data={}),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Member.objects.get_or_create",
            return_value=(Mock(), False),
        )

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.test/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        respond.assert_called_once_with(text=MODAL_OPEN_FAILED_TEXT, response_type="ephemeral")

    def test_incomplete_shortcut_payload_ignored(self, mocker):
        """Test incomplete shortcut payloads are ignored."""
        ack = Mock()
        client = Mock()
        get_workspace = mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id"
        )

        handle_report_content_shortcut(ack, {"user": {"id": "U_REP"}}, client, Mock())

        ack.assert_called_once()
        get_workspace.assert_not_called()
        client.views_open.assert_not_called()

    def test_post_alert_renew_failure(self, mocker):
        """Test renew failure posts already-reported and releases the lock."""
        context = SubmissionContext(
            workspace=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
            message=Mock(slack_message_id="1.0"),
            conversation=Mock(slack_channel_id="C1"),
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.test/r",
            source="shortcut",
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.renew",
            return_value=False,
        )
        release = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.release")
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        post_content_report_alert(
            client=Mock(),
            context=context,
            owner="owner",
            report_type="spam",
        )

        post.assert_called_once_with("https://hooks.slack.test/r", ALREADY_REPORTED_TEXT)
        release.assert_called_once()

    def test_post_alert_deliver_failure(self, mocker):
        """Test deliver failure posts submit-failed ephemeral."""
        context = SubmissionContext(
            workspace=enabled_workspace(content_report_alert_channel_id="C_ALERT"),
            message=Mock(slack_message_id="1.0", text="hi", raw_data={}),
            conversation=Mock(slack_channel_id="C1", content_origin="<#C1>"),
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.test/r",
            source="shortcut",
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
            "apps.slack.shortcuts.report_content.ContentReport.deliver_alert",
            return_value=False,
        )
        release = mocker.patch("apps.slack.shortcuts.report_content.ContentReport.release")
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        post_content_report_alert(
            client=Mock(),
            context=context,
            owner="owner",
            report_type="spam",
        )

        post.assert_called_once_with("https://hooks.slack.test/r", SUBMIT_FAILED_TEXT)
        release.assert_called_once()

    def test_make_ephemeral_noop_without_destinations(self, mocker):
        """Test make_ephemeral is a no-op without respond or response_url."""
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        make_ephemeral(None, "")(text="hi")

        post.assert_not_called()

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
            return_value=(5, "https://hooks.slack.test/r", "shortcut"),
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
        post.assert_called_once_with("https://hooks.slack.test/r", FEATURE_OFF_TEXT)

    def test_load_submission_missing_message(self, mocker):
        """Test submit path rejects missing stored messages."""
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.test/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(get=Mock(side_effect=Message.DoesNotExist)),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.test/r", MISSING_MESSAGE_TEXT)

    def test_load_submission_self_report(self, mocker):
        """Test submit path rejects self-reports."""
        message = Mock(
            slack_message_id="1.0",
            conversation=Mock(),
            raw_data={"user": "U_REP"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.test/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(get=Mock(return_value=message)),
        )
        post = mocker.patch("apps.slack.shortcuts.report_content.post_ephemeral_url")

        assert (
            load_submission_context(
                {"user": {"id": "U_REP"}, "team": {"id": "T1"}},
                {"private_metadata": "x"},
            )
            is None
        )
        post.assert_called_once_with("https://hooks.slack.test/r", SELF_REPORT_TEXT)

    def test_load_submission_already_reported(self, mocker):
        """Test submit path rejects messages that were already reported."""
        conversation = Mock()
        message = Mock(
            slack_message_id="1.0",
            conversation=conversation,
            raw_data={"user": "U_OTHER"},
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.decode_metadata",
            return_value=(5, "https://hooks.slack.test/r", "shortcut"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Workspace.get_by_workspace_id",
            return_value=enabled_workspace(),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.Message.objects.select_related",
            return_value=Mock(get=Mock(return_value=message)),
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
        post.assert_called_once_with("https://hooks.slack.test/r", ALREADY_REPORTED_TEXT)

    def test_submission_context_none_after_ack(self, mocker):
        """Test submission returns after ack when context cannot be loaded."""
        ack = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.load_submission_context",
            return_value=None,
        )

        handle_report_content_submission(
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

    def test_open_modal_without_author(self, mocker):
        """Test open path works when the message has no author user id."""
        respond = Mock()
        client = Mock()
        mocker.patch(
            "apps.slack.shortcuts.report_content.Conversation.get_or_create_for_report",
            return_value=Mock(is_im=False, is_mpim=False, slack_channel_id="C1"),
        )
        mocker.patch(
            "apps.slack.shortcuts.report_content.ContentReport.exists_for",
            return_value=False,
        )
        update = mocker.patch(
            "apps.slack.shortcuts.report_content.Message.update_data",
            return_value=Mock(pk=1, text="bot", raw_data={}),
        )
        get_or_create = mocker.patch(
            "apps.slack.shortcuts.report_content.Member.objects.get_or_create"
        )

        open_report_content_modal(
            client=client,
            workspace=enabled_workspace(),
            channel_id="C1",
            message_payload={"ts": "1.0", "text": "bot"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.test/r",
            trigger_id="trig",
            source=ReportSource.COMMAND,
            respond=respond,
        )

        update.assert_called_once()
        assert update.call_args.kwargs["author"] is None
        get_or_create.assert_not_called()
        client.views_open.assert_called_once()
        respond.assert_not_called()
