"""OWASP Nest API v1 configuration."""

from ninja import NinjaAPI

from apps.github.api.urls import router as github_router
from apps.owasp.api.urls import router as owasp_router

api = NinjaAPI(
    description="API for OWASP related entities",
    title="OWASP Nest API",
    version="1.0.0",
)

api.add_router("github", github_router)
api.add_router("owasp", owasp_router)
