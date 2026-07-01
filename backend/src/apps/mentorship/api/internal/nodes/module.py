"""GraphQL nodes for Module model."""

from datetime import datetime

import strawberry
from asgiref.sync import sync_to_async
from strawberry.types import Info

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.issue import MERGED_PULL_REQUESTS_PREFETCH, IssueNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models import Label
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.mentor import MentorNode
from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task

MAX_LIMIT = 1000


@strawberry.type
class ModuleNode:
    """A GraphQL node representing a mentorship module."""

    # TODO (@arkid15r): migrate to decorator for consistency.

    id: strawberry.ID
    key: str
    name: str
    description: str
    domains: list[str] | None = None
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] | None = None
    order: int = 0
    program: ProgramNode | None = None
    project_id: strawberry.ID | None = None
    started_at: datetime
    tags: list[str] | None = None

    @strawberry.field
    async def mentors(self) -> list[MentorNode]:
        """Get the list of mentors for this module."""
        return [mentor async for mentor in self.mentors.all()]

    @strawberry.field
    async def mentees(self) -> list[UserNode]:
        """Get the list of mentees for this module."""
        mentee_users = (
            self.menteemodule_set.select_related("mentee__github_user")
            .filter(mentee__github_user__isnull=False)
            .values_list("mentee__github_user", flat=True)
        )

        mentee_user_ids = [user_id async for user_id in mentee_users]
        return [
            user async for user in User.objects.filter(id__in=mentee_user_ids).order_by("login")
        ]

    @strawberry.field
    async def issue_mentees(self, issue_number: int) -> list[UserNode]:
        """Return mentees assigned to this module's issue identified by its number."""
        issue_ids = [
            issue_id
            async for issue_id in self.issues.filter(number=issue_number).values_list(
                "id", flat=True
            )
        ]
        if not issue_ids:
            return []

        mentee_users = [
            mentee_user
            async for mentee_user in (
                Task.objects.filter(module=self, issue_id__in=issue_ids, assignee__isnull=False)
                .select_related("assignee")
                .values_list("assignee", flat=True)
                .distinct()
            )
        ]

        return [user async for user in User.objects.filter(id__in=mentee_users).order_by("login")]

    @strawberry.field
    async def project_name(self) -> str | None:
        """Get the project name for this module."""
        project = await sync_to_async(lambda: self.project)()
        return project.name if project else None

    @strawberry.field
    async def issues(
        self, info: Info, limit: int = 20, offset: int = 0, label: str | None = None
    ) -> list[IssueNode]:
        """Return paginated issues linked to this module, optionally filtered by label."""
        user = await info.context.request.auser()
        if not self.program or (
            not await sync_to_async(self.program.has_admin)(user)
            and not await sync_to_async(self.has_mentor)(user)
        ):
            return []

        info.context.current_module = self

        deadline_map = {}
        assigned_map = {}

        async for row in (
            Task.objects.filter(module=self, deadline_at__isnull=False)
            .order_by("issue__number", "-assigned_at")
            .values("issue__number", "deadline_at")
        ):
            num = row["issue__number"]
            if num not in deadline_map:
                deadline_map[num] = row["deadline_at"]

        async for row in (
            Task.objects.filter(module=self, assigned_at__isnull=False)
            .order_by("issue__number", "-assigned_at")
            .values("issue__number", "assigned_at")
        ):
            num = row["issue__number"]
            if num not in assigned_map:
                assigned_map[num] = row["assigned_at"]

        info.context.task_deadlines_by_issue = deadline_map
        info.context.task_assigned_at_by_issue = assigned_map
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        queryset = self.issues.select_related("repository", "author").prefetch_related(
            "assignees",
            "labels",
            MERGED_PULL_REQUESTS_PREFETCH,
        )

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        return [
            issue
            async for issue in queryset.order_by("-updated_at")[offset : offset + normalized_limit]
        ]

    @strawberry.field
    async def issues_count(self, label: str | None = None) -> int:
        """Return total count of issues linked to this module, optionally filtered by label."""
        queryset = self.issues

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        return await queryset.acount()

    @strawberry.field
    async def available_labels(self) -> list[str]:
        """Return all unique labels from issues linked to this module."""
        return sorted(
            [
                name
                async for name in (
                    Label.objects.filter(issue__mentorship_modules=self)
                    .values_list("name", flat=True)
                    .distinct()
                )
            ]
        )

    @strawberry.field
    async def issue_by_number(self, info: Info, number: int) -> IssueNode | None:
        """Return a single issue by its GitHub number within this module's linked issues."""
        user = await info.context.request.auser()
        if not self.program or (
            not await sync_to_async(self.program.has_admin)(user)
            and not await sync_to_async(self.has_mentor)(user)
        ):
            return None

        info.context.current_module = self

        return (
            await self.issues.select_related("repository", "author")
            .prefetch_related(
                "assignees",
                "labels",
                MERGED_PULL_REQUESTS_PREFETCH,
            )
            .filter(number=number)
            .afirst()
        )

    @strawberry.field
    async def interested_users(self, issue_number: int) -> list[UserNode]:
        """Return users interested in this module's issue identified by its number."""
        issue_id_list = [
            issue_id
            async for issue_id in self.issues.filter(number=issue_number).values_list(
                "id", flat=True
            )
        ]
        if not issue_id_list:
            return []

        return [
            interest.user
            async for interest in (
                IssueUserInterest.objects.select_related("user")
                .filter(module=self, issue_id__in=issue_id_list)
                .order_by("user__login")
            )
        ]

    @strawberry.field
    async def task_deadline(self, info: Info, issue_number: int) -> datetime | None:
        """Return the deadline for the latest assigned task linked to this module and issue."""
        mapping = getattr(info.context, "task_deadlines_by_issue", None)
        if mapping is not None:
            return mapping.get(issue_number)

        # fallback (single issue query)
        return (
            await Task.objects.filter(
                module=self,
                issue__number=issue_number,
                deadline_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("deadline_at", flat=True)
            .afirst()
        )

    @strawberry.field
    async def task_assigned_at(self, info: Info, issue_number: int) -> datetime | None:
        """Return the latest assignment time for tasks linked to this module and issue."""
        mapping = getattr(info.context, "task_assigned_at_by_issue", None)
        if mapping is not None:
            return mapping.get(issue_number)

        return (
            await Task.objects.filter(
                module=self,
                issue__number=issue_number,
                assigned_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("assigned_at", flat=True)
            .afirst()
        )

    @strawberry.field
    async def recent_pull_requests(self, limit: int = 4, offset: int = 0) -> list[PullRequestNode]:
        """Return recent pull requests linked to issues in this module."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        offset = max(0, offset)

        issue_ids = [issue_id async for issue_id in self.issues.values_list("id", flat=True)]
        return [
            pr
            async for pr in (
                PullRequest.objects.filter(related_issues__id__in=issue_ids)
                .select_related("author")
                .distinct()
                .order_by("-created_at")[offset : offset + normalized_limit]
            )
        ]


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
