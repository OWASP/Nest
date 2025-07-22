"""GitHub REST API v1 URLs."""

from ninja import Router

from apps.github.api.rest.v1.issue import router as issue_router
from apps.github.api.rest.v1.label import router as label_router
from apps.github.api.rest.v1.organization import router as organization_router
from apps.github.api.rest.v1.release import router as release_router
from apps.github.api.rest.v1.repository import router as repository_router
from apps.github.api.rest.v1.user import router as user_router

router = Router()

router.add_router(r"/issues", issue_router)
router.add_router(r"/labels", label_router)
router.add_router(r"/organizations", organization_router)
router.add_router(r"/releases", release_router)
router.add_router(r"/repositories", repository_router)
router.add_router(r"/users", user_router)
