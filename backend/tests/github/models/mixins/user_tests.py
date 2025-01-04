from apps.github.models.mixins.user import UserIndexMixin

FOLLOWERS_COUNT = 5
FOLLOWING_COUNT = 3
REPOSITORIES_COUNT = 42


class TestUserIndexMixin:
    def test_user_index(self):
        class MockModel(UserIndexMixin):
            def __init__(self):
                self.avatar_url = "https://avatars.githubusercontent.com/u/1"
                self.bio = "Bio"
                self.company = "Company"
                self.created_at = "2021-01-01T00:00:00Z"
                self.email = "email@example.com"
                self.followers_count = 5
                self.following_count = 3
                self.location = "Earth"
                self.login = "user_login"
                self.name = "John Doe"
                self.public_repositories_count = 42
                self.title = "GitHub User"
                self.updated_at = "2021-12-31T23:59:59Z"
                self.url = "https://api.github.com/users/user_login"

        mock_instance = MockModel()

        assert isinstance(mock_instance, UserIndexMixin)

        assert mock_instance.idx_avatar_url == "https://avatars.githubusercontent.com/u/1"
        assert mock_instance.idx_bio == "Bio"
        assert mock_instance.idx_company == "Company"
        assert mock_instance.idx_created_at == "2021-01-01T00:00:00Z"
        assert mock_instance.idx_email == "email@example.com"
        assert mock_instance.idx_followers_count == FOLLOWERS_COUNT
        assert mock_instance.idx_following_count == FOLLOWING_COUNT
        assert mock_instance.idx_location == "Earth"
        assert mock_instance.idx_key == "user_login"
        assert mock_instance.idx_name == "John Doe"
        assert mock_instance.idx_public_repositories_count == REPOSITORIES_COUNT
        assert mock_instance.idx_title == "GitHub User"
        assert mock_instance.idx_updated_at == "2021-12-31T23:59:59Z"
        assert mock_instance.idx_url == "https://api.github.com/users/user_login"
