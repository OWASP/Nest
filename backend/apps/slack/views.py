"""Slack bot view for Slack events."""

from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

from apps.slack.apps import SlackConfig
from apps.slack.commands import *  # noqa: F403
from apps.slack.events import *  # noqa: F403

slack_handler = SlackRequestHandler(SlackConfig.app)


@csrf_exempt
def slack_events_handler(request):
    """Slack bot handle for incoming HttpRequests from Slack events."""
    return slack_handler.handle(request)
