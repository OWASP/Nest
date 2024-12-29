from apps.github.models.mixins.user import UserIndexMixin


class TestUserIndexMixin:
    def test_idx_avatar_url(self):
        class MockModel(UserIndexMixin):
            avatar_url = "https://avatars.githubusercontent.com/u/1"

        mock_instance = MockModel()
        assert mock_instance.idx_avatar_url == "https://avatars.githubusercontent.com/u/1"

    def test_idx_bio(self):
        class MockModel(UserIndexMixin):
            bio = "Bio"

        mock_instance = MockModel()
        assert mock_instance.idx_bio == "Bio"

    def test_idx_company(self):
        class MockModel(UserIndexMixin):
            company = "Company"

        mock_instance = MockModel()
        assert mock_instance.idx_company == "Company"

    def test_idx_created_at(self):
        class MockModel(UserIndexMixin):
            created_at = "2021-01-01T00:00:00Z"

        mock_instance = MockModel()
        assert mock_instance.idx_created_at == "2021-01-01T00:00:00Z"

    def test_idx_email(self):
        class MockModel(UserIndexMixin):
            email = "email@example.com"

        mock_instance = MockModel()
        assert mock_instance.idx_email == "email@example.com"

    def test_idx_followers_count(self):
        default_value = 5

        class MockModel(UserIndexMixin):
            followers_count = default_value

        mock_instance = MockModel()
        assert mock_instance.idx_followers_count == default_value

    def test_idx_following_count(self):
        default_follow_count = 3

        class MockModel(UserIndexMixin):
            following_count = default_follow_count

        mock_instance = MockModel()
        assert mock_instance.idx_following_count == default_follow_count

    def test_idx_location(self):
        class MockModel(UserIndexMixin):
            location = "Earth"

        mock_instance = MockModel()
        assert mock_instance.idx_location == "Earth"

    def test_idx_login(self):
        class MockModel(UserIndexMixin):
            login = "user_login"

        mock_instance = MockModel()
        assert mock_instance.idx_login == "user_login"

    def test_idx_name(self):
        class MockModel(UserIndexMixin):
            name = "John Doe"

        mock_instance = MockModel()
        assert mock_instance.idx_name == "John Doe"

    def test_idx_public_repositories_count(self):
        default_repo_count = 42

        class MockModel(UserIndexMixin):
            public_repositories_count = default_repo_count

        mock_instance = MockModel()
        assert mock_instance.idx_public_repositories_count == default_repo_count

    def test_idx_title(self):
        class MockModel(UserIndexMixin):
            title = "GitHub User"

        mock_instance = MockModel()
        assert mock_instance.idx_title == "GitHub User"

    def test_idx_updated_at(self):
        class MockModel(UserIndexMixin):
            updated_at = "2021-12-31T23:59:59Z"

        mock_instance = MockModel()
        assert mock_instance.idx_updated_at == "2021-12-31T23:59:59Z"

    def test_idx_url(self):
        class MockModel(UserIndexMixin):
            url = "https://api.github.com/users/user_login"

        mock_instance = MockModel()
        assert mock_instance.idx_url == "https://api.github.com/users/user_login"
