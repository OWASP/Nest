"""GitHub API URLs."""

from ninja import Router

from apps.owasp.api.v1.chapter import router as chapter_router
from apps.owasp.api.v1.committee import router as committee_router
from apps.owasp.api.v1.event import router as event_router
from apps.owasp.api.v1.project import router as project_router
from apps.owasp.api.v1.project_health_metrics import router as project_health_metrics_router

router = Router()

router.add_router(r"/chapters", chapter_router)
router.add_router(r"/committees", committee_router)
router.add_router(r"/events", event_router)
router.add_router(r"/projects", project_router)
router.add_router(r"/project-health-metrics", project_health_metrics_router)
