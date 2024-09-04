"""GitHub API URLs."""

from rest_framework import routers

from apps.owasp.api import (
    ChapterViewSet,
    CommitteeViewSet,
    EventViewSet,
    ProjectViewSet,
)

router = routers.SimpleRouter()

router.register(r"owasp/chapters", ChapterViewSet)
router.register(r"owasp/committees", CommitteeViewSet)
router.register(r"owasp/events", EventViewSet)
router.register(r"owasp/projects", ProjectViewSet)
