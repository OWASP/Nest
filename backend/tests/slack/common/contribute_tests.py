import pytest

from apps.slack.common.contribute import project_issues_url, projects_url, get_absolute_url

class TestProjectURLs:
    @pytest.mark.parametrize(
        ("expected_project_issues_url","expected_projects_url"),
        [
            ("projects/contribute","projects"),
        ],
    )
    def test_url(self, expected_project_issues_url, expected_projects_url):
        assert project_issues_url == get_absolute_url(expected_project_issues_url)
        assert projects_url == get_absolute_url(expected_projects_url)
