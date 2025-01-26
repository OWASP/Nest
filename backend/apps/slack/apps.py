from django.apps import AppConfig
from django.conf import settings
from slack_bolt import App


class SlackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.slack"

    app = (
        App(
            signing_secret=settings.SLACK_SIGNING_SECRET,
            token=settings.SLACK_BOT_TOKEN,
        )
        if settings.SLACK_BOT_TOKEN != "None" and settings.SLACK_SIGNING_SECRET != "None"  # noqa: S105
        else None
    )
