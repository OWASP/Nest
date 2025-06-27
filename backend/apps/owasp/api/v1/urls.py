"""GitHub API URLs."""

from ninja import Router

from apps.owasp.api.v1.chapter import router as chapter_router
from apps.owasp.api.v1.committee import router as committee_router
from apps.owasp.api.v1.event import router as event_router
from apps.owasp.api.v1.project import router as project_router

router = Router()

router.add_router(r"/chapters", chapter_router)
router.add_router(r"/committees", committee_router)
router.add_router(r"/events", event_router)
router.add_router(r"/projects", project_router)
