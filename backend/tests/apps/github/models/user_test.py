from unittest.mock import Mock, patch

import pytest

from apps.github.models.user import User


class TestUserModel:
    @pytest.mark.parametrize(
        ("name", "login", "expected_str"),
        [
            ("John Doe", "john-doe", "John Doe"),
            ("", "jane-doe", "jane-doe"),
            (None, "ghost", "ghost"),
        ],
    )
    def test_str_representation(self, name, login, expected_str):
        user = User(name=name, login=login)
        assert str(user) == expected_str

    def test_from_github(self):
        gh_user_mock = Mock(
            bio="Bio",
            hireable=True,
            twitter_username="twitter",
        )

        user = User()
        user.from_github(gh_user_mock)

        assert user.bio == "Bio"
        assert user.is_hireable
        assert user.twitter_username == "twitter"

    @patch("apps.github.models.user.User.objects.get")
    @patch("apps.github.models.user.User.save")
    def test_update_data(self, mock_save, mock_get):
        gh_user_mock = Mock()
        gh_user_mock.raw_data = {"node_id": "12345"}
        gh_user_mock.bio = "Bio"
        gh_user_mock.hireable = True
        gh_user_mock.twitter_username = "twitter"

        mock_user = Mock(spec=User)
        mock_user.node_id = "12345"
        mock_get.return_value = mock_user

        updated_user = User.update_data(gh_user_mock, save=True)

        mock_get.assert_called_once_with(node_id="12345")
        assert updated_user.node_id == "12345"

    @patch("apps.github.models.user.User.objects.get")
    @patch("apps.github.models.user.User.save")
    def test_update_data_user_does_not_exist(self, mock_save, mock_get):
        gh_user_mock = Mock()
        gh_user_mock.raw_data = {"node_id": "67890"}
        gh_user_mock.bio = "New Bio"
        gh_user_mock.hireable = False
        gh_user_mock.twitter_username = "new_twitter"

        mock_get.side_effect = User.DoesNotExist

        updated_user = User.update_data(gh_user_mock, save=True)

        mock_get.assert_called_once_with(node_id="67890")
        assert updated_user.node_id == "67890"
