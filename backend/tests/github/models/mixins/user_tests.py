from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from apps.github.models.mixins.user import UserIndexMixin


class MockModel(UserIndexMixin):
    def __init__(self):
        self.avatar_url = "https://example.com/avatar.png"
        self.bio = "Developer bio"
        self.company = "Test Company"
        self.created_at = datetime(2021, 1, 1, tzinfo=timezone.utc)
        self.email = "test@example.com"
        self.login = "test_user"
        self.followers_count = 100
        self.following_count = 50
        self.location = "Test Location"
        self.name = "Test User"
        self.public_repositories_count = 10
        self.title = "Developer"
        self.url = "https://github.com/test_user"
        self.updated_at = datetime(2021, 1, 2, tzinfo=timezone.utc)

        self.issues = MagicMock()
        self.issues.select_related.return_value.order_by.return_value = [
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
        self.issues.count.return_value = 5

        self.releases = MagicMock()
        self.releases.select_related.return_value.order_by.return_value = [
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
        self.releases.count.return_value = 3


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
def test_user_index_fields(attr, expected):
    mock_instance = MockModel()
    assert getattr(mock_instance, attr) == expected
