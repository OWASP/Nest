from unittest.mock import MagicMock, patch

from apps.owasp.models.crp.recognition_enums import EventTypeChoices
from apps.owasp.models.crp.scoring_weight import ScoringWeight


class TestScoringWeightModel:
    """Test suite for ScoringWeight model."""

    def test_str_representation(self):
        """Test __str__ for ScoringWeight."""
        weight = ScoringWeight(event_type=EventTypeChoices.PR_MERGED, score=25)
        with patch.object(weight, "get_event_type_display", return_value="Pull Request Merged"):
            assert str(weight) == "Pull Request Merged - 25 points"
