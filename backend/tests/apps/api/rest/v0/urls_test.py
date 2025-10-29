import pytest

from apps.api.rest.v0 import api as main_router
from apps.api.rest.v0 import api_root
from apps.api.rest.v0.chapter import router as chapter_router
from apps.api.rest.v0.committee import router as committee_router
from apps.api.rest.v0.event import router as event_router
from apps.api.rest.v0.issue import router as issue_router
from apps.api.rest.v0.member import router as member_router
from apps.api.rest.v0.milestone import router as milestone_router
from apps.api.rest.v0.organization import router as organization_router
from apps.api.rest.v0.project import router as project_router
from apps.api.rest.v0.release import router as release_router
from apps.api.rest.v0.repository import router as repository_router
from apps.api.rest.v0.sponsor import router as sponsor_router


class TestRouterRegistration:
    """Test the urls registration."""

    EXPECTED_ROUTERS = {
        "": api_root,
        "/chapters": chapter_router,
        "/committees": committee_router,
        "/events": event_router,
        "/issues": issue_router,
        "/members": member_router,
        "/milestones": milestone_router,
        "/organizations": organization_router,
        "/projects": project_router,
        "/releases": release_router,
        "/repositories": repository_router,
        "/sponsors": sponsor_router,
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
