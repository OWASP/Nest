"""GitHub API URLs."""

from rest_framework import routers

from apps.github.api import (
    IssueViewSet,
    LabelViewSet,
    OrganizationViewSet,
    ReleaseViewSet,
    RepositoryViewSet,
    UserViewSet,
)

router = routers.SimpleRouter()

router.register(r"github/issues", IssueViewSet)
router.register(r"github/labels", LabelViewSet)
router.register(r"github/organizations", OrganizationViewSet)
router.register(r"github/releases", ReleaseViewSet)
router.register(r"github/repositories", RepositoryViewSet)
router.register(r"github/users", UserViewSet)
