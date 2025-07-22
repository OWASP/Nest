"""OWASP Nest API v1 configuration."""

from ninja import NinjaAPI, Swagger
from ninja.throttling import AuthRateThrottle

from apps.core.api.ninja import ApiKeyAuth
from apps.github.api.rest.v1.urls import router as github_router
from apps.owasp.api.rest.v1.urls import router as owasp_router

api = NinjaAPI(
    description="API for OWASP related entities",
    docs=Swagger(settings={"persistAuthorization": True}),
    title="OWASP Nest API",
    version="1.0.0",
    auth=ApiKeyAuth(),
    throttle=[
        AuthRateThrottle("10/s"),
    ],
)

api.add_router("github", github_router)
api.add_router("owasp", owasp_router)
