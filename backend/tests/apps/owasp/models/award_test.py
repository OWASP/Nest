"""Tests for Award model."""

from django.test import TestCase


class AwardModelTest(TestCase):
    """Test cases for Award model."""

    def test_award_import(self):
        """Test that Award model can be imported."""
        from apps.owasp.models.award import Award

        assert Award is not None

    def test_award_category_choices(self):
        """Test Award category choices."""
        from apps.owasp.models.award import Award

        choices = Award.Category.choices
        assert ("WASPY", "WASPY") in choices
        assert (
            "Distinguished Lifetime Memberships",
            "Distinguished Lifetime Memberships",
        ) in choices

    def test_award_meta(self):
        """Test Award model meta."""
        from apps.owasp.models.award import Award

        assert Award._meta.db_table == "owasp_awards"
        assert Award._meta.verbose_name == "Award"
