from unittest.mock import Mock

import pytest
from django.db import IntegrityError

from apps.slack.models.reaction_alert import LOCK_TTL_SECONDS, ReactionAlert

LOCK_OWNER = "lock-owner"
LOCK_KEY = "slack:reaction-alert:7:123.000:spam"


class TestReactionAlert:
    def test_lock_key(self):
        """Test lock keys include conversation, message, and report type."""
        conversation = Mock(pk=7)

        assert ReactionAlert.lock_key(conversation, "123.000", "spam") == LOCK_KEY

    def test_acquire_returns_none_when_alert_exists(self, mocker):
        """Test an existing alert row skips the in-flight lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = True
        add = mocker.patch("apps.slack.models.reaction_alert.cache.add")

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is None
        add.assert_not_called()

    def test_acquire_returns_none_when_lock_held(self, mocker):
        """Test a held cache lock skips posting."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = False
        mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=False)

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is None

    def test_acquire_returns_owner_when_lock_taken(self, mocker):
        """Test a free lock is acquired when no alert row exists."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.return_value = False
        mocker.patch(
            "apps.slack.models.reaction_alert.uuid4",
            return_value=Mock(hex=LOCK_OWNER),
        )
        add = mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=True)

        assert ReactionAlert.acquire(conversation, "123.000", "spam") == LOCK_OWNER
        add.assert_called_once_with(LOCK_KEY, LOCK_OWNER, timeout=LOCK_TTL_SECONDS)

    def test_acquire_releases_lock_if_alert_appears_after_add(self, mocker):
        """Test a row created during lock acquisition releases the owned lock."""
        conversation = Mock(pk=7)
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.filter.return_value.exists.side_effect = [False, True]
        mocker.patch(
            "apps.slack.models.reaction_alert.uuid4",
            return_value=Mock(hex=LOCK_OWNER),
        )
        mocker.patch("apps.slack.models.reaction_alert.cache.add", return_value=True)
        mocker.patch("apps.slack.models.reaction_alert.cache.get", return_value=LOCK_OWNER)
        delete = mocker.patch("apps.slack.models.reaction_alert.cache.delete")

        assert ReactionAlert.acquire(conversation, "123.000", "spam") is None
        delete.assert_called_once_with(LOCK_KEY)

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
        """Test a concurrent unique insert does not raise."""
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.create.side_effect = IntegrityError
        manager.filter.return_value.exists.return_value = True

        ReactionAlert.record(
            Mock(),
            "123.000",
            "spam",
            1,
            "999.000",
            reporter_user_ids=["U1"],
        )

    def test_record_raises_unexpected_integrity_error(self, mocker):
        """Test a non-unique IntegrityError is not swallowed."""
        manager = mocker.patch("apps.slack.models.reaction_alert.ReactionAlert.objects")
        manager.create.side_effect = IntegrityError
        manager.filter.return_value.exists.return_value = False

        with pytest.raises(IntegrityError):
            ReactionAlert.record(
                Mock(),
                "123.000",
                "spam",
                1,
                "999.000",
                reporter_user_ids=["U1"],
            )

    def test_release_deletes_owned_lock(self, mocker):
        """Test release deletes the lock only when this process still owns it."""
        mocker.patch("apps.slack.models.reaction_alert.cache.get", return_value=LOCK_OWNER)
        delete = mocker.patch("apps.slack.models.reaction_alert.cache.delete")

        ReactionAlert.release(Mock(pk=7), "123.000", "spam", LOCK_OWNER)

        delete.assert_called_once_with(LOCK_KEY)

    def test_release_skips_delete_when_owner_mismatch(self, mocker):
        """Test release does not delete a lock taken by another process."""
        mocker.patch("apps.slack.models.reaction_alert.cache.get", return_value="other-owner")
        delete = mocker.patch("apps.slack.models.reaction_alert.cache.delete")

        ReactionAlert.release(Mock(pk=7), "123.000", "spam", LOCK_OWNER)

        delete.assert_not_called()

    def test_renew_extends_owned_lock(self, mocker):
        """Test renew touches the lock when this process still owns it."""
        mocker.patch("apps.slack.models.reaction_alert.cache.get", return_value=LOCK_OWNER)
        touch = mocker.patch("apps.slack.models.reaction_alert.cache.touch", return_value=True)

        assert ReactionAlert.renew(Mock(pk=7), "123.000", "spam", LOCK_OWNER) is True
        touch.assert_called_once_with(LOCK_KEY, LOCK_TTL_SECONDS)

    def test_renew_returns_false_when_owner_mismatch(self, mocker):
        """Test renew does not extend a lock taken by another process."""
        mocker.patch("apps.slack.models.reaction_alert.cache.get", return_value="other-owner")
        touch = mocker.patch("apps.slack.models.reaction_alert.cache.touch")

        assert ReactionAlert.renew(Mock(pk=7), "123.000", "spam", LOCK_OWNER) is False
        touch.assert_not_called()
