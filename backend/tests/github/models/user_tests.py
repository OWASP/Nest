import pytest

from apps.github.models.user import User


class TestUserModel:
    @pytest.mark.parametrize(
        ("name", "login", "expected_str"),
        [
            ("John Doe", "johndoe", "John Doe"),
            ("", "janedoe", "janedoe"),
            (None, "ghost", "ghost"),
        ],
    )
    def test_str_representation(self, name, login, expected_str):
        user = User(name=name, login=login)
        assert str(user) == expected_str

    @pytest.mark.parametrize(
        ("login", "expected_indexable"),
        [
            ("johndoe", True),
            ("janedoe", True),
            ("ghost", False),
        ],
    )
    def test_is_indexable(self, login, expected_indexable):
        user = User(login=login)
        assert user.is_indexable is expected_indexable

    def test_from_github(self, mocker):
        gh_user = mocker.Mock(
            bio="Bio",
            hireable=True,
            twitter_username="twitter",
        )

        user = User()
        user.from_github(gh_user)

        assert user.bio == "Bio"
        assert user.is_hireable
        assert user.twitter_username == "twitter"

    def test_update_data(self, mocker):
        gh_user = mocker.Mock()
        gh_user.raw_data = {"node_id": "12345"}

        mock_user = mocker.Mock(spec=User)
        mock_user.node_id = "12345"
        mocker.patch("apps.github.models.user.User.objects.get", return_value=mock_user)

        user = User()
        user.from_github = mocker.Mock()

        updated_user = User.update_data(gh_user)

        assert updated_user.node_id == mock_user.node_id
        assert updated_user.from_github.call_count == 1
