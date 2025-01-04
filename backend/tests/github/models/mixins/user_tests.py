from apps.github.models.mixins.user import UserIndexMixin


class TestUserIndexMixin:
    AVATAR_URL = "https://avatars.githubusercontent.com/u/1"
    BIO = "Bio"
    COMPANY = "Company"
    CREATED_AT = "2021-01-01T00:00:00Z"
    EMAIL = "email@example.com"
    FOLLOWERS_COUNT = 5
    FOLLOWING_COUNT = 3
    LOCATION = "Earth"
    LOGIN = "user_login"
    NAME = "John Doe"
    PUBLIC_REPOS_COUNT = 42
    TITLE = "GitHub User"
    UPDATED_AT = "2021-12-31T23:59:59Z"
    URL = "https://api.github.com/users/user_login"

    def test_user_index(self):
        class MockModel(UserIndexMixin):
            avatar_url = TestUserIndexMixin.AVATAR_URL
            bio = TestUserIndexMixin.BIO
            company = TestUserIndexMixin.COMPANY
            created_at = TestUserIndexMixin.CREATED_AT
            email = TestUserIndexMixin.EMAIL
            followers_count = TestUserIndexMixin.FOLLOWERS_COUNT
            following_count = TestUserIndexMixin.FOLLOWING_COUNT
            location = TestUserIndexMixin.LOCATION
            login = TestUserIndexMixin.LOGIN
            name = TestUserIndexMixin.NAME
            public_repositories_count = TestUserIndexMixin.PUBLIC_REPOS_COUNT
            title = TestUserIndexMixin.TITLE
            updated_at = TestUserIndexMixin.UPDATED_AT
            url = TestUserIndexMixin.URL

        mock_instance = MockModel()

        assert mock_instance.idx_avatar_url == TestUserIndexMixin.AVATAR_URL
        assert mock_instance.idx_bio == TestUserIndexMixin.BIO
        assert mock_instance.idx_company == TestUserIndexMixin.COMPANY
        assert mock_instance.idx_created_at == TestUserIndexMixin.CREATED_AT
        assert mock_instance.idx_email == TestUserIndexMixin.EMAIL
        assert mock_instance.idx_followers_count == TestUserIndexMixin.FOLLOWERS_COUNT
        assert mock_instance.idx_following_count == TestUserIndexMixin.FOLLOWING_COUNT
        assert mock_instance.idx_location == TestUserIndexMixin.LOCATION
        assert mock_instance.idx_login == TestUserIndexMixin.LOGIN
        assert mock_instance.idx_name == TestUserIndexMixin.NAME
        assert mock_instance.idx_public_repositories_count == TestUserIndexMixin.PUBLIC_REPOS_COUNT
        assert mock_instance.idx_title == TestUserIndexMixin.TITLE
        assert mock_instance.idx_updated_at == TestUserIndexMixin.UPDATED_AT
        assert mock_instance.idx_url == TestUserIndexMixin.URL
