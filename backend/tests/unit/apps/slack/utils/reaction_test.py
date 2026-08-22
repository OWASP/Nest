from apps.slack.utils.reaction import (
    format_emojis,
    mention_users,
    parse_message_reaction,
    reaction_from_payload,
)

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
        """Test reactions.get payloads expose unique reporters and permalink."""
        assert reaction_from_payload(PAYLOAD, ["spam"]) == (
            2,
            ["U_REACTOR", "U_OTHER"],
            "https://slack.test/message",
            ["spam"],
        )

    def test_reaction_from_payload_returns_none_when_emoji_missing(self):
        """Test an unmatched emoji set does not produce a snapshot."""
        assert reaction_from_payload(PAYLOAD, ["flag"]) is None

    def test_reaction_from_payload_unions_unique_reporters(self):
        """Test listed emojis share one unique-reporter count."""
        payload = {
            "message": {
                "permalink": "https://slack.test/message",
                "reactions": [
                    {"name": "spam", "count": 2, "users": ["U1", "U2"]},
                    {"name": "flag", "count": 2, "users": ["U2", "U3"]},
                    {"name": "thumbsup", "count": 4, "users": ["U4"]},
                ],
            }
        }

        assert reaction_from_payload(payload, ["spam", "flag"]) == (
            3,
            ["U1", "U2", "U3"],
            "https://slack.test/message",
            ["spam", "flag"],
        )

    def test_reaction_from_payload_returns_matched_emojis_only(self):
        """Test unused configured emojis are omitted from the snapshot."""
        assert reaction_from_payload(PAYLOAD, ["spam", "flag"]) == (
            2,
            ["U_REACTOR", "U_OTHER"],
            "https://slack.test/message",
            ["spam"],
        )

    def test_reaction_from_payload_ignores_non_list_emojis(self):
        """Test a JSON scalar emoji list does not produce a snapshot."""
        assert reaction_from_payload(PAYLOAD, "spam") is None


class TestFormatEmojis:
    def test_format_emojis_joins_names(self):
        """Test emoji names are formatted as Slack emoji markup."""
        assert format_emojis(["spam", "flag"]) == ":spam: :flag:"

    def test_format_emojis_handles_empty(self):
        """Test missing emoji names produce no markup."""
        assert format_emojis([]) == ""
        assert format_emojis(None) == ""

    def test_format_emojis_ignores_non_list_values(self):
        """Test JSON scalars and objects are not treated as emoji lists."""
        assert format_emojis("spam") == ""

    def test_format_emojis_ignores_empty_names(self):
        """Test blank emoji names are omitted from markup."""
        assert format_emojis(["", "spam", None, "flag"]) == ":spam: :flag:"


class TestMentionUsers:
    def test_mention_users_joins_ids(self):
        """Test Slack user IDs are formatted as mentions."""
        assert mention_users(["U1", "U2"]) == "<@U1> <@U2>"

    def test_mention_users_handles_empty(self):
        """Test missing user IDs produce no mention markup."""
        assert mention_users([]) == ""
        assert mention_users(None) == ""

    def test_mention_users_ignores_non_list_values(self):
        """Test JSON scalars and objects are not treated as user ID lists."""
        assert mention_users("U123") == ""
        assert mention_users({"U123": True}) == ""
        assert mention_users(123) == ""

    def test_mention_users_ignores_empty_ids(self):
        """Test blank user IDs are omitted from mention markup."""
        assert mention_users(["", "U1", None, "U2"]) == "<@U1> <@U2>"
