"""OWASP Nest URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework import routers

from apps.core.api.algolia import algolia_search
from apps.feedback.api.urls import router as feedback_router
from apps.github.api.urls import router as github_router
from apps.owasp.api.urls import router as owasp_router
from apps.slack.apps import SlackConfig

router = routers.DefaultRouter()
router.registry.extend(github_router.registry)
router.registry.extend(owasp_router.registry)
router.registry.extend(feedback_router.registry)

urlpatterns = [
    path("idx/", csrf_exempt(algolia_search)),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    path("api/v1/", include(router.urls)),
    path("a/", admin.site.urls),
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
