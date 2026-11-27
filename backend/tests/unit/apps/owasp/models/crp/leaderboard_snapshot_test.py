from datetime import date

from django.db import models

from apps.github.models.user import User
from apps.owasp.models.crp.leaderboard_snapshot import LeaderboardSnapshot


class TestLeaderboardSnapshotModel:
    """Test suite for LeaderboardSnapshot model."""

    def test_str_representation(self):
        """Test __str__ for LeaderboardSnapshot."""
        user = User(login="bob_coder")
        snapshot = LeaderboardSnapshot(
            github_user=user,
            global_rank=5,
            project_rank=2,
            chapter_rank=1,
            snapshot_date=date(2026, 8, 1),
        )

        assert (
            str(snapshot)
            == "bob_coder - Global Rank: 5, Project Rank: 2, Chapter Rank: 1 (2026-08-01)"
        )

    def test_unique_constraint_treats_null_scopes_as_equal(self):
        """Test one snapshot per user, scope, and date is enforced even for NULL scopes."""
        meta = LeaderboardSnapshot._meta

        assert not meta.unique_together
        constraint = next(
            c for c in meta.constraints if c.name == "unique_leaderboard_snapshot_per_scope"
        )
        assert isinstance(constraint, models.UniqueConstraint)
        assert constraint.fields == ("github_user", "project", "chapter", "snapshot_date")
        assert constraint.nulls_distinct is False

    def test_scope_ranks_are_optional(self):
        """Test project and chapter ranks may be empty for snapshots outside that scope."""
        for field_name in ("project_rank", "chapter_rank"):
            field = LeaderboardSnapshot._meta.get_field(field_name)
            assert field.null
            assert field.blank

        assert not LeaderboardSnapshot._meta.get_field("global_rank").null
