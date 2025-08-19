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
                "url": settings.SITE_URL,
            }
        ],
        "throttle": [],
    }
elif settings.IS_STAGING_ENVIRONMENT:
    api_settings_customization = {
        "servers": [
            {
                "description": "Staging",
                "url": settings.SITE_URL,
            }
        ],
    }
elif settings.IS_PRODUCTION_ENVIRONMENT:
    api_settings_customization = {
        "servers": [
            {
                "description": "Production",
                "url": settings.SITE_URL,
            }
        ],
    }


api = NinjaAPI(**{**api_settings, **api_settings_customization})


@api.get("/")
def api_root(request):
    """Handle API root endpoint requests."""
    return {
        "message": "Welcome to the OWASP Nest API v1",
        "docs_url": request.build_absolute_uri("docs"),
    }


api.add_router("owasp", owasp_router)
api.add_router("github", github_router)
