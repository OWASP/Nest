"""GitHub API URLs."""

#!/usr/bin/env python3
from rest_framework import routers

from apps.github.api.issue import IssueViewSet
from apps.github.api.label import LabelViewSet
from apps.github.api.organization import OrganizationViewSet
from apps.github.api.release import ReleaseViewSet
from apps.github.api.repository import RepositoryViewSet
from apps.github.api.user import UserViewSet

router = routers.SimpleRouter()

router.register(r"github/issues", IssueViewSet)
router.register(r"github/labels", LabelViewSet)
router.register(r"github/organizations", OrganizationViewSet)
router.register(r"github/releases", ReleaseViewSet)
router.register(r"github/repositories", RepositoryViewSet)
router.register(r"github/users", UserViewSet)
