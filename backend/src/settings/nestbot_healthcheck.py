"""NestBot queue probe settings without Slack authentication."""

from settings.staging import Staging as BaseStaging
from settings.values import OptionalSecretValue


class Staging(BaseStaging):
    """Read staging queue settings without configuring Slack handlers."""

    SLACK_BOT_TOKEN = OptionalSecretValue(environ=False)
    SLACK_SIGNING_SECRET = OptionalSecretValue(environ=False)
    SLACK_COMMANDS_ENABLED = False
    SLACK_EVENTS_ENABLED = False
