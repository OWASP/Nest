"""Tests for validating Nest issue Relay IDs."""

import pytest
from graphql import GraphQLError
from strawberry.relay import GlobalID

from apps.mentorship.api.internal.utils import get_issue_pk


def test_get_issue_pk():
    """Use the node's database ID rather than a GitHub issue number."""
    assert get_issue_pk(GlobalID("IssueNode", "101")) == 101


@pytest.mark.parametrize(
    "issue_id",
    [GlobalID("UserNode", "101"), GlobalID("IssueNode", "invalid")],
)
def test_get_issue_pk_invalid_id(issue_id):
    """Reject IDs of other node types and invalid database IDs."""
    with pytest.raises(GraphQLError, match="Invalid issue ID"):
        get_issue_pk(issue_id)
