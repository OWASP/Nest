import pytest

from apps.owasp.api.chapter import ChapterViewSet
from apps.owasp.api.committee import CommitteeViewSet
from apps.owasp.api.event import EventViewSet
from apps.owasp.api.project import ProjectViewSet
from apps.owasp.api.urls import router


@pytest.mark.parametrize(
    ("url_name", "expected_prefix", "viewset_class"),
    [
        ("chapter-list", "owasp/chapters", ChapterViewSet),
        ("committee-list", "owasp/committees", CommitteeViewSet),
        ("event-list", "owasp/events", EventViewSet),
        ("project-list", "owasp/projects", ProjectViewSet),
    ],
)
def test_router_registration(url_name, expected_prefix, viewset_class):
    # Find routes with the specified `url_name`
    matching_routes = [route for route in router.urls if route.name == url_name]
    assert matching_routes, f"Route '{url_name}' not found in router."

    for route in matching_routes:
        # Verify that the route's pattern includes the expected prefix
        assert (
            expected_prefix in route.pattern.describe()
        ), f"Prefix '{expected_prefix}' not found in route '{route.name}'."

        # Extract the viewset from the route and verify its type
        viewset = route.callback.cls
        assert issubclass(
            viewset, viewset_class
        ), f"Viewset for '{route.name}' does not match {viewset_class}."
