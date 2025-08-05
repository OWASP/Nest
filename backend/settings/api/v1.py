"""OWASP Nest API v1 configuration."""

from django.conf import settings
from ninja import NinjaAPI, Swagger
from ninja.throttling import AuthRateThrottle

from apps.core.api.ninja import ApiKeyAuth
from apps.github.api.rest.v1.urls import router as github_router
from apps.owasp.api.rest.v1.urls import router as owasp_router

api_settings = {
    "description": "Open Worldwide Application Security Project API",
    "docs": Swagger(settings={"persistAuthorization": True}),
    "title": "OWASP Nest",
    "servers": [
        {"url": "https://nest.owasp.org", "description": "Production"},
        {"url": "https://nest.owasp.dev", "description": "Staging"},
    ],
    "version": "1.0.0",
}
if not settings.IS_LOCAL_ENVIRONMENT:
    api_settings.update(
        {
            "auth": ApiKeyAuth(),
            "throttle": [AuthRateThrottle("10/s")],
        }
    )

api = NinjaAPI(**api_settings)

api.add_router("github", github_router)
api.add_router("owasp", owasp_router)
