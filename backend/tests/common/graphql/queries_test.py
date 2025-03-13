"""Test cases for BaseQuery and GraphQl Query."""

import pytest
from graphene.test import Client

from settings.graphql import schema

Expected_Recent_Issues_Releases_Distinct_TRUE_Counter = 2
Expected_Recent_Issues_Releases_Distinct_FALSE_Counter = 4


@pytest.fixture()
def client():
    return Client(schema)


def test_recent_issues_releases(client):
    query = """
    {
        recentIssuesReleases(distinct: true)
    }
    """
    result = client.execute(query)
    assert "recentIssuesReleases" in result["data"]
    assert (
        len(result["data"]["recentIssuesReleases"])
        == Expected_Recent_Issues_Releases_Distinct_TRUE_Counter
    )


def test_recent_issues_releases_without_distinct(client):
    query = """
    {
        recentIssuesReleases(distinct: false)
    }
    """
    result = client.execute(query)
    assert "recentIssuesReleases" in result["data"]
    assert (
        len(result["data"]["recentIssuesReleases"])
        == Expected_Recent_Issues_Releases_Distinct_FALSE_Counter
    )
