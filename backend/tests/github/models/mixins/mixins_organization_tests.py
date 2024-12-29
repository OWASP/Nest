from apps.github.models.organization import Organization


class TestOrganizationMixin:
    def test_idx_name(self):
        organization = Organization(name="Organization Name", login="login")
        assert organization.idx_name == "Organization Name login"

    def test_idx_company(self):
        organization = Organization(company="Company", location="Location")
        assert organization.idx_company == "Company Location"
