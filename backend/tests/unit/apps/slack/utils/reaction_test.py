from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.utils.reaction import mention_users, parse_message_reaction

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


class TestMatchReactions:
    def test_match_reactions_returns_matching_emoji(self):
        """Test matched reactions expose unique reporters and permalink."""
        assert ReactionRule.match_reactions(PAYLOAD, ["spam"]) == (
            2,
            ["U_REACTOR", "U_OTHER"],
            "https://slack.test/message",
            ["spam"],
        )

    def test_match_reactions_returns_none_when_emoji_missing(self):
        """Test unmatched emoji lists return None."""
        assert ReactionRule.match_reactions(PAYLOAD, ["flag"]) is None

    def test_match_reactions_unions_unique_reporters(self):
        """Test matching emojis union unique reporters."""
        payload = {
            "message": {
                "permalink": "https://slack.test/message",
                "reactions": [
                    {"name": "spam", "count": 2, "users": ["U_REACTOR", "U_OTHER"]},
                    {"name": "flag", "count": 2, "users": ["U_OTHER", "U_THIRD"]},
                ],
            }
        }

        assert ReactionRule.match_reactions(payload, ["spam", "flag"]) == (
            3,
            ["U_REACTOR", "U_OTHER", "U_THIRD"],
            "https://slack.test/message",
            ["spam", "flag"],
        )

    def test_match_reactions_returns_matched_emojis_only(self):
        """Test only configured emojis present on the message are returned."""
        assert ReactionRule.match_reactions(PAYLOAD, ["spam", "flag"]) == (
            2,
            ["U_REACTOR", "U_OTHER"],
            "https://slack.test/message",
            ["spam"],
        )

    def test_match_reactions_ignores_non_list_emojis(self):
        """Test non-list emoji config returns None."""
        assert ReactionRule.match_reactions(PAYLOAD, "spam") is None

    def test_match_reactions_ignores_empty_emoji_list(self):
        """Test empty or blank-only emoji lists return None."""
        assert ReactionRule.match_reactions(PAYLOAD, []) is None
        assert ReactionRule.match_reactions(PAYLOAD, ["", None]) is None


class TestFormatEmojis:
    def test_format_emojis_joins_names(self):
        """Test emoji names are rendered as Slack markup."""
        assert ReactionRule.format_emojis(["spam", "flag"]) == ":spam: :flag:"

    def test_format_emojis_handles_empty(self):
        """Test empty emoji lists render as empty strings."""
        assert ReactionRule.format_emojis([]) == ""
        assert ReactionRule.format_emojis(None) == ""

    def test_format_emojis_ignores_non_list_values(self):
        """Test non-list emoji values render as empty strings."""
        assert ReactionRule.format_emojis("spam") == ""

    def test_format_emojis_ignores_empty_names(self):
        """Test blank emoji names are skipped."""
        assert ReactionRule.format_emojis(["", "spam", None, "flag"]) == ":spam: :flag:"


class TestMentionUsers:
    def test_mention_users_joins_ids(self):
        """Test user IDs are rendered as Slack mentions."""
        assert mention_users(["U1", "U2"]) == "<@U1> <@U2>"

    def test_mention_users_handles_empty(self):
        """Test empty user lists render as empty strings."""
        assert mention_users([]) == ""
        assert mention_users(None) == ""
