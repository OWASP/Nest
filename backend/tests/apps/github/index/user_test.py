from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.github.index.user import UserIndex


class TestUserIndex(SimpleTestCase):
    """Test the UserIndex class."""

    databases = []

    def setUp(self):
        self.model = MagicMock()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.user_index = UserIndex(self.model, self.client, self.settings)

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        with patch.object(UserIndex, "get_client", return_value=self.client):
            UserIndex.update_synonyms()
            mock_reindex_synonyms.assert_called_once_with("github", "users")

    @patch("apps.github.models.user.User.get_non_indexable_logins")
    def test_get_entities(self, mock_get_non_indexable_logins):
        mock_get_non_indexable_logins.return_value = ["bot1", "bot2"]
        mock_queryset = MagicMock()

        with patch("apps.github.models.user.User.objects") as mock_objects:
            mock_objects.exclude.return_value = mock_queryset

            result = self.user_index.get_entities()

            mock_objects.exclude.assert_called_once_with(
                is_bot=False,
                login__in=mock_get_non_indexable_logins.return_value,
            )
            assert result == mock_queryset
