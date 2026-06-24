from unittest.mock import Mock

from django.db import IntegrityError
from slack_sdk.errors import SlackApiError

from apps.slack.models.moderation import ModerationAlert
from apps.slack.services.moderation import _get_or_create_alert, process_reaction_added

EVENT = {
    "item": {"type": "message", "channel": "C_SOURCE", "ts": "123.000"},
    "reaction": "spam",
}


def slack_error(error="invalid_auth"):
    """Build a Slack API error for service tests."""
    return SlackApiError(message="API error", response={"error": error})


def mock_rule(threshold=1):
    """Build a moderation rule mock."""
    return Mock(
        alert_channel_id="C_ALERT",
        alert_user_ids=["U_MOD"],
        report_type="spam",
        threshold=threshold,
    )


def mock_client(users=None):
    """Build a Slack client mock with reaction and post responses."""
    client = Mock()
    client.reactions_get.return_value = {
        "message": {
            "reactions": [
                {
                    "count": len(set(users or ["U1"])),
                    "name": "spam",
                    "users": users or ["U1"],
                }
            ]
        }
    }
    client.chat_getPermalink.return_value = {"permalink": "https://slack.test/message"}
    client.chat_postMessage.return_value = {"ts": "999.000"}
    return client


def patch_rule_lookup(mocker, rule=None):
    """Patch conversation and moderation rule lookups."""
    mocker.patch(
        "apps.slack.services.moderation.Conversation.objects.get",
        return_value=Mock(),
    )
    mocker.patch(
        "apps.slack.services.moderation.ModerationRule.objects.get",
        return_value=rule or mock_rule(),
    )


class TestModerationService:
    def test_process_reaction_added_posts_alert_and_records_it(self, mocker):
        """Test threshold hit posts a Slack alert and records its message timestamp."""
        client = mock_client(users=["U1", "U2", "U1"])
        moderation_alert = Mock()
        patch_rule_lookup(mocker, mock_rule(threshold=2))
        mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create",
            return_value=(moderation_alert, True),
        )

        process_reaction_added(EVENT, client)

        client.reactions_get.assert_called_once_with(channel="C_SOURCE", timestamp="123.000")
        client.chat_getPermalink.assert_called_once_with(channel="C_SOURCE", message_ts="123.000")
        client.chat_postMessage.assert_called_once()
        _, kwargs = client.chat_postMessage.call_args
        assert kwargs["channel"] == "C_ALERT"
        assert "<@U_MOD>" in kwargs["text"]
        assert "spam report threshold reached" in kwargs["text"]
        assert "Count: 2" in kwargs["text"]
        assert "https://slack.test/message" in kwargs["text"]
        assert moderation_alert.alert_message_ts == "999.000"
        moderation_alert.save.assert_called_once_with(update_fields=["alert_message_ts"])

    def test_process_reaction_added_skips_existing_alert(self, mocker):
        """Test an existing moderation alert suppresses duplicate Slack posts."""
        client = mock_client()
        moderation_alert = Mock()
        patch_rule_lookup(mocker)
        mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create",
            return_value=(moderation_alert, False),
        )

        process_reaction_added(EVENT, client)

        client.chat_getPermalink.assert_not_called()
        client.chat_postMessage.assert_not_called()
        moderation_alert.save.assert_not_called()

    def test_process_reaction_added_stops_below_threshold(self, mocker):
        """Test reactions below the configured threshold do not create alerts."""
        client = mock_client()
        patch_rule_lookup(mocker, mock_rule(threshold=2))
        get_or_create = mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create"
        )

        process_reaction_added(EVENT, client)

        get_or_create.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_process_reaction_added_deletes_claimed_alert_when_post_fails(self, mocker):
        """Test a claimed alert is deleted when Slack posting fails."""
        client = mock_client()
        client.chat_postMessage.side_effect = slack_error("channel_not_found")
        moderation_alert = Mock()
        patch_rule_lookup(mocker)
        mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create",
            return_value=(moderation_alert, True),
        )

        process_reaction_added(EVENT, client)

        moderation_alert.delete.assert_called_once()
        moderation_alert.save.assert_not_called()

    def test_process_reaction_added_deletes_claimed_alert_when_permalink_fails(self, mocker):
        """Test a claimed alert is deleted when permalink lookup fails."""
        client = mock_client()
        client.chat_getPermalink.side_effect = slack_error("message_not_found")
        moderation_alert = Mock()
        patch_rule_lookup(mocker)
        mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create",
            return_value=(moderation_alert, True),
        )

        process_reaction_added(EVENT, client)

        moderation_alert.delete.assert_called_once()
        client.chat_postMessage.assert_not_called()
        moderation_alert.save.assert_not_called()

    def test_process_reaction_added_stops_when_reactions_get_fails(self, mocker):
        """Test Slack reaction API failures stop before claiming an alert."""
        client = Mock()
        client.reactions_get.side_effect = slack_error()
        patch_rule_lookup(mocker)
        get_or_create = mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create"
        )

        process_reaction_added(EVENT, client)

        get_or_create.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_process_reaction_added_uses_slack_reaction_count(self, mocker):
        """Test Slack reaction count is used when the users list is truncated."""
        client = mock_client(users=["U1"])
        client.reactions_get.return_value = {
            "message": {"reactions": [{"count": 3, "name": "spam", "users": ["U1"]}]}
        }
        moderation_alert = Mock()
        patch_rule_lookup(mocker, mock_rule(threshold=3))
        mocker.patch(
            "apps.slack.services.moderation.ModerationAlert.objects.get_or_create",
            return_value=(moderation_alert, True),
        )

        process_reaction_added(EVENT, client)

        _, kwargs = client.chat_postMessage.call_args
        assert "Count: 3" in kwargs["text"]

    def test_get_or_create_alert_handles_deleted_race_fallback(self, mocker):
        """Test IntegrityError fallback tolerates a concurrently deleted alert row."""
        manager = mocker.patch("apps.slack.services.moderation.ModerationAlert.objects")
        manager.get_or_create.side_effect = IntegrityError
        manager.get.side_effect = ModerationAlert.DoesNotExist

        alert, created = _get_or_create_alert(Mock(), "123.000", "spam", 1)

        assert alert is None
        assert not created
        assert manager.get_or_create.call_count == 2
        assert manager.get.call_count == 2
