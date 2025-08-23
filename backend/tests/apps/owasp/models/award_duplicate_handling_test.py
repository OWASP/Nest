"""Tests for Award model duplicate handling."""

from unittest.mock import patch

from django.test import TestCase

from apps.owasp.models import Award


class TestAwardDuplicateHandling(TestCase):
    """Test cases for Award model duplicate handling."""

    def test_update_data_handles_multiple_objects_returned(self):
        """Test that update_data gracefully handles MultipleObjectsReturned."""
        award_data = {
            "title": "Test Award",
            "category": Award.Category.WASPY,
            "year": 2024,
            "name": "Test Winner",
            "info": "Test info",
        }

        # Create the first award normally
        award1 = Award.update_data(award_data, save=True)

        # Keep a single real row; simulate duplicates at the ORM level by
        # forcing get() to raise MultipleObjectsReturned.

        # Now call update_data again - should handle MultipleObjectsReturned gracefully
        with patch(
            "apps.owasp.models.award.Award.objects.get", side_effect=Award.MultipleObjectsReturned
        ):
            result_award = Award.update_data(award_data, save=False)

        # Should return the first award (ordered by id)
        assert result_award.id == award1.id

        # No cleanup needed; no duplicate row was created
