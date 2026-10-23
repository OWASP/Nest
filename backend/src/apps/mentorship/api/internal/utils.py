"""Helpers for mentorship GraphQL issue identifiers."""

from graphql import GraphQLError
from strawberry.relay import GlobalID


def get_issue_pk(issue_id: GlobalID) -> int:
    """Validate a Nest issue Relay ID and return its database primary key."""
    if issue_id.type_name != "IssueNode" or not issue_id.node_id.isdecimal():
        msg = "Invalid issue ID."
        raise GraphQLError(msg)
    return int(issue_id.node_id)
