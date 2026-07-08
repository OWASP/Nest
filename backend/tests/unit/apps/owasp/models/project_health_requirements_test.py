import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class TestProjectHealthRequirementsModel:
    """Unit tests for ProjectHealthRequirements model validation and behavior."""

    VALID_LEVELS = ProjectLevel.values
    INVALID_LEVEL = "invalid_level"
    POSITIVE_INTEGER_FIELDS = [
        "contributors_count",
        "age_days",
        "forks_count",
        "last_release_days",
        "last_commit_days",
        "open_issues_count",
        "open_pull_requests_count",
        "owasp_page_last_update_days",
        "last_pull_request_days",
        "recent_releases_count",
        "recent_releases_time_window_days",
        "stars_count",
        "total_pull_requests_count",
        "total_releases_count",
        "unanswered_issues_count",
        "unassigned_issues_count",
    ]

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            (ProjectLevel.FLAGSHIP, "Health Requirements for Flagship Projects"),
            (ProjectLevel.INCUBATOR, "Health Requirements for Incubator Projects"),
            (ProjectLevel.LAB, "Health Requirements for Lab Projects"),
            (ProjectLevel.OTHER, "Health Requirements for Other Projects"),
            (ProjectLevel.PRODUCTION, "Health Requirements for Production Projects"),
            ("", "Health Requirements for  Projects"),
        ],
    )
    def test_str_representation(self, level, expected):
        assert str(ProjectHealthRequirements(level=level)) == expected

    @pytest.mark.parametrize("field", POSITIVE_INTEGER_FIELDS)
    def test_positive_integer_fields_default_to_zero(self, field):
        assert getattr(ProjectHealthRequirements(), field) == 0

    @pytest.mark.parametrize("level", VALID_LEVELS)
    def test_valid_level_choices(self, level):
        requirements = ProjectHealthRequirements(level=level)
        requirements.clean_fields(exclude=[])

    @pytest.mark.parametrize("invalid_level", [INVALID_LEVEL, None])
    def test_invalid_level_raises_error(self, invalid_level):
        requirements = ProjectHealthRequirements(level=invalid_level)
        with pytest.raises(ValidationError) as exc:
            requirements.clean_fields(exclude=[])
        assert "level" in exc.value.error_dict
