import pytest

from apps.feedback.api.feedback import FeedbackViewSet
from apps.feedback.api.urls import router


@pytest.mark.parametrize(
    ("url_name", "expected_prefix", "viewset_class"),
    [
        ("feedback-list", "feedback", FeedbackViewSet),
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
