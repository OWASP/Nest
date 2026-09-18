"""Common schemas and filters for the API."""

from datetime import UTC, datetime

from django.db.models import OuterRef, QuerySet, Subquery
from ninja import Field, FilterSchema, Schema

from apps.owasp.models.board_meeting_action import BoardMeetingAction
from apps.owasp.models.entity_member import EntityMember


def normalize_datetime(value: datetime | None) -> datetime | None:
    """Normalize aware datetimes to UTC so PostgreSQL accepts the offset.

    Args:
        value (datetime, optional): The datetime to normalize.

    Returns:
        datetime: The datetime normalized to UTC, or the original value when it is
            ``None`` or timezone-naive.

    """
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(UTC)


def annotate_meeting_date(
    queryset: QuerySet, *, action_field: str, outer_ref: str = "pk"
) -> QuerySet:
    """Annotate each row with the date of its parent board meeting.

    Args:
        queryset (QuerySet): The queryset to annotate.
        action_field (str): The ``BoardMeetingAction`` field referencing this model,
            e.g. "discussion", "motion", or "outcome".
        outer_ref (str, optional): The queryset field matching the action foreign key.
            Defaults to "pk".

    Returns:
        QuerySet: The queryset annotated with ``meeting_date``.

    """
    return queryset.annotate(
        meeting_date=Subquery(
            BoardMeetingAction.objects.filter(**{action_field: OuterRef(outer_ref)}).values(
                "meeting__date"
            )[:1]
        )
    )


class Leader(Schema):
    """Schema for Leader."""

    key: str | None = None
    name: str


class LocationFilter(FilterSchema):
    """Filter for Location."""

    latitude_gte: float | None = Field(
        None, description="Latitude greater than or equal to", q="latitude__gte"
    )
    latitude_lte: float | None = Field(
        None, description="Latitude less than or equal to", q="latitude__lte"
    )
    longitude_gte: float | None = Field(
        None, description="Longitude greater than or equal to", q="longitude__gte"
    )
    longitude_lte: float | None = Field(
        None, description="Longitude less than or equal to", q="longitude__lte"
    )


class Person(Schema):
    """Reference to a person represented by an EntityMember row."""

    id: int
    name: str

    @staticmethod
    def resolve_name(obj: EntityMember) -> str:
        """Resolve the display name for the referenced person."""
        return obj.member.login if obj.member_id else obj.member_name


class ValidationErrorSchema(Schema):
    """Schema for validation error."""

    message: str
    errors: list[dict] | dict | None = None
