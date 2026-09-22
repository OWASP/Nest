"""Tests for snapshot feedback model."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.snapshot_feedback import MAX_RATING, MIN_RATING, SnapshotFeedback


class TestSnapshotFeedback:
    """Test SnapshotFeedback model."""

    def test_str_representation(self):
        """Test string representation includes user, snapshot and rating."""
        feedback = MagicMock(spec=SnapshotFeedback)
        feedback.user = "alice"
        feedback.snapshot = "2025-02"
        feedback.rating = 4

        assert SnapshotFeedback.__str__(feedback) == "alice — 2025-02 (4/5)"

    def test_meta_options(self):
        """Test model meta configuration."""
        meta = SnapshotFeedback._meta

        assert meta.db_table == "owasp_snapshot_feedback"
        assert meta.verbose_name_plural == "Snapshot Feedback"

    def test_unique_constraint_on_snapshot_and_user(self):
        """Test a user can only leave one feedback entry per snapshot."""
        constraint = next(
            c
            for c in SnapshotFeedback._meta.constraints
            if c.name == "unique_snapshot_user_feedback"
        )

        assert set(constraint.fields) == {"snapshot", "user"}

    def test_snapshot_index(self):
        """Test feedback is indexed for per-snapshot lookups."""
        index = next(
            i for i in SnapshotFeedback._meta.indexes if i.name == "owasp_feedback_snapshot_idx"
        )

        assert index.fields == ["snapshot", "-created_at"]

    def test_comment_is_optional(self):
        """Test comment defaults to an empty string and is blankable."""
        field = SnapshotFeedback._meta.get_field("comment")

        assert field.blank
        assert field.default == ""

    def test_rating_validator_bounds(self):
        """Test rating validators enforce the 1-5 range."""
        field = SnapshotFeedback._meta.get_field("rating")
        limits = {getattr(validator, "limit_value", None) for validator in field.validators}

        assert MIN_RATING in limits
        assert MAX_RATING in limits

    def test_related_names(self):
        """Test reverse accessors used by the API and node resolvers."""
        assert SnapshotFeedback._meta.get_field("snapshot").remote_field.related_name == "feedback"
        assert (
            SnapshotFeedback._meta.get_field("user").remote_field.related_name
            == "snapshot_feedback"
        )


class TestSnapshotFeedbackSubmit:
    """Test SnapshotFeedback.submit()."""

    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_creates_feedback(self, mock_objects):
        """Test submit delegates to update_or_create with cleaned values."""
        snapshot = MagicMock()
        user = MagicMock()
        expected = (MagicMock(), True)
        mock_objects.update_or_create.return_value = expected

        result = SnapshotFeedback.submit(
            snapshot=snapshot,
            user=user,
            rating=5,
            comment="Great work",
        )

        assert result == expected
        mock_objects.update_or_create.assert_called_once_with(
            snapshot=snapshot,
            user=user,
            defaults={"comment": "Great work", "rating": 5},
        )

    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_updates_existing_feedback(self, mock_objects):
        """Test submit reports created=False when updating."""
        mock_objects.update_or_create.return_value = (MagicMock(), False)

        _, created = SnapshotFeedback.submit(
            snapshot=MagicMock(),
            user=MagicMock(),
            rating=3,
        )

        assert not created

    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_normalizes_missing_comment(self, mock_objects):
        """Test a None comment is stored as an empty string."""
        mock_objects.update_or_create.return_value = (MagicMock(), True)

        SnapshotFeedback.submit(
            snapshot=MagicMock(),
            user=MagicMock(),
            rating=1,
            comment=None,
        )

        assert mock_objects.update_or_create.call_args.kwargs["defaults"]["comment"] == ""

    @pytest.mark.parametrize("rating", [0, -1, 6, 100])
    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_rejects_out_of_range_rating(self, mock_objects, rating):
        """Test submit raises before touching the database for bad ratings."""
        snapshot = MagicMock()
        user = MagicMock()

        with pytest.raises(ValidationError):
            SnapshotFeedback.submit(snapshot=snapshot, user=user, rating=rating)

        mock_objects.update_or_create.assert_not_called()

    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_accepts_every_valid_rating(self, mock_objects, rating):
        """Test all ratings within the range are accepted."""
        mock_objects.update_or_create.return_value = (MagicMock(), True)

        SnapshotFeedback.submit(snapshot=MagicMock(), user=MagicMock(), rating=rating)

        assert mock_objects.update_or_create.call_args.kwargs["defaults"]["rating"] == rating

    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_rejects_non_numeric_rating(self, mock_objects):
        """Test a non-numeric rating is rejected."""
        snapshot = MagicMock()
        user = MagicMock()

        with pytest.raises(ValidationError):
            SnapshotFeedback.submit(snapshot=snapshot, user=user, rating="five")

        mock_objects.update_or_create.assert_not_called()

    @pytest.mark.parametrize("rating", [True, False])
    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_rejects_boolean_rating(self, mock_objects, rating):
        """Test boolean ratings are rejected even though bool is a subclass of int."""
        with pytest.raises(ValidationError):
            SnapshotFeedback.submit(snapshot=MagicMock(), user=MagicMock(), rating=rating)

        mock_objects.update_or_create.assert_not_called()

    @pytest.mark.parametrize("rating", [3.0, 4.5])
    @patch("apps.owasp.models.snapshot_feedback.SnapshotFeedback.objects")
    def test_submit_rejects_float_rating(self, mock_objects, rating):
        """Test float ratings are rejected to enforce whole numbers."""
        with pytest.raises(ValidationError):
            SnapshotFeedback.submit(snapshot=MagicMock(), user=MagicMock(), rating=rating)

        mock_objects.update_or_create.assert_not_called()
