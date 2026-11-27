from apps.github.models.user import User
from apps.owasp.models.crp.contribution_score import ContributionScore
from apps.owasp.models.crp.recognition_enums import TierChoices


class TestContributionScoreModel:
    """Test suite for ContributionScore model."""

    def test_str_representation(self):
        """Test __str__ for ContributionScore."""
        user = User(login="alice_dev")
        score = ContributionScore(github_user=user, tier=TierChoices.LEVEL_3, value=350)

        assert str(score) == "alice_dev - LEVEL_3 (350 points)"
