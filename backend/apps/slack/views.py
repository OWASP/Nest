from django.views.decorators.csrf import csrf_exempt  # noqa: D100
from slack_bolt.adapter.django import SlackRequestHandler

from apps.slack.apps import SlackConfig
from apps.slack.commands import *  # noqa: F403
from apps.slack.events import *  # noqa: F403

slack_handler = SlackRequestHandler(SlackConfig.app)


@csrf_exempt
def slack_events(request):  # noqa: D103
    return slack_handler.handle(request)
