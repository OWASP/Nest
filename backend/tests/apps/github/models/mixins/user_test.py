from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.mixins.user import UserIndexMixin
from apps.github.models.user import User


@pytest.fixture
def user_index_mixin_instance():
    instance = UserIndexMixin()
    instance.avatar_url = "https://example.com/avatar.png"
    instance.bio = "Developer bio"
    instance.company = "Test Company"
    instance.created_at = datetime(2021, 1, 1, tzinfo=UTC)
    instance.email = "test@example.com"
    instance.login = "test_user"
    instance.followers_count = 100
    instance.following_count = 50
    instance.location = "Test Location"
    instance.name = "Test User"
    instance.public_repositories_count = 10
    instance.title = "Developer"
    instance.url = "https://github.com/test_user"
    instance.updated_at = datetime(2021, 1, 2, tzinfo=UTC)

    instance.issues = MagicMock()
    instance.issues.select_related.return_value.order_by.return_value = [
        MagicMock(
            created_at=datetime(2021, 1, 1, tzinfo=UTC),
            comments_count=5,
            number=1,
            repository=MagicMock(
                key="repo_key",
                owner=MagicMock(login="owner_login"),
            ),
            title="Issue Title",
            url="https://example.com/issue/1",
        )
    ]
    instance.issues.count.return_value = 5

    instance.releases = MagicMock()
    instance.releases.select_related.return_value.order_by.return_value = [
        MagicMock(
            is_pre_release=False,
            name="Release Name",
            published_at=datetime(2021, 1, 1, tzinfo=UTC),
            repository=MagicMock(
                key="repo_key",
                owner=MagicMock(login="owner_login"),
            ),
            tag_name="v1.0.0",
        )
    ]
    instance.releases.count.return_value = 3

    instance.user_badges = MagicMock()
    instance.user_badges.filter.return_value.count.return_value = 2

    instance.contributions_count = 150

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
            ("idx_created_at", datetime(2021, 1, 1, tzinfo=UTC).timestamp()),
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
            ("idx_updated_at", datetime(2021, 1, 2, tzinfo=UTC).timestamp()),
            (
                "idx_issues",
                [
                    {
                        "created_at": datetime(2021, 1, 1, tzinfo=UTC).timestamp(),
                        "comments_count": 5,
                        "number": 1,
                        "repository": {"key": "repo_key", "owner_key": "owner_login"},
                        "title": "Issue Title",
                        "url": "https://example.com/issue/1",
                    }
                ],
            ),
            ("idx_issues_count", 5),
            ("idx_contributions_count", 150),
            ("idx_releases_count", 3),
        ],
    )
    def test_user_index_fields(self, user_index_mixin_instance, attr, expected):
        assert getattr(user_index_mixin_instance, attr) == expected

    def test_idx_badge_count(self, user_index_mixin_instance):
        """Test idx_badge_count property."""
        assert user_index_mixin_instance.idx_badge_count == 2
        user_index_mixin_instance.user_badges.filter.assert_called_once_with(is_active=True)

    def test_idx_releases_with_owner_key(self, user_index_mixin_instance):
        """Test idx_releases includes owner_key in repository dict."""
        releases = user_index_mixin_instance.idx_releases
        assert len(releases) == 1
        assert releases[0]["repository"]["owner_key"] == "owner_login"

    def test_idx_releases_with_tag_name(self):
        """Test idx_releases includes tag_name in release dict."""
        from apps.github.models.mixins.user import UserIndexMixin

        instance = UserIndexMixin()

        mock_release = MagicMock()
        mock_release.is_pre_release = False
        mock_release.name = "Release Name"
        mock_release.published_at = datetime(2021, 1, 1, tzinfo=UTC)
        mock_release.tag_name = "v1.0.0"
        mock_release.repository.key = "repo_key"
        mock_release.repository.owner.login = "owner_login"

        instance.releases = MagicMock()
        instance.releases.select_related.return_value.order_by.return_value = [mock_release]

        releases = instance.idx_releases
        assert len(releases) == 1
        assert releases[0]["tag_name"] == "v1.0.0"

    def test_idx_contributions_with_and_without_latest_release(self):
        """Test idx_contributions with latest_release truthy and None."""
        instance = UserIndexMixin()
        instance.get_non_indexable_logins = MagicMock(return_value=set())

        rc_with_release = MagicMock()
        rc_with_release.contributions_count = 10
        rc_with_release.repository.contributors_count = 5
        rc_with_release.repository.description = "Test repo"
        rc_with_release.repository.forks_count = 3
        rc_with_release.repository.key = "Test-Repo"
        rc_with_release.repository.name = "test-repo"
        rc_with_release.repository.latest_release = MagicMock(summary="v1.0 release")
        rc_with_release.repository.license = "MIT"
        rc_with_release.repository.owner.login = "Test-Owner"
        rc_with_release.repository.stars_count = 50

        rc_without_release = MagicMock()
        rc_without_release.contributions_count = 5
        rc_without_release.repository.contributors_count = 3
        rc_without_release.repository.description = "Another repo"
        rc_without_release.repository.forks_count = 1
        rc_without_release.repository.key = "Other-Repo"
        rc_without_release.repository.name = "other-repo"
        rc_without_release.repository.latest_release = None
        rc_without_release.repository.license = "Apache-2.0"
        rc_without_release.repository.owner.login = "Other-Owner"
        rc_without_release.repository.stars_count = 10

        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects"
        ) as mock_objects:
            mock_qs = mock_objects.filter.return_value
            mock_qs.exclude.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_qs.select_related.return_value.__getitem__.return_value = [
                rc_with_release,
                rc_without_release,
            ]

            contributions = instance.idx_contributions

        assert len(contributions) == 2
        assert contributions[0]["repository_latest_release"] == "v1.0 release"
        assert contributions[0]["repository_key"] == "test-repo"
        assert contributions[0]["repository_owner_key"] == "test-owner"
        assert contributions[1]["repository_latest_release"] == ""
        assert contributions[1]["repository_key"] == "other-repo"
