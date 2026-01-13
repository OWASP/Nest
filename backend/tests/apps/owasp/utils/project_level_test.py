from decimal import Decimal

from django.test import SimpleTestCase

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.utils.project_level import map_level


class ProjectLevelMappingTest(SimpleTestCase):

    def test_flagship_levels(self):
        assert map_level(Decimal("4")) == ProjectLevel.FLAGSHIP
        assert map_level(Decimal("3.5")) == ProjectLevel.FLAGSHIP

    def test_production_level(self):
        assert map_level(Decimal("3")) == ProjectLevel.PRODUCTION

    def test_incubator_level(self):
        assert map_level(Decimal("2")) == ProjectLevel.INCUBATOR

    def test_lab_level(self):
        assert map_level(Decimal("1")) == ProjectLevel.LAB

    def test_other_level(self):
        assert map_level(Decimal("0")) == ProjectLevel.OTHER

    def test_negative_level_returns_none(self):
        assert map_level(Decimal("-1")) is None
