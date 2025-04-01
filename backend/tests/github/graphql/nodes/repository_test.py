"""Test cases for RepositoryNode."""

from unittest.mock import MagicMock

from graphene import List

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import (
    RECENT_ISSUES_LIMIT,
    RECENT_RELEASES_LIMIT,
    RepositoryNode,
)
from apps.github.models.repository import Repository


class TestRepositoryNode:
    def test_repository_node_inheritance(self):
        assert issubclass(RepositoryNode, BaseNode)

    def test_meta_configuration(self):
        assert RepositoryNode._meta.model == Repository
        expected_fields = {
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "issues",
            "key",
            "languages",
            "license",
            "name",
            "open_issues_count",
            "owner_key",
            "latest_release",
            "releases",
            "size",
            "stars_count",
            "subscribers_count",
            "top_contributors",
            "topics",
            "updated_at",
            "url",
        }
        assert set(RepositoryNode._meta.fields) == expected_fields

    def test_resolve_languages(self, mocker):
        field = RepositoryNode._meta.fields.get("languages")
        assert field is not None
        assert str(field.type) == "[String]"

        node = RepositoryNode(MagicMock())

        node.languages = {"Python": 10000, "JavaScript": 5000}

        result = node.resolve_languages(None)

        assert sorted(result) == sorted(["Python", "JavaScript"])

    def test_resolve_topics(self, mocker):
        field = RepositoryNode._meta.fields.get("topics")
        assert field is not None
        assert str(field.type) == "[String]"

        node = RepositoryNode(MagicMock())

        node.topics = ["python", "django", "graphql"]

        result = node.resolve_topics(None)
        assert result == ["python", "django", "graphql"]

    def test_resolve_issues(self, mocker):
        field = RepositoryNode._meta.fields.get("issues")
        assert field is not None
        assert field.type == List(IssueNode)

        node = RepositoryNode(MagicMock())

        mock_issues = MagicMock()
        mock_select_related = MagicMock()
        mock_order_by = MagicMock()

        mock_issues.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = ["issue1", "issue2"]

        node.issues = mock_issues

        result = node.resolve_issues(None)

        mock_issues.select_related.assert_called_once_with("author")
        mock_select_related.order_by.assert_called_once_with("-created_at")
        mock_order_by.__getitem__.assert_called_once_with(slice(None, RECENT_ISSUES_LIMIT))
        assert result == ["issue1", "issue2"]

    def test_resolve_releases(self, mocker):
        field = RepositoryNode._meta.fields.get("releases")
        assert field is not None
        assert field.type == List(ReleaseNode)

        node = RepositoryNode(MagicMock())

        mock_published_releases = MagicMock()
        mock_order_by = MagicMock()

        mock_published_releases.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = ["release1", "release2"]

        node.published_releases = mock_published_releases

        result = node.resolve_releases(None)

        mock_published_releases.order_by.assert_called_once_with("-published_at")
        mock_order_by.__getitem__.assert_called_once_with(slice(None, RECENT_RELEASES_LIMIT))
        assert result == ["release1", "release2"]

    def test_resolve_top_contributors(self, mocker):
        field = RepositoryNode._meta.fields.get("top_contributors")
        assert field is not None
        assert str(field.type) == "[RepositoryContributorNode]"

        node = RepositoryNode(MagicMock())

        node.idx_top_contributors = ["contributor1", "contributor2"]

        result = node.resolve_top_contributors(None)

        assert result == ["contributor1", "contributor2"]

    def test_resolve_url(self, mocker):
        url = RepositoryNode._meta.fields.get("url")
        assert url is not None
        assert str(url.type) == "String"

        node = RepositoryNode(MagicMock())

        node.url = "https://github.com/example/repo"

        result = node.resolve_url(None)

        assert result == "https://github.com/example/repo"

    def test_resolve_latest_release(self, mocker):
        field = RepositoryNode._meta.fields.get("latest_release")
        assert field is not None
        assert str(field.type) == "String"

        node = RepositoryNode(MagicMock())

        node.latest_release = "v1.0.0"

        result = node.resolve_latest_release(None)

        assert result == "v1.0.0"

    def test_resolve_owner_key(self, mocker):
        field = RepositoryNode._meta.fields.get("owner_key")
        assert field is not None
        assert str(field.type) == "String"

        node = RepositoryNode(MagicMock())

        node.owner_key = "owner123"

        result = node.resolve_owner_key(None)

        assert result == "owner123"
