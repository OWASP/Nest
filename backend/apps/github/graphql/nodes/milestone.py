"""Github Milestone Node."""

from apps.common.graphql.nodes import BaseNode
from apps.github.models.milestone import Milestone


class MilestoneNode(BaseNode):
    """Github Milestone Node."""

    class Meta:
        model = Milestone

        fields = (
            "author",
            "created_at",
            "state",
            "title",
            "open_issues_count",
            "closed_issues_count",
        )
