"""OWASP REST API v0."""

from typing import Any

from django.conf import settings
from ninja import NinjaAPI, Swagger
from ninja.errors import ValidationError
from ninja.pagination import RouterPaginated

from apps.api.rest.auth.api_key import ApiKey
from apps.api.rest.throttle.rate_limit_headers import RateLimitHeadersThrottle
from apps.api.rest.v0.chapter import router as chapter_router
from apps.api.rest.v0.committee import router as committee_router
from apps.api.rest.v0.event import router as event_router
from apps.api.rest.v0.issue import router as issue_router
from apps.api.rest.v0.member import router as member_router
from apps.api.rest.v0.milestone import router as milestone_router
from apps.api.rest.v0.organization import router as organization_router
from apps.api.rest.v0.project import router as project_router
from apps.api.rest.v0.release import router as release_router
from apps.api.rest.v0.repository import router as repository_router
from apps.api.rest.v0.snapshot import router as snapshot_router
from apps.api.rest.v0.sponsor import router as sponsor_router

ROUTERS = {
    "/chapters": chapter_router,
    "/committees": committee_router,
    "/events": event_router,
    "/issues": issue_router,
    "/members": member_router,
    "/milestones": milestone_router,
    "/organizations": organization_router,
    "/projects": project_router,
    "/releases": release_router,
    "/repositories": repository_router,
    "/snapshots": snapshot_router,
    "/sponsors": sponsor_router,
}


api_settings = {
    "auth": ApiKey(),  # The `api_key` param name is based on the ApiKey class name.
    "default_router": RouterPaginated(),
    "description": "Open Worldwide Application Security Project API",
    "docs": Swagger(settings={"persistAuthorization": True}),
    "throttle": [RateLimitHeadersThrottle("10/s")],
    "title": "OWASP Nest",
    "version": "0.3.6",
}

api_settings_customization: dict[str, Any] = {}
if settings.IS_PRODUCTION_ENVIRONMENT:
    api_settings_customization = {
        "servers": [
            {
                "description": "Production",
                "url": settings.SITE_URL,
            }
        ],
    }
elif settings.IS_E2E_ENVIRONMENT:
    api_settings_customization = {
        "auth": None,
        "servers": [
            {
                "description": "E2E",
                "url": settings.SITE_URL,
            }
        ],
        "throttle": [],
    }
elif settings.IS_FUZZ_ENVIRONMENT:
    api_settings_customization = {
        "auth": None,
        "servers": [
            {
                "description": "Fuzz",
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
elif settings.IS_LOCAL_ENVIRONMENT:
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

api = NinjaAPI(**{**api_settings, **api_settings_customization})


@api.exception_handler(ValidationError)
def validation_exception_handler(request, exc):
    """Handle validation exceptions."""
    return api.create_response(
        request,
        {"message": "Invalid request", "errors": exc.errors},
        status=400,
    )


@api.get("/", include_in_schema=False)
def api_root(request):
    """Handle API root endpoint requests."""
    return {
        "message": "Welcome to the OWASP Nest API v0",
        "docs_url": request.build_absolute_uri("docs"),
    }


for prefix, router in ROUTERS.items():
    api.add_router(prefix, router)
