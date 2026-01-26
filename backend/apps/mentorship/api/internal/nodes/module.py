"""GraphQL nodes for Module model."""

from datetime import datetime

import strawberry

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models import Label
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.export_types import ExportFormatEnum, ExportResult
from apps.mentorship.api.internal.nodes.mentor import MentorNode
from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task
from apps.mentorship.utils.export import (
    MAX_EXPORT_LIMIT,
    ExportFormat,
    generate_export_filename,
    serialize_issues_to_csv,
    serialize_issues_to_json,
)


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
    program: ProgramNode | None = None
    project_id: strawberry.ID | None = None
    started_at: datetime
    tags: list[str] | None = None

    @strawberry.field
    def mentors(self) -> list[MentorNode]:
        """Get the list of mentors for this module."""
        return self.mentors.all()

    @strawberry.field
    def mentees(self) -> list[UserNode]:
        """Get the list of mentees for this module."""
        mentee_users = (
            self.menteemodule_set.select_related("mentee__github_user")
            .filter(mentee__github_user__isnull=False)
            .values_list("mentee__github_user", flat=True)
        )

        return list(User.objects.filter(id__in=mentee_users).order_by("login"))

    @strawberry.field
    def issue_mentees(self, issue_number: int) -> list[UserNode]:
        """Return mentees assigned to this module's issue identified by its number."""
        issue_ids = list(self.issues.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []

        # Get mentees assigned to tasks for this issue
        mentee_users = (
            Task.objects.filter(module=self, issue_id__in=issue_ids, assignee__isnull=False)
            .select_related("assignee")
            .values_list("assignee", flat=True)
            .distinct()
        )

        return list(User.objects.filter(id__in=mentee_users).order_by("login"))

    @strawberry.field
    def project_name(self) -> str | None:
        """Get the project name for this module."""
        return self.project.name if self.project else None

    @strawberry.field
    def issues(
        self, limit: int = 20, offset: int = 0, label: str | None = None
    ) -> list[IssueNode]:
        """Return paginated issues linked to this module, optionally filtered by label."""
        queryset = self.issues.select_related("repository", "author").prefetch_related(
            "assignees", "labels"
        )

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        return list(queryset.order_by("-updated_at")[offset : offset + limit])

    @strawberry.field
    def issues_count(self, label: str | None = None) -> int:
        """Return total count of issues linked to this module, optionally filtered by label."""
        queryset = self.issues

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        return queryset.count()

    @strawberry.field
    def available_labels(self) -> list[str]:
        """Return all unique labels from issues linked to this module."""
        label_names = (
            Label.objects.filter(issue__mentorship_modules=self)
            .values_list("name", flat=True)
            .distinct()
        )

        return sorted(label_names)

    @strawberry.field
    def issue_by_number(self, number: int) -> IssueNode | None:
        """Return a single issue by its GitHub number within this module's linked issues."""
        return (
            self.issues.select_related("repository", "author")
            .prefetch_related("assignees", "labels")
            .filter(number=number)
            .first()
        )

    @strawberry.field
    def interested_users(self, issue_number: int) -> list[UserNode]:
        """Return users interested in this module's issue identified by its number."""
        issue_ids = list(self.issues.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []
        interests = (
            IssueUserInterest.objects.select_related("user")
            .filter(module=self, issue_id__in=issue_ids)
            .order_by("user__login")
        )
        return [i.user for i in interests]

    @strawberry.field
    def task_deadline(self, issue_number: int) -> datetime | None:
        """Return the deadline for the latest assigned task linked to this module and issue."""
        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                deadline_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("deadline_at", flat=True)
            .first()
        )

    @strawberry.field
    def task_assigned_at(self, issue_number: int) -> datetime | None:
        """Return the latest assignment time for tasks linked to this module and issue number."""
        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                assigned_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("assigned_at", flat=True)
            .first()
        )

    @strawberry.field
    def recent_pull_requests(self, limit: int = 5) -> list[PullRequestNode]:
        """Return recent pull requests linked to issues in this module."""
        issue_ids = self.issues.values_list("id", flat=True)
        return list(
            PullRequest.objects.filter(related_issues__id__in=issue_ids)
            .select_related("author")
            .distinct()
            .order_by("-created_at")[:limit]
        )

    @strawberry.field
    def export_issues(
        self,
        format: ExportFormatEnum,
        label: str | None = None,
        limit: int = MAX_EXPORT_LIMIT,
    ) -> ExportResult:
        """Export issues in CSV or JSON format.

        Args:
            format: Export format (CSV or JSON).
            label: Optional label filter.
            limit: Maximum number of issues to export (default: 1000).

        Returns:
            ExportResult with content, filename, and MIME type.
        """
        # Enforce maximum limit
        effective_limit = min(limit, MAX_EXPORT_LIMIT)

        # Reuse existing issue query logic
        queryset = self.issues.select_related("repository", "author").prefetch_related(
            "assignees", "labels"
        )

        if label and label != "all":
            queryset = queryset.filter(labels__name=label)

        issues = list(queryset.order_by("-updated_at")[:effective_limit])

        # Serialize based on format
        if format == ExportFormatEnum.CSV:
            content = serialize_issues_to_csv(issues)
            mime_type = "text/csv; charset=utf-8"
            export_format = ExportFormat.CSV
        else:
            content = serialize_issues_to_json(issues, self.key)
            mime_type = "application/json; charset=utf-8"
            export_format = ExportFormat.JSON

        filename = generate_export_filename(self.key, export_format)

        return ExportResult(
            content=content,
            filename=filename,
            mime_type=mime_type,
            count=len(issues),
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
