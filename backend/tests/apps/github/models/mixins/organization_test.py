import pytest

from apps.github.models.organization import Organization

EXPECTED_CONTRIBUTOR_COUNT = 5


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

    def test_is_indexable(self):
        organization = Organization(name="Organization Name", login="login")
        assert organization.is_indexable

        organization = Organization(login="login")
        assert not organization.is_indexable

        organization = Organization(name="Organization Name")
        assert not organization.is_indexable

        organization = Organization()
        assert not organization.is_indexable

    def test_idx_description_with_value(self):
        organization = Organization(description="Organization Description")
        assert organization.idx_description == "Organization Description"

    def test_idx_description_empty(self):
        organization = Organization()
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
