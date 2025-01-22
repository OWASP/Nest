"""Slack bot view for Slack events."""

from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

from apps.slack.apps import SlackConfig

slack_handler = SlackRequestHandler(SlackConfig.app)


@csrf_exempt
def slack_request_handler(request):
    """Slack request handler."""
    return slack_handler.handle(request)
