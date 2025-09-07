import pytest

from apps.github.api.rest.v1.issue import router as issue_router
from apps.github.api.rest.v1.member import router as member_router
from apps.github.api.rest.v1.organization import router as organization_router
from apps.github.api.rest.v1.release import router as release_router
from apps.github.api.rest.v1.repository import router as repository_router
from apps.owasp.api.rest.v1.chapter import router as chapter_router
from apps.owasp.api.rest.v1.committee import router as committee_router
from apps.owasp.api.rest.v1.event import router as event_router
from apps.owasp.api.rest.v1.project import router as project_router
from settings.api.v1 import api as main_router
from settings.api.v1 import api_root


class TestRouterRegistration:
    """Test the urls registration."""

    EXPECTED_ROUTERS = {
        "": api_root,
        "/chapters": chapter_router,
        "/committees": committee_router,
        "/events": event_router,
        "/issues": issue_router,
        "/members": member_router,
        "/organizations": organization_router,
        "/projects": project_router,
        "/releases": release_router,
        "/repositories": repository_router,
    }

    def test_all_routers_are_registered(self):
        """Verifies that the main router has the correct number of registered sub-routers."""
        assert len(main_router._routers) == len(self.EXPECTED_ROUTERS)

    @pytest.mark.parametrize(
        ("prefix", "expected_router_instance"), list(EXPECTED_ROUTERS.items())
    )
    def test_sub_router_registration(self, prefix, expected_router_instance):
        """Tests that each specific router is registered with the correct prefix."""
        registered_router_map = dict(main_router._routers)

        assert prefix in registered_router_map
        if prefix:
            assert registered_router_map[prefix] is expected_router_instance
