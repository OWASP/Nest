from datetime import date

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

        assert str(snapshot) == "bob_coder - Global Rank: 5, Project Rank: 2, Chapter Rank: 1 (2026-08-01)"
