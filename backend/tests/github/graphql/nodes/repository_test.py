"""Test cases for RepositoryNode."""

from graphene import List

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
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

    def test_resolve_topics(self, mocker):
        field = RepositoryNode._meta.fields.get("topics")
        assert field is not None
        assert str(field.type) == "[String]"

    def test_resolve_issues(self, mocker):
        field = RepositoryNode._meta.fields.get("issues")
        assert field is not None
        assert field.type == List(IssueNode)

    def test_resolve_releases(self, mocker):
        field = RepositoryNode._meta.fields.get("releases")
        assert field is not None
        assert field.type == List(ReleaseNode)

    def test_resolve_top_contributors(self, mocker):
        field = RepositoryNode._meta.fields.get("top_contributors")
        assert field is not None
        assert str(field.type) == "[RepositoryContributorNode]"

    def test_resolve_url(self, mocker):
        url = RepositoryNode._meta.fields.get("url")
        assert url is not None
        assert str(url.type) == "String"
