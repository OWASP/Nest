from unittest.mock import Mock

from slack_sdk.errors import SlackApiError

from apps.slack.events.reaction_added import ReactionAdded

EVENT = {
    "item": {"type": "message", "channel": "C_SOURCE", "ts": "123.000"},
    "reaction": "spam",
    "user": "U_REACTOR",
}

REACTIONS_GET = {
    "message": {
        "permalink": "https://slack.test/message",
        "reactions": [
            {"name": "spam", "count": 2, "users": ["U_REACTOR", "U_OTHER"]},
        ],
    }
}


def slack_error(error="invalid_auth"):
    """Build a Slack API error for reaction tests."""
    return SlackApiError(message="API error", response={"error": error})


def mock_rule(threshold=1):
    """Build a reaction rule mock."""
    return Mock(
        alert_channel_id="C_ALERT",
        alert_user_ids=["U_MOD"],
        conversation=Mock(),
        report_type="spam",
        threshold=threshold,
    )


def mock_client(payload=None):
    """Build a Slack client mock with reactions and post responses."""
    client = Mock()
    client.reactions_get.return_value = payload if payload is not None else REACTIONS_GET
    client.chat_postMessage.return_value = {"ts": "999.000"}
    return client


def patch_rule_lookup(mocker, rule=None, *, missing=False):
    """Patch reaction rule lookup."""
    mocker.patch(
        "apps.slack.events.reaction_added.ReactionRule.for_reaction",
        return_value=None if missing else (rule or mock_rule()),
    )


def patch_alert_lock(mocker, *, acquired=True, recorded=False):
    """Patch reaction alert lookup, lock, and record helpers."""
    mocker.patch(
        "apps.slack.events.reaction_added.ReactionAlert.exists_for",
        return_value=recorded,
    )
    acquire = mocker.patch(
        "apps.slack.events.reaction_added.ReactionAlert.acquire",
        return_value=acquired,
    )
    release = mocker.patch("apps.slack.events.reaction_added.ReactionAlert.release")
    record = mocker.patch("apps.slack.events.reaction_added.ReactionAlert.record")
    return acquire, release, record


class TestReactionAdded:
    def test_handle_event_stops_when_no_rule(self, mocker):
        """Test missing reaction rules skip Slack lookups and alerts."""
        client = mock_client()
        patch_rule_lookup(mocker, missing=True)
        acquire, _, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        client.reactions_get.assert_not_called()
        acquire.assert_not_called()
        record.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_handle_event_posts_alert_and_records_it(self, mocker):
        """Test threshold hit posts a Slack alert with reporters and records it."""
        client = mock_client()
        rule = mock_rule(threshold=2)
        patch_rule_lookup(mocker, rule)
        _, release, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        client.reactions_get.assert_called_once_with(
            channel="C_SOURCE",
            full=True,
            timestamp="123.000",
        )
        client.chat_postMessage.assert_called_once()
        _, kwargs = client.chat_postMessage.call_args
        assert kwargs["channel"] == "C_ALERT"
        assert "<@U_MOD>" in kwargs["text"]
        assert "A message in <#C_SOURCE> reached the spam report threshold." in kwargs["text"]
        assert "Reported by: <@U_REACTOR> <@U_OTHER>" in kwargs["text"]
        assert "https://slack.test/message" in kwargs["text"]
        record.assert_called_once_with(
            rule.conversation,
            "123.000",
            "spam",
            2,
            "999.000",
            reporter_user_ids=["U_REACTOR", "U_OTHER"],
        )
        release.assert_called_once_with(rule.conversation, "123.000", "spam")

    def test_handle_event_skips_recorded_alert(self, mocker):
        """Test an existing reaction alert skips Slack lookups and posts."""
        client = mock_client()
        patch_rule_lookup(mocker)
        acquire, release, record = patch_alert_lock(mocker, recorded=True)

        ReactionAdded().handle_event(EVENT, client)

        client.reactions_get.assert_not_called()
        client.chat_postMessage.assert_not_called()
        acquire.assert_not_called()
        record.assert_not_called()
        release.assert_not_called()

    def test_handle_event_skips_existing_alert(self, mocker):
        """Test an in-flight reaction alert suppresses duplicate Slack posts."""
        client = mock_client()
        patch_rule_lookup(mocker)
        _, release, record = patch_alert_lock(mocker, acquired=False)

        ReactionAdded().handle_event(EVENT, client)

        client.reactions_get.assert_called_once()
        client.chat_postMessage.assert_not_called()
        record.assert_not_called()
        release.assert_not_called()

    def test_handle_event_stops_below_threshold(self, mocker):
        """Test reactions below the configured threshold do not create alerts."""
        client = mock_client(
            {
                "message": {
                    "permalink": "https://slack.test/message",
                    "reactions": [{"name": "spam", "count": 1, "users": ["U_REACTOR"]}],
                }
            }
        )
        patch_rule_lookup(mocker, mock_rule(threshold=2))
        acquire, _, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        acquire.assert_not_called()
        record.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_handle_event_releases_lock_when_post_fails(self, mocker):
        """Test a Slack post failure releases the lock and does not record an alert."""
        client = mock_client()
        client.chat_postMessage.side_effect = slack_error("channel_not_found")
        rule = mock_rule()
        patch_rule_lookup(mocker, rule)
        _, release, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        record.assert_not_called()
        release.assert_called_once_with(rule.conversation, "123.000", "spam")

    def test_handle_event_skips_when_reactions_get_fails(self, mocker):
        """Test a reactions.get failure does not post or lock."""
        client = mock_client()
        client.reactions_get.side_effect = slack_error("message_not_found")
        patch_rule_lookup(mocker)
        acquire, release, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        acquire.assert_not_called()
        record.assert_not_called()
        release.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_handle_event_skips_when_emoji_missing_from_message(self, mocker):
        """Test a reactions.get payload without the emoji does not post."""
        client = mock_client(
            {
                "message": {
                    "permalink": "https://slack.test/message",
                    "reactions": [{"name": "thumbsup", "count": 4, "users": ["U_OTHER"]}],
                }
            }
        )
        patch_rule_lookup(mocker)
        acquire, _, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        acquire.assert_not_called()
        record.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_handle_event_skips_non_message_items(self, mocker):
        """Test file reactions do not look up Slack reactions."""
        client = mock_client()
        patch_rule_lookup(mocker)
        event = {**EVENT, "item": {"type": "file", "channel": "C_SOURCE"}}

        ReactionAdded().handle_event(event, client)

        client.reactions_get.assert_not_called()
        client.chat_postMessage.assert_not_called()

    def test_handle_event_skips_when_permalink_missing(self, mocker):
        """Test a reactions.get payload without a permalink does not post."""
        client = mock_client(
            {
                "message": {
                    "reactions": [{"name": "spam", "count": 1, "users": ["U_REACTOR"]}],
                }
            }
        )
        patch_rule_lookup(mocker)
        acquire, _, record = patch_alert_lock(mocker)

        ReactionAdded().handle_event(EVENT, client)

        acquire.assert_not_called()
        record.assert_not_called()
        client.chat_postMessage.assert_not_called()
