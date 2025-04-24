"""Github Milestone Node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.milestone import Milestone
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.pull_request import PullRequestNode




class MilestoneNode(BaseNode):
    """Github Milestone Node."""

    issues = graphene.List(IssueNode)
    pull_requests = graphene.List(PullRequestNode)
    
    class Meta:
        model = Milestone

        fields = (
            "author",
            "created_at",
            "state",
            "title",
            "open_issues_count",
            "closed_issues_count",
            "due_on",
            "repository",
            "issues",
            "pull_requests",
        )

    
    def resolve_issues(self, info):
        """Resolve issues."""
        return self.issues.all()
    
    def resolve_pull_requests(self, info):
        """Resolve pull requests."""
        return self.pull_requests.all()
