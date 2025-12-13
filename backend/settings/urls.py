"""OWASP Nest URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from strawberry.django.views import GraphQLView

from apps.api.rest.v0 import api as api_v0
from apps.core.api.internal.algolia import algolia_search
from apps.core.api.internal.csrf import get_csrf_token
from apps.core.api.internal.status import get_status
from apps.owasp.api.internal.views.urls import urlpatterns as owasp_urls
from apps.slack.apps import SlackConfig
from settings.graphql import schema


def csrf_decorator(view_func):
    """Apply CSRF protection or exemption based on the environment.

    Args:
        view_func (function): The view function to decorate.

    Returns:
        function: The decorated view function with CSRF protection or exemption.

    """
    environment = settings.ENVIRONMENT
    if environment == "Fuzz":
        return csrf_exempt(view_func)  # NOSONAR
    return csrf_protect(view_func)


urlpatterns = [
    path("csrf/", get_csrf_token),
    path("idx/", csrf_protect(algolia_search)),
    path("graphql/", csrf_decorator(GraphQLView.as_view(schema=schema, graphiql=settings.DEBUG))),
    path("api/v0/", api_v0.urls),
    path("a/", admin.site.urls),
    path("owasp/", include(owasp_urls)),
    path("status/", get_status),
    path("", include("apps.sitemap.urls")),
    path("django-rq/", include("django_rq.urls")),
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
