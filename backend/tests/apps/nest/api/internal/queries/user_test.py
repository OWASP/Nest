from unittest.mock import MagicMock

from apps.nest.api.internal.nodes.user import AuthUserNode
from apps.nest.api.internal.queries.user import UserQueries


def mock_info() -> MagicMock:
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock(spec=AuthUserNode)
    info.context.request.user.is_authenticated = True
    return info


class TestUserQueries:
    def test_me_field_exists(self):
        assert hasattr(UserQueries, "__strawberry_definition__")
        field_names = [f.name for f in UserQueries.__strawberry_definition__.fields]
        assert "me" in field_names

    def test_me_returns_user(self):
        q = UserQueries()
        info = mock_info()
        result = q.__class__.__dict__["me"](q, info)
        assert result is info.context.request.user
