"""Pydantic extraction schema for board meeting markdown parsing."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import StrEnum

from pydantic import BaseModel, Field


class ActionKind(StrEnum):
    """Discriminator for the payload carried by a ParsedAction."""

    DISCUSSION = "discussion"
    MOTION = "motion"
    OUTCOME = "outcome"


class MeetingType(StrEnum):
    """Board meeting type."""

    PRIVATE = "private"
    PUBLIC = "public"
    SPECIAL = "special"
    SUMMIT = "summit"


class OutcomeStatus(StrEnum):
    """Board outcome status."""

    CANCELLED = "cancelled"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class VoteResult(StrEnum):
    """Result of a recorded vote."""

    DEFERRED = "deferred"
    FAILED = "failed"
    PASSED = "passed"
    TABLED = "tabled"
    WITHDRAWN = "withdrawn"


class VoteType(StrEnum):
    """Vote type."""

    E_VOTE = "e_vote"
    VOTE = "vote"


class LabeledUrl(BaseModel):
    """A titled link that appears in meeting minutes."""

    label: str
    url: str


class ParsedPersonRef(BaseModel):
    """A person mentioned in the meeting."""

    name: str


class ParsedVote(BaseModel):
    """A recorded vote on a motion."""

    result: VoteResult
    type: VoteType
    tally: str = ""
    in_favor: list[ParsedPersonRef] = Field(default_factory=list)
    against: list[ParsedPersonRef] = Field(default_factory=list)
    abstain: list[ParsedPersonRef] = Field(default_factory=list)
    recused: list[ParsedPersonRef] = Field(default_factory=list)


class ParsedMotion(BaseModel):
    """A motion put forward at a meeting."""

    title: str
    description: str
    background: str = ""
    references: list[LabeledUrl] = Field(default_factory=list)
    sponsor: ParsedPersonRef | None = None
    second: ParsedPersonRef | None = None
    vote: ParsedVote | None = None


class ParsedDiscussion(BaseModel):
    """A discussion item on the meeting agenda."""

    topic: str
    description: str
    participants: list[ParsedPersonRef] = Field(default_factory=list)


class ParsedOutcome(BaseModel):
    """An action item / outcome produced by a meeting."""

    description: str
    status: OutcomeStatus = OutcomeStatus.PENDING
    due_date: str | None = None
    assignees: list[ParsedPersonRef] = Field(default_factory=list)


class ParsedAction(BaseModel):
    """A single agenda item."""

    kind: ActionKind
    motion: ParsedMotion | None = None
    discussion: ParsedDiscussion | None = None
    outcome: ParsedOutcome | None = None


class ParsedMeeting(BaseModel):
    """The full extraction of a single meeting markdown file."""

    title: str
    date: datetime
    type: MeetingType = MeetingType.PUBLIC
    location: str = ""
    call_in_url: str = ""
    recording_url: str = ""
    quorum_present: bool | None = None
    attachments: list[LabeledUrl] = Field(default_factory=list)
    attendees: list[ParsedPersonRef] = Field(default_factory=list)
    absentees: list[ParsedPersonRef] = Field(default_factory=list)
    guests: list[str] = Field(default_factory=list)
    actions: list[ParsedAction] = Field(default_factory=list)
