"""Tests for AI agent tools."""

from unittest.mock import patch

from apps.ai.agents.contribution.tools.contribute_info import get_contribute_info
from apps.ai.agents.project.tools.get_flagship_projects import get_flagship_projects


class TestProjectTools:
    """Test cases for project agent tools."""

    def test_get_flagship_projects_default_limit(self):
        """Test getting flagship projects with default limit of 15."""
        mock_hits = [
            {
                "idx_name": f"Project {i}",
                "idx_level": "flagship",
                "idx_summary": f"Summary {i}",
                "idx_url": f"https://owasp.org/p{i}",
                "idx_stars_count": 10,
                "idx_contributors_count": 5,
            }
            for i in range(25)
        ]
        with patch(
            "apps.ai.agents.project.tools.get_flagship_projects.get_projects",
            return_value={"hits": mock_hits},
        ) as mock_get_projects:
            result = get_flagship_projects.run()
            mock_get_projects.assert_called_once_with("", limit=100)

            assert "Project 0" in result
            assert "Project 14" in result
            assert "Project 15" not in result

    def test_get_flagship_projects_custom_limit_and_cap(self):
        """Test custom limit and maximum cap of 30."""
        mock_hits = [
            {
                "idx_name": f"Project {i}",
                "idx_level": "flagship",
                "idx_summary": f"Summary {i}",
                "idx_url": f"https://owasp.org/p{i}",
            }
            for i in range(35)
        ]
        with patch(
            "apps.ai.agents.project.tools.get_flagship_projects.get_projects",
            return_value={"hits": mock_hits},
        ) as mock_get_projects:
        
            result_25 = get_flagship_projects.run(limit=25)
            assert "Project 24" in result_25
            assert "Project 25" not in result_25

            # Test upper cap of 30
            result_capped = get_flagship_projects.run(limit=50)
            assert "Project 29" in result_capped
            assert "Project 30" not in result_capped

            # Test boundary inputs 
            result_zero = get_flagship_projects.run(limit=0)
            assert "No projects found at Flagship level." in result_zero

            result_neg = get_flagship_projects.run(limit=-1)
            assert "No projects found at Flagship level." in result_neg

            mock_get_projects.assert_called_with("", limit=100)
            assert mock_get_projects.call_count == 4

    def test_get_flagship_projects_filters_non_flagship(self):
        """Test that non-flagship, None, and missing level projects are filtered out."""
        mock_hits = [
            {
                "idx_name": "Flagship Project",
                "idx_level": "flagship",
                "idx_url": "https://owasp.org/f",
            },
            {
                "idx_name": "Lab Project",
                "idx_level": "lab",
                "idx_url": "https://owasp.org/l",
            },
            {
                "idx_name": "Incubator Project",
                "idx_level": "incubator",
                "idx_url": "https://owasp.org/i",
            },
            {
                "idx_name": "None Level Project",
                "idx_level": None,
                "idx_url": "https://owasp.org/n",
            },
            {
                "idx_name": "Missing Level Project",
                "idx_url": "https://owasp.org/m",
            },
            {
                "idx_name": "Non-String Level Project",
                "idx_level": 123,
                "idx_url": "https://owasp.org/int",
            },
        ]
        with patch(
            "apps.ai.agents.project.tools.get_flagship_projects.get_projects",
            return_value={"hits": mock_hits},
        ) as mock_get_projects:
            result = get_flagship_projects.run()
            mock_get_projects.assert_called_once_with("", limit=100)
            assert "Flagship Project" in result
            assert "Lab Project" not in result
            assert "Incubator Project" not in result
            assert "None Level Project" not in result
            assert "Missing Level Project" not in result
            assert "Non-String Level Project" not in result

    def test_get_flagship_projects_empty(self):
        """Test when no flagship projects are returned."""
        with patch(
            "apps.ai.agents.project.tools.get_flagship_projects.get_projects",
            return_value={"hits": []},
        ) as mock_get_projects:
            result = get_flagship_projects.run()
            mock_get_projects.assert_called_once_with("", limit=100)
            assert "No projects found at Flagship level." in result


class TestContributionTools:
    """Test cases for contribution agent tools."""

    def test_get_contribute_info(self):
        """Test contribution info tool renders template with channel suggestion."""
        result = get_contribute_info.run()
        assert "#contribute" in result
        assert "CONTRIBUTING.md" in result
        assert "Contributing to OWASP Nest" in result
