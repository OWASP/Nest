import pytest

from apps.github.models.mixins.user import UserIndexMixin

FOLLOWERS_COUNT = 5
FOLLOWING_COUNT = 3
REPOSITORIES_COUNT = 42


class TestUserIndexMixin:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_avatar_url", "https://avatars.githubusercontent.com/u/1"),
            ("idx_bio", "Bio"),
            ("idx_company", "Company"),
            ("idx_created_at", "2021-01-01T00:00:00Z"),
            ("idx_email", "email@example.com"),
            ("idx_followers_count", FOLLOWERS_COUNT),
            ("idx_following_count", FOLLOWING_COUNT),
            ("idx_location", "Earth"),
            ("idx_key", "user_login"),
            ("idx_name", "John Doe"),
            ("idx_public_repositories_count", REPOSITORIES_COUNT),
            ("idx_title", "GitHub User"),
            ("idx_updated_at", "2021-12-31T23:59:59Z"),
            ("idx_url", "https://api.github.com/users/user_login"),
        ],
    )
    def test_user_index(self, attr, expected):
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

        assert getattr(mock_instance, attr) == expected
