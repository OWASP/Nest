from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from apps.github.graphql.queries.release import ReleaseQuery

default_limit = 15
custom_limit = 3
graphql_limit = 2


@pytest.fixture
def releases_setup():
    dates = [
        datetime(2023, 5, 1, tzinfo=timezone.utc),
        datetime(2023, 4, 1, tzinfo=timezone.utc),
        datetime(2023, 3, 1, tzinfo=timezone.utc),
        datetime(2023, 2, 1, tzinfo=timezone.utc),
        datetime(2023, 1, 1, tzinfo=timezone.utc),
    ]

    mock_releases = []
    for i, date in enumerate(dates):
        mock_release = MagicMock()
        mock_release.name = f"Release {i + 1}"
        mock_release.tag_name = f"v1.{i}"
        mock_release.created_at = date
        mock_releases.append(mock_release)

    return mock_releases


def test_resolve_recent_releases(releases_setup):
    """Test the resolve_recent_releases method with default limit."""
    query = ReleaseQuery()

    with patch("apps.github.models.release.Release.objects") as mock_objects:
        mock_objects.order_by.return_value = releases_setup
        result = query.resolve_recent_releases(None, default_limit)

        mock_objects.order_by.assert_called_once_with("-created_at")
        assert list(result) == releases_setup
        assert len(result) == len(releases_setup)


def test_resolve_recent_releases_with_limit(releases_setup):
    """Test the resolve_recent_releases method with custom limit."""
    query = ReleaseQuery()

    with patch("apps.github.models.release.Release.objects") as mock_objects:
        mock_queryset = MagicMock()
        mock_queryset.__getitem__.return_value = releases_setup[:custom_limit]
        mock_objects.order_by.return_value = mock_queryset

        result = query.resolve_recent_releases(None, custom_limit)

        mock_objects.order_by.assert_called_once_with("-created_at")
        mock_queryset.__getitem__.assert_called_once_with(slice(None, custom_limit))
        assert list(result) == releases_setup[:custom_limit]
        assert len(result) == custom_limit


def test_recent_releases_graphql_query(releases_setup):
    """Test the recent_releases GraphQL query."""
    query_result = {
        "data": {
            "recentReleases": [
                {"name": releases_setup[0].name, "tagName": releases_setup[0].tag_name},
                {"name": releases_setup[1].name, "tagName": releases_setup[1].tag_name},
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
              recentReleases(limit: {graphql_limit}) {{
                name
                tagName
              }}
            }}
            """
        )

        assert "errors" not in executed
        assert len(executed["data"]["recentReleases"]) == graphql_limit
        assert executed["data"]["recentReleases"][0]["name"] == releases_setup[0].name
        assert executed["data"]["recentReleases"][0]["tagName"] == releases_setup[0].tag_name
