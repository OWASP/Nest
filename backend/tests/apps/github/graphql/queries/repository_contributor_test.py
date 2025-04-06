from unittest.mock import MagicMock, patch

import pytest

from apps.github.graphql.queries.repository_contributor import RepositoryContributorQuery

top_contributors_limit = 2
custom_limit = 1
graphql_query_limit = 2
user2_contributions = 120
user1_contributions = 100
user2_login = "user2"
user1_login = "user1"
user2_name = "User Two"
user1_name = "User One"
user2_avatar_url = "https://example.com/avatar2.jpg"
user1_avatar_url = "https://example.com/avatar1.jpg"
user2_project_name = "Project Beta"
user1_project_name = "Project Alpha"
user2_project_url = "beta"
user1_project_url = "alpha"


@pytest.fixture
def mock_contributor_data():
    return [
        {
            "contributions_count": user2_contributions,
            "user__avatar_url": user2_avatar_url,
            "user__login": user2_login,
            "user__name": user2_name,
            "project_name": user2_project_name,
            "project_url": user2_project_url,
        },
        {
            "contributions_count": user1_contributions,
            "user__avatar_url": user1_avatar_url,
            "user__login": user1_login,
            "user__name": user1_name,
            "project_name": user1_project_name,
            "project_url": user1_project_url,
        },
    ]


def test_resolve_top_contributors(mock_contributor_data):
    query = RepositoryContributorQuery()

    with patch(
        "apps.github.models.repository_contributor.RepositoryContributor.objects"
    ) as mock_manager:
        mock_qs = MagicMock()
        mock_manager.by_humans.return_value = mock_qs
        mock_qs.to_community_repositories.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_contributor_data

        result = query.resolve_top_contributors(None, 15)

        assert len(result) == top_contributors_limit
        assert result[0].login == user2_login
        assert result[0].contributions_count == user2_contributions
        assert result[0].project_name == user2_project_name
        assert result[0].project_url == user2_project_url

        assert result[1].login == user1_login
        assert result[1].contributions_count == user1_contributions
        assert result[1].project_name == user1_project_name
        assert result[1].project_url == user1_project_url


def test_resolve_top_contributors_with_limit(mock_contributor_data):
    query = RepositoryContributorQuery()

    with patch(
        "apps.github.models.repository_contributor.RepositoryContributor.objects"
    ) as mock_manager:
        mock_qs = MagicMock()
        mock_manager.by_humans.return_value = mock_qs
        mock_qs.to_community_repositories.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_contributor_data[:custom_limit]

        result = query.resolve_top_contributors(None, custom_limit)

        assert len(result) == custom_limit
        assert result[0].login == user2_login
        assert result[0].contributions_count == user2_contributions


def test_top_contributors_graphql_query():
    query_result = {
        "data": {
            "topContributors": [
                {
                    "login": user2_login,
                    "name": user2_name,
                    "avatarUrl": user2_avatar_url,
                    "contributionsCount": user2_contributions,
                    "projectName": user2_project_name,
                    "projectUrl": user2_project_url,
                },
                {
                    "login": user1_login,
                    "name": user1_name,
                    "avatarUrl": user1_avatar_url,
                    "contributionsCount": user1_contributions,
                    "projectName": user1_project_name,
                    "projectUrl": user1_project_url,
                },
            ]
        }
    }

    mock_client = MagicMock()
    mock_client.execute.return_value = query_result

    with patch("graphene.test.Client", return_value=mock_client):
        from graphene.test import Client

        client = Client(MagicMock())

        executed = client.execute(
            f"""
            query {{
              topContributors(limit: {graphql_query_limit}) {{
                login
                name
                avatarUrl
                contributionsCount
                projectName
                projectUrl
              }}
            }}
            """
        )

        assert "errors" not in executed
        assert len(executed["data"]["topContributors"]) == top_contributors_limit
        assert executed["data"]["topContributors"][0]["login"] == user2_login
        assert executed["data"]["topContributors"][0]["contributionsCount"] == user2_contributions
        assert executed["data"]["topContributors"][1]["login"] == user1_login
        assert executed["data"]["topContributors"][1]["contributionsCount"] == user1_contributions
