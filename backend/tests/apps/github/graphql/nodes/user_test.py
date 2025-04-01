"""Test cases for UserNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import IssueType, ReleaseType, RepositoryType, UserNode
from apps.github.models.user import User

created_at_timestamp = 1629462000.0
updated_at_timestamp = 1629465600.0
github_url = "https://github.com/testuser"
issues_count = 10
releases_count = 5
comments_count_issue_1 = 5
comments_count_issue_2 = 3
issue_number_1 = 1
issue_number_2 = 2
release_name_1 = "Release 1.0"
release_name_2 = "Beta 1.1"
release_tag_1 = "v1.0"
release_tag_2 = "v1.1-beta"


class TestUserNode:
    """Test cases for UserNode class."""

    def test_user_node_inheritance(self):
        """Test if UserNode inherits from BaseNode."""
        assert issubclass(UserNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert UserNode._meta.model == User
        expected_fields = {
            "avatar_url",
            "bio",
            "company",
            "contributions_count",
            "created_at",
            "email",
            "followers_count",
            "following_count",
            "id",
            "issues_count",
            "location",
            "login",
            "name",
            "public_repositories_count",
            "releases_count",
            "updated_at",
            "url",
        }
        assert set(UserNode._meta.fields) == expected_fields

    def test_resolve_created_at(self):
        """Test resolve_created_at method."""
        user_node = UserNode()
        user_node.idx_created_at = created_at_timestamp

        result = user_node.resolve_created_at(None)

        assert result == created_at_timestamp

    def test_resolve_updated_at(self):
        """Test resolve_updated_at method."""
        user_node = UserNode()
        user_node.idx_updated_at = updated_at_timestamp

        result = user_node.resolve_updated_at(None)

        assert result == updated_at_timestamp

    def test_resolve_url(self):
        """Test resolve_url method."""
        user_node = UserNode()
        user_node.url = github_url

        result = user_node.resolve_url(None)

        assert result == github_url

    def test_resolve_issues(self):
        """Test resolve_issues method."""
        user_node = UserNode()
        mock_issues = [
            {
                "created_at": created_at_timestamp,
                "comments_count": comments_count_issue_1,
                "number": issue_number_1,
                "repository": {"key": "repo1", "owner_key": "owner1"},
                "title": "Issue 1",
            },
            {
                "created_at": updated_at_timestamp,
                "comments_count": comments_count_issue_2,
                "number": issue_number_2,
                "repository": {"key": "repo1", "owner_key": "owner1"},
                "title": "Issue 2",
            },
        ]
        user_node.idx_issues = mock_issues

        result = user_node.resolve_issues(None)

        assert result == mock_issues

    def test_resolve_issues_count(self):
        """Test resolve_issues_count method."""
        user_node = UserNode()
        user_node.idx_issues_count = issues_count

        result = user_node.resolve_issues_count(None)

        assert result == issues_count

    def test_resolve_releases(self):
        """Test resolve_releases method."""
        user_node = UserNode()
        mock_releases = [
            {
                "is_pre_release": False,
                "name": release_name_1,
                "published_at": created_at_timestamp,
                "repository": {"key": "repo1", "owner_key": "owner1"},
                "tag_name": release_tag_1,
            },
            {
                "is_pre_release": True,
                "name": release_name_2,
                "published_at": updated_at_timestamp,
                "repository": {"key": "repo1", "owner_key": "owner1"},
                "tag_name": release_tag_2,
            },
        ]
        user_node.idx_releases = mock_releases

        result = user_node.resolve_releases(None)

        assert result == mock_releases

    def test_resolve_releases_count(self):
        """Test resolve_releases_count method."""
        user_node = UserNode()
        user_node.idx_releases_count = releases_count

        result = user_node.resolve_releases_count(None)

        assert result == releases_count

    def test_repository_type(self):
        """Test RepositoryType class."""
        repo = RepositoryType(key="repo1", owner_key="owner1")
        assert repo.key == "repo1"
        assert repo.owner_key == "owner1"

    def test_issue_type(self):
        """Test IssueType class."""
        repo = RepositoryType(key="repo1", owner_key="owner1")
        issue = IssueType(
            created_at=created_at_timestamp,
            comments_count=comments_count_issue_1,
            number=issue_number_1,
            repository=repo,
            title="Test Issue",
        )
        assert issue.created_at == created_at_timestamp
        assert issue.comments_count == comments_count_issue_1
        assert issue.number == issue_number_1
        assert issue.repository == repo
        assert issue.title == "Test Issue"

    def test_release_type(self):
        """Test ReleaseType class."""
        repo = RepositoryType(key="repo1", owner_key="owner1")
        release = ReleaseType(
            is_pre_release=False,
            name=release_name_1,
            published_at=created_at_timestamp,
            repository=repo,
            tag_name=release_tag_1,
        )
        assert release.is_pre_release is False
        assert release.name == release_name_1
        assert release.published_at == created_at_timestamp
        assert release.repository == repo
        assert release.tag_name == release_tag_1
