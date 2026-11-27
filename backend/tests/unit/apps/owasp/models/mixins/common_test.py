from unittest.mock import MagicMock

import pytest

from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class EntityModelMixin(RepositoryBasedEntityModel, RepositoryBasedEntityModelMixin):
    class Meta:
        abstract = False  # Abstract models cannot be instantiated
        app_label = "owasp"


class TestRepositoryBasedEntityModelMixin:
    @pytest.mark.parametrize(
        ("has_active_repositories", "expected_indexable"),
        [
            (False, False),
            (True, True),
        ],
    )
    def test_is_indexable(self, has_active_repositories, expected_indexable):
        instance = EntityModelMixin(has_active_repositories=has_active_repositories)
        assert instance.is_indexable == expected_indexable

    def test_idx_description(self):
        """Test idx_description returns description."""
        instance = EntityModelMixin(has_active_repositories=True, description="Test description")
        assert instance.idx_description == "Test description"

    def test_idx_leaders(self):
        """Test idx_leaders returns leaders without @ prefixed entries."""
        instance = EntityModelMixin(has_active_repositories=True)
        instance.leaders_raw = ["John Doe", "@hidden_user", "Jane Smith"]
        assert instance.idx_leaders == ["John Doe", "Jane Smith"]

    def test_idx_leaders_empty(self):
        """Test idx_leaders returns empty list when no leaders."""
        instance = EntityModelMixin(has_active_repositories=True)
        instance.leaders_raw = []
        assert instance.idx_leaders == []

    def test_idx_name(self):
        """Test idx_name returns name."""
        instance = EntityModelMixin(has_active_repositories=True, name="Test Entity")
        assert instance.idx_name == "Test Entity"

    def test_idx_summary(self):
        """Test idx_summary returns summary."""
        instance = EntityModelMixin(has_active_repositories=True, summary="Test summary")
        assert instance.idx_summary == "Test summary"

    def test_idx_tags(self):
        """Test idx_tags returns tags."""
        instance = EntityModelMixin(has_active_repositories=True, tags=["security", "owasp"])
        assert instance.idx_tags == ["security", "owasp"]

    def test_idx_topics(self):
        """Test idx_topics returns topics."""
        instance = EntityModelMixin(has_active_repositories=True, topics=["web", "mobile"])
        assert instance.idx_topics == ["web", "mobile"]

    def test_idx_url(self):
        """Test idx_url returns owasp_url."""
        mock_instance = MagicMock()
        mock_instance.owasp_url = "https://owasp.org/test"

        result = RepositoryBasedEntityModelMixin.idx_url.fget(mock_instance)
        assert result == "https://owasp.org/test"
