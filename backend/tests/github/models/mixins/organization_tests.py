from apps.github.models.organization import Organization


class TestOrganizationIndexMixin:
    def test_organization_index(self):
        organization = Organization(
            name="Organization Name", login="login", company="Company", location="Location"
        )

        assert organization.idx_name == "Organization Name login"
        assert organization.idx_company == "Company Location"
