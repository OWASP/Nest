from unittest.mock import Mock

from django.db import IntegrityError

from apps.slack.models.reaction_alert import LOCK_TTL_SECONDS, ReactionAlert


class TestReactionAlert:
    def test_lock_key(self):
        """Test lock keys include conversation, message, and report type."""
        conversation = Mock(pk=7)

        assert (
            ReactionAlert.lock_key(conversation, "123.000", "spam")
            == "slack:reaction-alert:7:123.000:spam"
        )

    def test_acquire_returns_false_when_alert_exists(self, mocker):
        """Test an existing alert row skips the in-flight lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = True
        add = mocker.patch("apps.slack.models.reaction_alert.cache.add")

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is False
        add.assert_not_called()

    def test_acquire_returns_false_when_lock_held(self, mocker):
        """Test a held cache lock skips posting."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = False
        mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=False)

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is False

    def test_acquire_returns_true_when_lock_taken(self, mocker):
        """Test a free lock is acquired when no alert row exists."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = False
        add = mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=True)

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is True
        add.assert_called_once_with(
            "slack:reaction-alert:7:123.000:spam",
            1,
            timeout=LOCK_TTL_SECONDS,
        )

    def test_acquire_releases_lock_if_alert_appears_after_add(self, mocker):
        """Test a row created during lock acquisition releases the lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.side_effect = [False, True]
        mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=True)
        delete = mocker.patch("apps.slack.models.reaction_alert.cache.delete")

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is False
        delete.assert_called_once_with("slack:reaction-alert:7:123.000:spam")

    def test_exists_for_uses_conversation_message_and_report_type(self, mocker):
        """Test exists_for looks up the unique alert row."""
        conversation = Mock()
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = True

        assert ReactionAlert.exists_for(conversation, "123.000", "spam") is True
        manager.filter.assert_called_once_with(
            conversation=conversation,
            message_ts="123.000",
            report_type="spam",
        )

    def test_record_creates_alert(self, mocker):
        """Test a successful Slack post is stored as a reaction alert."""
        conversation = Mock()
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")

        ReactionAlert.record(
            conversation,
            "123.000",
            "spam",
            2,
            "999.000",
            reporter_user_ids=["U1", "U2"],
        )

        manager.create.assert_called_once_with(
            alert_message_ts="999.000",
            conversation=conversation,
            message_ts="123.000",
            reaction_count=2,
            report_type="spam",
            reporter_user_ids=["U1", "U2"],
        )

    def test_record_ignores_existing_row(self, mocker):
        """Test a concurrent insert does not raise."""
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.create.side_effect = IntegrityError

        ReactionAlert.record(
            Mock(),
            "123.000",
            "spam",
            1,
            "999.000",
            reporter_user_ids=["U1"],
        )

    def test_release_deletes_lock(self, mocker):
        """Test release deletes the in-flight cache lock."""
        delete = mocker.patch("apps.slack.models.reaction_alert.cache.delete")

        ReactionAlert.release(Mock(pk=7), "123.000", "spam")

        delete.assert_called_once_with("slack:reaction-alert:7:123.000:spam")
