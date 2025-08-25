from unittest.mock import MagicMock, patch

import pytest

from apps.nest.api.internal.mutations.badge import BadgeMutations


def mock_info() -> MagicMock:
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    return info


class TestBadgeMutations:
    @pytest.fixture
    def badge_mutations(self) -> BadgeMutations:
        return BadgeMutations()

    @patch("apps.nest.api.internal.mutations.badge.Badge.objects.get")
    def test_add_badge_to_user(self, mock_get, badge_mutations):
        info = mock_info()
        user = info.context.request.user

        badge = MagicMock()
        mock_get.return_value = badge
        # user.badges.order_by returns list
        user.badges.order_by.return_value = [badge]

        result = badge_mutations.add_badge_to_user(info, badge_id=1)

        mock_get.assert_called_once_with(pk=1)
        user.badges.add.assert_called_once_with(badge)
        user.badges.order_by.assert_called_once_with("weight", "name")
        assert isinstance(result, list)

    @patch("apps.nest.api.internal.mutations.badge.Badge.objects.get")
    def test_remove_badge_from_user(self, mock_get, badge_mutations):
        info = mock_info()
        user = info.context.request.user

        badge = MagicMock()
        mock_get.return_value = badge
        user.badges.order_by.return_value = []

        result = badge_mutations.remove_badge_from_user(info, badge_id=1)

        mock_get.assert_called_once_with(pk=1)
        user.badges.remove.assert_called_once_with(badge)
        user.badges.order_by.assert_called_once_with("weight", "name")
        assert isinstance(result, list)
