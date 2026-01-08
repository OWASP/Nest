from unittest.mock import MagicMock

from apps.github.models import User as GithubUser
from apps.mentorship.models import Mentee


class TestMentee:
    def test_str_returns_github_login(self):
        github_user = MagicMock(spec=GithubUser, login="test_mentee")

        mentee = MagicMock(spec=Mentee)
        mentee.github_user = github_user

        assert Mentee.__str__(mentee) == "test_mentee"
