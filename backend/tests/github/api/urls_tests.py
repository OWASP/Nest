import pytest

from apps.github.api.issue import IssueViewSet
from apps.github.api.label import LabelViewSet
from apps.github.api.organization import OrganizationViewSet
from apps.github.api.release import ReleaseViewSet
from apps.github.api.repository import RepositoryViewSet
from apps.github.api.urls import router
from apps.github.api.user import UserViewSet


@pytest.mark.parametrize(
    ("url_name", "viewset_class", "expected_prefix"),
    [
        ("issue-list", IssueViewSet, "github/issues"),
        ("label-list", LabelViewSet, "github/labels"),
        ("organization-list", OrganizationViewSet, "github/organizations"),
        ("release-list", ReleaseViewSet, "github/releases"),
        ("repository-list", RepositoryViewSet, "github/repositories"),
        ("user-list", UserViewSet, "github/users"),
    ],
)
def test_router_registration(url_name, expected_prefix, viewset_class):
    matching_routes = [route for route in router.urls if route.name == url_name]
    assert matching_routes, f"Route '{url_name}' not found in router."

    for route in matching_routes:
        assert (
            expected_prefix in route.pattern.describe()
        ), f"Prefix '{expected_prefix}' not found in route '{route.name}'."

        viewset = route.callback.cls
        assert issubclass(
            viewset, viewset_class
        ), f"Viewset for '{route.name}' does not match {viewset_class}."
