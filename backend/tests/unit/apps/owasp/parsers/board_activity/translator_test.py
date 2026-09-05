"""Tests for board_activity.translator."""

from contextlib import contextmanager
from datetime import UTC, date, datetime
from unittest.mock import Mock

import pytest

from apps.owasp.models.entity_member import EntityMember
from apps.owasp.parsers.board_activity import translator
from apps.owasp.parsers.board_activity.schemas import (
    ActionKind,
    LabeledUrl,
    ParsedAction,
    ParsedDiscussion,
    ParsedMeeting,
    ParsedMotion,
    ParsedOutcome,
    ParsedPersonRef,
    ParsedVote,
)


@contextmanager
def noop_transaction():
    """No-op replacement for django.db.transaction.atomic in unit tests."""
    yield


@pytest.fixture(autouse=True)
def stub_transaction_atomic(mocker):
    """Stub out transaction.atomic so tests don't open a real DB connection.

    The @transaction.atomic decorator on translator.upsert calls
    connection.get_autocommit(), which requires a real DB. Replace it with a
    no-op context manager for unit tests.
    """
    mocker.patch(
        "apps.owasp.parsers.board_activity.translator.transaction.atomic",
        side_effect=noop_transaction,
    )


class TestResolvePerson:
    """Tests for resolve_person."""

    def test_returns_existing_member(self, mocker):
        """Existing EntityMember matched by (board, member_name) is returned as-is."""
        existing = Mock()
        mock_qs = Mock()
        mock_qs.first.return_value = existing
        mock_manager = mocker.patch("apps.owasp.models.entity_member.EntityMember.objects")
        mock_manager.filter.return_value = mock_qs

        board = Mock(id=42)
        ct = Mock()

        result = translator.resolve_person(board, ct, "Ricardo Griffith", EntityMember.Role.MEMBER)

        assert result is existing
        mock_manager.filter.assert_called_once_with(
            entity_type=ct, entity_id=42, member_name="Ricardo Griffith"
        )
        mock_manager.create.assert_not_called()

    def test_creates_new_member_when_missing(self, mocker):
        """Missing person triggers create with the supplied role."""
        mock_qs = Mock()
        mock_qs.first.return_value = None
        created = Mock()
        mock_manager = mocker.patch("apps.owasp.models.entity_member.EntityMember.objects")
        mock_manager.filter.return_value = mock_qs
        mock_manager.create.return_value = created

        board = Mock(id=7)
        ct = Mock()

        result = translator.resolve_person(board, ct, "Guest Name", EntityMember.Role.MEMBER)

        assert result is created
        mock_manager.create.assert_called_once_with(
            entity_type=ct,
            entity_id=7,
            member_name="Guest Name",
            role=EntityMember.Role.MEMBER,
        )


class TestBuildPersonResolver:
    """Tests for build_person_resolver."""

    def test_resolver_calls_resolve_person_per_input(self, mocker):
        """The returned callable resolves each person via resolve_person."""
        mock_resolve = mocker.patch("apps.owasp.parsers.board_activity.translator.resolve_person")
        mock_resolve.side_effect = ["a", "b", "c"]

        board = Mock()
        ct = Mock()
        resolver = translator.build_person_resolver(board, ct)
        people = [ParsedPersonRef(name=n) for n in ("Alice", "Bob", "Carol")]

        result = resolver(people, EntityMember.Role.MEMBER)

        assert result == ["a", "b", "c"]
        assert mock_resolve.call_count == 3

    def test_resolver_handles_empty_input(self, mocker):
        """An empty input list yields an empty output list without calling resolve_person."""
        mock_resolve = mocker.patch("apps.owasp.parsers.board_activity.translator.resolve_person")

        resolver = translator.build_person_resolver(Mock(), Mock())
        assert resolver([], EntityMember.Role.MEMBER) == []
        mock_resolve.assert_not_called()


class TestCreateDiscussion:
    """Tests for create_discussion."""

    def test_creates_row_and_sets_participants(self, mocker):
        """Discussion row is created and participants M2M is populated."""
        row = Mock()
        mocker.patch(
            "apps.owasp.models.board_discussion.BoardDiscussion.objects.create",
            return_value=row,
        )
        resolve = Mock(return_value=["p1", "p2"])
        discussion = ParsedDiscussion(
            topic="Marketing",
            description="Discuss Q1 marketing plan.",
            participants=[ParsedPersonRef(name="Alice"), ParsedPersonRef(name="Bob")],
        )

        result = translator.create_discussion(discussion, resolve)

        assert result is row
        row.participants.set.assert_called_once_with(["p1", "p2"])
        resolve.assert_called_once_with(discussion.participants, EntityMember.Role.MEMBER)


class TestCreateMotion:
    """Tests for create_motion."""

    def test_creates_motion_without_vote(self, mocker):
        """Motion without a vote produces a single BoardMotion row."""
        row = Mock()
        mock_create = mocker.patch(
            "apps.owasp.models.board_motion.BoardMotion.objects.create",
            return_value=row,
        )
        mock_vote = mocker.patch("apps.owasp.parsers.board_activity.translator.create_vote")
        resolve = Mock(return_value=[Mock(), Mock()])

        motion = ParsedMotion(
            title="Approve Budget",
            description="Resolved, that the budget is approved.",
            sponsor=ParsedPersonRef(name="Alice"),
            second=ParsedPersonRef(name="Bob"),
            references=[LabeledUrl(label="Doc", url="https://example.com/doc")],
        )

        result = translator.create_motion(motion, resolve)

        assert result is row
        mock_create.assert_called_once()
        assert mock_create.call_args.kwargs["title"] == "Approve Budget"
        assert mock_create.call_args.kwargs["references"] == [
            {"label": "Doc", "url": "https://example.com/doc"}
        ]
        mock_vote.assert_not_called()

    def test_creates_motion_with_vote(self, mocker):
        """Motion with a vote triggers create_vote."""
        row = Mock()
        mocker.patch(
            "apps.owasp.models.board_motion.BoardMotion.objects.create",
            return_value=row,
        )
        mock_vote = mocker.patch("apps.owasp.parsers.board_activity.translator.create_vote")
        resolve = Mock(return_value=[])

        vote = ParsedVote(result="passed", type="vote", tally="7-0")
        motion = ParsedMotion(title="M", description="D", vote=vote)

        translator.create_motion(motion, resolve)

        mock_vote.assert_called_once_with(row, vote, resolve)

    def test_null_sponsor_and_second_pass_through(self, mocker):
        """Motion with no sponsor/second creates row with None for those FKs."""
        mock_create = mocker.patch("apps.owasp.models.board_motion.BoardMotion.objects.create")
        mocker.patch("apps.owasp.parsers.board_activity.translator.create_vote")
        resolve = Mock()

        motion = ParsedMotion(title="M", description="D")

        translator.create_motion(motion, resolve)

        assert mock_create.call_args.kwargs["sponsor"] is None
        assert mock_create.call_args.kwargs["second"] is None
        resolve.assert_not_called()


class TestCreateOutcome:
    """Tests for create_outcome."""

    def test_creates_row_and_sets_assignees(self, mocker):
        """Outcome row is created and assignees M2M is populated."""
        row = Mock()
        mock_create = mocker.patch(
            "apps.owasp.models.board_outcome.BoardOutcome.objects.create",
            return_value=row,
        )
        resolve = Mock(return_value=["a1"])

        outcome = ParsedOutcome(
            description="Ship the audit",
            status="in_progress",
            due_date="2026-01-15",
            assignees=[ParsedPersonRef(name="Alice")],
        )

        result = translator.create_outcome(outcome, resolve)

        assert result is row
        assert mock_create.call_args.kwargs["due_date"] == date(2026, 1, 15)
        row.assignees.set.assert_called_once_with(["a1"])

    def test_malformed_due_date_is_dropped_to_none(self, mocker):
        """A due_date the LLM couldn't format properly saves as None instead of raising."""
        mock_create = mocker.patch("apps.owasp.models.board_outcome.BoardOutcome.objects.create")

        outcome = ParsedOutcome(description="X", status="pending", due_date="end of Q1")
        translator.create_outcome(outcome, Mock(return_value=[]))

        assert mock_create.call_args.kwargs["due_date"] is None


class TestDeleteMeetingChildren:
    """Tests for delete_meeting_children."""

    def test_deletes_discussions_motions_and_outcomes(self, mocker):
        """Distinct child ids across the meeting's actions are collected and deleted per type."""
        actions = Mock()
        actions.exclude.side_effect = lambda **_: actions
        actions.values_list.side_effect = [[1, 2], [3], [4, 5]]
        meeting = Mock()
        meeting.actions.all.return_value = actions

        mock_discussion = mocker.patch(
            "apps.owasp.models.board_discussion.BoardDiscussion.objects.filter"
        )
        mock_motion = mocker.patch("apps.owasp.models.board_motion.BoardMotion.objects.filter")
        mock_outcome = mocker.patch("apps.owasp.models.board_outcome.BoardOutcome.objects.filter")

        translator.delete_meeting_children(meeting)

        mock_discussion.assert_called_once_with(id__in=[1, 2])
        mock_motion.assert_called_once_with(id__in=[3])
        mock_outcome.assert_called_once_with(id__in=[4, 5])
        mock_discussion.return_value.delete.assert_called_once()
        mock_motion.return_value.delete.assert_called_once()
        mock_outcome.return_value.delete.assert_called_once()


class TestCreateVote:
    """Tests for create_vote."""

    def test_creates_vote_and_sets_all_four_m2ms(self, mocker):
        """Vote row is created and all four cast M2Ms are populated."""
        row = Mock()
        mocker.patch(
            "apps.owasp.models.board_vote.BoardVote.objects.create",
            return_value=row,
        )
        resolve = Mock(side_effect=[["f"], ["a"], ["ab"], ["r"]])
        motion = Mock()

        vote = ParsedVote(
            result="passed",
            type="vote",
            tally="6-1",
            in_favor=[ParsedPersonRef(name="A")],
            against=[ParsedPersonRef(name="B")],
            abstain=[ParsedPersonRef(name="C")],
            recused=[ParsedPersonRef(name="D")],
        )

        translator.create_vote(motion, vote, resolve)

        row.in_favor.set.assert_called_once_with(["f"])
        row.against.set.assert_called_once_with(["a"])
        row.abstain.set.assert_called_once_with(["ab"])
        row.recused.set.assert_called_once_with(["r"])


class TestCreateAction:
    """Tests for create_action dispatch."""

    @pytest.fixture
    def mock_action_create(self, mocker):
        """Patch BoardMeetingAction.objects.create."""
        return mocker.patch(
            "apps.owasp.models.board_meeting_action.BoardMeetingAction.objects.create"
        )

    def test_dispatches_to_discussion(self, mocker, mock_action_create):
        """Discussion kind creates a discussion and creates a linked action."""
        creator = Mock(return_value="d_row")
        mocker.patch.dict(
            "apps.owasp.parsers.board_activity.translator.ACTION_CREATORS",
            {ActionKind.DISCUSSION: creator},
        )
        meeting = Mock()
        action = ParsedAction(
            kind=ActionKind.DISCUSSION,
            discussion=ParsedDiscussion(topic="t", description="d"),
        )

        translator.create_action(meeting, 1, action, Mock())

        creator.assert_called_once()
        mock_action_create.assert_called_once_with(meeting=meeting, order=1, discussion="d_row")

    def test_dispatches_to_motion(self, mocker, mock_action_create):
        """Motion kind creates a motion and creates a linked action."""
        creator = Mock(return_value="m_row")
        mocker.patch.dict(
            "apps.owasp.parsers.board_activity.translator.ACTION_CREATORS",
            {ActionKind.MOTION: creator},
        )
        meeting = Mock()
        action = ParsedAction(
            kind=ActionKind.MOTION,
            motion=ParsedMotion(title="t", description="d"),
        )

        translator.create_action(meeting, 2, action, Mock())

        creator.assert_called_once()
        mock_action_create.assert_called_once_with(meeting=meeting, order=2, motion="m_row")

    def test_dispatches_to_outcome(self, mocker, mock_action_create):
        """Outcome kind creates an outcome and creates a linked action."""
        creator = Mock(return_value="o_row")
        mocker.patch.dict(
            "apps.owasp.parsers.board_activity.translator.ACTION_CREATORS",
            {ActionKind.OUTCOME: creator},
        )
        meeting = Mock()
        action = ParsedAction(
            kind=ActionKind.OUTCOME,
            outcome=ParsedOutcome(description="do it"),
        )

        translator.create_action(meeting, 3, action, Mock())

        creator.assert_called_once()
        mock_action_create.assert_called_once_with(meeting=meeting, order=3, outcome="o_row")

    def test_raises_when_payload_missing(self, mock_action_create):
        """Malformed action (kind set but payload None) raises so upsert rolls back."""
        action = ParsedAction(kind=ActionKind.MOTION, motion=None)
        meeting = Mock()
        resolve = Mock()

        with pytest.raises(ValueError, match="has no matching payload"):
            translator.create_action(meeting, 1, action, resolve)

        mock_action_create.assert_not_called()


class TestUpsert:
    """Tests for the top-level upsert function."""

    def test_upsert_creates_meeting_and_dispatches_actions(self, mocker):
        """Upsert wires the board, meeting, attendance M2Ms, and actions correctly."""
        board = Mock(id=1)
        mock_board_get_or_create = mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(board, True),
        )
        meeting = Mock()
        mock_delete_children = mocker.patch(
            "apps.owasp.parsers.board_activity.translator.delete_meeting_children"
        )
        mock_update_or_create = mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.update_or_create",
            return_value=(meeting, True),
        )
        ct = Mock()
        mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=ct,
        )
        resolver = Mock(side_effect=lambda people, role: [f"{p.name}:{role}" for p in people])
        mocker.patch(
            "apps.owasp.parsers.board_activity.translator.build_person_resolver",
            return_value=resolver,
        )
        mock_action = mocker.patch("apps.owasp.parsers.board_activity.translator.create_action")

        parsed = ParsedMeeting(
            title="August 2025",
            date="2025-08-26T13:00:00+00:00",
            type="public",
            attendees=[ParsedPersonRef(name="Alice")],
            absentees=[ParsedPersonRef(name="Bob")],
            guests=["Guest"],
            actions=[
                ParsedAction(
                    kind=ActionKind.MOTION, motion=ParsedMotion(title="M", description="D")
                ),
                ParsedAction(
                    kind=ActionKind.DISCUSSION,
                    discussion=ParsedDiscussion(topic="t", description="d"),
                ),
            ],
        )

        result = translator.upsert(
            parsed, source_path="meetings-historical/2025/202508.md", source_checksum="abc123"
        )

        assert result is meeting
        assert mock_update_or_create.call_args.kwargs["defaults"]["guests"] == ["Guest"]
        assert mock_update_or_create.call_args.kwargs["defaults"]["date"] == datetime(
            2025, 8, 26, 13, 0, 0, tzinfo=UTC
        )
        mock_board_get_or_create.assert_called_once_with(year=2025)
        mock_delete_children.assert_called_once_with(meeting)
        meeting.attendees.set.assert_called_once()
        meeting.absentees.set.assert_called_once()
        assert mock_action.call_count == 2
        assert mock_action.call_args_list[0].args[1] == 1
        assert mock_action.call_args_list[1].args[1] == 2
