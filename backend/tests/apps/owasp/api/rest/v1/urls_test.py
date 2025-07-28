import pytest

from apps.owasp.api.rest.v1.chapter import router as chapter_router
from apps.owasp.api.rest.v1.committee import router as committee_router
from apps.owasp.api.rest.v1.event import router as event_router
from apps.owasp.api.rest.v1.project import router as project_router
from apps.owasp.api.rest.v1.urls import router as main_router


class TestRouterRegistration:
    """Test the urls registration."""

    EXPECTED_ROUTERS = {
        "/chapters": chapter_router,
        "/committees": committee_router,
        "/events": event_router,
        "/projects": project_router,
    }

    def test_all_routers_are_registered(self):
        """Verifies that the main router has the correct number of registered sub-routers."""
        registered_sub_routers = main_router._routers
        assert len(registered_sub_routers) == len(self.EXPECTED_ROUTERS)

    @pytest.mark.parametrize(
        ("prefix", "expected_router_instance"), list(EXPECTED_ROUTERS.items())
    )
    def test_sub_router_registration(self, prefix, expected_router_instance):
        """Tests that each specific router is registered with the correct prefix."""
        registered_router_map = dict(main_router._routers)

        assert prefix in registered_router_map
        actual_router = registered_router_map[prefix]

        assert actual_router is expected_router_instance
