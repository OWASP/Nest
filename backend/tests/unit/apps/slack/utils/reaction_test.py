from apps.slack.utils.reaction import mention_users, parse_message_reaction, reaction_from_payload

EVENT = {
    "item": {"type": "message", "channel": "C_SOURCE", "ts": "123.000"},
    "reaction": "spam",
    "user": "U_REACTOR",
}

PAYLOAD = {
    "message": {
        "permalink": "https://slack.test/message",
        "reactions": [
            {"name": "thumbsup", "count": 1, "users": ["U_OTHER"]},
            {"name": "spam", "count": 2, "users": ["U_REACTOR", "U_OTHER"]},
        ],
    }
}


class TestParseMessageReaction:
    def test_parse_message_reaction_returns_details(self):
        """Test message reaction events expose channel, timestamp, and emoji."""
        assert parse_message_reaction(EVENT) == ("C_SOURCE", "123.000", "spam")

    def test_parse_message_reaction_skips_non_message_items(self):
        """Test file reactions are ignored."""
        event = {**EVENT, "item": {"type": "file", "channel": "C_SOURCE"}}

        assert parse_message_reaction(event) is None

    def test_parse_message_reaction_skips_missing_user(self):
        """Test reaction events without a user are ignored."""
        event = {**EVENT, "user": ""}

        assert parse_message_reaction(event) is None


class TestReactionFromPayload:
    def test_reaction_from_payload_returns_matching_emoji(self):
        """Test reactions.get payloads expose count, reporters, and permalink."""
        assert reaction_from_payload(PAYLOAD, "spam") == (
            2,
            ["U_REACTOR", "U_OTHER"],
            "https://slack.test/message",
        )

    def test_reaction_from_payload_returns_none_when_emoji_missing(self):
        """Test an unmatched emoji does not produce a snapshot."""
        assert reaction_from_payload(PAYLOAD, "flag") is None


class TestMentionUsers:
    def test_mention_users_joins_ids(self):
        """Test Slack user IDs are formatted as mentions."""
        assert mention_users(["U1", "U2"]) == "<@U1> <@U2>"

    def test_mention_users_handles_empty(self):
        """Test missing user IDs produce no mention markup."""
        assert mention_users([]) == ""
        assert mention_users(None) == ""
