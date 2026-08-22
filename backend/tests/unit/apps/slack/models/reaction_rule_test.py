from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from apps.slack.enums import ReportType
from apps.slack.models.conversation import Conversation
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.models.workspace import Workspace


class TestReactionRule:
    def test_str(self):
        """Test reaction rule string includes conversation and emojis."""
        workspace = Workspace(name="OWASP")
        conversation = Conversation(name="general", workspace=workspace)
        rule = ReactionRule(conversation=conversation, emojis=["spam", "flag"])

        assert str(rule) == "OWASP #general :spam: :flag:"

    def test_report_type_defaults_to_spam(self):
        """Test report type choices are shared and limited to spam."""
        assert ReportType.SPAM == "spam"
        assert ReportType.choices == [
            ("harassment", "Harassment"),
            ("off_topic", "Off-topic"),
            ("other", "Other"),
            ("spam", "Spam"),
        ]
        assert ReactionRule._meta.get_field("report_type").choices == list(ReportType.choices)

    def test_unique_conversation_report_type_constraint(self):
        """Test one reaction rule is allowed per conversation and report type."""
        constraint = next(
            item
            for item in ReactionRule._meta.constraints
            if item.name == "unique_reactionrule_conversation_report_type"
        )

        assert tuple(constraint.fields) == ("conversation", "report_type")

    def test_for_emoji_returns_matching_rule(self, mocker):
        """Test reaction rule lookup returns the active rule that lists the emoji."""
        rule = Mock(emojis=["spam", "flag"])
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.select_related.return_value.filter.return_value = [rule]

        result = ReactionRule.for_emoji("C123", "flag")

        assert result is rule
        manager.select_related.assert_called_once_with("conversation")
        manager.select_related.return_value.filter.assert_called_once_with(
            conversation__slack_channel_id="C123",
            is_active=True,
        )

    def test_for_emoji_returns_none_when_missing(self, mocker):
        """Test reaction rule lookup returns None when no rule lists the emoji."""
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.select_related.return_value.filter.return_value = [Mock(emojis=["spam"])]

        assert ReactionRule.for_emoji("C123", "flag") is None

    def test_clean_accepts_plain_emojis(self, mocker):
        """Test valid emojis are stripped and stored."""
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.filter.return_value = []
        rule = ReactionRule(emojis=[" spam ", "flag"])
        rule.conversation_id = 7

        rule.clean()

        assert rule.emojis == ["spam", "flag"]

    def test_clean_rejects_empty_emojis(self):
        """Test a rule requires at least one emoji."""
        rule = ReactionRule(emojis=[])

        with pytest.raises(ValidationError, match="at least one"):
            rule.clean()

    def test_clean_rejects_colon_wrapped_names(self):
        """Test emojis must be stored without Slack colons."""
        rule = ReactionRule(emojis=[":spam:"])

        with pytest.raises(ValidationError, match="without colons"):
            rule.clean()

    def test_clean_rejects_duplicate_names(self):
        """Test a rule cannot list the same emoji twice."""
        rule = ReactionRule(emojis=["spam", "spam"])

        with pytest.raises(ValidationError, match="Duplicate"):
            rule.clean()

    def test_clean_rejects_overlapping_emoji_on_same_conversation(self, mocker):
        """Test two active rules on one channel cannot share an emoji."""
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        manager.filter.return_value = [Mock(emojis=["flag", "x"])]
        rule = ReactionRule(emojis=["spam", "flag"])
        rule.conversation_id = 7

        with pytest.raises(ValidationError, match="already used"):
            rule.clean()

        manager.filter.assert_called_once_with(conversation_id=7, is_active=True)

    def test_clean_rejects_empty_string_emoji(self):
        """Test blank emoji entries are rejected."""
        rule = ReactionRule(emojis=["spam", "  "])

        with pytest.raises(ValidationError, match="non-empty"):
            rule.clean()

    def test_clean_skips_overlap_check_without_conversation(self):
        """Test clean returns after normalizing when conversation is unset."""
        rule = ReactionRule(emojis=["spam"])
        rule.conversation_id = None

        rule.clean()

        assert rule.emojis == ["spam"]

    def test_clean_excludes_self_when_checking_overlap(self, mocker):
        """Test updating a rule excludes its own emojis from overlap checks."""
        manager = mocker.patch("apps.slack.models.reaction_rule.ReactionRule.objects")
        filtered = Mock()
        manager.filter.return_value = filtered
        filtered.exclude.return_value = []
        rule = ReactionRule(emojis=["spam"], pk=3)
        rule.conversation_id = 7

        rule.clean()

        filtered.exclude.assert_called_once_with(pk=3)
