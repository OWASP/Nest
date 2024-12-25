from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler
from apps.slack.apps import SlackConfig
from apps.slack.commands import *
from apps.slack.events import *

slack_handler = SlackRequestHandler(SlackConfig.app)

@csrf_exempt
def slack_events(request):
    return slack_handler.handle(request)
