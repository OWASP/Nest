"""GraphQL nodes for Module model."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.issue import (
    MERGED_PULL_REQUESTS_PREFETCH,
    IssueNode,
)
from apps.github.api.internal.nodes.pull_request import PullRequestNode  # noqa: TC001
from apps.github.api.internal.nodes.user import UserNode  # noqa: TC001
from apps.github.models import Label
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum  # noqa: TC001
from apps.mentorship.api.internal.nodes.mentor import MentorNode  # noqa: TC001
from apps.mentorship.api.internal.nodes.program import ProgramNode  # noqa: TC001
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.module import Module
from apps.mentorship.models.task import Task

# TC001/TC003: These imports must stay at runtime. Strawberry GraphQL introspects
# type annotations when building the schema; moving them under TYPE_CHECKING would
# cause UnresolvedFieldTypeError at startup.

MAX_LIMIT = 1000


@strawberry_django.type(
    Module,
    fields=[
        "description",
        "domains",
        "ended_at",
        "experience_level",
        "id",
        "key",
        "labels",
        "name",
        "order",
        "started_at",
        "tags",
    ],
)
class ModuleNode:
    """A GraphQL node representing a mentorship module."""

    @strawberry_django.field
    def program(self, root: Module) -> ProgramNode | None:
        """Get the program for this module."""
        return root.program

    @strawberry_django.field
    def project_id(self, root: Module) -> strawberry.ID | None:
        """Get the project ID for this module."""
        return root.project_id

    @strawberry_django.field
    def project_name(self, root: Module) -> str | None:
        """Get the project name for this module."""
        return root.project.name if root.project else None

    @strawberry_django.field
    def mentors(self, root: Module) -> list[MentorNode]:
        """Get the list of mentors for this module."""
        return root.mentors.all()

    @strawberry_django.field
    def mentees(self, root: Module) -> list[UserNode]:
        """Get the list of mentees for this module."""
        mentee_users = (
            root.menteemodule_set.select_related("mentee__github_user")
            .filter(mentee__github_user__isnull=False)
            .values_list("mentee__github_user", flat=True)
        )

        return list(User.objects.filter(id__in=mentee_users).order_by("login"))

    @strawberry_django.field
    def issue_mentees(self, root: Module, issue_number: int) -> list[UserNode]:
        """Return mentees assigned to this module's issue identified by its number."""
        issue_ids = root.issues.filter(number=issue_number).values_list("id", flat=True)
        mentee_users = (
            Task.objects.filter(module=root, issue_id__in=issue_ids, assignee__isnull=False)
            .select_related("assignee")
            .values_list("assignee", flat=True)
            .distinct()
        )
        return list(User.objects.filter(id__in=mentee_users).order_by("login"))

    @strawberry_django.field
    def issues(
        self, root: Module, info: Info, limit: int = 20, offset: int = 0, label: str | None = None
    ) -> list[IssueNode]:
        """Return paginated issues linked to this module, optionally filtered by label."""
        info.context.current_module = root

        # BULK load data
        deadline_rows = (
            Task.objects.filter(module=root, deadline_at__isnull=False)
            .order_by("issue__number", "-assigned_at")
            .values("issue__number", "deadline_at")
        )
        assigned_rows = (
            Task.objects.filter(module=root, assigned_at__isnull=False)
            .order_by("issue__number", "-assigned_at")
            .values("issue__number", "assigned_at")
        )

        deadline_map = {}
        assigned_map = {}

        for row in deadline_rows:
            num = row["issue__number"]
            if num not in deadline_map:
                deadline_map[num] = row["deadline_at"]
        for row in assigned_rows:
            num = row["issue__number"]
            if num not in assigned_map:
                assigned_map[num] = row["assigned_at"]

        info.context.task_deadlines_by_issue = deadline_map
        info.context.task_assigned_at_by_issue = assigned_map
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        queryset = root.issues.select_related("repository", "author").prefetch_related(
            "assignees",
            "labels",
            MERGED_PULL_REQUESTS_PREFETCH,
        )

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        return list(queryset.order_by("-updated_at")[offset : offset + normalized_limit])

    @strawberry_django.field
    def issues_count(self, root: Module, label: str | None = None) -> int:
        """Return total count of issues linked to this module, optionally filtered by label."""
        queryset = root.issues
        if label and label != "all":
            queryset = queryset.filter(labels__name=label)
        return queryset.count()

    @strawberry_django.field
    def available_labels(self, root: Module) -> list[str]:
        """Return all unique labels from issues linked to this module."""
        label_names = (
            Label.objects.filter(issue__mentorship_modules=root)
            .values_list("name", flat=True)
            .distinct()
        )

        return sorted(label_names)

    @strawberry_django.field
    def issue_by_number(self, root: Module, info: Info, number: int) -> IssueNode | None:
        """Return a single issue by its GitHub number within this module's linked issues."""
        info.context.current_module = root

        return (
            root.issues.select_related("repository", "author")
            .prefetch_related(
                "assignees",
                "labels",
                MERGED_PULL_REQUESTS_PREFETCH,
            )
            .filter(number=number)
            .first()
        )

    @strawberry_django.field
    def interested_users(self, root: Module, issue_number: int) -> list[UserNode]:
        """Return users interested in this module's issue identified by its number."""
        return [
            issue_user_interest.user
            for issue_user_interest in IssueUserInterest.objects.select_related("user")
            .filter(
                module=root,
                issue_id__in=root.issues.filter(number=issue_number).values_list("id", flat=True),
            )
            .order_by("user", "user__login")
            .distinct("user")
        ]

    @strawberry_django.field
    def task_deadline(self, root: Module, info: Info, issue_number: int) -> datetime | None:
        """Return the deadline for the latest assigned task linked to this module and issue."""
        mapping = getattr(info.context, "task_deadlines_by_issue", None)
        if mapping is not None:
            return mapping.get(issue_number)

        # fallback (single issue query)
        return (
            Task.objects.filter(
                module=root,
                issue__number=issue_number,
                deadline_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("deadline_at", flat=True)
            .first()
        )

    @strawberry_django.field
    def task_assigned_at(self, root: Module, info: Info, issue_number: int) -> datetime | None:
        """Return the latest assignment time for tasks linked to this module and issue."""
        mapping = getattr(info.context, "task_assigned_at_by_issue", None)
        if mapping is not None:
            return mapping.get(issue_number)

        return (
            Task.objects.filter(
                module=root,
                issue__number=issue_number,
                assigned_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("assigned_at", flat=True)
            .first()
        )

    @strawberry_django.field
    def recent_pull_requests(self, root: Module, limit: int = 5) -> list[PullRequestNode]:
        """Return recent pull requests linked to issues in this module."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return list(
            PullRequest.objects.filter(
                related_issues__id__in=root.issues.values_list("id", flat=True)
            )
            .select_related("author")
            .distinct()
            .order_by("-created_at")[:normalized_limit]
        )


@strawberry.input
class CreateModuleInput:
    """Input for creating a mentorship module."""

    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] = strawberry.field(default_factory=list)
    mentor_logins: list[str] | None = None
    program_key: str
    project_name: str
    project_id: strawberry.ID
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateModuleInput:
    """Input for updating a mentorship module."""

    key: str
    program_key: str
    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] = strawberry.field(default_factory=list)
    mentor_logins: list[str] | None = None
    project_id: strawberry.ID
    project_name: str
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class ReorderModulesInput:
    """Input for reordering modules within a program."""

    program_key: str
    module_keys: list[str]
