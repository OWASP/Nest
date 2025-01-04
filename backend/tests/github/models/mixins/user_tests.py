from apps.github.models.mixins.user import UserIndexMixin


class TestUserIndexMixin:
    def test_user_index(self):
        class MockModel(UserIndexMixin):
            avatar_url = "https://avatars.githubusercontent.com/u/1"
            bio = "Bio"
            company = "Company"
            created_at = "2021-01-01T00:00:00Z"
            email = "email@example.com"
            followers_count = 5
            following_count = 3
            location = "Earth"
            login = "user_login"
            name = "John Doe"
            public_repositories_count = 42
            title = "GitHub User"
            updated_at = "2021-12-31T23:59:59Z"
            url = "https://api.github.com/users/user_login"

        mock_instance = MockModel()

        assert mock_instance.idx_avatar_url == "https://avatars.githubusercontent.com/u/1"
        assert mock_instance.idx_bio == "Bio"
        assert mock_instance.idx_company == "Company"
        assert mock_instance.idx_created_at == "2021-01-01T00:00:00Z"
        assert mock_instance.idx_email == "email@example.com"
        assert mock_instance.idx_followers_count == 5
        assert mock_instance.idx_following_count == 3
        assert mock_instance.idx_location == "Earth"
        assert mock_instance.idx_login == "user_login"
        assert mock_instance.idx_name == "John Doe"
        assert mock_instance.idx_public_repositories_count == 42
        assert mock_instance.idx_title == "GitHub User"
        assert mock_instance.idx_updated_at == "2021-12-31T23:59:59Z"
        assert mock_instance.idx_url == "https://api.github.com/users/user_login"
