"""Tests for Report content Slack shortcut helpers and handlers."""

from unittest.mock import Mock

import requests
from slack_sdk.errors import SlackApiError, SlackClientError

from apps.slack.common.text import preview_text
from apps.slack.enums import ReportSource, ReportType
from apps.slack.modals.report import (
    ALREADY_REPORTED_TEXT,
    FEATURE_OFF_TEXT,
    MISSING_MESSAGE_TEXT,
    MODAL_OPEN_FAILED_TEXT,
    MODAL_REPORT_TYPES,
    PRIVATE_CHANNEL_TEXT,
    SELF_REPORT_TEXT,
    SUBMIT_FAILED_TEXT,
    SUCCESS_TEXT,
    build_report_modal,
    consent_given,
    decode_metadata,
    encode_metadata,
    selected_report_type,
)
from apps.slack.models.content_report import ContentReport
from apps.slack.models.conversation import Conversation
from apps.slack.models.message import Message
from apps.slack.shortcuts.report_content import (
    ReportContent,
    load_submission_context,
    post_content_report_alert,
)
from apps.slack.utils.report import (
    WORKSPACE_MISMATCH_TEXT,
    is_allowed_response_url,
    make_ephemeral,
    open_report_content_modal,
    post_ephemeral_url,
)
from tests.unit.apps.slack.conftest import disabled_workspace, enabled_workspace


class TestContentReportUtils:
    def test_preview_text_escapes_mrkdwn(self):
        """Test preview text is sanitized for mrkdwn."""
        assert "&lt;" in preview_text("<script>")
        assert "\\*" in preview_text("hello *bold*")

    def test_encode_decode_metadata(self):
        """Test thin private_metadata round-trips with source."""
        encoded = encode_metadata(
            42,
            "https://hooks.slack.com/response",
            ReportSource.SHORTCUT,
        )
        assert decode_metadata(encoded) == (
            42,
            "https://hooks.slack.com/response",
            ReportSource.SHORTCUT,
        )
        assert decode_metadata("not-json") is None
        assert (
            decode_metadata(encode_metadata(1, "https://hooks.slack.com/r", "not-a-source"))
            is None
        )
        assert (
            decode_metadata('{"message_db_id": 1, "response_url": "", "source": "shortcut"}')
            is None
        )
        assert (
            decode_metadata(
                '{"message_db_id": true, "response_url": "https://hooks.slack.com/r",'
                ' "source": "shortcut"}'
            )
            is None
        )
        assert (
            decode_metadata(
                '{"message_db_id": 1.5, "response_url": "https://hooks.slack.com/r",'
                ' "source": "shortcut"}'
            )
            is None
        )
        assert (
            decode_metadata(
                '{"message_db_id": 0, "response_url": "https://hooks.slack.com/r",'
                ' "source": "shortcut"}'
            )
            is None
        )
        assert (
            decode_metadata(
                '{"message_db_id": -1, "response_url": "https://hooks.slack.com/r",'
                ' "source": "shortcut"}'
            )
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
        assert Message.parse_permalink(
            "<https://owasp.slack.com/archives/C123ABC/p1700000000123456|link with spaces> "
            "extra trailing text"
        ) == ("C123ABC", "1700000000.123456", None)
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
        """Test report category select parsing accepts spam-only options."""
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
                                    "selected_option": {"value": "not_a_category"},
                                }
                            }
                        }
                    }
                }
            )
            is None
        )

    def test_build_report_modal_includes_preview_and_consent(self):
        """Test modal shows origin first, then preview, category, and consent."""
        message = Mock(pk=9, text="hello spam", raw_data={"user": "U_AUTHOR"})
        conversation = Conversation(
            is_im=True,
            is_mpim=False,
            is_private=False,
            name="",
            slack_channel_id="D123",
        )

        view = build_report_modal(
            message=message,
            conversation=conversation,
            response_url="https://hooks.slack.com/response",
            source=ReportSource.SHORTCUT,
        )

        assert view["callback_id"] == "report_content_submit"
        assert view["title"]["text"] == "Report Content"
        summary = view["blocks"][0]["text"]["text"]
        assert summary.startswith("*Report Content Origin:* direct message by <@U_AUTHOR>")
        assert "*Content Preview:*" in summary
        assert ">hello spam" in summary
        assert view["blocks"][1]["block_id"] == "report_type"
        assert view["blocks"][1]["label"]["text"] == "Report Category"
        assert view["blocks"][1]["element"]["options"] == [
            {
                "text": {"type": "plain_text", "text": ReportType(report_type).label},
                "value": report_type,
            }
            for report_type in MODAL_REPORT_TYPES
        ]
        assert view["blocks"][2]["block_id"] == "consent"
        assert view["blocks"][2]["label"]["text"] == "Sharing Consent"
        assert (
            "my name and the reported message content"
            in (view["blocks"][2]["element"]["options"][0]["text"]["text"])
        )
        assert decode_metadata(view["private_metadata"]) == (
            9,
            "https://hooks.slack.com/response",
            ReportSource.SHORTCUT,
        )

    def test_build_report_modal_omits_preview_when_no_text(self):
        """Test Content Preview section is omitted when the message has no text."""
        message = Mock(pk=1, text="", raw_data={"user": "U_AUTHOR"})
        conversation = Conversation(
            is_im=True,
            is_mpim=False,
            is_private=False,
            name="",
            slack_channel_id="D123",
        )

        view = build_report_modal(
            message=message,
            conversation=conversation,
            response_url="https://hooks.slack.com/r",
            source=ReportSource.SHORTCUT,
        )

        summary = view["blocks"][0]["text"]["text"]
        assert "*Content Preview:*" not in summary
        assert "*Report Content Origin:* direct message by <@U_AUTHOR>" in summary
        assert view["blocks"][1]["block_id"] == "report_type"

    def test_build_report_modal_source_for_channel(self):
        """Test Report Content Origin uses the channel name when there is no author."""
        message = Mock(pk=1, text="hi", raw_data={})
        conversation = Conversation(
            is_im=False,
            is_mpim=False,
            is_private=False,
            name="general",
            slack_channel_id="C123",
        )

        view = build_report_modal(
            message=message,
            conversation=conversation,
            response_url="https://hooks.slack.com/r",
            source=ReportSource.COMMAND,
        )

        summary = view["blocks"][0]["text"]["text"]
        assert "*Report Content Origin:* #general" in summary
        assert " by <@" not in summary

    def test_build_report_modal_source_for_group_chat(self):
        """Test Report Content Origin labels multi-party DMs as group chat with author."""
        message = Mock(pk=1, text="hi", raw_data={"user": "U1"})
        conversation = Conversation(
            is_im=False,
            is_mpim=True,
            is_private=False,
            name="",
            slack_channel_id="G123",
        )

        view = build_report_modal(
            message=message,
            conversation=conversation,
            response_url="https://hooks.slack.com/r",
            source=ReportSource.SHORTCUT,
        )

        assert (
            "*Report Content Origin:* group chat by <@U1>" in (view["blocks"][0]["text"]["text"])
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
        conversation = Mock(is_im=True, is_mpim=False, is_private=False, slack_channel_id="D1")
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
        mocker.patch(
            "apps.slack.utils.report.Conversation.get_or_create",
            return_value=Mock(is_private=True),
        )

        open_report_content_modal(
            client=Mock(),
            workspace=enabled_workspace(),
            channel_id="G1",
            message_payload={"ts": "1.0", "user": "U_OTHER"},
            reporter_user_id="U_REP",
            response_url="https://hooks.slack.com/r",
            trigger_id="trig",
            source=ReportSource.SHORTCUT,
            respond=respond,
        )

        respond.assert_called_once_with(text=PRIVATE_CHANNEL_TEXT, response_type="ephemeral")

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

    def test_make_ephemeral_noop_without_destinations(self, mocker):
        """Test make_ephemeral is a no-op without respond or response_url."""
        post = mocker.patch("apps.slack.utils.report.post_ephemeral_url")

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
