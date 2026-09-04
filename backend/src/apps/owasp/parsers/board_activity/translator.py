"""Translator of pydantic to Django board-activity rows."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.owasp.models.board_discussion import BoardDiscussion
from apps.owasp.models.board_meeting import BoardMeeting
from apps.owasp.models.board_meeting_action import BoardMeetingAction
from apps.owasp.models.board_motion import BoardMotion
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.board_outcome import BoardOutcome
from apps.owasp.models.board_vote import BoardVote
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.parsers.board_activity.schemas import (
    ActionKind,
    ParsedAction,
    ParsedDiscussion,
    ParsedMeeting,
    ParsedMotion,
    ParsedOutcome,
    ParsedPersonRef,
    ParsedVote,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    PersonResolver = Callable[..., list[EntityMember]]


def upsert(parsed: ParsedMeeting, *, source_path: str, source_checksum: str) -> BoardMeeting:
    """Upsert a parsed meeting and its child rows.

    Args:
        parsed (ParsedMeeting): The parsed meeting payload.
        source_path (str): Repo-relative path of the source markdown file.
        source_checksum (str): Git blob SHA of the source file.

    Returns:
        BoardMeeting: The upserted meeting row.

    """
    with transaction.atomic():
        board, _ = BoardOfDirectors.objects.get_or_create(year=parsed.date.year)

        meeting, _ = BoardMeeting.objects.update_or_create(
            source_path=source_path,
            defaults={
                "attachments": [a.model_dump() for a in parsed.attachments],
                "board": board,
                "call_in_url": parsed.call_in_url,
                "date": parsed.date,
                "guests": list(parsed.guests),
                "location": parsed.location,
                "quorum_present": parsed.quorum_present,
                "recording_url": parsed.recording_url,
                "source_checksum": source_checksum,
                "title": parsed.title,
                "type": parsed.type,
            },
        )

        delete_meeting_children(meeting)

        board_content_type = ContentType.objects.get_for_model(BoardOfDirectors)
        resolve = build_person_resolver(board, board_content_type)

        meeting.attendees.set(resolve(parsed.attendees, EntityMember.Role.MEMBER))
        meeting.absentees.set(resolve(parsed.absentees, EntityMember.Role.MEMBER))

        for order, action in enumerate(parsed.actions, start=1):
            create_action(meeting, order, action, resolve)

    return meeting


def delete_meeting_children(meeting: BoardMeeting) -> None:
    """Delete all action rows and their referenced children for a meeting.

    Args:
        meeting (BoardMeeting): The meeting whose agenda should be cleared.

    """
    actions = meeting.actions.all()
    discussion_ids = list(actions.exclude(discussion=None).values_list("discussion_id", flat=True))
    motion_ids = list(actions.exclude(motion=None).values_list("motion_id", flat=True))
    outcome_ids = list(actions.exclude(outcome=None).values_list("outcome_id", flat=True))

    BoardDiscussion.objects.filter(id__in=discussion_ids).delete()
    BoardMotion.objects.filter(id__in=motion_ids).delete()
    BoardOutcome.objects.filter(id__in=outcome_ids).delete()


def build_person_resolver(
    board: BoardOfDirectors, board_content_type: ContentType
) -> PersonResolver:
    """Build a person to EntityMember resolver bound to a board year.

    Args:
        board (BoardOfDirectors): The board year to bind the resolver to.
        board_content_type (ContentType): ContentType for BoardOfDirectors.

    Returns:
        PersonResolver: A resolver callable.

    """

    def resolver(people: Iterable[ParsedPersonRef], role) -> list[EntityMember]:
        return [resolve_person(board, board_content_type, person.name, role) for person in people]

    return resolver


def resolve_person(
    board: BoardOfDirectors,
    board_content_type: ContentType,
    name: str,
    role,
) -> EntityMember:
    """Get or create an EntityMember for a named person on a board.

    Args:
        board (BoardOfDirectors): The board year to attach the person to.
        board_content_type (ContentType): ContentType for BoardOfDirectors.
        name (str): The person's source-text name.
        role: An EntityMember.Role value assigned when a new row is created.

    Returns:
        EntityMember: The resolved entity member row.

    """
    existing = EntityMember.objects.filter(
        entity_id=board.id,
        entity_type=board_content_type,
        member_name=name,
    ).first()
    if existing:
        return existing

    return EntityMember.objects.create(
        entity_id=board.id,
        entity_type=board_content_type,
        member_name=name,
        role=role,
    )


def create_discussion(discussion: ParsedDiscussion, resolve: PersonResolver) -> BoardDiscussion:
    """Create a BoardDiscussion row from parsed input.

    Args:
        discussion (ParsedDiscussion): The parsed discussion payload.
        resolve (PersonResolver): Person resolver from build_person_resolver.

    Returns:
        BoardDiscussion: The created row.

    """
    row = BoardDiscussion.objects.create(
        description=discussion.description,
        topic=discussion.topic,
    )
    row.participants.set(resolve(discussion.participants, EntityMember.Role.MEMBER))
    return row


def create_motion(motion: ParsedMotion, resolve: PersonResolver) -> BoardMotion:
    """Create a BoardMotion row and any attached vote from parsed input.

    Args:
        motion (ParsedMotion): The parsed motion payload.
        resolve (PersonResolver): Person resolver from build_person_resolver.

    Returns:
        BoardMotion: The created row.

    """
    sponsor = resolve([motion.sponsor], EntityMember.Role.MEMBER)[0] if motion.sponsor else None
    second = resolve([motion.second], EntityMember.Role.MEMBER)[0] if motion.second else None

    row = BoardMotion.objects.create(
        background=motion.background,
        description=motion.description,
        references=[r.model_dump() for r in motion.references],
        second=second,
        sponsor=sponsor,
        title=motion.title,
    )

    if motion.vote:
        create_vote(row, motion.vote, resolve)

    return row


def create_outcome(outcome: ParsedOutcome, resolve: PersonResolver) -> BoardOutcome:
    """Create a BoardOutcome row from parsed input.

    Args:
        outcome (ParsedOutcome): The parsed outcome payload.
        resolve (PersonResolver): Person resolver from build_person_resolver.

    Returns:
        BoardOutcome: The created row.

    """
    try:
        due_date = date.fromisoformat(outcome.due_date) if outcome.due_date else None
    except ValueError:
        due_date = None

    row = BoardOutcome.objects.create(
        description=outcome.description,
        due_date=due_date,
        status=outcome.status,
    )
    row.assignees.set(resolve(outcome.assignees, EntityMember.Role.MEMBER))
    return row


def create_vote(motion: BoardMotion, vote: ParsedVote, resolve: PersonResolver) -> BoardVote:
    """Create a BoardVote row attached to the given motion.

    Args:
        motion (BoardMotion): The motion the vote applies to.
        vote (ParsedVote): The parsed vote payload.
        resolve (PersonResolver): Person resolver from build_person_resolver.

    Returns:
        BoardVote: The created row.

    """
    row = BoardVote.objects.create(
        motion=motion,
        result=vote.result,
        tally=vote.tally,
        type=vote.type,
    )
    row.in_favor.set(resolve(vote.in_favor, EntityMember.Role.MEMBER))
    row.against.set(resolve(vote.against, EntityMember.Role.MEMBER))
    row.abstain.set(resolve(vote.abstain, EntityMember.Role.MEMBER))
    row.recused.set(resolve(vote.recused, EntityMember.Role.MEMBER))
    return row


ACTION_CREATORS = {
    ActionKind.DISCUSSION: create_discussion,
    ActionKind.MOTION: create_motion,
    ActionKind.OUTCOME: create_outcome,
}


def create_action(
    meeting: BoardMeeting,
    order: int,
    action: ParsedAction,
    resolve: PersonResolver,
) -> None:
    """Create the child row for a parsed action and link it to the meeting.

    Args:
        meeting (BoardMeeting): The parent meeting.
        order (int): position in the agenda.
        action (ParsedAction): The parsed action payload.
        resolve (PersonResolver): Person resolver from build_person_resolver.

    """
    payload = getattr(action, action.kind)
    if not payload:
        return

    row = ACTION_CREATORS[action.kind](payload, resolve)
    BoardMeetingAction.objects.create(
        meeting=meeting,
        order=order,
        **{action.kind: row},
    )
