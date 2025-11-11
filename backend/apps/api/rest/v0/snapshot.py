"""Snapshot API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.chapter import Chapter
from apps.api.rest.v0.issue import Issue
from apps.api.rest.v0.member import Member
from apps.api.rest.v0.project import Project
from apps.api.rest.v0.release import Release
from apps.github.models.issue import Issue as IssueModel
from apps.github.models.release import Release as ReleaseModel
from apps.github.models.user import User as UserModel
from apps.owasp.models.chapter import Chapter as ChapterModel
from apps.owasp.models.project import Project as ProjectModel
from apps.owasp.models.snapshot import Snapshot as SnapshotModel

router = RouterPaginated(tags=["Snapshots"])


class SnapshotBase(Schema):
    """Base schema for Snapshot (used in list endpoints)."""

    created_at: datetime
    end_at: datetime
    key: str
    start_at: datetime
    title: str
    updated_at: datetime


class Snapshot(SnapshotBase):
    """Schema for Snapshot (minimal fields for list display)."""


class SnapshotDetail(SnapshotBase):
    """Detail schema for Snapshot (used in single item endpoints)."""

    new_chapters_count: int
    new_issues_count: int
    new_projects_count: int
    new_releases_count: int
    new_users_count: int


class SnapshotIssue(Issue):
    """Schema for Snapshot Issue (used in list endpoints)."""

    organization_login: str | None
    repository_name: str | None

    @staticmethod
    def resolve_organization_login(obj: IssueModel) -> str | None:
        """Resolve organization login from issue model."""
        if obj.repository and obj.repository.organization:
            return obj.repository.organization.login
        return None

    @staticmethod
    def resolve_repository_name(obj: IssueModel) -> str | None:
        """Resolve repository name from issue model."""
        if obj.repository:
            return obj.repository.name
        return None


class SnapshotRelease(Release):
    """Schema for Snapshot Release (used in list endpoints)."""

    organization_login: str | None
    repository_name: str | None

    @staticmethod
    def resolve_organization_login(obj: ReleaseModel) -> str | None:
        """Resolve organization_login."""
        if obj.repository and obj.repository.organization:
            return obj.repository.organization.login
        return None

    @staticmethod
    def resolve_repository_name(obj: ReleaseModel) -> str | None:
        """Resolve repository_name."""
        if obj.repository:
            return obj.repository.name
        return None


class SnapshotError(Schema):
    """Snapshot error schema."""

    message: str


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP snapshots.",
    operation_id="list_snapshots",
    response=list[Snapshot],
    summary="List snapshots",
)
@decorate_view(cache_response())
def list_snapshots(
    request: HttpRequest,
    ordering: Literal[
        "created_at", "-created_at", "updated_at", "-updated_at", "start_at", "-start_at"
    ]
    | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Snapshot]:
    """Get all snapshots."""
    return SnapshotModel.objects.filter(status=SnapshotModel.Status.COMPLETED).order_by(
        ordering or "-created_at"
    )


@router.get(
    "/{str:snapshot_key}",
    description="Retrieve snapshot details.",
    operation_id="get_snapshot",
    response={
        HTTPStatus.NOT_FOUND: SnapshotError,
        HTTPStatus.OK: SnapshotDetail,
    },
    summary="Get snapshot",
)
@decorate_view(cache_response())
def get_snapshot(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
) -> SnapshotDetail | SnapshotError:
    """Get snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot

    return Response({"message": "Snapshot not found"}, status=HTTPStatus.NOT_FOUND)


@router.get(
    "/{str:snapshot_key}/chapters/",
    description="Retrieve a paginated list of new chapters in a snapshot.",
    operation_id="list_snapshot_chapters",
    response=list[Chapter],
    summary="List new chapters in snapshot",
)
@decorate_view(cache_response())
def list_snapshot_chapters(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Chapter]:
    """Get new chapters in snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot.new_chapters.order_by(ordering or "-created_at")

    return ChapterModel.objects.none()


@router.get(
    "/{str:snapshot_key}/issues/",
    description="Retrieve a paginated list of new issues in a snapshot.",
    operation_id="list_snapshot_issues",
    response=list[SnapshotIssue],
    summary="List new issues in snapshot",
)
@decorate_view(cache_response())
def list_snapshot_issues(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[SnapshotIssue]:
    """Get new issues in snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot.new_issues.select_related("repository__organization").order_by(
            ordering or "-created_at"
        )
    return IssueModel.objects.none()


@router.get(
    "/{str:snapshot_key}/members/",
    description="Retrieve a paginated list of new members in a snapshot.",
    operation_id="list_snapshot_members",
    response=list[Member],
    summary="List new members in snapshot",
)
@decorate_view(cache_response())
def list_snapshot_members(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Member]:
    """Get new members in snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot.new_users.order_by(ordering or "-created_at")
    return UserModel.objects.none()


@router.get(
    "/{str:snapshot_key}/projects/",
    description="Retrieve a paginated list of new projects in a snapshot.",
    operation_id="list_snapshot_projects",
    response=list[Project],
    summary="List new projects in snapshot",
)
@decorate_view(cache_response())
def list_snapshot_projects(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Project]:
    """Get new projects in snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot.new_projects.order_by(ordering or "-created_at")
    return ProjectModel.objects.none()


@router.get(
    "/{str:snapshot_key}/releases/",
    description="Retrieve a paginated list of new releases in a snapshot.",
    operation_id="list_snapshot_releases",
    response=list[SnapshotRelease],
    summary="List new releases in snapshot",
)
@decorate_view(cache_response())
def list_snapshot_releases(
    request: HttpRequest,
    snapshot_key: str = Path(example="2025-02"),
    ordering: Literal["created_at", "-created_at", "published_at", "-published_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[SnapshotRelease]:
    """Get new releases in snapshot."""
    if snapshot := SnapshotModel.objects.filter(
        key__iexact=snapshot_key, status=SnapshotModel.Status.COMPLETED
    ).first():
        return snapshot.new_releases.select_related("repository__organization").order_by(
            ordering or "-created_at"
        )
    return ReleaseModel.objects.none()
