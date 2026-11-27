"""Tests for snapshot feedback GraphQL mutations."""

from unittest.mock import MagicMock, patch

import pydantic as _pydantic
import pytest

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.mutations.snapshot_feedback import (
    MAX_COMMENT_LENGTH,
    SnapshotFeedbackMutations,
    SnapshotFeedbackResult,
    SubmitFeedbackPydanticInput,
    SubmitSnapshotFeedbackInput,
)
from apps.owasp.api.internal.mutations.snapshot_subscription import FieldError
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_feedback import SnapshotFeedback

SNAPSHOT_KEY = "2025-02"


def mock_info():
    """Create a mock GraphQL info object with an authenticated user."""
    info = MagicMock()
    info.context.request.user = MagicMock(spec=True, pk=1)
    return info


def _make_validated_input(*, snapshot_key=SNAPSHOT_KEY, rating=5, comment=""):
    """Create a SubmitSnapshotFeedbackInput with pre-validated data attached."""
    input_data = SubmitSnapshotFeedbackInput(
        snapshot_key=snapshot_key,
        rating=rating,
        comment=comment,
    )
    input_data.validated_data = SubmitFeedbackPydanticInput(
        snapshot_key=snapshot_key,
        rating=rating,
        comment=comment,
    )
    return input_data


class TestSnapshotFeedbackResult:
    """Test SnapshotFeedbackResult type."""

    def test_default_feedback_is_none(self):
        """Test default feedback field is None."""
        assert SnapshotFeedbackResult(ok=True, message="test").feedback is None

    def test_result_with_feedback(self):
        """Test result includes feedback when provided."""
        feedback = MagicMock()
        result = SnapshotFeedbackResult(ok=True, message="test", feedback=feedback)

        assert result.feedback == feedback

    def test_error_result(self):
        """Test error result carries a message and no feedback."""
        result = SnapshotFeedbackResult(ok=False, message="error")

        assert not result.ok
        assert result.message == "error"
        assert result.feedback is None

    def test_result_with_field_errors(self):
        """Test result includes field_errors."""
        errors = [FieldError(field="rating", messages=["Invalid"])]
        result = SnapshotFeedbackResult(ok=False, message="Validation failed", field_errors=errors)

        assert result.field_errors is not None
        assert len(result.field_errors) == 1
        assert result.field_errors[0].field == "rating"


class TestPydanticValidation:
    """Test Pydantic validation directly on the input model."""

    def test_strips_comment_whitespace(self):
        """Test Pydantic strips whitespace from comment."""
        model = SubmitFeedbackPydanticInput(
            snapshot_key=SNAPSHOT_KEY, rating=3, comment="  padded  "
        )
        assert model.comment == "padded"

    def test_rejects_overlong_comment(self):
        """Test Pydantic rejects comment over max length."""
        with pytest.raises(_pydantic.ValidationError):
            SubmitFeedbackPydanticInput(
                snapshot_key=SNAPSHOT_KEY,
                rating=3,
                comment="x" * (MAX_COMMENT_LENGTH + 1),
            )

    def test_accepts_comment_at_max_length(self):
        """Test Pydantic accepts comment at exactly max length."""
        model = SubmitFeedbackPydanticInput(
            snapshot_key=SNAPSHOT_KEY,
            rating=3,
            comment="x" * MAX_COMMENT_LENGTH,
        )
        assert len(model.comment) == MAX_COMMENT_LENGTH

    def test_rejects_rating_below_minimum(self):
        """Test Pydantic rejects rating below 1."""
        with pytest.raises(_pydantic.ValidationError):
            SubmitFeedbackPydanticInput(snapshot_key=SNAPSHOT_KEY, rating=0)

    def test_rejects_rating_above_maximum(self):
        """Test Pydantic rejects rating above 5."""
        with pytest.raises(_pydantic.ValidationError):
            SubmitFeedbackPydanticInput(snapshot_key=SNAPSHOT_KEY, rating=6)

    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    def test_accepts_valid_ratings(self, rating):
        """Test Pydantic accepts all valid ratings."""
        model = SubmitFeedbackPydanticInput(snapshot_key=SNAPSHOT_KEY, rating=rating)
        assert model.rating == rating

    def test_comment_defaults_to_empty(self):
        """Test comment defaults to empty string."""
        model = SubmitFeedbackPydanticInput(snapshot_key=SNAPSHOT_KEY, rating=5)
        assert model.comment == ""

    def test_rejects_empty_snapshot_key(self):
        """Test Pydantic rejects empty snapshot key."""
        with pytest.raises(_pydantic.ValidationError):
            SubmitFeedbackPydanticInput(snapshot_key="", rating=5)


class TestSubmitSnapshotFeedback:
    """Test cases for the submitSnapshotFeedback mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotFeedbackMutations()

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.SnapshotFeedback.submit")
    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.Snapshot.objects.get")
    def test_submit_creates_feedback(self, mock_get, mock_submit, mutations):
        """Test a first-time submission returns a thank-you message."""
        snapshot = MagicMock()
        mock_get.return_value = snapshot
        feedback = MagicMock()
        mock_submit.return_value = (feedback, True)
        info = mock_info()

        result = mutations.submit_snapshot_feedback(
            info,
            _make_validated_input(rating=5, comment="Nice"),
        )

        assert result.ok
        assert result.message == "Thanks for your feedback!"
        assert result.feedback == feedback
        mock_get.assert_called_once_with(
            key=SNAPSHOT_KEY,
            status=Snapshot.Status.COMPLETED,
        )
        mock_submit.assert_called_once_with(
            snapshot=snapshot,
            user=info.context.request.user,
            rating=5,
            comment="Nice",
        )

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.SnapshotFeedback.submit")
    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.Snapshot.objects.get")
    def test_submit_updates_existing_feedback(self, mock_get, mock_submit, mutations):
        """Test resubmitting reports an update rather than a creation."""
        mock_get.return_value = MagicMock()
        mock_submit.return_value = (MagicMock(), False)

        result = mutations.submit_snapshot_feedback(
            mock_info(),
            _make_validated_input(rating=2),
        )

        assert result.ok
        assert result.message == "Feedback updated successfully."

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.Snapshot.objects.get")
    def test_submit_unknown_snapshot(self, mock_get, mutations):
        """Test submitting against a missing snapshot fails gracefully."""
        mock_get.side_effect = Snapshot.DoesNotExist

        result = mutations.submit_snapshot_feedback(
            mock_info(),
            _make_validated_input(snapshot_key="missing"),
        )

        assert not result.ok
        assert result.message == "Snapshot not found."
        assert result.feedback is None

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.SnapshotFeedback.submit")
    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.Snapshot.objects.get")
    def test_submit_uses_request_user(self, mock_get, mock_submit, mutations):
        """Test feedback is attributed to the requesting user."""
        mock_get.return_value = MagicMock()
        mock_submit.return_value = (MagicMock(), True)
        info = mock_info()

        mutations.submit_snapshot_feedback(
            info,
            _make_validated_input(rating=1),
        )

        assert mock_submit.call_args.kwargs["user"] == info.context.request.user


class TestDeleteSnapshotFeedback:
    """Test cases for the deleteSnapshotFeedback mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotFeedbackMutations()

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.SnapshotFeedback.objects.get")
    def test_delete_removes_feedback(self, mock_get, mutations):
        """Test deleting existing feedback succeeds."""
        feedback = MagicMock()
        mock_get.return_value = feedback
        info = mock_info()

        result = mutations.delete_snapshot_feedback(info, SNAPSHOT_KEY)

        assert result.ok
        assert result.message == "Feedback removed successfully."
        assert result.feedback is None
        feedback.delete.assert_called_once()
        mock_get.assert_called_once_with(
            snapshot__key=SNAPSHOT_KEY,
            user=info.context.request.user,
        )

    @patch("apps.owasp.api.internal.mutations.snapshot_feedback.SnapshotFeedback.objects.get")
    def test_delete_missing_feedback(self, mock_get, mutations):
        """Test deleting non-existent feedback fails gracefully."""
        mock_get.side_effect = SnapshotFeedback.DoesNotExist

        result = mutations.delete_snapshot_feedback(mock_info(), SNAPSHOT_KEY)

        assert not result.ok
        assert result.message == "Feedback not found."


class TestSnapshotFeedbackMutationPermissions:
    """Test authentication is required for feedback mutations."""

    @pytest.mark.parametrize(
        "field_name",
        ["submit_snapshot_feedback", "delete_snapshot_feedback"],
    )
    def test_mutation_requires_authentication(self, field_name):
        """Test each mutation is guarded by the IsAuthenticated permission."""
        field = next(
            f
            for f in SnapshotFeedbackMutations.__strawberry_definition__.fields
            if f.name == field_name
        )
        permissions = {
            type(permission)
            for extension in field.extensions
            for permission in getattr(extension, "permissions", [])
        }

        assert IsAuthenticated in permissions
