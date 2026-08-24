"""Tests for Slack content-report modal builders and parsers."""

from unittest.mock import Mock

from apps.slack.enums import ReportSource
from apps.slack.modals.report import (
    MODAL_REPORT_TYPES,
    build_report_modal,
    consent_given,
    decode_metadata,
    encode_metadata,
    moderator_inaccessibility_note,
    report_type_option,
    selected_report_type,
)
from apps.slack.models.conversation import Conversation


class TestReportModal:
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
        assert summary.startswith("*Reported From:* direct message by <@U_AUTHOR>")
        assert "*Content Preview:*" in summary
        assert ">hello spam" in summary
        assert view["blocks"][1]["block_id"] == "report_type"
        assert view["blocks"][1]["label"]["text"] == "Report Category"
        assert view["blocks"][1]["element"]["options"] == [
            report_type_option(report_type) for report_type in MODAL_REPORT_TYPES
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
        assert "*Reported From:* direct message by <@U_AUTHOR>" in summary
        assert view["blocks"][1]["block_id"] == "report_type"

    def test_build_report_modal_source_for_channel(self):
        """Test Reported From uses the channel name when there is no author."""
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
        assert "*Reported From:* #general" in summary
        assert " by <@" not in summary

    def test_build_report_modal_source_for_group_chat(self):
        """Test Reported From labels multi-party DMs as group chat with author."""
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

        assert "*Reported From:* group chat by <@U1>" in (view["blocks"][0]["text"]["text"])


class TestModeratorInaccessibilityNote:
    def test_direct_message_note(self):
        """Test DM conversations get the direct-message moderator note."""
        conversation = Conversation(
            is_im=True,
            is_mpim=False,
            is_private=False,
            name="",
            slack_channel_id="D123",
        )

        note = moderator_inaccessibility_note(conversation)

        assert note is not None
        assert "direct message" in note
        assert "group chat" not in note

    def test_group_chat_note(self):
        """Test MPIM conversations get the group-chat moderator note."""
        conversation = Conversation(
            is_im=False,
            is_mpim=True,
            is_private=False,
            name="",
            slack_channel_id="G123",
        )

        note = moderator_inaccessibility_note(conversation)

        assert note is not None
        assert "group chat" in note
        assert "direct message" not in note

    def test_public_channel_has_no_note(self):
        """Test public channels omit the inaccessibility note."""
        conversation = Conversation(
            is_channel=True,
            is_im=False,
            is_mpim=False,
            is_private=False,
            name="general",
            slack_channel_id="C123",
        )

        assert moderator_inaccessibility_note(conversation) is None
