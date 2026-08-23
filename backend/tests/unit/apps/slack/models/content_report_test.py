from unittest.mock import Mock

import pytest
from django.db import IntegrityError
from slack_sdk.errors import SlackApiError, SlackClientError

from apps.slack.models.content_report import LOCK_TTL_SECONDS, ContentReport

LOCK_OWNER = "lock-owner"
LOCK_KEY = "slack:content-report:7:123.000"


class TestContentReport:
    def test_lock_key(self):
        """Test lock keys include conversation and message."""
        conversation = Mock(pk=7)

        assert ContentReport.lock_key(conversation, "123.000") == LOCK_KEY

    def test_acquire_returns_none_when_report_exists(self, mocker):
        """Test an existing report row skips the in-flight lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.filter.return_value.exists.return_value = True
        add = mocker.patch("apps.slack.models.content_report.cache.add")

        assert ContentReport.acquire(conversation, "123.000") is None
        add.assert_not_called()

    def test_acquire_returns_none_when_lock_held(self, mocker):
        """Test a held cache lock skips posting."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.filter.return_value.exists.return_value = False
        mocker.patch("apps.slack.models.content_report.cache.add", return_value=False)

        assert ContentReport.acquire(conversation, "123.000") is None

    def test_acquire_returns_owner_when_lock_taken(self, mocker):
        """Test a free lock is acquired when no report row exists."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.filter.return_value.exists.return_value = False
        mocker.patch(
            "apps.slack.models.content_report.uuid4",
            return_value=Mock(hex=LOCK_OWNER),
        )
        add = mocker.patch("apps.slack.models.content_report.cache.add", return_value=True)

        assert ContentReport.acquire(conversation, "123.000") == LOCK_OWNER
        add.assert_called_once_with(LOCK_KEY, LOCK_OWNER, timeout=LOCK_TTL_SECONDS)

    def test_acquire_releases_lock_if_report_appears_after_add(self, mocker):
        """Test a row created during lock acquisition releases the owned lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.filter.return_value.exists.side_effect = [False, True]
        mocker.patch(
            "apps.slack.models.content_report.uuid4",
            return_value=Mock(hex=LOCK_OWNER),
        )
        mocker.patch("apps.slack.models.content_report.cache.add", return_value=True)
        mocker.patch("apps.slack.models.content_report.cache.get", return_value=LOCK_OWNER)
        delete = mocker.patch("apps.slack.models.content_report.cache.delete")

        assert ContentReport.acquire(conversation, "123.000") is None
        delete.assert_called_once_with(LOCK_KEY)

    def test_exists_for_uses_conversation_and_message(self, mocker):
        """Test exists_for looks up the unique report row."""
        conversation = Mock()
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.filter.return_value.exists.return_value = True

        assert ContentReport.exists_for(conversation, "123.000") is True
        manager.filter.assert_called_once_with(
            conversation=conversation,
            message_ts="123.000",
        )

    def test_record_creates_report(self, mocker):
        """Test a successful Slack post is stored as a content report."""
        conversation = Mock()
        message = Mock()
        mocker.patch(
            "apps.slack.models.content_report.transaction.atomic",
            return_value=mocker.MagicMock(),
        )
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")

        ContentReport.record(
            conversation,
            "123.000",
            "spam",
            "999.000",
            source="emoji",
            reporter_user_ids=["U1", "U2"],
            reaction_count=2,
            message=message,
        )

        manager.create.assert_called_once_with(
            alert_message_ts="999.000",
            conversation=conversation,
            message=message,
            message_ts="123.000",
            reaction_count=2,
            report_type="spam",
            reporter_user_ids=["U1", "U2"],
            source="emoji",
        )

    def test_record_ignores_existing_row(self, mocker):
        """Test a concurrent unique insert does not raise."""
        mocker.patch(
            "apps.slack.models.content_report.transaction.atomic",
            return_value=mocker.MagicMock(),
        )
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.create.side_effect = IntegrityError
        manager.filter.return_value.exists.return_value = True

        ContentReport.record(
            Mock(),
            "123.000",
            "spam",
            "999.000",
            source="shortcut",
            reporter_user_ids=["U1"],
        )

    def test_record_raises_unexpected_integrity_error(self, mocker):
        """Test a non-unique IntegrityError is not swallowed."""
        mocker.patch(
            "apps.slack.models.content_report.transaction.atomic",
            return_value=mocker.MagicMock(),
        )
        manager = mocker.patch("apps.slack.models.content_report.ContentReport.objects")
        manager.create.side_effect = IntegrityError
        manager.filter.return_value.exists.return_value = False

        with pytest.raises(IntegrityError):
            ContentReport.record(
                Mock(),
                "123.000",
                "spam",
                "999.000",
                source="shortcut",
                reporter_user_ids=["U1"],
            )

    def test_release_deletes_owned_lock(self, mocker):
        """Test release deletes the lock only when this process still owns it."""
        mocker.patch("apps.slack.models.content_report.cache.get", return_value=LOCK_OWNER)
        delete = mocker.patch("apps.slack.models.content_report.cache.delete")

        ContentReport.release(Mock(pk=7), "123.000", LOCK_OWNER)

        delete.assert_called_once_with(LOCK_KEY)

    def test_release_skips_delete_when_owner_mismatch(self, mocker):
        """Test release does not delete a lock taken by another process."""
        mocker.patch("apps.slack.models.content_report.cache.get", return_value="other-owner")
        delete = mocker.patch("apps.slack.models.content_report.cache.delete")

        ContentReport.release(Mock(pk=7), "123.000", LOCK_OWNER)

        delete.assert_not_called()

    def test_renew_extends_owned_lock(self, mocker):
        """Test renew touches the lock when this process still owns it."""
        mocker.patch("apps.slack.models.content_report.cache.get", return_value=LOCK_OWNER)
        touch = mocker.patch("apps.slack.models.content_report.cache.touch", return_value=True)

        assert ContentReport.renew(Mock(pk=7), "123.000", LOCK_OWNER) is True
        touch.assert_called_once_with(LOCK_KEY, LOCK_TTL_SECONDS)

    def test_renew_returns_false_when_owner_mismatch(self, mocker):
        """Test renew does not extend a lock taken by another process."""
        mocker.patch("apps.slack.models.content_report.cache.get", return_value="other-owner")
        touch = mocker.patch("apps.slack.models.content_report.cache.touch")

        assert ContentReport.renew(Mock(pk=7), "123.000", LOCK_OWNER) is False
        touch.assert_not_called()

    def test_build_alert_text_includes_author_quote_and_permalink(self, mocker):
        """Test alert text includes author, quote, and permalink when present."""
        mocker.patch(
            "apps.slack.models.content_report.mention_users",
            return_value="<@U_MOD>",
        )
        mocker.patch(
            "apps.slack.models.content_report.preview_text",
            return_value="quoted spam",
        )
        workspace = Mock(content_report_alert_user_ids=["U_MOD"])
        conversation = Mock(content_origin="<#C123>")
        message = Mock(text="spam", raw_data={"user": "U_AUTHOR"})

        text = ContentReport.build_alert_text(
            workspace=workspace,
            conversation=conversation,
            message=message,
            reporter_user_id="U_REP",
            report_type="spam",
            permalink="https://example.slack.com/archives/C123/p1",
        )

        assert "<@U_MOD>" in text
        assert "spam" in text
        assert "<@U_REP>" in text
        assert "Author: <@U_AUTHOR>" in text
        assert ">quoted spam" in text
        assert "https://example.slack.com/archives/C123/p1" in text

    def test_build_alert_text_skips_optional_lines(self, mocker):
        """Test alert text omits author, quote, and permalink when absent."""
        mocker.patch("apps.slack.models.content_report.mention_users", return_value="")
        mocker.patch("apps.slack.models.content_report.preview_text", return_value="")
        workspace = Mock(content_report_alert_user_ids=[])
        conversation = Mock(content_origin="a direct message")
        message = Mock(text="", raw_data={})

        text = ContentReport.build_alert_text(
            workspace=workspace,
            conversation=conversation,
            message=message,
            reporter_user_id="U_REP",
            report_type="custom",
            permalink="",
        )

        assert "Author:" not in text
        assert "custom" in text
        assert "<@U_REP>" in text
        assert "https://" not in text
        assert "\n>" not in text
        assert not text.startswith(">")

    def test_post_alert_posts_and_records(self, mocker):
        """Test post_alert posts to Slack then records the report."""
        client = Mock()
        client.chat_postMessage.return_value = {"ts": "alert.ts"}
        record = mocker.patch("apps.slack.models.content_report.ContentReport.record")
        conversation = Mock()
        message = Mock()

        assert (
            ContentReport.post_alert(
                client,
                channel_id="C_ALERT",
                text="alert",
                conversation=conversation,
                message_ts="1.0",
                report_type="spam",
                source="shortcut",
                reporter_user_ids=["U1"],
                message=message,
            )
            is True
        )
        client.chat_postMessage.assert_called_once()
        record.assert_called_once()

    def test_post_alert_returns_false_on_slack_error(self, mocker):
        """Test post_alert does not record when chat_postMessage fails."""
        client = Mock()
        client.chat_postMessage.side_effect = SlackApiError(
            message="fail",
            response={"ok": False, "error": "channel_not_found"},
        )
        record = mocker.patch("apps.slack.models.content_report.ContentReport.record")

        assert (
            ContentReport.post_alert(
                client,
                channel_id="C_ALERT",
                text="alert",
                conversation=Mock(),
                message_ts="1.0",
                report_type="spam",
                source="emoji",
                reporter_user_ids=["U1"],
            )
            is False
        )
        record.assert_not_called()

    def test_post_alert_returns_false_on_client_error(self, mocker):
        """Test post_alert does not record when Slack transport fails."""
        client = Mock()
        client.chat_postMessage.side_effect = SlackClientError("timeout")
        record = mocker.patch("apps.slack.models.content_report.ContentReport.record")

        assert (
            ContentReport.post_alert(
                client,
                channel_id="C_ALERT",
                text="alert",
                conversation=Mock(),
                message_ts="1.0",
                report_type="spam",
                source="emoji",
                reporter_user_ids=["U1"],
            )
            is False
        )
        record.assert_not_called()
