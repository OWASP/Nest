"""GitHub API URLs."""

from ninja import Router

from apps.owasp.api.chapter import router as chapter_router
from apps.owasp.api.committee import router as committee_router
from apps.owasp.api.event import router as event_router
from apps.owasp.api.project import router as project_router

router = Router()

router.add_router(r"/chapters", chapter_router)
router.add_router(r"/committees", committee_router)
router.add_router(r"/events", event_router)
router.add_router(r"/projects", project_router)
