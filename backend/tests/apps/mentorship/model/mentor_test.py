from unittest.mock import MagicMock

from apps.github.models import User as GithubUser
from apps.mentorship.models import Mentor


class TestMentor:
    def test_str_returns_github_login(self):
        github_user = MagicMock(spec=GithubUser, login="test_mentor")

        mentor = MagicMock(spec=Mentor)
        mentor.github_user = github_user

        assert Mentor.__str__(mentor) == "test_mentor"
