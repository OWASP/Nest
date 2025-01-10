import pytest

from apps.slack.common.contribute import (
    get_absolute_url,
    project_issues_url,
    projects_url,
)


class TestContribute:
    @pytest.mark.parametrize(
        ("expected_project_issues_url", "expected_projects_url"),
        [
            ("projects/contribute", "projects"),
        ],
    )
    def test_urls(self, expected_project_issues_url, expected_projects_url):
        assert project_issues_url == get_absolute_url(expected_project_issues_url)
        assert projects_url == get_absolute_url(expected_projects_url)
