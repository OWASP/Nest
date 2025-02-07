from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.mixins.user import UserIndexMixin
from apps.github.models.user import User


@pytest.fixture()
def user_index_mixin_instance():
    instance = UserIndexMixin()
    instance.avatar_url = "https://example.com/avatar.png"
    instance.bio = "Developer bio"
    instance.company = "Test Company"
    instance.created_at = datetime(2021, 1, 1, tzinfo=timezone.utc)
    instance.email = "test@example.com"
    instance.login = "test_user"
    instance.followers_count = 100
    instance.following_count = 50
    instance.location = "Test Location"
    instance.name = "Test User"
    instance.public_repositories_count = 10
    instance.title = "Developer"
    instance.url = "https://github.com/test_user"
    instance.updated_at = datetime(2021, 1, 2, tzinfo=timezone.utc)

    instance.issues = MagicMock()
    instance.issues.select_related.return_value.order_by.return_value = [
        MagicMock(
            created_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
            comments_count=5,
            number=1,
            repository=MagicMock(
                key="repo_key",
                owner=MagicMock(login="owner_login"),
            ),
            title="Issue Title",
        )
    ]
    instance.issues.count.return_value = 5

    instance.releases = MagicMock()
    instance.releases.select_related.return_value.order_by.return_value = [
        MagicMock(
            is_pre_release=False,
            name="Release Name",
            published_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
            repository=MagicMock(
                key="repo_key",
                owner=MagicMock(login="owner_login"),
            ),
            tag_name="v1.0.0",
        )
    ]
    instance.releases.count.return_value = 3
    return instance


class TestUserIndexMixin:
    @pytest.mark.parametrize(
        ("login", "expected_indexable"),
        [
            ("john-doe", True),
            ("jane-doe", True),
            ("ghost", False),
        ],
    )
    @patch(
        "apps.github.models.organization.Organization.get_logins", return_value=["org1", "org2"]
    )
    def test_is_indexable(self, mock_get_logins, login, expected_indexable):
        user = User(login=login)
        assert user.is_indexable == expected_indexable

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_avatar_url", "https://example.com/avatar.png"),
            ("idx_bio", "Developer bio"),
            ("idx_company", "Test Company"),
            ("idx_created_at", datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp()),
            ("idx_email", "test@example.com"),
            ("idx_key", "test_user"),
            ("idx_followers_count", 100),
            ("idx_following_count", 50),
            ("idx_location", "Test Location"),
            ("idx_login", "test_user"),
            ("idx_name", "Test User"),
            ("idx_public_repositories_count", 10),
            ("idx_title", "Developer"),
            ("idx_url", "https://github.com/test_user"),
            ("idx_updated_at", datetime(2021, 1, 2, tzinfo=timezone.utc).timestamp()),
            (
                "idx_issues",
                [
                    {
                        "created_at": datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp(),
                        "comments_count": 5,
                        "number": 1,
                        "repository": {"key": "repo_key", "owner_key": "owner_login"},
                        "title": "Issue Title",
                    }
                ],
            ),
            ("idx_issues_count", 5),
            ("idx_releases_count", 3),
        ],
    )
    def test_user_index_fields(self, user_index_mixin_instance, attr, expected):
        assert getattr(user_index_mixin_instance, attr) == expected
