"""Tests for the slack_sync_moderation_rules management command."""

from io import StringIO
from unittest.mock import Mock

import pytest
from django.core.management.base import CommandError

from apps.slack.management.commands.slack_sync_moderation_rules import Command
from apps.slack.models import Conversation


class TestSlackSyncModerationRulesCommand:
    """Test cases for the slack_sync_moderation_rules management command."""

    def test_missing_config_warns_and_continues(self, tmp_path):
        """Test missing config skips moderation rule sync without failing startup."""
        command = Command()
        command.stdout = StringIO()

        command.handle(config=str(tmp_path / "missing.yaml"))

        assert "Moderation config not found" in command.stdout.getvalue()

    def test_comment_only_config_warns_and_continues(self, tmp_path):
        """Test comment-only config skips moderation rule sync without failing startup."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text("# moderation_rules:\n#   - channel_id: C_SOURCE\n")

        command = Command()
        command.stdout = StringIO()

        command.handle(config=str(config_path))

        assert "Moderation config has no rules" in command.stdout.getvalue()

    def test_missing_conversation_warns_and_skips_rule(self, mocker, tmp_path):
        """Test rules for unknown channels are skipped without failing sync."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text(
            """
moderation_rules:
  - channel_id: C_UNKNOWN
    emoji_name: spam
    report_type: spam
    threshold: 3
    alert_channel_id: C_MODERATION
"""
        )
        mocker.patch(
            "apps.slack.management.commands.slack_sync_moderation_rules.Conversation.objects.get",
            side_effect=Conversation.DoesNotExist,
        )
        update_or_create = mocker.patch(
            "apps.slack.management.commands.slack_sync_moderation_rules."
            "ModerationRule.objects.update_or_create"
        )

        command = Command()
        command.stdout = StringIO()

        command.handle(config=str(config_path))

        output = command.stdout.getvalue()
        assert "Skipping moderation rule for missing channel: C_UNKNOWN" in output
        update_or_create.assert_not_called()

    def test_valid_rule_updates_moderation_rule(self, mocker, tmp_path):
        """Test a valid YAML rule creates or updates a moderation rule."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text(
            """
moderation_rules:
  - channel_id: C_SOURCE
    emoji_name: spam
    report_type: spam
    threshold: 3
    alert_channel_id: C_MODERATION
    alert_user_ids:
      - U_MOD
    is_enabled: true
"""
        )
        conversation = Mock()
        mocker.patch(
            "apps.slack.management.commands.slack_sync_moderation_rules.Conversation.objects.get",
            return_value=conversation,
        )
        update_or_create = mocker.patch(
            "apps.slack.management.commands.slack_sync_moderation_rules."
            "ModerationRule.objects.update_or_create"
        )

        command = Command()
        command.stdout = StringIO()

        command.handle(config=str(config_path))

        update_or_create.assert_called_once_with(
            conversation=conversation,
            emoji_name="spam",
            defaults={
                "report_type": "spam",
                "threshold": 3,
                "alert_channel_id": "C_MODERATION",
                "alert_user_ids": ["U_MOD"],
                "is_enabled": True,
            },
        )
        assert "Synced 1 moderation rule(s), skipped 0" in command.stdout.getvalue()

    def test_non_mapping_config_raises_command_error(self, tmp_path):
        """Test non-mapping YAML config fails with a clear command error."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text("- invalid\n")

        with pytest.raises(CommandError, match="Moderation config must be a mapping"):
            Command().handle(config=str(config_path))

    def test_non_list_rules_config_raises_command_error(self, tmp_path):
        """Test moderation_rules must be a list."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text("moderation_rules: invalid\n")

        with pytest.raises(CommandError, match="moderation_rules list"):
            Command().handle(config=str(config_path))

    def test_missing_required_rule_field_raises_command_error(self, tmp_path):
        """Test malformed rules fail before syncing any data."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text(
            """
moderation_rules:
  - channel_id: C_SOURCE
    emoji_name: spam
"""
        )

        with pytest.raises(CommandError, match="missing required fields"):
            Command().handle(config=str(config_path))

    def test_non_integer_threshold_raises_command_error(self, tmp_path):
        """Test non-integer thresholds fail with a clear command error."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text(
            """
moderation_rules:
  - channel_id: C_SOURCE
    emoji_name: spam
    report_type: spam
    threshold: high
    alert_channel_id: C_MODERATION
"""
        )

        with pytest.raises(CommandError, match="threshold must be an integer"):
            Command().handle(config=str(config_path))

    def test_invalid_rule_stops_before_partial_sync(self, mocker, tmp_path):
        """Test all rules are validated before any moderation rule is synced."""
        config_path = tmp_path / "moderation_rules.yaml"
        config_path.write_text(
            """
moderation_rules:
  - channel_id: C_SOURCE
    emoji_name: spam
    report_type: spam
    threshold: 3
    alert_channel_id: C_MODERATION
  - channel_id: C_BROKEN
    emoji_name: abusive
"""
        )
        update_or_create = mocker.patch(
            "apps.slack.management.commands.slack_sync_moderation_rules."
            "ModerationRule.objects.update_or_create"
        )

        with pytest.raises(CommandError, match="missing required fields"):
            Command().handle(config=str(config_path))

        update_or_create.assert_not_called()
