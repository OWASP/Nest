from unittest.mock import Mock

from apps.slack.models.conversation import Conversation
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.models.workspace import Workspace


class TestReactionRule:
    def test_str(self):
        """Test reaction rule string includes conversation and emoji."""
        workspace = Workspace(name="OWASP")
        conversation = Conversation(name="general", workspace=workspace)
        rule = ReactionRule(conversation=conversation, emoji_name="spam")

        assert str(rule) == "OWASP #general :spam"

    def test_report_type_defaults_to_spam(self):
        """Test report type is limited to spam."""
        assert ReactionRule.ReportType.SPAM == "spam"
        assert ReactionRule.ReportType.choices == [("spam", "Spam")]

    def test_for_reaction_returns_matching_rule(self, mocker):
        """Test reaction rule lookup returns the matching active rule."""
        rule = Mock()
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.select_related.return_value.filter.return_value.first.return_value = rule

        result = ReactionRule.for_reaction("C123", "spam")

        assert result is rule
        manager.select_related.assert_called_once_with("conversation")
        manager.select_related.return_value.filter.assert_called_once_with(
            conversation__slack_channel_id="C123",
            emoji_name="spam",
            is_active=True,
        )

    def test_for_reaction_returns_none_when_missing(self, mocker):
        """Test reaction rule lookup returns None when no rule exists."""
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.select_related.return_value.filter.return_value.first.return_value = None

        assert ReactionRule.for_reaction("C123", "spam") is None
