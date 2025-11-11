from datetime import UTC, datetime

import pytest

from apps.github.models.organization import Organization

EXPECTED_CONTRIBUTOR_COUNT = 5


@pytest.fixture
def organization_instance():
    """Provide a test instance of the Organization model."""
    return Organization(
        name="Test Organization",
        login="test-org",
        company="Test Company",
        location="Test Location",
        description="A test organization.",
        followers_count=100,
        public_repositories_count=10,
        avatar_url="https://github.com/avatars/test-org",
    )


class TestOrganizationIndexMixin:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [("idx_name", "Organization Name")],
    )
    def test_organization_index(self, attr, expected):
        organization = Organization(
            name="Organization Name", login="login", company="Company", location="Location"
        )
        assert getattr(organization, attr) == expected

    @pytest.mark.parametrize(
        ("created_at_value", "expected_timestamp"),
        [
            (datetime(2023, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC).timestamp()),
            (None, None),
        ],
    )
    def test_idx_created_at(self, organization_instance, created_at_value, expected_timestamp):
        """Tests the idx_created_at property returns the correct timestamp or None."""
        organization_instance.created_at = created_at_value
        assert organization_instance.idx_created_at == expected_timestamp

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_login", "test-org"),
            ("idx_location", "Test Location"),
            ("idx_followers_count", 100),
            ("idx_public_repositories_count", 10),
            ("idx_url", "https://github.com/test-org"),
            ("idx_avatar_url", "https://github.com/avatars/test-org"),
        ],
    )
    def test_additional_index_properties(self, organization_instance, attr, expected):
        """Tests additional simple index properties that directly return model attributes."""
        assert getattr(organization_instance, attr) == expected

    def test_is_indexable(self):
        organization = Organization(name="Organization Name", login="login")
        assert organization.is_indexable

        organization = Organization(login="login")
        assert not organization.is_indexable

        organization = Organization(name="Organization Name")
        assert not organization.is_indexable

        organization = Organization()
        assert not organization.is_indexable

    @pytest.mark.parametrize(
        ("is_owasp_related", "expected_indexable"),
        [
            (True, True),
            (False, False),
        ],
    )
    def test_is_indexable_owasp_related(self, is_owasp_related, expected_indexable):
        """Tests the is_indexable property based on is_owasp_related_organization."""
        organization = Organization(
            name="Organization Name", login="login", is_owasp_related_organization=is_owasp_related
        )
        assert organization.is_indexable == expected_indexable

    def test_idx_description_with_value(self):
        organization = Organization(description="Organization Description")
        assert organization.idx_description == "Organization Description"

    def test_idx_description_empty(self):
        organization = Organization()
        assert organization.idx_description == ""

    def test_idx_description_none(self):
        """Tests the idx_description property returns an empty string when description is None."""
        organization = Organization(description=None)
        assert organization.idx_description == ""

    def test_idx_collaborators_count(self, mocker):
        mock_repository_filter = mocker.patch(
            "apps.github.models.repository.Repository.objects.filter"
        )
        mock_repository_contributor_filter = mocker.patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects.filter"
        )

        organization = Organization(name="Organization Name", login="login", collaborators_count=0)

        mock_repository_filter.return_value.exists.return_value = False
        assert organization.idx_collaborators_count == 0

        mock_repository_filter.return_value.exists.return_value = True

        contributor_query = mock_repository_contributor_filter.return_value.values.return_value
        contributor_query.distinct.return_value.count.return_value = EXPECTED_CONTRIBUTOR_COUNT

        assert organization.idx_collaborators_count == EXPECTED_CONTRIBUTOR_COUNT

        mock_repository_filter.assert_called_with(organization=organization)
        mock_repository_contributor_filter.assert_called_with(
            repository__in=mock_repository_filter.return_value
        )
