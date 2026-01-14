"""
Tests for mapping OWASP official numeric project levels to internal ProjectLevel enums.

These tests ensure that the utility correctly translates official OWASP project
classification values into the corresponding Nest ProjectLevel values and
handles invalid or unsupported inputs safely.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.utils.project_level import map_level


class ProjectLevelMappingTest(SimpleTestCase):
    """Test cases for the `map_level` utility function."""

    def test_flagship_levels(self):
        """Flagship projects should be mapped from levels 4 and 3.5."""
        assert map_level(Decimal(4)) == ProjectLevel.FLAGSHIP
        assert map_level(Decimal("3.5")) == ProjectLevel.FLAGSHIP

    def test_production_level(self):
        """Production projects should be mapped from level 3."""
        assert map_level(Decimal(3)) == ProjectLevel.PRODUCTION

    def test_incubator_level(self):
        """Incubator projects should be mapped from level 2."""
        assert map_level(Decimal(2)) == ProjectLevel.INCUBATOR

    def test_lab_level(self):
        """Lab projects should be mapped from level 1."""
        assert map_level(Decimal(1)) == ProjectLevel.LAB

    def test_other_level(self):
        """Other projects should be mapped from level 0."""
        assert map_level(Decimal(0)) == ProjectLevel.OTHER

    def test_negative_level_returns_none(self):
        """Negative or invalid levels should not map to any ProjectLevel."""
        assert map_level(Decimal(-1)) is None
