"""OWASP Nest URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_protect
from strawberry.django.views import GraphQLView

from apps.core.api.algolia import algolia_search
from apps.core.api.csrf import get_csrf_token
from apps.core.api.status import get_status
from apps.slack.apps import SlackConfig
from settings.api_v1 import api as api_v1
from settings.graphql import schema

urlpatterns = [
    path("csrf/", get_csrf_token),
    path("idx/", csrf_protect(algolia_search)),
    path("graphql/", csrf_protect(GraphQLView.as_view(schema=schema, graphiql=settings.DEBUG))),
    path("api/v1/", api_v1.urls),
    path("a/", admin.site.urls),
    path("status/", get_status),
    path("", include("apps.sitemap.urls")),
]

if SlackConfig.app:
    from apps.slack.views import slack_request_handler

    urlpatterns += [
        path("integrations/slack/commands/", slack_request_handler),
        path("integrations/slack/events/", slack_request_handler),
        path("integrations/slack/interactivity/", slack_request_handler),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
