from unittest.mock import Mock, patch

from django.db.models import Q

from apps.github.models.managers.organization import RelatedOrganizationsManager
from apps.owasp.constants import OWASP_ORGANIZATION_NAME


class TestRelatedOrganizationsManager:
    def test_get_queryset_excludes_organizations(self):
        """Test that get_queryset excludes OWASP and non-OWASP related organizations."""
        mock_super_queryset = Mock()
        mock_super_queryset.exclude.return_value = mock_super_queryset

        with patch(
            "apps.github.models.managers.organization.super",
            return_value=Mock(get_queryset=Mock(return_value=mock_super_queryset)),
        ) as mock_super:
            manager = RelatedOrganizationsManager()
            queryset = manager.get_queryset()

            mock_super.return_value.get_queryset.assert_called_once()
            mock_super_queryset.exclude.assert_called_once_with(
                Q(login=OWASP_ORGANIZATION_NAME) | Q(is_owasp_related_organization=False),
            )
            assert queryset == mock_super_queryset
