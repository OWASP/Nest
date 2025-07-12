"""OWASP Nest API v1 configuration."""

from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from apps.core.api.ninja import ApiKeyAuth
from apps.github.api.v1.urls import router as github_router
from apps.owasp.api.v1.urls import router as owasp_router

api = NinjaAPI(
    description="API for OWASP related entities",
    title="OWASP Nest API",
    version="1.0.0",
    auth=ApiKeyAuth(),
    throttle=[
        AnonRateThrottle("1/s"),
        AuthRateThrottle("10/s"),
    ],
)

api.add_router("github", github_router)
api.add_router("owasp", owasp_router)
