import pytest

from apps.github.api.v1.issue import router as issue_router
from apps.github.api.v1.label import router as label_router
from apps.github.api.v1.organization import router as organization_router
from apps.github.api.v1.release import router as release_router
from apps.github.api.v1.repository import router as repository_router
from apps.github.api.v1.urls import router as main_router
from apps.github.api.v1.user import router as user_router


class TestRouterRegistration:
    """Test the urls registration."""

    EXPECTED_ROUTERS = {
        "/issues": issue_router,
        "/labels": label_router,
        "/organizations": organization_router,
        "/releases": release_router,
        "/repositories": repository_router,
        "/users": user_router,
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
