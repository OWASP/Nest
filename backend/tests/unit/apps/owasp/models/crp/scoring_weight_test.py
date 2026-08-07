from apps.owasp.models.crp.recognition_enums import EventTypeChoices
from apps.owasp.models.crp.scoring_weight import ScoringWeight


class TestScoringWeightModel:
    """Test suite for ScoringWeight model."""

    def test_str_representation(self):
        """Test __str__ for ScoringWeight using real choice display."""
        weight = ScoringWeight(event_type=EventTypeChoices.PR_MERGED, score=25)
        assert str(weight) == "Pull Request Merged - 25 points"
