"""OWASP Nest API v1 configuration."""

from django.conf import settings
from ninja import NinjaAPI, Swagger
from ninja.throttling import AuthRateThrottle

from apps.core.api.ninja import ApiKeyAuth
from apps.github.api.rest.v1.urls import router as github_router
from apps.owasp.api.rest.v1.urls import router as owasp_router

api_settings = {
    "auth": ApiKeyAuth(),
    "description": "Open Worldwide Application Security Project API",
    "docs": Swagger(settings={"persistAuthorization": True}),
    "throttle": [AuthRateThrottle("10/s")],
    "title": "OWASP Nest",
    "version": "1.0.0",
}


api_settings_customization = {}
if settings.IS_LOCAL_ENVIRONMENT:
    api_settings_customization = {
        "auth": None,
        "servers": [
            {
                "description": "Local",
                "url": "http://localhost:8000",
            }
        ],
        "throttle": [],
    }
elif settings.IS_STAGING_ENVIRONMENT:
    api_settings_customization = {
        "servers": [
            {
                "description": "Staging",
                "url": "https://nest.owasp.dev",
            }
        ],
    }
elif settings.IS_PRODUCTION_ENVIRONMENT:
    api_settings_customization = {
        "servers": [
            {
                "description": "Production",
                "url": "https://nest.owasp.org",
            }
        ],
    }


api = NinjaAPI(**{**api_settings, **api_settings_customization})

api.add_router("owasp", owasp_router)
api.add_router("github", github_router)