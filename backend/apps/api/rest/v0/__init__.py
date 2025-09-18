"""OWASP REST API v0."""

from django.conf import settings
from ninja import NinjaAPI, Swagger
from ninja.throttling import AuthRateThrottle

from apps.api.rest.auth.api_key import ApiKey as ApiKey
from apps.api.rest.v0.committee import router as committee_router
from apps.api.rest.v0.event import router as event_router
from apps.api.rest.v0.issue import router as issue_router
from apps.api.rest.v0.member import router as member_router
from apps.api.rest.v0.organization import router as organization_router
from apps.api.rest.v0.project import router as project_router
from apps.api.rest.v0.release import router as release_router
from apps.api.rest.v0.repository import router as repository_router

from .chapter import router as chapter_router

ROUTERS = {
    # Chapters.
    "/chapters": chapter_router,
    # Committees.
    "/committees": committee_router,
    # Community.
    "/members": member_router,
    "/organizations": organization_router,
    # Events.
    "/events": event_router,
    # Issues.
    "/issues": issue_router,
    # Projects.
    "/projects": project_router,
    # Releases.
    "/releases": release_router,
    # Repositories.
    "/repositories": repository_router,
}


api_settings = {
    "auth": ApiKey(),  # The `api_key` param name is based on the ApiKey class name.
    "description": "Open Worldwide Application Security Project API",
    "docs": Swagger(settings={"persistAuthorization": True}),
    "throttle": [AuthRateThrottle("10/s")],
    "title": "OWASP Nest",
    "version": "0.2.1",
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


@api.get("/", include_in_schema=False)
def api_root(request):
    """Handle API root endpoint requests."""
    return {
        "message": "Welcome to the OWASP Nest API v0",
        "docs_url": request.build_absolute_uri("docs"),
    }


for prefix, router in ROUTERS.items():
    api.add_router(prefix, router)
