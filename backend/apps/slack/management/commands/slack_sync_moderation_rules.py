"""Sync Slack moderation rules from YAML config."""

from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.slack.models import Conversation
from apps.slack.models.moderation import ModerationRule

DEFAULT_CONFIG_PATH = Path(settings.BASE_DIR) / "apps/slack/config/moderation_rules.yaml"

REQUIRED_FIELDS = {
    "channel_id",
    "emoji_name",
    "report_type",
    "threshold",
    "alert_channel_id",
}


class Command(BaseCommand):
    """Sync Slack moderation rules from a YAML file."""

    help = "Sync Slack moderation rules from YAML config"

    def add_arguments(self, parser):
        """Define command line arguments."""
        parser.add_argument(
            "--config",
            default=str(DEFAULT_CONFIG_PATH),
            help="Path to the Slack moderation rules YAML file",
        )

    def handle(self, *args, **options):
        """Sync moderation rules from YAML."""
        config_path = Path(options["config"])

        if not config_path.exists():
            self.stdout.write(self.style.WARNING(f"Moderation config not found: {config_path}"))
            return

        with config_path.open() as config_file:
            config = yaml.safe_load(config_file)

        if config is None:
            self.stdout.write(self.style.WARNING("Moderation config has no rules"))
            return

        if not isinstance(config, dict):
            msg = "Moderation config must be a mapping"
            raise CommandError(msg)

        rules = config.get("moderation_rules", [])
        if not isinstance(rules, list):
            msg = "Moderation config must contain a moderation_rules list"
            raise CommandError(msg)

        for rule in rules:
            self._validate_rule(rule)

        synced_count = 0
        skipped_count = 0

        for rule in rules:
            try:
                conversation = Conversation.objects.get(slack_channel_id=rule["channel_id"])
            except Conversation.DoesNotExist:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping moderation rule for missing channel: {rule['channel_id']}"
                    )
                )
                continue

            ModerationRule.objects.update_or_create(
                conversation=conversation,
                emoji_name=rule["emoji_name"],
                defaults={
                    "report_type": rule["report_type"],
                    "threshold": rule["threshold"],
                    "alert_channel_id": rule["alert_channel_id"],
                    "alert_user_ids": rule.get("alert_user_ids", []),
                    "is_enabled": rule.get("is_enabled", True),
                },
            )
            synced_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {synced_count} moderation rule(s), skipped {skipped_count}"
            )
        )

    def _validate_rule(self, rule):
        """Validate one moderation rule config entry."""
        if not isinstance(rule, dict):
            msg = "Each moderation rule must be a mapping"
            raise CommandError(msg)

        missing_fields = REQUIRED_FIELDS - rule.keys()
        if missing_fields:
            msg = f"Moderation rule missing required fields: {', '.join(sorted(missing_fields))}"
            raise CommandError(msg)

        if not isinstance(rule["threshold"], int):
            msg = "Moderation rule threshold must be an integer"
            raise CommandError(msg)

        if rule["threshold"] < 1:
            msg = "Moderation rule threshold must be at least 1"
            raise CommandError(msg)
