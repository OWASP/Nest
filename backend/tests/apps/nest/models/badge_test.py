"""Unit tests for Badge model."""

from apps.nest.models import Badge


class TestBadgeModel:
    """Unit tests for Badge model."""

    def test_str_representation(self):
        """Test __str__ returns the badge name."""
        badge = Badge(name="Contributor")
        assert str(badge) == "Contributor"

    def test_badge_with_different_names(self):
        """Test __str__ with various badge names."""
        test_cases = [
            "OWASP Staff",
            "Project Leader",
            "Community Member",
            "🏆 Champion",
        ]

        for name in test_cases:
            badge = Badge(name=name)
            assert str(badge) == name
