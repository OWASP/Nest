"""A command to start Slack bot."""

import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from slack_bolt.adapter.socket_mode import SocketModeHandler

from apps.slack.apps import SlackConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs Slack bot application."

    def handle(self, *args, **options):
        if settings.SLACK_APP_TOKEN:
            SocketModeHandler(SlackConfig.app, settings.SLACK_APP_TOKEN).start()
