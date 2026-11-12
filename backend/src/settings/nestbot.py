"""NestBot staging configuration."""

from configurations import values

from settings.staging import Staging as BaseStaging


class Staging(BaseStaging):
    """Enable Slack only in the dedicated staging NestBot service."""

    SLACK_BOT_TOKEN = values.SecretValue()
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True
    SLACK_SIGNING_SECRET = values.SecretValue()
