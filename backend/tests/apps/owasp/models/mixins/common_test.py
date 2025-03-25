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
