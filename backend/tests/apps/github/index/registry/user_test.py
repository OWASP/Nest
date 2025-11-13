from unittest.mock import MagicMock, patch

import pytest
from django.db.models import Q

from apps.github.index.registry.user import UserIndex
from apps.github.models.user import User


@pytest.fixture
def user_index(mocker):
    """Return an instance of the UserIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return UserIndex()


class TestUserIndex:
    """Test suite for the UserIndex."""

    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert UserIndex.index_name == "users"
        assert UserIndex.should_index == "is_indexable"
        assert isinstance(UserIndex.fields, tuple)
        assert len(UserIndex.fields) > 0
        assert isinstance(UserIndex.settings, dict)
        assert "attributesForFaceting" in UserIndex.settings

    @patch("apps.github.index.registry.user.UserIndex.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        UserIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("github", "users")

    @patch("apps.github.models.user.User.get_non_indexable_logins", return_value=["user2"])
    def test_get_entities(self, mock_get_non_indexable_logins, user_index):
        """Test that get_entities constructs the correct queryset by excluding.

        bots and non-indexable users.
        """
        mock_user_manager = MagicMock()
        mock_user_manager.exclude.return_value = "final_queryset"

        with patch.object(User, "objects", mock_user_manager):
            queryset = user_index.get_entities()

            mock_user_manager.exclude.assert_called_once_with(
                Q(is_bot=True) | Q(login__in=["user2"])
            )
            assert queryset == "final_queryset"
