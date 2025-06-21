"""GitHub API URLs."""

from ninja import Router

from apps.github.api.issue import router as issue_router
from apps.github.api.label import router as label_router
from apps.github.api.organization import router as organization_router
from apps.github.api.release import router as release_router
from apps.github.api.repository import router as repository_router
from apps.github.api.user import router as user_router

router = Router()

router.add_router("/issues", issue_router)
router.add_router("/labels", label_router)
router.add_router("/organizations", organization_router)
router.add_router("/releases", release_router)
router.add_router("/repositories", repository_router)
router.add_router("/users", user_router)
