"""Tests for validating Nest issue Relay IDs."""

import pytest
from graphql import GraphQLError
from strawberry.relay import GlobalID

from apps.mentorship.api.internal.utils import get_issue_pk


@pytest.mark.parametrize("node_id", ["101", str(2**31), str(2**63 - 1)])
def test_get_issue_pk(node_id):
    """Use the node's database ID rather than a GitHub issue number."""
    assert get_issue_pk(GlobalID("IssueNode", node_id)) == int(node_id)


@pytest.mark.parametrize(
    "issue_id",
    [
        GlobalID("UserNode", "101"),
        GlobalID("IssueNode", "invalid"),
        GlobalID("IssueNode", "-1"),
        GlobalID("IssueNode", ""),
        GlobalID("IssueNode", str(2**63)),
        GlobalID("IssueNode", "9" * 5000),
    ],
)
def test_get_issue_pk_invalid_id(issue_id):
    """Reject IDs of other node types and invalid database IDs."""
    with pytest.raises(GraphQLError, match="Invalid issue ID"):
        get_issue_pk(issue_id)
