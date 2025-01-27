"""GitHub API URLs."""

from rest_framework import routers

from apps.github.api.issue import IssueViewSet
from apps.owasp.api.chapter import ChapterViewSet
from apps.owasp.api.committee import CommitteeViewSet
from apps.owasp.api.event import EventViewSet
from apps.owasp.api.project import ProjectViewSet

router = routers.SimpleRouter()

router.register(r"owasp/chapters", ChapterViewSet)
router.register(r"owasp/committees", CommitteeViewSet)
router.register(r"owasp/contribute", IssueViewSet)
router.register(r"owasp/events", EventViewSet)
router.register(r"owasp/projects", ProjectViewSet)
